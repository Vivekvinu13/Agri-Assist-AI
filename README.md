# 🌾 Agri Assist AI

> **For Farmers. For a Greener Tomorrow.**

Agri Assist AI is a conversational **Retrieval-Augmented Generation (RAG)** application for agriculture-related government schemes and farmer support.

The project combines **web/data ingestion, Playwright, OpenAI Embeddings, FAISS, query classification, conversation memory, contextual query rewriting, retrieval grading, Corrective RAG, OpenAI LLM generation, Redis caching, provenance, and a farmer-friendly Streamlit UI**.

---

## ✨ Features

- 🌐 Web data collection with **Playwright**
- 📄 Multi-format data ingestion
- 🧹 Data cleaning and normalization
- 🏷️ Metadata enrichment
- ✂️ Text chunking
- 🧮 **OpenAI Embeddings**
- 🔎 **FAISS** semantic retrieval
- 🧠 Query classification
- 💬 Conversation memory
- 🔄 Contextual query rewriting
- ✍️ Query rewriting
- ✅ Retrieval grading
- 🛠️ **Corrective RAG**
- 🤖 **OpenAI API / ChatOpenAI**
- 🎯 Grounded answer generation
- 🔗 Provenance tracking
- ⚡ **Redis caching**
- 👥 Farmer / Public / Government / Agency profiles
- 🌱 Scheme-specific retrieval
- 👋 Greeting and courtesy handling
- 🚫 Out-of-domain protection
- ⌨️ Character-by-character answer streaming
- 🖥️ Streamlit UI

---

# 🏗️ Architecture

```text
                    SOURCE DATA
                         │
            ┌────────────┼────────────┐
            │            │            │
           Web          PDF      XLSX/PPTX
            │            │            │
            ▼            ▼            ▼
        Playwright / Document Ingestion
                         │
                         ▼
                Cleaning + Metadata
                         │
                         ▼
                     Chunking
                         │
                         ▼
                 OpenAI Embeddings
                         │
                         ▼
                       FAISS
                         │
                         │
                  USER QUESTION
                         │
                         ▼
              Conversational Handling
                         │
                         ▼
                 Conversation Memory
                         │
                         ▼
              Contextual Query Rewrite
                         │
                         ▼
                Query Classification
                         │
                         ▼
                    Redis Cache
                         │
                  ┌──────┴──────┐
                  │             │
                 HIT           MISS
                  │             │
                  ▼             ▼
            Cached Answer   FAISS Retrieval
                                  │
                                  ▼
                           Retrieval Grading
                                  │
                         ┌────────┴────────┐
                         │                 │
                       GOOD              WEAK
                         │                 │
                         ▼                 ▼
                  Answer Generation   Corrective RAG
                                           │
                                           ▼
                                     Query Rewrite
                                           │
                                           ▼
                                    Retry Retrieval
                                           │
                                           ▼
                                       Re-grade
                                           │
                                           ▼
                                    Answer Generation
                                           │
                                           ▼
                                    Grounded Answer
                                           │
                                           ▼
                                     Redis + Memory
                                           │
                                           ▼
                                  Character Streaming
                                           │
                                           ▼
                                      Streamlit UI
```

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Application and RAG logic |
| **Playwright** | Browser automation and dynamic web-data collection |
| **OpenAI Embeddings** | Convert document/query text into vectors |
| **FAISS** | Vector similarity search |
| **LangChain** | LLM and RAG integration |
| **OpenAI API / ChatOpenAI** | Classification, reasoning, rewriting and answer generation |
| **Corrective RAG** | Correct weak first-pass retrieval |
| **Redis** | Response caching |
| **Streamlit** | User interface |

> The current `rag/retriever.py` uses `OpenAIEmbeddings` and FAISS. The exact embedding model is supplied through the project's `EMBEDDING_MODEL` configuration and should be documented from that configuration rather than assumed.

---

# 📥 Data Ingestion

The RAG knowledge base is built from agriculture-related sources.

## Web Data with Playwright

Playwright is used for browser-based collection when websites require rendering, JavaScript execution, navigation, or interaction before extracting information.

```text
Website
  ↓
Playwright
  ↓
Rendered Content
  ↓
Extracted Knowledge
```

## Document Ingestion

The project can ingest source documents such as:

```text
PDF
PPTX
XLSX
XLS
```

The ingestion process is:

```text
Source
  ↓
Extraction
  ↓
Cleaning
  ↓
Metadata
  ↓
Chunking
  ↓
Embeddings
  ↓
FAISS
```

---

# ✂️ Text Chunking

Large documents are divided into smaller retrieval units before embeddings are generated.

The chunking stage improves retrieval by allowing FAISS to search smaller pieces of relevant content rather than entire documents.

Conceptually:

```text
Large Document
      ↓
Chunk 1
Chunk 2
Chunk 3
...
Chunk N
```

---

# 🧮 Text Embeddings

The current retrieval implementation uses:

```python
from langchain_openai import OpenAIEmbeddings
```

The embedding object is created using the project's `EMBEDDING_MODEL` configuration.

The flow is:

```text
Document Chunk
      ↓
OpenAI Embeddings
      ↓
Embedding Vector
      ↓
FAISS
```

Embeddings enable semantic retrieval, so questions can match relevant information even when wording is different.

---

# 🔎 FAISS Vector Search

FAISS is used to index and search the embedding vectors.

Runtime flow:

```text
User Query
    ↓
Query Embedding
    ↓
FAISS Similarity Search
    ↓
Relevant Chunks
```

The main RAG pipeline uses:

```python
DEFAULT_TOP_K = 5
```

---

# 🧠 Query Classification

Before normal retrieval, the system classifies the query.

The classifier determines:

- Domain
- Intent
- Confidence
- Whether retrieval should happen

Example:

```text
Who is eligible for PM-KISAN?
```

can be classified as:

```text
Domain         : agriculture
Intent         : eligibility
Should retrieve: True
```

An unrelated weather query can be classified outside the agriculture retrieval scope.

---

# 💬 Conversation Memory

Conversation memory enables multi-turn conversations.

Example:

```text
USER:
Who is eligible for PM-KISAN?

USER:
How much do they get?
```

The second question depends on the first question.

Conversation history is therefore used to resolve references such as:

```text
they
this scheme
the benefit
how much
```

---

# 🔄 Contextual Query Rewriting

Follow-up questions are converted into standalone queries.

Example:

```text
How much do they get?
```

can become:

```text
How much financial assistance do eligible farmers receive under the PM-KISAN scheme?
```

Flow:

```text
Conversation History
       +
Current Question
       ↓
Contextual Query Rewriter
       ↓
Standalone Query
```

This makes downstream retrieval more reliable.

---

# ✍️ Query Rewriting

The project also includes query rewriting as part of the retrieval correction flow.

When retrieval is weak, the system can generate a clearer search query and use it for a retry.

---

# ✅ Retrieval Grading

Retrieved documents are evaluated before answer generation.

The grader returns information such as:

```text
Relevant
Confidence
Reason
Useful chunks
```

The pipeline uses:

```python
DEFAULT_MIN_CONFIDENCE = 0.65
```

Initial retrieval is accepted when it is relevant and sufficiently confident.

---

# 🛠️ Corrective RAG

The project uses **Corrective RAG**.

If the first retrieval is not good enough, the pipeline rewrites the query and retries retrieval.

```text
Initial Retrieval
       ↓
Retrieval Grading
       ↓
Relevant enough?
   ┌────┴────┐
  YES        NO
   │          │
   ▼          ▼
 Answer    Rewrite Query
             ↓
        Retry Retrieval
             ↓
          Re-Grading
             ↓
        Answer Generation
```

Configuration:

```python
DEFAULT_MAX_RETRIES = 1
```

This is particularly useful for vague or poorly worded farmer questions.

---

# 🤖 OpenAI API

The application uses the **OpenAI API** through LangChain's `ChatOpenAI`.

OpenAI is used for LLM-driven tasks such as:

- Query classification
- Context reasoning
- Retrieval grading
- Query rewriting
- Grounded answer generation

Example:

```python
ChatOpenAI(
    model=OPENAI_MODEL,
    temperature=0
)
```

### OpenAI API vs OpenAPI

This project uses **OpenAI API**.

**OpenAPI** is a separate specification format for describing APIs.

---

# 🎯 Grounded Answer Generation

After retrieval and grading, relevant evidence is sent to the LLM.

```text
User Question
      +
Retrieved Evidence
      +
Retrieval Grade
      +
Role
      ↓
OpenAI LLM
      ↓
Grounded Answer
```

The system also tracks whether the result is grounded.

---

# 🔗 Provenance

The system retains source metadata for retrieved chunks.

Typical fields include:

```text
chunk_id
scheme_id
scheme_name
source_type
source_file
page
```

This provides traceability:

```text
Answer
  ↓
Retrieved Chunk
  ↓
Source Document
  ↓
Page / Metadata
```

Detailed provenance is retained internally for testing and traceability but is not shown to normal end users.

---

# ⚡ Redis Caching

Redis is used to cache grounded answers.

```text
Question
    ↓
Redis Lookup
    │
 ┌──┴──┐
HIT   MISS
 │      │
 ▼      ▼
Cache   RAG
Answer   │
         ▼
      Answer
         │
         ▼
       Redis
```

The cache key includes context such as:

```text
query
role
conversation_id
scheme_id
```

Repeated requests can therefore avoid unnecessary RAG and LLM work.

---

# 👋 Conversational Guardrails

Simple conversational messages are handled without retrieval.

### Greetings

```text
Hi
Hello
Hey
Good morning
```

Response:

```text
Hello, I'm your Agri Assist chat bot, how can I help you?
```

### Thanks

```text
Thanks
Thank you
Thanks a lot
Thank you so much
```

Response:

```text
You're welcome! I'm happy to help.
Ask me anything about agriculture schemes and farmer support.
```

Small talk, acknowledgements and farewells are handled similarly.

---

# 🚫 Out-of-Domain Handling

The application does not force unrelated questions through the agriculture knowledge base.

Example:

```text
What is the weather forecast tomorrow?
```

can be classified as:

```text
Should retrieve: False
```

The application then returns an agriculture-focused response instead of using unrelated documents.

---

# 👥 User Profiles

The UI supports:

```text
👨‍🌾 Farmer
👤 Public
🏛️ Government
🤝 Agency
```

The selected role is passed to the RAG pipeline and can be used to tailor the response.

---

# 🌱 Scheme Selection

Users can choose a scheme or:

```text
All Schemes
```

The application includes scheme options such as:

```text
PM-KISAN
PMFBY – Crop Insurance
Kisan Credit Card (KCC)
PM Krishi Sinchai Yojana
Soil Health Card
National Mission for Sustainable Agriculture
Agricultural Mechanization
PM-KUSUM
Weather Based Crop Insurance Scheme
Coconut Palm Insurance Scheme
Unified Package Insurance Scheme
PM Kisan Maandhan Yojana
Dairy Interest Subvention
```

The selected `scheme_id` is passed into the retrieval pipeline.

---

# 🔄 Role and Scheme Reset

Changing the role or scheme starts a clean conversation context.

The application:

- Clears visible conversation history
- Creates a new conversation ID
- Clears relevant role/conversation Redis entries

This prevents follow-up questions from using stale context from another role or scheme.

The cache cleanup is targeted rather than flushing the entire Redis database.

---

# 🖥️ Streamlit UI

The final UI was designed for farmers and non-technical users.

### Main area

- Agriculture hero image
- Selected scheme information
- Conversation
- Chat input

### Right panel

- 💡 Tip of the Day
- 🌱 What Can I Ask?
- 💬 Dynamic Example Questions
- 🌿 Sustainable Agriculture visual

### Chat identity

```text
User      : 👨‍🌾
Assistant : 🌾
```

The layout keeps:

```text
USER       → LEFT
ASSISTANT  → RIGHT
```

Technical details such as chunk IDs, retrieval scores and source metadata are hidden from normal users.

---

# ⌨️ Character-by-Character Streaming

The application uses a typewriter-style UI effect.

A helper function is used conceptually as:

```python
def stream_answer_text(
    placeholder,
    answer: str,
    delay: float = 0.018,
    chunk_size: int = 2,
):
    ...
```

The flow is:

```text
RAG generates complete answer
          ↓
stream_answer_text()
          ↓
Character-by-character display
          ↓
Final answer
```

Example:

```text
H▌
He▌
Hel▌
Hell▌
Hello▌
Hello, I'm▌
Hello, I'm your▌
...
```

The cursor disappears when streaming finishes.

### Important

This is a **UI typewriter effect**. The RAG backend still generates the complete grounded answer first.

---

# 📁 Project Structure

```text
GEN AI RAG/
│
├── app.py
├── README.md
├── requirements.txt
├── .env
│
├── assets/
│   ├── hero.png
│   ├── sidebar-card.png
│   └── sustainable.png
│
├── rag/
│   ├── __init__.py
│   ├── pipeline.py
│   ├── retriever.py
│   ├── query_classifier.py
│   ├── contextual_query.py
│   ├── query_rewriter.py
│   ├── retrieval_grader.py
│   ├── answer_generator.py
│   ├── conversation_memory.py
│   └── cache.py
│
├── tests/
│   ├── test_rewriter.py
│   ├── test_corrective_rag.py
│   ├── test_answer_generator.py
│   ├── test_conversation_memory.py
│   ├── test_contextual_query.py
│   ├── test_conversation_pipeline.py
│   ├── test_pipeline.py
│   ├── test_pipeline_cache.py
│   └── test_provenance.py
│
├── data/
└── vectorstores/
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone <repository-url>
cd GEN-AI-RAG
```

## 2. Create a virtual environment

```bash
python3 -m venv venv
```

## 3. Activate the environment

### macOS / Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
```

Do not commit secrets.

Recommended `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
.streamlit/secrets.toml
```

The embedding model is controlled through the project's `EMBEDDING_MODEL` configuration.

---

# 🗄️ Redis Setup

On macOS:

```bash
brew install redis
```

Start Redis:

```bash
brew services start redis
```

Verify:

```bash
redis-cli ping
```

Expected:

```text
PONG
```

---

# ▶️ Run the Application

```bash
source venv/bin/activate
redis-cli ping
streamlit run app.py
```

---

# 🧪 Testing

Run the main tests:

```bash
python3 -m tests.test_rewriter
python3 -m tests.test_corrective_rag
python3 -m tests.test_answer_generator
python3 -m tests.test_conversation_memory
python3 -m tests.test_contextual_query
python3 -m tests.test_conversation_pipeline
python3 -m tests.test_pipeline
python3 -m tests.test_pipeline_cache
python3 -m tests.test_provenance
```

---

# ✅ Validation Examples

### PM-KISAN

```text
Who is eligible for PM-KISAN?
```

Validates:

```text
Classification
Retrieval
Grading
Grounded Answer
Provenance
```

### Follow-up

```text
Who is eligible for PM-KISAN?
How much do they get?
```

Validates:

```text
Conversation Memory
+
Contextual Query Rewriting
+
RAG
```

### Micro Irrigation

```text
What assistance is available for micro irrigation?
```

Validates scheme-related retrieval.

### Vague Query

```text
Tell me about help for water.
```

Validates semantic retrieval and the Corrective RAG workflow.

### Out-of-Domain

```text
What is the weather forecast tomorrow?
```

Validates that irrelevant queries are not forced into agriculture retrieval.

### Redis

Ask the same question twice:

```text
First request  → Cache Miss
Second request → Cache Hit
```

---

# 🎬 Demo Flow

A good demonstration sequence is:

1. Say `Hi`
2. Select **PM-KISAN**
3. Ask `Who is eligible for PM-KISAN?`
4. Follow up with `How much do they get?`
5. Change to **PM Krishi Sinchai Yojana**
6. Ask about micro irrigation
7. Ask the vague question `Tell me about help for water.`
8. Ask an unrelated weather question
9. Repeat a previous question to demonstrate Redis caching

---

# 🔑 Key Engineering Decisions

### Playwright
Used for dynamic browser-based web data collection.

### Data Ingestion
Converts source information into a searchable knowledge base.

### OpenAI Embeddings
Convert text chunks into vectors for semantic retrieval.

### FAISS
Provides vector similarity search.

### Conversation Memory
Maintains multi-turn context.

### Contextual Query Rewriting
Converts follow-up questions into standalone queries.

### Retrieval Grading
Evaluates whether retrieved evidence is relevant enough.

### Corrective RAG
Retries weak retrieval with an improved query.

### OpenAI API
Provides LLM-based classification, reasoning, rewriting, grading and answer generation.

### Redis
Caches grounded answers.

### Provenance
Maintains traceability from retrieved chunks to source documents.

### Character Streaming
Provides a conversational typewriter-style response experience.

---

# 🏆 Final Capability Summary

```text
✅ Playwright
✅ Data ingestion
✅ Multi-format documents
✅ Data cleaning
✅ Metadata enrichment
✅ Text chunking
✅ OpenAI Embeddings
✅ FAISS
✅ Query classification
✅ Conversation memory
✅ Contextual query rewriting
✅ Query rewriting
✅ Retrieval grading
✅ Corrective RAG
✅ OpenAI API
✅ Grounded answer generation
✅ Redis caching
✅ Provenance
✅ Role selection
✅ Scheme selection
✅ Dynamic scheme content
✅ Greeting handling
✅ Courtesy handling
✅ Small talk handling
✅ Farewell handling
✅ Out-of-domain protection
✅ Character-by-character streaming
✅ Streamlit UI
```

---

# 🔮 Future Enhancements

- 🌐 Multilingual and regional-language support
- 🎙️ Voice input/output
- 📍 Location/state-specific recommendations
- 🧾 Document upload
- ✅ Personalized eligibility assessment
- 🔗 Government portal integration
- 📊 Scheme comparison
- 📈 Analytics and monitoring
- 🐳 Docker deployment
- ☁️ Cloud deployment

---

# 🌾 Agri Assist AI

> **For Farmers. For a Greener Tomorrow.**

**Playwright + Data Ingestion + OpenAI Embeddings + FAISS + Corrective RAG + OpenAI API + Redis + Conversation Memory + Streamlit + Character Streaming**
