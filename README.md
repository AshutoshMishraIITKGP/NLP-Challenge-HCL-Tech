# Agentic RAG System with Web Interface

An intelligent IT/HR support system combining Retrieval-Augmented Generation (RAG) with agentic workflows for automated ticket generation, meeting scheduling, and leave requests.

## 🎯 Overview

This system provides:
- **Information Retrieval**: Query PDF documents using natural language
- **Action Generation**: Automatically create IT tickets, schedule HR meetings, and request leave
- **Web Interface**: ChatGPT-like UI for conversational interactions
- **Conversational Ticket Editing**: Modify tickets through natural language

## 📁 Directory Structure

```
NLP challenge/
├── data/
│   ├── pdf/                    # Source PDF files
│   ├── raw_text/               # Extracted text with page markers
│   ├── structured_blocks/      # JSON blocks with metadata
│   ├── chunks/                 # CDFG chunked data
│   └── faiss_cache/            # Vector index storage (index.faiss, metadata.pkl)
├── src/
│   ├── agent/                  # Agent orchestration and action generation
│   │   ├── orchestrator.py     # Main agent orchestrator
│   │   ├── action_generator.py # Action JSON generation
│   │   └── intent_router.py    # Intent classification
│   ├── embeddings/             # FAISS index building
│   │   └── build_faiss_index.py
│   ├── ingestion/              # Data ingestion pipeline
│   │   ├── pdf_to_text.py      # PDF extraction
│   │   ├── block_extraction.py # Block identification
│   │   └── cdfg_chunker.py     # Context-aware chunking
│   ├── rag/                    # RAG answer generation
│   │   ├── answer_generator.py # Answer synthesis
│   │   └── prompts.py          # System prompts
│   ├── retrieval/              # Vector retrieval
│   │   └── retrieval.py        # FAISS retrieval logic
│   └── utils/                  # Utility modules
│       ├── confirmation.py     # User confirmation classifier
│       ├── description_enhancer.py # Ticket description enhancement
│       └── logger.py           # Logging utilities
├── static/                     # Frontend assets
│   ├── app.js                  # Frontend JavaScript
│   └── style.css               # UI styling
├── templates/
│   └── index.html              # Main web interface
├── user_requests/              # Generated ticket JSONs
├── logs/                       # System logs
├── app.py                      # CLI version
├── backend_api.py              # FastAPI backend
├── web_server.py               # Flask frontend server
├── start_web.bat               # Windows startup script
├── run_pipeline.py             # Data ingestion pipeline
└── requirements.txt            # Python dependencies
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Mistral API Key

### Step 1: Clone and Install Dependencies

```bash
# Navigate to project directory
cd "NLP challenge"

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Environment

Create a `.env` file in the root directory:

```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

### Step 3: Prepare Data (If using your own PDF)

```bash
# Run the complete ingestion pipeline
python run_pipeline.py
```

This will:
1. Extract text from PDFs in `data/pdf/`
2. Create structured blocks in `data/structured_blocks/`
3. Generate chunks in `data/chunks/`
4. Build FAISS index in `data/faiss_cache/`

**Note**: The repository already includes pre-processed data for `Annual-Report-2024-25.pdf`

### Step 4: Start the Application

#### Option A: Web Interface (Recommended)

```bash
# Windows
start_web.bat

# Manual start (any OS)
# Terminal 1: Start backend
python backend_api.py

# Terminal 2: Start frontend
python web_server.py
```

Access the web interface at: `http://localhost:5000`

#### Option B: CLI Version

```bash
python app.py
```

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                        Web Interface                         │
│                    (Flask + JavaScript)                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                             │
│                      (FastAPI)                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Orchestrator                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Intent Router│  │ RAG Pipeline │  │Action Generator│     │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Retriever  │ │  Mistral LLM │ │ Confirmation │
│   (FAISS)    │ │              │ │  Classifier  │
└──────────────┘ └──────────────┘ └──────────────┘
```

### Data Flow

1. **User Query** → Web Interface
2. **Intent Classification** → Determine if INFO_QUERY or ACTION_REQUEST
3. **Processing**:
   - **INFO_QUERY**: RAG Pipeline → FAISS Retrieval → Answer Generation
   - **ACTION_REQUEST**: Action Generator → Confirmation → Ticket Generation
4. **Ticket Modification Loop**: Natural language modifications via LLM
5. **Export**: Save ticket JSON to `user_requests/`

### Key Technologies

- **LLM**: Mistral AI (mistral-small-2503)
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Backend**: FastAPI
- **Frontend**: Flask + Vanilla JavaScript
- **PDF Processing**: PyPDF2
- **Chunking**: Custom CDFG (Context-Dependent Fragment Generation)

## 🎮 Usage

### Web Interface

1. **Information Query**:
   ```
   User: "What is the revenue for FY25?"
   System: [Retrieves from PDF and provides answer]
   ```

2. **Action Request - IT Ticket**:
   ```
   User: "My laptop is not connecting to WiFi"
   System: "I understand you're facing a WiFi connectivity issue. Do you want me to create an IT ticket?"
   User: "yes"
   System: [Generates ticket with fields]
   User: "make priority high and add date 17th Jan 2026"
   System: [Updates ticket]
   User: "looks good"
   System: "Ticket exported to user_requests/ticket_20260116_123456.json"
   ```

3. **Action Request - HR Meeting**:
   ```
   User: "I need to schedule a meeting with HR"
   System: "Do you want me to proceed with scheduling an HR meeting?"
   User: "yes"
   System: [Generates meeting request]
   ```

4. **Action Request - Leave**:
   ```
   User: "I want to apply for leave"
   System: "Do you want me to submit a leave request?"
   User: "yes"
   System: [Generates leave request]
   User: "start date 20th Jan, end date 25th Jan, reason is medical"
   System: [Updates leave request]
   ```

### CLI Version

```bash
python app.py
```

Follow the interactive prompts for queries and actions.

## 🔧 Configuration

### Modify Action Types

Edit `src/agent/action_generator.py` to add new action types:

```python
ACTIONS = {
    "create_it_ticket": {...},
    "schedule_hr_meeting": {...},
    "request_leave": {...},
    "your_new_action": {...}  # Add here
}
```

### Adjust Retrieval Parameters

Edit `src/retrieval/retrieval.py`:

```python
def retrieve(self, query, top_k=5):  # Change top_k
    ...
```

### Customize Prompts

Edit `src/rag/prompts.py` for RAG system prompts.

## 📊 Data Ingestion Pipeline

### CDFG Chunking Strategy

- **Token-aware**: Chunks respect token limits (default: 512 tokens)
- **Context preservation**: Overlapping chunks maintain context
- **Metadata tracking**: Page numbers and block IDs preserved
- **Semantic boundaries**: Respects document structure

### Pipeline Steps

1. **PDF to Text** (`pdf_to_text.py`):
   - Extracts text page-by-page
   - Adds page markers
   - Outputs to `data/raw_text/`

2. **Block Extraction** (`block_extraction.py`):
   - Identifies headings, paragraphs, tables
   - Creates structured JSON
   - Outputs to `data/structured_blocks/`

3. **CDFG Chunking** (`cdfg_chunker.py`):
   - Token-aware chunking
   - Overlap strategy
   - Outputs to `data/chunks/`

4. **FAISS Index Building** (`build_faiss_index.py`):
   - Generates embeddings
   - Builds vector index
   - Outputs to `data/faiss_cache/`

## 🔍 Troubleshooting

### Issue: "Information not available in the knowledge base"

- Ensure FAISS index is built: Check `data/faiss_cache/index.faiss` exists
- Verify chunks exist: Check `data/chunks/` has JSON files
- Rebuild index: `python src/embeddings/build_faiss_index.py`

### Issue: Backend not starting

- Check Mistral API key in `.env`
- Verify port 8000 is available
- Check logs in `logs/` directory

### Issue: Frontend not loading

- Verify backend is running on port 8000
- Check port 5000 is available
- Clear browser cache

## 📝 API Endpoints

### POST /chat

Request:
```json
{
  "query": "user message",
  "chat_id": "chat_123456",
  "conversation_history": [...],
  "pending_action": {...},
  "pending_state": "awaiting_modification",
  "original_query": "original user query"
}
```

Response:
```json
{
  "type": "TICKET_GENERATED",
  "content": {...},
  "pending_action": {...},
  "pending_state": "awaiting_modification",
  "original_query": "..."
}
```

### GET /health

Returns: `{"status": "ok"}`

## 🛠️ Development

### Adding New Features

1. **New Action Type**: Edit `action_generator.py`
2. **New Intent**: Edit `intent_router.py`
3. **Custom Prompts**: Edit `prompts.py`
4. **UI Changes**: Edit `static/app.js` and `static/style.css`

### Logging

Logs are stored in `logs/system_YYYYMMDD_HHMMSS.log`

## 📦 Dependencies

Core dependencies:
- `fastapi` - Backend API
- `uvicorn` - ASGI server
- `flask` - Frontend server
- `mistralai` - LLM API
- `faiss-cpu` - Vector search
- `sentence-transformers` - Embeddings
- `PyPDF2` - PDF processing
- `tiktoken` - Token counting

See `requirements.txt` for complete list.

## 🎨 UI Features

- **Multi-chat support**: Create and switch between multiple conversations
- **Chat persistence**: Conversations saved in browser localStorage
- **Delete chats**: Hover over chat to show delete button
- **Red/Black theme**: Modern, professional interface
- **Responsive design**: Works on desktop and mobile

## 📄 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

This is a hackathon project. For improvements, modify the code directly.

## 📧 Support

Check logs in `logs/` directory for debugging information.
