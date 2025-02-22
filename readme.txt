# Multi-Agent DeepSeek Project

## Project Overview

This project is a multi-agent system that uses DeepSeek R1 1.5b along with advanced NLP tools to enable autonomous conversation among several specialized AI agents. The system utilizes:

- **DeepSeek R1 1.5b** for generating responses via the Ollama CLI.
- **SentenceTransformer ("all-mpnet-base-v2")** for generating semantic embeddings.
- **FAISS** for vector-based semantic search.
- **SQLite** for storing learned knowledge.
- **Asyncio** for asynchronous processing.
- **Python's logging module** to log all interactions and errors to `agents.log`.

The specialized agents include:
- **Omega AI** (Master Coordinator)
- **Logic AI** (Reasoning & Problem-Solving)
- **Philosopher AI** (Existential Thinking)
- **Scientist AI** (Theoretical Research)
- **Strategist AI** (Future Predictions)
- **Creative AI** (Creative)
- **Data Analyst AI** (Data Analysis & Insights)

## Setup Instructions

1. **Navigate to the project directory:**
   ```cmd
   cd C:\Users\Deven\deepseek_project
