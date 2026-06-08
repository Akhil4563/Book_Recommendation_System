# 📚 BookMind — AI Book Recommendation System
 
> An intelligent book recommendation engine powered by NLP, sentiment analysis, graph-based entity linking, and AI-driven summarization — with a sleek literary-themed frontend.
 
![Python](https://img.shields.io/badge/Python-3.11-blue) ![Flask](https://img.shields.io/badge/Flask-REST%20API-green) ![NLP](https://img.shields.io/badge/NLP-BART%20%7C%20LDA%20%7C%20NetworkX-orange) ![Frontend](https://img.shields.io/badge/Frontend-HTML%20%7C%20CSS%20%7C%20JS-purple)
 
---
 
## 👤 My Role — Project Manager
 
**Name:** Akhil Vijayan
**Role:** Project Manager
**Type:** University Capstone Project — University of Ottawa
 
This was a academic capstone project where I took on the Project Manager role within a small team. My responsibilities included:
 
- 📋 **Requirements & Scope** — Defined the project idea, scope, and functional requirements for the recommendation engine and chatbot interface
- 🗓️ **Sprint Planning** — Organised development into sprints, set milestones, and kept the team on track to deliver
- 👥 **Team Coordination** — Coordinated between team members handling ML, backend, data, and frontend to ensure everything came together
- 🚀 **Deployment Oversight** — Managed the deployment process including backend setup and frontend hosting on Vercel
- 🧪 **QA & Testing** — Coordinated testing across the full stack and ensured the system worked end to end
- 📝 **Documentation** — Authored all project documentation including this README, API reference, and system architecture
---
 
## 🌐 Live Demo
 
- **Frontend:** [bookmind.vercel.app](https://bookmind.vercel.app)
- **Backend API:** Powered by Flask + Gunicorn
- **📄 Project Documentation:** [Download Full Dev Doc](https://brs-front-end.vercel.app/documents/BRS_Dev_Doc.docx)
---
 
## 📖 About
 
BookMind is a full-stack AI application that allows users to discover books, explore reader sentiment, and receive intelligent recommendations — all through a natural language interface.
 
It processes a dataset of **25,000+ books**, extracts entities and topics using graph networks and LDA topic modeling, and generates human-readable summaries using Facebook's **BART** transformer model.
 
---
 
## ✨ Features
 
| Feature | Description |
|---|---|
| 📖 Book Information | Returns author, sentiment overview, and key metadata |
| 😊 Positive Reviews | AI-summarized positive reviews with the highest-rated review |
| 😞 Negative Reviews | AI-summarized negative reviews with the lowest-rated review |
| 🔗 Similar Books | Graph-based entity matching to find related books |
| 🏷️ Review Topics | LDA topic modeling to surface key themes from reviews |
| 💬 Chat Interface | Conversational AI that detects intent from natural language |
| ⚡ Real-time WebSocket | Live communication via Flask-SocketIO |
| 🌐 Webhook Integration | Dialogflow-compatible REST webhook endpoint |
 
---
 
## 🏗️ Architecture
 
```
┌─────────────────────────┐        ┌──────────────────────────────┐
│   BookMind Frontend      │──────▶│   Flask Webhook / SocketIO   │
│   (Vercel)               │        │   (Backend Server)           │
└─────────────────────────┘        └──────────────┬───────────────┘
                                                   │
                                   ┌───────────────▼───────────────┐
                                   │      book_recommendation.py   │
                                   │  - Sentiment Analysis         │
                                   │  - BART Summarization         │
                                   │  - Graph Recommendations      │
                                   │  - LDA Topic Modeling         │
                                   └───────────────┬───────────────┘
                                                   │
                                   ┌───────────────▼───────────────┐
                                   │        DataProcessing.py      │
                                   │  - 25,000 Books Dataset       │
                                   │  - NetworkX Knowledge Graph   │
                                   │  - Gensim LDA Model           │
                                   │  - MySQL Database             │
                                   └───────────────────────────────┘
```
 
---
 
## 🛠️ Tech Stack
 
### Backend
- **Python 3.11**
- **Flask** — REST API framework
- **Flask-SocketIO** — WebSocket real-time communication
- **Flask-CORS** — Cross-origin resource sharing
- **HuggingFace Transformers** — `facebook/bart-large-cnn` for AI summarization
- **NetworkX** — Graph-based entity relationship modeling
- **Gensim** — LDA topic modeling
- **Pandas** — Data processing and manipulation
- **MySQL** — Book data storage
- **Gunicorn** — Production WSGI server
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
├── application.py              # Flask app — webhook + WebSocket server
├── book_recommendation.py      # Core NLP logic
├── DataProcessing.py           # Data pipeline
├── import_csv_to_mysql.py      # CSV → MySQL import utility
│
├── 25000_books.csv             # Raw book dataset
├── cleaned_books.csv           # Preprocessed dataset
├── requirements.txt            # Python dependencies
├── .python-version             # Python 3.11 pin
└── .gitignore
```
 
---
 
## 🚀 Getting Started
 
### Prerequisites
- Python 3.11
- MySQL database running locally
- pip
### Backend Setup
 
```bash
# 1. Clone the repository
git clone https://github.com/Akhil4563/Book_Recommendation_System.git
cd Book_Recommendation_System
 
# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
 
# 3. Install dependencies
pip install -r requirements.txt
 
# 4. Start MySQL and import book data
python import_csv_to_mysql.py
 
# 5. Run the application
python application.py
```
 
Server starts on `http://localhost:5000`
 
### Frontend Setup
 
Open `frontend/index.html` in a browser, or deploy to Vercel.
 
---
 
## 📡 API Reference
 
### Webhook Endpoint
 
**`POST /webhook`**
 
| Intent | Action |
|---|---|
| `General Information` | Returns book sentiment and author |
| `PositiveFeedback` | Returns summarized positive reviews |
| `NegativeFeedback` | Returns summarized negative reviews |
| `SimilarBooksEntites` | Returns top 5 similar books |
| `ReviewTopics` | Returns key themes from reviews |
 
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
  "fulfillmentText": "Feedback for 'afterworld':\nOverall sentiment: Positive\nThe book is written by Jane Doe.\n"
}
```
 
---
 
## 🤖 How the AI Works
 
1. **Data Processing** — Raw CSV is cleaned, entities extracted, and a NetworkX knowledge graph links books to authors, genres, and named entities
2. **Sentiment Analysis** — Each book's reviews are scored and aggregated into positive/negative feedback pools
3. **LDA Topic Modeling** — Gensim LDA identifies the main themes discussed across reviews
4. **BART Summarization** — Facebook's `bart-large-cnn` generates concise summaries from raw review text
5. **Graph Recommendations** — Similar books are found by matching common entities in the knowledge graph
---
 
## 👥 Team
 
> Created by Students of the University of Ottawa
 
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
 
- [HuggingFace](https://huggingface.co/) for the BART transformer model
- [Gensim](https://radimrehurek.com/gensim/) for topic modeling
- [NetworkX](https://networkx.org/) for graph-based entity linking
- [Google Dialogflow](https://cloud.google.com/dialogflow) for conversational AI integration
 
