import difflib
import gzip
import json
import logging
import os
import re

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("bookmind")

# ----------------------------------------------------------------------
# Flask + CORS + SocketIO (open CORS so the Vercel frontend can connect)
# ----------------------------------------------------------------------
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# ----------------------------------------------------------------------
# Load the precomputed bundle once at startup
# ----------------------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "book_data.json.gz")

log.info("Loading %s ...", DATA_PATH)
with gzip.open(DATA_PATH, "rt", encoding="utf-8") as f:
    BUNDLE = json.load(f)

META = BUNDLE["meta"]
BOOKS = BUNDLE["books"]                      # cleaned-title -> record
TOPIC_OF = BUNDLE["topic_of"]                # cleaned-title -> topic id
TOPICS = META.get("topics", {})              # topic id -> {words, summary}

# Alias map: lowercase display titles -> canonical cleaned key
ALIAS = {}
for key, rec in BOOKS.items():
    ALIAS[key] = key
    dt_low = re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", rec["dt"].lower())).strip()
    ALIAS.setdefault(dt_low, key)

ALIAS_KEYS = list(ALIAS.keys())
log.info("Loaded %d books, %d reviews analysed.",
         META.get("books_indexed", len(BOOKS)), META.get("reviews_analyzed", 0))


# ----------------------------------------------------------------------
# Forgiving title lookup: exact -> substring -> fuzzy
# ----------------------------------------------------------------------
def normalise(q: str) -> str:
    q = str(q or "").lower()
    q = re.sub(r"[^\w\s]", " ", q)
    return re.sub(r"\s+", " ", q).strip()


def find_book(query: str):
    """Return (canonical_key, matched_exactly) or (None, False)."""
    q = normalise(query)
    if not q:
        return None, False
    if q in ALIAS:
        return ALIAS[q], True

    # substring containment, prefer the closest length.
    # Query-in-title always allowed; title-in-query only for titles of 5+ chars
    # (otherwise a book called "Q" matches any query containing the letter q).
    candidates = [k for k in ALIAS_KEYS
                  if (len(q) >= 4 and q in k) or (len(k) >= 5 and k in q)]
    if candidates:
        best = min(candidates, key=lambda k: abs(len(k) - len(q)))
        return ALIAS[best], False

    # fuzzy match as a last resort
    close = difflib.get_close_matches(q, ALIAS_KEYS, n=1, cutoff=0.78)
    if close:
        return ALIAS[close[0]], False
    return None, False


def not_found_text(query: str) -> str:
    samples = META.get("sample_titles", [])[:6]
    hint = ", ".join(samples) if samples else "another title"
    return (f"Sorry, I couldn't find \"{query}\" among the "
            f"{META.get('books_indexed', 'many')} books I've analysed. "
            f"Try one of these: {hint}.")


def sentiment_word(score: float) -> str:
    return "Positive" if score > 0.05 else "Negative" if score < -0.05 else "Neutral"


# ----------------------------------------------------------------------
# Intent handlers (all read precomputed fields only)
# ----------------------------------------------------------------------
def prefix_for(query, key, exact):
    rec = BOOKS[key]
    if exact or normalise(query) == normalise(rec["dt"]):
        return ""
    return f"Showing results for \"{rec['dt']}\" (closest match to \"{query}\").\n\n"


def book_information(query):
    key, exact = find_book(query)
    if not key:
        return not_found_text(query)
    b = BOOKS[key]
    lines = [f"Feedback for '{b['dt']}':",
             f"Overall sentiment: {sentiment_word(b['sent'])}",
             f"The book is written by '{b['au']}'."]
    details = []
    if b.get("pub") and b["pub"] != "Unknown publisher":
        details.append(f"published by {b['pub']}")
    if b.get("yr"):
        details.append(f"in {b['yr']}")
    if details:
        lines.append("It was " + " ".join(details) + ".")
    if b.get("cat"):
        lines.append(f"Category: {b['cat']}.")
    lines.append(f"Average reader score: {b['score']}/5 across {b['nrev']} "
                 f"review{'s' if b['nrev'] != 1 else ''} analysed.")
    return prefix_for(query, key, exact) + "\n".join(lines)


def generate_feedback(query, sentiment_type):
    key, exact = find_book(query)
    if not key:
        return not_found_text(query)
    b = BOOKS[key]
    summary = b["psum"] if sentiment_type == "positive" else b["nsum"]
    review = b["best"] if sentiment_type == "positive" else b["worst"]
    if not summary and not review:
        return (prefix_for(query, key, exact) +
                f"Readers left no clearly {sentiment_type} reviews for '{b['dt']}' "
                f"in the data I analysed.")
    out = f"Feedback for '{b['dt']}':\n"
    if summary:
        out += f"Summary of {sentiment_type} reviews: \"{summary}\"\n\n"
    if review:
        out += f"Most {sentiment_type} review: \"{review}\""
    return prefix_for(query, key, exact) + out


def similar_books(query):
    key, exact = find_book(query)
    if not key:
        return not_found_text(query)
    b = BOOKS[key]
    sims = [BOOKS[s]["dt"] for s in b.get("sim", []) if s in BOOKS]
    if not sims:
        return f"I couldn't compute similar books for '{b['dt']}'."
    return prefix_for(query, key, exact) + ", ".join(sims)


def review_topics(query):
    key, exact = find_book(query)
    if not key:
        return not_found_text(query)
    b = BOOKS[key]
    tid = str(TOPIC_OF.get(key, -1))
    topic = TOPICS.get(tid)
    if not topic:
        return f"No topics found for '{b['dt']}'."
    words = ", ".join(f"'{w}'" for w in topic["words"])
    # Use the book's own review summary as the key point, not the topic words again.
    first_sent = (b.get("psum") or b.get("best") or "").split(". ")[0].strip()
    key_points = (f"Key points from reviews:\n{first_sent}."
                  if first_sent else topic.get("summary", ""))
    out = (f"Main topics for '{b['dt']}': [{words}]\n\n{key_points}")
    return prefix_for(query, key, exact) + out


INTENT_MAP = {
    "General Information": book_information,
    "PositiveFeedback": lambda t: generate_feedback(t, "positive"),
    "NegativeFeedback": lambda t: generate_feedback(t, "negative"),
    "SimilarBooksEntites": similar_books,
    "ReviewTopics": review_topics,
}


def handle(intent_name, book_title):
    if not book_title:
        return "Please provide a book title."
    fn = INTENT_MAP.get(intent_name)
    if fn is None:
        return ("Unknown request. Try: General Information, PositiveFeedback, "
                "NegativeFeedback, SimilarBooksEntites, or ReviewTopics.")
    try:
        return fn(str(book_title))
    except Exception:                                    # noqa: BLE001
        log.exception("Error handling intent '%s' for '%s'", intent_name, book_title)
        return "Sorry, something went wrong on the server while handling that request."


# ----------------------------------------------------------------------
# HTTP routes
# ----------------------------------------------------------------------
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "BookMind backend",
        "books_indexed": META.get("books_indexed"),
        "reviews_analyzed": META.get("reviews_analyzed"),
        "data_built": META.get("built"),
        "endpoints": {"POST /webhook": "Dialogflow-style intent requests"},
    })


@app.route("/webhook", methods=["POST"])
@app.route("/", methods=["POST"])
def webhook():
    req = request.get_json(silent=True) or {}
    log.info("Webhook request: %s", req)
    qr = req.get("queryResult", {})
    intent_name = qr.get("intent", {}).get("displayName")
    params = qr.get("parameters", {}) or {}
    book_title = params.get("booktitle") or params.get("book_name") or params.get("any")
    return jsonify({"fulfillmentText": handle(intent_name, book_title)})


# ----------------------------------------------------------------------
# WebSocket events (kept for parity with the original API; the current
# frontend uses plain fetch(), so these are optional extras)
# ----------------------------------------------------------------------
@socketio.on("connect")
def handle_connect():
    log.info("Socket client connected")
    emit("response", {"message": "Connection established!"})


@socketio.on("message")
def handle_message(message):
    log.info("Socket message: %s", message)
    if not isinstance(message, dict):
        emit("response", {"message": "Invalid message format."})
        return
    emit("response", {"message": handle(message.get("intent", ""),
                                        message.get("book_title", ""))})


@socketio.on("disconnect")
def handle_disconnect():
    log.info("Socket client disconnected")


# ----------------------------------------------------------------------
# Local development entry point (Render uses gunicorn instead)
# ----------------------------------------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False,
                 allow_unsafe_werkzeug=True, use_reloader=False)
