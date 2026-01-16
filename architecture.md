# Architecture of the Agentic RAG System

This document outlines the architecture and flow of the Agentic Retrieval-Augmented Generation (RAG) system, detailing the rationale behind each component and the two primary workflows: **Query Flow** and **Agentic Flow**.

## Overview

The Agentic RAG system is designed to handle two types of user inputs:
1. **Query Flow**: For retrieving information from a knowledge base.
2. **Agentic Flow**: For performing actions such as creating IT tickets, scheduling meetings, or requesting leaves. This flow includes a feedback loop for iterative corrections.

The system combines the following key components:
- **CDFG Chunking**: Prepares the data for efficient retrieval.
- **Semantic Embedding**: Converts text into vector representations using the `intfloat/e5-large-v2` model.
- **Intent Classification**: Uses the `mistral-small-2503` model to classify user intent.
- **Retrieval**: Searches for relevant information using FAISS.
- **Answer Generation**: Synthesizes responses using the `mistral-small-2503` model.
- **Action Generation**: Creates actionable outputs (e.g., tickets, meeting requests).

---

## Data Preparation Pipeline

### 1. **CDFG Chunking**
- **File**: `src/ingestion/cdfg_chunker.py`
- **Purpose**: Splits large documents into smaller, context-aware chunks while preserving semantic boundaries.
- **Rationale**: Ensures that the text is tokenized into manageable sizes (default: 512 tokens) for efficient processing by the embedding model.
- **Process**:
  1. Text is tokenized using a simple word-based tokenizer.
  2. Blocks exceeding the token limit are split into smaller chunks with overlapping tokens to preserve context.
  3. Outputs are saved as JSON files in `data/chunks/`.

### 2. **Semantic Embedding**
- **File**: `src/embeddings/build_faiss_index.py`
- **Model**: `intfloat/e5-large-v2` (via `sentence-transformers` library)
- **Purpose**: Converts text chunks into high-dimensional vector embeddings.
- **Rationale**: Embeddings enable efficient similarity search using FAISS.
- **Process**:
  1. Text chunks are loaded from `data/chunks/`.
  2. The embedding model generates vector representations for each chunk.
  3. A FAISS index is built and stored in `data/faiss_cache/` for fast retrieval.

---

## Query Flow

### 1. **Intent Classification**
- **File**: `src/agent/intent_router.py`
- **Model**: `mistral-small-2503`
- **Purpose**: Classifies user input as either `INFO_QUERY` or `ACTION_REQUEST`.
- **Rationale**: Determines the appropriate processing pipeline for the user query.
- **Process**:
  1. The user query is passed to the `IntentRouter`.
  2. The `mistral-small-2503` model is used to classify the intent based on a predefined prompt.

### 2. **Retrieval**
- **File**: `src/retrieval/retrieval.py`
- **Model**: `intfloat/e5-large-v2`
- **Purpose**: Retrieves the most relevant chunks from the FAISS index.
- **Rationale**: Provides context for generating accurate and grounded answers.
- **Process**:
  1. The query is embedded using the same model used for chunk embeddings.
  2. The FAISS index is queried to retrieve the top-k most relevant chunks.

### 3. **Answer Generation**
- **File**: `src/rag/answer_generator.py`
- **Model**: `mistral-small-2503`
- **Purpose**: Synthesizes a response using the retrieved chunks as context.
- **Rationale**: Combines the power of LLMs with grounded retrieval for accurate answers.
- **Process**:
  1. Retrieved chunks are passed to the `AnswerGenerator`.
  2. The `mistral-small-2503` model generates a response based on a predefined prompt.

---

## Agentic Flow

### 1. **Intent Classification**
- Same as in the Query Flow.

### 2. **Action Generation**
- **File**: `src/agent/action_generator.py`
- **Model**: `mistral-small-2503`
- **Purpose**: Generates actionable outputs (e.g., IT tickets, meeting requests).
- **Rationale**: Automates repetitive tasks based on user input.
- **Process**:
  1. The user query is passed to the `ActionGenerator`.
  2. The `mistral-small-2503` model generates an action JSON based on a predefined prompt.

### 3. **Feedback Loop**
- **File**: `src/agent/orchestrator.py`
- **Purpose**: Allows users to iteratively modify the generated action.
- **Rationale**: Ensures the generated action meets user requirements.
- **Process**:
  1. The generated action is presented to the user for feedback.
  2. The user provides corrections or modifications via natural language.
  3. The system updates the action and repeats the process until the user confirms.

---

## Summary

The Agentic RAG system combines state-of-the-art LLMs, vector search, and agentic workflows to provide a robust solution for both information retrieval and action generation. The architecture ensures:
- Efficient data processing through CDFG chunking and FAISS indexing.
- Accurate intent classification and response generation using the `mistral-small-2503` model.
- A seamless feedback loop for agentic tasks, enabling iterative refinement of actions.

This modular design allows for easy extension and customization, making it suitable for a wide range of IT/HR support scenarios.