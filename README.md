# 🌾 Agri Assist AI

> **For Farmers. For a Greener Tomorrow.**

Agri Assist AI is a conversational **Retrieval-Augmented Generation (RAG)** application designed to help farmers, the public, government users, and agencies understand agriculture-related government schemes and farmer support using simple, everyday language.

The project combines:

- 🌐 Web data collection with **Playwright**
- 📄 Multi-format data ingestion
- 🧹 Data cleaning and normalization
- 🏷️ Metadata enrichment
- ✂️ Text chunking
- 🧮 Text embeddings
- 🔎 **FAISS vector search**
- 🧠 Query classification
- 🔄 Contextual query rewriting
- ✍️ Query rewriting
- 🛠️ **Corrective RAG**
- ✅ Retrieval grading
- 🤖 **OpenAI API**
- 🎯 Grounded answer generation
- 💬 Conversation memory
- ⚡ **Redis caching**
- 🔗 Provenance tracking
- 👥 Role-aware responses
- 🌱 Scheme-specific filtering
- 🖥️ Streamlit UI
- 👋 Conversational greetings and small talk
- ⌨️ Character-by-character answer streaming

---

# 📌 Table of Contents

- [Project Overview](#-project-overview)
- [Why RAG](#-why-rag)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Data Ingestion Pipeline](#-data-ingestion-pipeline)
- [Text Chunking](#-text-chunking)
- [Text Embeddings](#-text-embeddings)
- [FAISS Vector Store](#-faiss-vector-store)
- [Query Classification](#-query-classification)
- [Conversation Memory](#-conversation-memory)
- [Contextual Query Rewriting](#-contextual-query-rewriting)
- [Redis Caching](#-redis-caching)
- [Vector Retrieval](#-vector-retrieval)
- [Retrieval Grading](#-retrieval-grading)
- [Corrective RAG](#-corrective-rag)
- [OpenAI API](#-openai-api)
- [Grounded Answer Generation](#-grounded-answer-generation)
- [Provenance](#-provenance)
- [Conversational Guardrails](#-conversational-guardrails)
- [Character Streaming](#-character-streaming)
- [Streamlit UI](#-streamlit-ui)
- [Role Selection](#-role-selection)
- [Scheme Selection](#-scheme-selection)
- [Role and Scheme Reset](#-role-and-scheme-reset)
- [Testing](#-testing)
- [Installation](#-installation)
- [Redis Setup](#-redis-setup)
- [Environment Variables](#-environment-variables)
- [Running the Application](#-running-the-application)
- [Example Questions](#-example-questions)
- [Validation Results](#-validation-results)
- [Future Enhancements](#-future-enhancements)

---

# 🌱 Project Overview

Agri Assist AI provides a conversational interface over an agriculture-focused knowledge base.

Instead of manually searching through multiple government documents and scheme pages, a user can ask:

```text
Who is eligible for PM-KISAN?
