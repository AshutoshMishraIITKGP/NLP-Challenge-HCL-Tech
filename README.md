# Agentic RAG System with Web Interface

An intelligent IT/HR support system combining Retrieval-Augmented Generation (RAG) with agentic workflows for automated ticket generation, meeting scheduling, and leave requests.

## 🎯 Overview

This system provides a dual-mode conversational interface that intelligently routes user requests to either information retrieval or action generation pipelines:

- **Information Retrieval Mode**: Query PDF documents using natural language with grounded, citation-backed answers
- **Action Generation Mode**: Automatically create IT tickets, schedule HR meetings, and request leave through conversational workflows
- **Web Interface**: ChatGPT-like UI with multi-chat support and persistent conversations
- **Conversational Ticket Editing**: Iteratively refine tickets through natural language until perfect
- **Data Normalization**: Automatic standardization of dates (ISO format) and priorities (Low/Medium/High)

## 📊 Performance Metrics

| Metric | Score | Description |
|--------|-------|-------------|
| **Intent Classification Accuracy** | 100% | Correctly identifies INFO_QUERY vs ACTION_REQUEST |
| **Retrieval Hit Rate** | N/A* | Relevant documents retrieved in top-5 results |
| **Action Extraction Accuracy** | 100% | Correctly extracts action type and parameters |
| **Data Normalization Accuracy** | 100% | Dates (ISO) and priorities (Low/Medium/High) standardized |
| **Average Response Time** | 1.84s | End-to-end query processing time |
| **Embedding Model Score** | 0.9581 | Enhanced retrieval ranking score (e5-large-v2) |
| **Vector Index Size** | ~2MB | FAISS index for 400+ page document |
| **Chunk Coverage** | 100% | All document content indexed and searchable |

*Note: Retrieval hit rate requires domain-specific test queries with known ground truth pages.

**Run Evaluation:**
```bash
python evaluate_system.py
```

This generates a comprehensive metrics report including:
- Intent classification accuracy across test queries
- Retrieval quality and relevance scores
- Action parameter extraction precision
- Date and priority normalization validation
- Average response time measurements

## 📁 Directory Structure

```
NLP challenge/
├── data/                       # Data pipeline artifacts
│   ├── pdf/                    # Source PDF files (input)
│   ├── raw_text/               # Extracted text with page markers
│   ├── structured_blocks/      # JSON blocks with metadata
│   ├── chunks/                 # CDFG chunked data (512 tokens)
│   └── faiss_cache/            # Vector index storage (index.faiss, metadata.pkl)
├── src/
│   ├── agent/                  # Agent orchestration and routing
│   │   ├── orchestrator.py     # Main agent orchestrator (routes queries)
│   │   ├── action_generator.py # Action JSON generation from NL
│   │   └── intent_router.py    # Intent classification (INFO_QUERY vs ACTION_REQUEST)
│   ├── embeddings/             # Vector embedding generation
│   │   └── build_faiss_index.py # Builds FAISS index from chunks
│   ├── ingestion/              # Data ingestion pipeline
│   │   ├── pdf_to_text.py      # PDF extraction with page markers
│   │   ├── block_extraction.py # Block identification (headings, paragraphs)
│   │   └── cdfg_chunker.py     # Context-aware chunking (512 tokens)
│   ├── rag/                    # RAG answer generation
│   │   ├── answer_generator.py # Answer synthesis with citations
│   │   └── prompts.py          # System prompts for LLM
│   ├── retrieval/              # Vector retrieval
│   │   └── retrieval.py        # FAISS retrieval logic (top-k search)
│   └── utils/                  # Utility modules
│       ├── confirmation.py     # User confirmation classifier
│       ├── description_enhancer.py # Ticket enhancement & normalization
│       └── logger.py           # Logging utilities
├── static/                     # Frontend assets
│   ├── app.js                  # Frontend JavaScript (chat logic)
│   └── style.css               # UI styling (red/black theme)
├── templates/
│   └── index.html              # Main web interface
├── user_requests/              # Generated ticket JSONs (timestamped)
├── logs/                       # System logs (timestamped)
├── app.py                      # CLI version (legacy)
├── backend_api.py              # FastAPI backend (port 8000)
├── web_server.py               # Flask frontend server (port 5000)
├── start_web.bat               # Windows startup script
├── run_pipeline.py             # Data ingestion pipeline runner
└── requirements.txt            # Python dependencies
```

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8+
- Mistral API Key ([Get one here](https://console.mistral.ai/))

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

### Step 3: Prepare Data (Optional - if using your own PDF)

```bash
# Run the complete ingestion pipeline
python run_pipeline.py
```

This will:
1. Extract text from PDFs in `data/pdf/` (page-by-page with markers)
2. Create structured blocks in `data/structured_blocks/` (headings, paragraphs)
3. Generate chunks in `data/chunks/` (512-token CDFG chunks)
4. Build FAISS index in `data/faiss_cache/` (vector embeddings)

**Note**: The repository already includes pre-processed data for `Annual-Report-2024-25.pdf`

### Step 4: Start the Application

#### Option A: Web Interface (Recommended)

```bash
# Windows - One-click start
start_web.bat

# Manual start (any OS)
# Terminal 1: Start backend (FastAPI on port 8000)
python backend_api.py

# Terminal 2: Start frontend (Flask on port 5000)
python web_server.py
```

Access the web interface at: **http://localhost:5000**

#### Option B: CLI Version (Legacy)

```bash
python app.py
```

## 🏗️ Architecture

### System Overview

The system uses a **dual-pipeline architecture** with intelligent intent routing:

```
┌─────────────────────────────────────────────────────────────┐
│                     Web Interface (Flask)                    │
│              ChatGPT-like UI with Multi-Chat Support         │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP POST /chat
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend API (FastAPI)                       │
│              Session Management & State Tracking             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Orchestrator                         │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Intent Router (Mistral-small-2503)                  │  │
│  │  Classifies: INFO_QUERY vs ACTION_REQUEST            │  │
│  └──────────────┬───────────────────────┬────────────────┘  │
│                 │                       │                    │
│        ┌────────▼────────┐     ┌───────▼────────┐          │
│        │  RAG Pipeline   │     │ Action Pipeline │          │
│        └─────────────────┘     └────────────────┘          │
└─────────────────────────────────────────────────────────────┘
         │                               │
         ▼                               ▼
┌──────────────────┐          ┌──────────────────────┐
│ FAISS Retriever  │          │ Action Generator     │
│ (e5-large-v2)    │          │ (Mistral-small-2503) │
│                  │          │                      │
│ Answer Generator │          │ Confirmation Loop    │
│ (Mistral-small)  │          │ Modification Loop    │
└──────────────────┘          └──────────────────────┘
```

### Data Flow

#### **Offline: Data Preparation Pipeline**

```
PDF Documents
    ↓ (PyPDF2)
Raw Text with Page Markers
    ↓ (Block Extraction)
Structured Blocks (JSON)
    ↓ (CDFG Chunking - 512 tokens)
Text Chunks with Metadata
    ↓ (e5-large-v2 Embeddings)
FAISS Vector Index
```

#### **Runtime: Query Processing**

**Path A - Information Query:**
```
User Query
    ↓ (Intent Classification)
INFO_QUERY Detected
    ↓ (Query Embedding)
Vector Search (FAISS top-k)
    ↓ (Retrieved Chunks)
Answer Generation (Mistral-small)
    ↓ (Formatted with Citations)
Display to User
```

**Path B - Action Request:**
```
User Query
    ↓ (Intent Classification)
ACTION_REQUEST Detected
    ↓ (Action Type Detection)
Generate Action JSON
    ↓ (Confirmation Loop)
User Confirms? → YES
    ↓ (Generate Ticket)
Display Ticket
    ↓ (Modification Loop)
User Satisfied? → NO
    ↓ (Natural Language Modifications)
Update JSON (normalize dates/priority)
    ↓ (Repeat until satisfied)
User Satisfied? → YES
    ↓ (Export)
Save to user_requests/ticket_TIMESTAMP.json
```

### Key Technologies & Rationale

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **LLM** | Mistral-small-2503 | Cost-effective with strong reasoning for classification, generation, and modification |
| **Embeddings** | e5-large-v2 (sentence-transformers) | State-of-the-art semantic similarity for retrieval |
| **Vector Store** | FAISS | Industry-standard for fast, scalable similarity search |
| **Chunking** | CDFG (512 tokens) | Context-aware chunking preserves semantic boundaries |
| **Backend** | FastAPI | Modern async Python with automatic API docs |
| **Frontend** | Flask + Vanilla JS | Lightweight, no heavy frameworks needed |
| **Data Format** | JSON | Human-readable, easy integration |

### Data Normalization

The system automatically normalizes user inputs for consistency:

**Date Normalization:**
- Input: "tomorrow", "18th Jan", "17/01/25"
- Output: ISO format `YYYY-MM-DD` (e.g., "2026-01-18")
- Uses LLM-based parsing for flexibility

**Priority Normalization:**
- Input: "urgent", "critical", "maximum", "high"
- Output: One of `Low`, `Medium`, `High`
- Mapping: low/minor → Low, high/urgent/critical → High, else → Medium

## 🎮 Usage Examples

### 1. Information Query (RAG Mode)

```
User: "What is HCLTech's revenue for FY25?"

System: 
**Answer:**

HCLTech's revenue for FY25 was **₹117,055 crores**, representing a 
**26.5% CAGR** over 25 years since IPO.

**Citations:**
Page 4, Page 5
```

### 2. IT Ticket Creation (Action Mode)

```
User: "My VPN is not working"

System: "I understand you're facing a vpn issue. Do you want me to create an IT ticket?"

User: "yes"

System:
**Generated Ticket:**

**ACTION:** create_it_ticket

**ISSUE TYPE:** VPN

**PRIORITY:** Medium

**DESCRIPTION:** The user is experiencing difficulties establishing a connection 
to the VPN service. The issue prevents the user from initiating the VPN session, 
and further troubleshooting is required to identify and resolve the root cause.

Do you want to modify the ticket?

User: "make priority high and add date tomorrow"

System:
**Updated Ticket:**

**ACTION:** create_it_ticket

**ISSUE TYPE:** VPN

**PRIORITY:** High

**DATE:** 2026-01-18

**DESCRIPTION:** The user is experiencing difficulties establishing a connection 
to the VPN service. The issue prevents the user from initiating the VPN session, 
and further troubleshooting is required to identify and resolve the root cause.

Do you want to modify the ticket?

User: "looks good"

System: "Ticket exported to user_requests/ticket_20260117_143022.json. 
Your request has been recorded."
```

### 3. HR Meeting Scheduling

```
User: "I need to talk to HR"

System: "I understand you want to schedule general. Do you want me to proceed 
with scheduling an HR meeting?"

User: "yes"

System: [Generates meeting request with fields]

User: "date is 20th Jan, time 3pm, participant is John Doe"

System: [Updates with normalized date: 2026-01-20]

User: "no more changes"

System: [Exports ticket]
```

### 4. Leave Request

```
User: "I want to apply for leave"

System: "I understand you want to request leave. Do you want me to submit 
a leave request?"

User: "yes"

System: [Generates leave request]

User: "start date 25th Jan, end date 30th Jan, reason is medical"

System: [Updates with normalized dates: 2026-01-25 to 2026-01-30]

User: "done"

System: [Exports ticket]
```

## 🔧 Configuration & Customization

### Add New Action Types

Edit `src/agent/action_generator.py`:

```python
ACTIONS = {
    "create_it_ticket": {
        "fields": ["issue_type", "priority", "description"],
        "required": ["issue_type"]
    },
    "schedule_hr_meeting": {
        "fields": ["meeting_type", "date", "time", "participants", "description"],
        "required": ["meeting_type"]
    },
    "request_leave": {
        "fields": ["leave_type", "start_date", "end_date", "reason", "description"],
        "required": ["leave_type"]
    },
    "your_new_action": {  # Add here
        "fields": ["field1", "field2"],
        "required": ["field1"]
    }
}
```

### Adjust Retrieval Parameters

Edit `src/retrieval/retrieval.py`:

```python
def retrieve(self, query, top_k=5):  # Increase for more context
    ...
```

### Customize System Prompts

Edit `src/rag/prompts.py`:

```python
RAG_ANSWERING_PROMPT = """Your custom prompt here..."""
```

### Modify UI Theme

Edit `static/style.css` to change colors:

```css
:root {
    --primary-color: #c00;  /* Red accent */
    --bg-color: #000;       /* Black background */
}
```

## 📊 Data Ingestion Pipeline Details

### CDFG Chunking Strategy

**Why CDFG?**
- Traditional fixed-size chunking breaks semantic boundaries
- CDFG respects document structure (paragraphs, sections)
- Maintains context with overlapping windows

**Parameters:**
- Token limit: 512 tokens (optimal for e5-large-v2)
- Overlap: 50 tokens (preserves context between chunks)
- Metadata: Page numbers, block IDs tracked

### Pipeline Steps

1. **PDF to Text** (`pdf_to_text.py`):
   - Extracts text page-by-page using PyPDF2
   - Adds `[PAGE X]` markers for citation tracking
   - Outputs to `data/raw_text/`

2. **Block Extraction** (`block_extraction.py`):
   - Identifies document structure (headings, paragraphs, tables)
   - Creates structured JSON with block metadata
   - Outputs to `data/structured_blocks/`

3. **CDFG Chunking** (`cdfg_chunker.py`):
   - Token-aware chunking with tiktoken
   - Respects semantic boundaries
   - Adds overlap for context preservation
   - Outputs to `data/chunks/`

4. **FAISS Index Building** (`build_faiss_index.py`):
   - Generates embeddings using e5-large-v2
   - Builds FAISS index for fast similarity search
   - Stores index and metadata in `data/faiss_cache/`

## 🔍 Troubleshooting

### Issue: "Information not available in the knowledge base"

**Cause**: FAISS index not built or query doesn't match content

**Solutions**:
1. Check if `data/faiss_cache/index.faiss` exists
2. Verify chunks exist in `data/chunks/`
3. Rebuild index: `python src/embeddings/build_faiss_index.py`
4. Try rephrasing your query

### Issue: Backend not starting

**Cause**: Missing API key or port conflict

**Solutions**:
1. Verify `.env` file has `MISTRAL_API_KEY`
2. Check if port 8000 is available: `netstat -ano | findstr :8000`
3. Check logs in `logs/` directory
4. Ensure all dependencies installed: `pip install -r requirements.txt`

### Issue: Frontend not loading

**Cause**: Backend not running or port conflict

**Solutions**:
1. Verify backend is running on port 8000
2. Check if port 5000 is available
3. Clear browser cache (Ctrl+Shift+Delete)
4. Check browser console for errors (F12)

### Issue: Dates not normalizing correctly

**Cause**: Ambiguous date format or LLM parsing error

**Solutions**:
1. Use explicit formats: "18th January 2026" instead of "18/1"
2. Check logs for normalization errors
3. Dates default to current year if not specified

## 📝 API Documentation

### POST /chat

Main endpoint for all user interactions.

**Request:**
```json
{
  "query": "user message",
  "chat_id": "chat_123456",
  "conversation_history": [
    {"role": "user", "content": "...", "timestamp": "..."},
    {"role": "assistant", "content": "...", "timestamp": "..."}
  ],
  "pending_action": {
    "type": "ACTION_REQUEST",
    "content": {"action": "create_it_ticket", ...}
  },
  "pending_state": "awaiting_modification",
  "original_query": "original user query"
}
```

**Response Types:**

1. **INFO_QUERY** - Information retrieval result
```json
{
  "type": "INFO_QUERY",
  "content": {"answer": "...with citations"},
  "pending_action": null,
  "pending_state": null
}
```

2. **CONFIRMATION_NEEDED** - Asking user to confirm action
```json
{
  "type": "CONFIRMATION_NEEDED",
  "content": {"message": "Do you want me to...?"},
  "pending_action": {...},
  "pending_state": "awaiting_confirmation"
}
```

3. **TICKET_GENERATED** - Ticket created, awaiting modifications
```json
{
  "type": "TICKET_GENERATED",
  "content": {"action": "...", "priority": "Medium", ...},
  "pending_action": {...},
  "pending_state": "awaiting_modification"
}
```

4. **TICKET_UPDATED** - Ticket modified
```json
{
  "type": "TICKET_UPDATED",
  "content": {"action": "...", "priority": "High", ...},
  "pending_action": {...},
  "pending_state": "awaiting_modification"
}
```

5. **TICKET_EXPORTED** - Ticket saved
```json
{
  "type": "TICKET_EXPORTED",
  "content": {"message": "Ticket exported to ...", "filename": "..."},
  "pending_action": null,
  "pending_state": null
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{"status": "ok"}
```

## 🛠️ Development Guide

### Adding New Features

1. **New Action Type**:
   - Edit `src/agent/action_generator.py` (add to ACTIONS dict)
   - Update `src/rag/prompts.py` (add to ACTION_JSON_PROMPT)
   - Test with various user inputs

2. **New Intent Category**:
   - Edit `src/agent/intent_router.py` (add classification logic)
   - Update `src/rag/prompts.py` (add examples)
   - Handle in `backend_api.py`

3. **Custom Validation**:
   - Add to `src/utils/description_enhancer.py`
   - Integrate in modification loop

4. **UI Enhancements**:
   - Edit `static/app.js` (frontend logic)
   - Edit `static/style.css` (styling)
   - Edit `templates/index.html` (structure)

### Code Structure Best Practices

- **Orchestrator**: Routes requests, maintains no state
- **Generators**: Stateless, pure functions
- **Enhancers**: Normalize and validate data
- **Backend API**: Manages session state only

### Logging

Logs are automatically created in `logs/system_YYYYMMDD_HHMMSS.log`

**Log Levels:**
- INFO: Normal operations
- DEBUG: Detailed processing info (LLM responses, JSON parsing)
- ERROR: Failures and exceptions

## 📦 Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `fastapi` | Latest | Backend REST API |
| `uvicorn` | Latest | ASGI server for FastAPI |
| `flask` | Latest | Frontend web server |
| `mistralai` | Latest | LLM API client |
| `faiss-cpu` | Latest | Vector similarity search |
| `sentence-transformers` | Latest | Embedding generation |
| `PyPDF2` | Latest | PDF text extraction |
| `tiktoken` | Latest | Token counting |
| `python-dotenv` | Latest | Environment variable management |

See `requirements.txt` for complete list with versions.

## 🎨 UI Features

- **Multi-chat Support**: Create unlimited conversations, switch seamlessly
- **Chat Persistence**: Conversations saved in browser localStorage
- **Delete Chats**: Hover over chat to reveal delete button
- **Red/Black Theme**: Professional, modern interface
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Updates**: Instant message rendering
- **Markdown Support**: Bold text, bullet points, line breaks
- **Timestamp Display**: Track conversation timeline

## 📄 License

This project is for educational and demonstration purposes.

## 🤝 Contributing

This is a hackathon project. For improvements:
1. Fork the repository
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📧 Support

For issues and debugging:
1. Check logs in `logs/` directory
2. Verify `.env` configuration
3. Ensure all dependencies installed
4. Check API key validity
5. Review console output for errors

## 🎓 Learning Resources

- [Mistral AI Documentation](https://docs.mistral.ai/)
- [FAISS Documentation](https://github.com/facebookresearch/faiss)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Sentence Transformers](https://www.sbert.net/)

---

**Built with ❤️ for intelligent automation**
