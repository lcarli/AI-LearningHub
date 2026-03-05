# 📚 Parcours RAG

<span class="level-badge level-100">L100</span> <span class="level-badge level-200">L200</span> <span class="level-badge level-300">L300</span> <span class="level-badge level-400">L400</span>

**Retrieval-Augmented Generation (RAG)** est le patron le plus courant pour ancrer les agents IA dans vos propres données. Au lieu de s'appuyer sur les données d'entraînement du LLM, vous récupérez les documents pertinents au moment de la requête et les incluez dans le prompt.

---

## Ce que Vous Allez Construire

- ✅ Comprendre le pipeline RAG de bout en bout
- ✅ Charger, découper et générer des embeddings de documents avec **GitHub Models (gratuit)**
- ✅ Stocker et interroger des vecteurs avec un **pgvector local** (Docker)
- ✅ Construire une recherche sémantique sur **Azure PostgreSQL + pgvector**
- ✅ Évaluer la qualité du RAG avec le Azure AI Evaluation SDK

---

## Laboratoires du Parcours (7 laboratoires, ~355 min au total)

| Lab | Titre | Niveau | Coût |
|-----|-------|--------|------|
| [Lab 006](../../labs/lab-006-what-is-rag.md) | Qu'est-ce que RAG ? | <span class="level-badge level-50">L50</span> | ✅ Free |
| [Lab 007](../../labs/lab-007-what-are-embeddings.md) | Que sont les Embeddings ? | <span class="level-badge level-50">L50</span> | ✅ Free |
| [Lab 022](../../labs/lab-022-rag-github-models-pgvector.md) | Pipeline RAG avec GitHub Models + pgvector | <span class="level-badge level-200">L200</span> | ✅ Free |
| [Lab 026](../../labs/lab-026-agentic-rag.md) | Patron RAG Agentique | <span class="level-badge level-200">L200</span> | ✅ GitHub Free |
| [Lab 031](../../labs/lab-031-pgvector-semantic-search.md) | Recherche Sémantique pgvector sur Azure | <span class="level-badge level-300">L300</span> | Free |
| [Lab 039](../../labs/lab-039-vector-db-comparison.md) | Comparaison de Bases de Données Vectorielles | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 042](../../labs/lab-042-enterprise-rag.md) | RAG Entreprise avec Évaluations | <span class="level-badge level-400">L400</span> | ⚠️ Azure |

---

## Le Pipeline RAG

![Pipeline RAG](../../assets/diagrams/rag-pipeline.svg)

---

## Ressources Externes

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Azure AI Search + RAG](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)
- [API Embeddings GitHub Models](https://docs.github.com/en/github-models)
- [Azure AI Evaluation SDK](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/agent-evaluate-sdk)
