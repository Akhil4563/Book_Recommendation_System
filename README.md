## 🌐 Live Demo
 
- **Frontend (Vercel):** [bookmind-two.vercel.app](https://bookmind-two.vercel.app)
- **Backend API (Render):** [book-recommendation-system-8qdz.onrender.com](https://book-recommendation-system-8qdz.onrender.com)
> ⚠️ **Note:** The backend runs on Render's free tier, which sleeps after 15 minutes of inactivity. The **first** request after an idle period takes ~50 seconds while the server wakes up — the frontend shows a "Waking server…" status during this time. Subsequent requests are fast.
 
---
 
## 📖 About
 
BookMind is a full-stack AI application that lets users discover books, explore reader sentiment, and receive intelligent recommendations through a natural-language chat interface.
 
It is built on a dataset of **13,669 unique book titles** and **24,713 reader reviews**. The system scores review sentiment, models discussion topics with LDA, generates extractive review summaries, and finds related titles using content-based similarity.
 
### 🔑 Architecture Highlight — Offline Precompute
 
The original prototype ran all NLP **live** on each request (a 1.6 GB transformer model plus a live database). This made it impossible to host on any free tier due to memory and build-size limits.
 
The system was **re-architected around an offline precompute step**: all heavy NLP is run once ahead of time (`precompute_data.py`) and the results are baked into a single compressed data file (`book_data.json.gz`, ~5.5 MB). The deployed backend simply loads this file and serves answers — booting in seconds and staying well under the 512 MB free-tier memory limit.
 
This is the same idea as a kitchen prepping ingredients in advance instead of cooking every dish from scratch on order: identical output, a fraction of the runtime footprint.
 
---
 
## ✨ Features
 
| Feature | Description |
|---|---|
| 📖 Book Information | Returns author, publisher, category, average rating, and an overall sentiment read |
| 😊 Positive Reviews | Extractive summary of positive reviews plus the highest-sentiment real review |
| 😞 Negative Reviews | Extractive summary of negative reviews plus the lowest-sentiment real review |
| 🔗 Similar Books | Content-based similarity (TF-IDF) re-ranked by shared entities and author |
| 🏷️ Review Topics | LDA topic modeling to surface key themes across reviews |
| 💬 Chat Interface | Conversational UI that maps natural language to intents |
| 🔎 Fuzzy Title Matching | Forgiving lookup — handles partial titles and minor misspellings |
| 🌐 Webhook Integration | Dialogflow-compatible REST webhook endpoint |
 
---
 
## 🏗️ Architecture
 
```
  OFFLINE (run once, locally)
┌──────────────────────────────────────────────┐
│              precompute_data.py               │
│  ┌──────────────────────────────────────────┐ │
│  │  cleaned_books.csv + 25000_books.csv     │ │
│  │  • TextBlob sentiment scoring            │ │
│  │  • Extractive review summaries           │ │
│  │  • Entity extraction (spaCy NER /        │ │
│  │    heuristic fallback)                   │ │
│  │  • Gensim LDA topic modeling             │ │
│  │  • TF-IDF + NearestNeighbors similarity  │ │
│  └──────────────────────────────────────────┘ │
│                      │                         │
│                      ▼                         │
│            book_data.json.gz (~5.5 MB)         │
└──────────────────────────────────────────────┘
                       │  committed to repo
                       ▼
  RUNTIME (deployed, free tier)
┌─────────────────────────┐      ┌──────────────────────────────┐
│   BookMind Frontend     │─────▶│   Flask Webhook / SocketIO   │
│   (Vercel, static HTML) │◀─────│   (Render, loads .json.gz)   │
└─────────────────────────┘      └──────────────────────────────┘
```
 
---
 
## 🛠️ Tech Stack
 
### Runtime Backend (deployed)
- **Python 3.11**
- **Flask** — REST API framework
- **Flask-CORS** — Cross-origin resource sharing
- **Flask-SocketIO** — WebSocket support
- **Gunicorn + gevent** — Production WSGI server
- **Render** — Free-tier backend hosting
### Offline Precompute Pipeline
- **Pandas** — Data processing
- **TextBlob** — Sentiment analysis
- **Gensim** — LDA topic modeling
- **scikit-learn** — TF-IDF vectorization + NearestNeighbors similarity
- **NLTK** — Text cleaning, stopwords, lemmatization
- **spaCy** *(optional)* — Named-entity recognition, with a heuristic fallback when the model isn't installed
### Frontend
- **HTML5 / CSS3 / JavaScript** — Pure static frontend
- **Playfair Display + DM Sans** — Literary typography
- **Vercel** — Frontend hosting
---
 
## 📁 Project Structure
 
```
Book_Recommendation_System/
│
├── frontend/
│   ├── index.html              # Full frontend UI
│   └── vercel.json             # Vercel static config
│
├── application.py              # Flask app — loads book_data.json.gz, serves intents
├── precompute_data.py          # Offline NLP pipeline (run once to build the data file)
├── book_data.json.gz           # Precomputed results (sentiment, topics, summaries, similarity)
│
├── 25000_books.csv             # Raw review dataset
├── cleaned_books.csv           # Preprocessed book dataset
├── requirements.txt            # Runtime Python dependencies (lightweight)
├── .python-version             # Python 3.11 pin
└── .gitignore
```
 
---
 
## 🚀 Getting Started
 
### Prerequisites
- Python 3.11
- pip
### Option A — Run the deployed backend locally (fast)
 
The precomputed data file is already in the repo, so you only need the lightweight runtime dependencies:
 
```bash
# 1. Clone the repository
git clone https://github.com/Akhil4563/Book_Recommendation_System.git
cd Book_Recommendation_System
 
# 2. Install runtime dependencies
pip install -r requirements.txt
 
# 3. Run the application
python application.py
```
 
Server starts on `http://localhost:5000`.
 
### Option B — Rebuild the data file from scratch
 
To regenerate `book_data.json.gz` from the raw CSVs:
 
```bash
# Install the precompute dependencies
pip install pandas scikit-learn gensim textblob nltk
# (optional, for true NER) python -m spacy download en_core_web_sm
 
# Run the offline pipeline (~1-2 minutes)
python precompute_data.py
```
 
### Frontend
 
Open `frontend/index.html` in a browser, or deploy the `frontend/` folder to Vercel with **Framework Preset = Other** and **Root Directory = frontend**. Set the backend URL near the top of the `<script>` block:
 
```javascript
window.BACKEND_URL = 'https://book-recommendation-system-8qdz.onrender.com';
```
 
---
 
## ☁️ Deployment
 
### Backend — Render (free tier)
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn -k gevent -w 1 application:app`
- **Instance Type:** Free
### Frontend — Vercel (free tier)
- **Framework Preset:** Other
- **Root Directory:** `frontend`
- Auto-redeploys on every push to `main`.
---
 
## 📡 API Reference
 
### Webhook Endpoint
 
**`POST /webhook`** (also accepts `POST /`)
 
| Intent | Action |
|---|---|
| `General Information` | Returns author, metadata, and sentiment overview |
| `PositiveFeedback` | Returns an extractive summary of positive reviews + top review |
| `NegativeFeedback` | Returns an extractive summary of negative reviews + lowest review |
| `SimilarBooksEntites` | Returns top similar books |
| `ReviewTopics` | Returns key themes from reviews |
 
**Health check:** `GET /` returns service status and dataset counts.
 
**Example Request:**
```json
{
  "queryResult": {
    "intent": { "displayName": "General Information" },
    "parameters": { "booktitle": "afterworld" }
  }
}
```
 
**Example Response:**
```json
{
  "fulfillmentText": "Feedback for 'Afterworld':\nOverall sentiment: Positive\nThe book is written by '...'.\n..."
}
```
 
---
 
## 🤖 How the NLP Works
 
1. **Data Cleaning** — Raw review CSVs are cleaned and joined to the book spine (lowercasing, punctuation/digit stripping, NLTK stopword removal, lemmatization).
2. **Sentiment Analysis** — Each book's reviews are scored with TextBlob and aggregated into positive/negative pools with an overall sentiment read.
3. **Extractive Summaries** — Representative sentences are selected from real reviews via word-frequency scoring. *(This replaces the original prototype's generative BART summaries — a deliberate tradeoff to fit the free-tier memory budget while keeping summaries grounded in real reader text.)*
4. **Entity Extraction** — Named entities are extracted with spaCy NER where available, falling back to a capitalized-phrase heuristic.
5. **LDA Topic Modeling** — Gensim LDA identifies the main themes discussed across reviews (7 topics).
6. **Content-Based Similarity** — TF-IDF vectors + cosine NearestNeighbors find candidate similar books, re-ranked by shared entities and same-author bonus.
---
 
## 👥 Team
 
> Created by students of the University of Ottawa
 
| Name | Role |
|---|---|
| **Akhil Vijayan** | Project Manager |
| **Milad Kianzadah** | Backend Developer |
| **Sharini Rithigaa Baranisrinivasan Sumalatha** | Full Stack Developer |
 
---
 
## 📄 License
 
This project is open source and available under the [MIT License](LICENSE).
 
---
 
## 🙏 Acknowledgements
 
- [Gensim](https://radimrehurek.com/gensim/) for topic modeling
- [TextBlob](https://textblob.readthedocs.io/) for sentiment analysis
- [scikit-learn](https://scikit-learn.org/) for TF-IDF similarity
- [spaCy](https://spacy.io/) for named-entity recognition
- [Google Dialogflow](https://cloud.google.com/dialogflow) for the webhook contract
 
