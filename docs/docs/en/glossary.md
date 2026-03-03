# Glossary

Common terms used throughout the AI Agents Learning Hub, organized alphabetically.

---

## A

**Agent**
A software system that perceives its environment, makes decisions, and takes actions to achieve a goal. AI agents use LLMs as a reasoning engine combined with tools, memory, and planning.

**AgentGroupChat**
A Semantic Kernel construct that enables multiple agents to collaborate in a shared conversation. Each agent sees the conversation history and can respond, delegate, or call tools.

**Agentic RAG**
An extension of basic RAG where an agent decides *when* to retrieve information, *what* query to use, and *whether* to retrieve again if the first result is insufficient.

**ARM Template**
Azure Resource Manager template — a JSON file that declaratively describes Azure infrastructure. Can be deployed with the "Deploy to Azure" button.

---

## B

**Bicep**
A domain-specific language (DSL) for Azure infrastructure as code. Compiles to ARM JSON. Cleaner syntax than raw JSON templates. Used in the `infra/` folder of this repo.

**Chunking**
The process of splitting a large document into smaller pieces before embedding and indexing. Chunk size affects retrieval quality — too small loses context, too large loses precision.

---

## C

**Chat Participant**
A VS Code extension concept — a custom `@agent` that plugs into GitHub Copilot Chat. Registered via `contributes.chatParticipants` in `package.json`.

**Completion**
A response from an LLM given an input prompt. Also called a "generation" or "inference."

**Copilot Extension**
A GitHub integration that adds a custom agent to GitHub Copilot across github.com, VS Code, and other surfaces. Requires an API endpoint (webhooks).

**Context Window**
The maximum amount of text (measured in tokens) an LLM can process in a single request. As of 2025, ranges from 8k (small models) to 1M+ tokens (Gemini 1.5).

---

## D

**Dense Embedding**
A numerical vector representation of text, where semantically similar texts have similar vectors. Produced by embedding models like `text-embedding-3-small`.

**Document Grounding**
Providing retrieved documents to the LLM as context, so the answer is based on specific sources rather than the model's training data. Reduces hallucination.

---

## E

**Embedding**
A fixed-length numerical vector that captures the semantic meaning of text. See [Lab 007 — What are Embeddings?](labs/lab-007-embeddings.md).

**Embedding Model**
A model that converts text to embeddings. Examples: `text-embedding-3-small` (OpenAI), `text-embedding-ada-002`, `nomic-embed-text` (local/Ollama).

---

## F

**Function Calling**
An LLM feature where the model can request to call a specific function with structured arguments, rather than returning plain text. Also called "tool use."

**Foundry Agent Service**
Microsoft's managed service for deploying AI agents with built-in tool integration, tracing, and evaluation. Part of Azure AI Foundry.

---

## G

**GitHub Models**
A free service (github.com/marketplace/models) providing API access to leading LLMs (GPT-4o, Llama 3, etc.) using a GitHub token. No credit card required.

**Grounding**
See *Document Grounding*.

---

## H

**Hallucination**
When an LLM generates confident-sounding but factually incorrect output. Grounding with RAG reduces hallucination by providing accurate source documents.

**Hybrid Search**
Combining dense vector search (semantic similarity) with sparse keyword search (BM25/full-text) for better retrieval. Usually scored with Reciprocal Rank Fusion (RRF).

---

## I

**Intent Classification**
Determining what a user wants from their message. Agents use this to route to the correct specialist, tool, or workflow.

---

## K

**Kernel (Semantic Kernel)**
The central orchestration object in Semantic Kernel. Holds AI services, plugins, memory, and planners. Entry point for all SK operations.

---

## L

**Language Model API (VS Code)**
`vscode.lm` — an API that lets VS Code extensions use the LLM powering Copilot, without needing a separate API key. Available in VS Code 1.90+.

**LLM**
Large Language Model — a deep learning model trained on large text datasets to understand and generate human language. Examples: GPT-4o, Claude 3.5, Llama 3.

---

## M

**MCP (Model Context Protocol)**
An open standard by Anthropic for connecting AI models to external tools and data sources via a structured protocol. See [Lab 012 — What is MCP?](labs/lab-012-what-is-mcp.md).

**MCP Server**
A process that exposes tools and resources to AI agents via the MCP protocol. Can be local or remote. Written in Python, TypeScript, C#, etc.

**Memory (agent)**
The ability of an agent to store and recall information. Types: *in-context* (within the prompt), *external* (vector DB, key-value store), *episodic* (conversation history).

**Multi-Agent System**
An architecture where multiple specialized agents collaborate to solve a task. Includes an orchestrator that routes requests and specialists that handle domain-specific work.

---

## O

**Ollama**
An open-source tool for running LLMs locally on your laptop. Supports Llama, Mistral, Phi, Gemma, and 100+ models. Completely free, no internet required.

**Orchestrator**
An agent whose primary role is to understand user intent and delegate sub-tasks to specialist agents or tools.

---

## P

**pgvector**
An open-source PostgreSQL extension that adds vector data types and similarity search. Enables storing embeddings directly in a Postgres database.

**Planner (Semantic Kernel)**
A component that breaks a high-level goal into a sequence of steps, each mapped to an available plugin function. Examples: `FunctionChoiceBehavior.Auto()`.

**Plugin (Semantic Kernel)**
A class with methods decorated with `@kernel_function`. Exposed to the LLM as callable tools. Equivalent to "tools" or "functions" in OpenAI terminology.

**Prompt Engineering**
The practice of crafting effective prompts to guide LLM behavior. Includes system prompts, few-shot examples, chain-of-thought, and output formatting. See [Lab 005](labs/lab-005-prompt-engineering.md).

**Prompt Injection**
An attack where malicious content in external data (documents, user input) overwrites the agent's instructions. A key security concern for RAG and agentic systems.

---

## R

**RAG (Retrieval Augmented Generation)**
A pattern that enhances LLM responses by first retrieving relevant documents from a knowledge base, then including them in the prompt. See [Lab 006 — What is RAG?](labs/lab-006-what-is-rag.md).

**Reranking**
A second-pass step after initial retrieval that reorders results by relevance using a cross-encoder model. Improves precision at the cost of additional latency.

**Row Level Security (RLS)**
A PostgreSQL feature that restricts which rows a database user can see. Policy defined in SQL: `CREATE POLICY ... USING (customer_id = current_user)`. See [Lab 032](labs/lab-032-row-level-security.md).

---

## S

**Semantic Kernel (SK)**
Microsoft's open-source SDK for building AI agents in Python, C#, and Java. Provides kernels, plugins, memory, planners, and multi-agent patterns.

**Semantic Search**
Finding results based on meaning/intent rather than exact keyword match. Uses vector similarity (cosine, dot product) on embeddings.

**Sparse Embedding**
A high-dimensional vector where most values are zero. Used in keyword/BM25 search. Contrasts with *dense embedding*.

**Streaming**
Returning LLM output token by token as it's generated, rather than waiting for the full response. Improves perceived latency.

**System Prompt**
Instructions given to the LLM at the start of a conversation that define its persona, capabilities, and constraints. Not visible to the user in most UIs.

---

## T

**Temperature**
A parameter (0.0–2.0) controlling LLM randomness. 0 = deterministic (best for structured output), 1 = balanced, >1 = more creative/random.

**Token**
The basic unit of text processed by an LLM. Roughly 3/4 of a word in English. Costs and context limits are measured in tokens.

**Tool Calling**
See *Function Calling*.

**Top-K / Top-P**
Sampling strategies for LLM output. Top-K: only consider the K most likely next tokens. Top-P (nucleus sampling): consider tokens whose cumulative probability exceeds P.

---

## V

**Vector Database**
A database optimized for storing and querying embeddings by similarity. Examples: pgvector, ChromaDB, Pinecone, Weaviate, Azure AI Search.

**Vector Search**
Finding the nearest vectors (most similar embeddings) to a query vector using metrics like cosine similarity or L2 distance.

---

## W

**Webhook**
An HTTP endpoint that receives events from an external service. GitHub Copilot Extensions use webhooks to receive chat messages and return responses.

---

## Common Acronyms

| Acronym | Full Name |
|---------|-----------|
| AI | Artificial Intelligence |
| API | Application Programming Interface |
| BM25 | Best Match 25 (keyword scoring algorithm) |
| CE | Conformité Européenne (safety certification) |
| CLI | Command Line Interface |
| CV | Computer Vision |
| DI | Dependency Injection |
| DSL | Domain-Specific Language |
| GPT | Generative Pre-trained Transformer |
| JSON | JavaScript Object Notation |
| JWT | JSON Web Token |
| LLM | Large Language Model |
| MCP | Model Context Protocol |
| ML | Machine Learning |
| NLP | Natural Language Processing |
| RAG | Retrieval Augmented Generation |
| RLS | Row Level Security |
| RRF | Reciprocal Rank Fusion |
| SDK | Software Development Kit |
| SK | Semantic Kernel |
| SQL | Structured Query Language |

---

*Missing a term? [Open an issue](https://github.com/lcarli/AI-LearningHub/issues/new) or submit a PR!*
