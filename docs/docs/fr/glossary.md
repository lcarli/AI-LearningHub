# Glossaire

Termes courants utilisés dans le Hub d'Apprentissage des Agents IA, organisés par ordre alphabétique.

---

## A

**Agent**
Un système logiciel qui perçoit son environnement, prend des décisions et entreprend des actions pour atteindre un objectif. Les agents IA utilisent les LLM comme moteur de raisonnement combiné avec des outils, de la mémoire et de la planification.

**AgentGroupChat**
Un concept de Semantic Kernel qui permet à plusieurs agents de collaborer dans une conversation partagée. Chaque agent voit l'historique de la conversation et peut répondre, déléguer ou appeler des outils.

**Agentic RAG**
Une extension du RAG basique où un agent décide *quand* récupérer des informations, *quelle* requête utiliser et *s'il faut* récupérer à nouveau si le premier résultat est insuffisant.

**ARM Template**
Modèle Azure Resource Manager — un fichier JSON qui décrit de manière déclarative l'infrastructure Azure. Peut être déployé avec le bouton « Déployer sur Azure ».

---

## B

**Bicep**
Un langage spécifique au domaine (DSL) pour l'infrastructure Azure en tant que code. Se compile en JSON ARM. Syntaxe plus propre que les modèles JSON bruts. Utilisé dans le dossier `infra/` de ce dépôt.

**Chunking**
Le processus de découpage d'un grand document en morceaux plus petits avant la vectorisation et l'indexation. La taille des morceaux affecte la qualité de la récupération — trop petit perd le contexte, trop grand perd la précision.

---

## C

**Chat Participant**
Un concept d'extension VS Code — un `@agent` personnalisé qui s'intègre dans le chat GitHub Copilot. Enregistré via `contributes.chatParticipants` dans `package.json`.

**Completion**
Une réponse d'un LLM à partir d'un prompt en entrée. Aussi appelé « génération » ou « inférence ».

**Copilot Extension**
Une intégration GitHub qui ajoute un agent personnalisé à GitHub Copilot sur github.com, VS Code et d'autres surfaces. Nécessite un point de terminaison API (webhooks).

**Context Window**
La quantité maximale de texte (mesurée en tokens) qu'un LLM peut traiter en une seule requête. En 2025, varie de 8k (petits modèles) à plus de 1M de tokens (Gemini 1.5).

---

## D

**Dense Embedding**
Une représentation vectorielle numérique du texte, où les textes sémantiquement similaires ont des vecteurs similaires. Produit par des modèles de vectorisation comme `text-embedding-3-small`.

**Document Grounding**
Fournir des documents récupérés au LLM comme contexte, afin que la réponse soit basée sur des sources spécifiques plutôt que sur les données d'entraînement du modèle. Réduit les hallucinations.

---

## E

**Embedding**
Un vecteur numérique de longueur fixe qui capture le sens sémantique du texte. Voir [Lab 007 — Que sont les embeddings ?](labs/lab-007-what-are-embeddings.md).

**Embedding Model**
Un modèle qui convertit le texte en embeddings. Exemples : `text-embedding-3-small` (OpenAI), `text-embedding-ada-002`, `nomic-embed-text` (local/Ollama).

---

## F

**Function Calling**
Une fonctionnalité des LLM où le modèle peut demander d'appeler une fonction spécifique avec des arguments structurés, plutôt que de retourner du texte brut. Aussi appelé « utilisation d'outils ».

**Foundry Agent Service**
Le service géré de Microsoft pour déployer des agents IA avec intégration d'outils, traçage et évaluation intégrés. Fait partie d'Azure AI Foundry.

---

## G

**GitHub Models**
Un service gratuit (github.com/marketplace/models) fournissant un accès API aux principaux LLM (GPT-4o, Llama 3, etc.) à l'aide d'un jeton GitHub. Aucune carte bancaire requise.

**Grounding**
Voir *Document Grounding*.

---

## H

**Hallucination**
Lorsqu'un LLM génère une sortie qui semble confiante mais qui est factuellement incorrecte. L'ancrage avec le RAG réduit les hallucinations en fournissant des documents sources précis.

**Hybrid Search**
La combinaison de la recherche vectorielle dense (similarité sémantique) avec la recherche par mots-clés sparse (BM25/texte intégral) pour une meilleure récupération. Généralement notée avec la Reciprocal Rank Fusion (RRF).

---

## I

**Intent Classification**
Déterminer ce que l'utilisateur veut à partir de son message. Les agents utilisent cela pour router vers le spécialiste, l'outil ou le workflow approprié.

---

## K

**Kernel (Semantic Kernel)**
L'objet d'orchestration central dans Semantic Kernel. Contient les services d'IA, les plugins, la mémoire et les planificateurs. Point d'entrée pour toutes les opérations SK.

---

## L

**Language Model API (VS Code)**
`vscode.lm` — une API qui permet aux extensions VS Code d'utiliser le LLM alimentant Copilot, sans avoir besoin d'une clé API séparée. Disponible dans VS Code 1.90+.

**LLM**
Large Language Model (grand modèle de langage) — un modèle d'apprentissage profond entraîné sur de grands ensembles de données textuelles pour comprendre et générer le langage humain. Exemples : GPT-4o, Claude 3.5, Llama 3.

---

## M

**MCP (Model Context Protocol)**
Un standard ouvert d'Anthropic pour connecter les modèles d'IA aux outils et sources de données externes via un protocole structuré. Voir [Lab 012 — Qu'est-ce que MCP ?](labs/lab-012-what-is-mcp.md).

**MCP Server**
Un processus qui expose des outils et des ressources aux agents IA via le protocole MCP. Peut être local ou distant. Écrit en Python, TypeScript, C#, etc.

**Memory (agent)**
La capacité d'un agent à stocker et rappeler des informations. Types : *en contexte* (dans le prompt), *externe* (base de données vectorielle, stockage clé-valeur), *épisodique* (historique de conversation).

**Multi-Agent System**
Une architecture où plusieurs agents spécialisés collaborent pour résoudre une tâche. Comprend un orchestrateur qui route les requêtes et des spécialistes qui gèrent le travail spécifique au domaine.

---

## O

**Ollama**
Un outil open source pour exécuter des LLM localement sur votre ordinateur portable. Supporte Llama, Mistral, Phi, Gemma et plus de 100 modèles. Entièrement gratuit, aucune connexion internet requise.

**Orchestrator**
Un agent dont le rôle principal est de comprendre l'intention de l'utilisateur et de déléguer des sous-tâches à des agents spécialisés ou des outils.

---

## P

**pgvector**
Une extension PostgreSQL open source qui ajoute des types de données vectorielles et la recherche par similarité. Permet de stocker des embeddings directement dans une base de données Postgres.

**Planner (Semantic Kernel)**
Un composant qui décompose un objectif de haut niveau en une séquence d'étapes, chacune associée à une fonction de plugin disponible. Exemples : `FunctionChoiceBehavior.Auto()`.

**Plugin (Semantic Kernel)**
Une classe avec des méthodes décorées avec `@kernel_function`. Exposée au LLM comme outils appelables. Équivalent aux « tools » ou « functions » dans la terminologie OpenAI.

**Prompt Engineering**
La pratique de rédaction de prompts efficaces pour guider le comportement du LLM. Inclut les prompts système, les exemples few-shot, le raisonnement en chaîne et le formatage de sortie. Voir [Lab 005](labs/lab-005-prompt-engineering.md).

**Prompt Injection**
Une attaque où du contenu malveillant dans des données externes (documents, saisie utilisateur) écrase les instructions de l'agent. Une préoccupation majeure de sécurité pour les systèmes RAG et agentiques.

---

## R

**RAG (Retrieval Augmented Generation)**
Un pattern qui améliore les réponses des LLM en récupérant d'abord des documents pertinents d'une base de connaissances, puis en les incluant dans le prompt. Voir [Lab 006 — Qu'est-ce que le RAG ?](labs/lab-006-what-is-rag.md).

**Reranking**
Une étape de second passage après la récupération initiale qui réordonne les résultats par pertinence à l'aide d'un modèle cross-encoder. Améliore la précision au prix d'une latence supplémentaire.

**Row Level Security (RLS)**
Une fonctionnalité PostgreSQL qui restreint les lignes qu'un utilisateur de base de données peut voir. Politique définie en SQL : `CREATE POLICY ... USING (customer_id = current_user)`. Voir [Lab 032](labs/lab-032-row-level-security.md).

---

## S

**Semantic Kernel (SK)**
Le SDK open source de Microsoft pour créer des agents IA en Python, C# et Java. Fournit des kernels, des plugins, de la mémoire, des planificateurs et des patterns multi-agents.

**Semantic Search**
Trouver des résultats basés sur le sens/l'intention plutôt que sur la correspondance exacte de mots-clés. Utilise la similarité vectorielle (cosinus, produit scalaire) sur les embeddings.

**Sparse Embedding**
Un vecteur de haute dimension où la plupart des valeurs sont nulles. Utilisé dans la recherche par mots-clés/BM25. S'oppose au *dense embedding*.

**Streaming**
Retourner la sortie du LLM token par token au fur et à mesure de la génération, plutôt que d'attendre la réponse complète. Améliore la latence perçue.

**System Prompt**
Instructions données au LLM au début d'une conversation qui définissent sa personnalité, ses capacités et ses contraintes. Non visible par l'utilisateur dans la plupart des interfaces.

---

## T

**Temperature**
Un paramètre (0.0–2.0) contrôlant le caractère aléatoire du LLM. 0 = déterministe (idéal pour la sortie structurée), 1 = équilibré, >1 = plus créatif/aléatoire.

**Token**
L'unité de base du texte traitée par un LLM. Environ 3/4 d'un mot en anglais. Les coûts et les limites de contexte sont mesurés en tokens.

**Tool Calling**
Voir *Function Calling*.

**Top-K / Top-P**
Stratégies d'échantillonnage pour la sortie du LLM. Top-K : ne considérer que les K tokens les plus probables suivants. Top-P (échantillonnage par noyau) : considérer les tokens dont la probabilité cumulée dépasse P.

---

## V

**Vector Database**
Une base de données optimisée pour stocker et interroger des embeddings par similarité. Exemples : pgvector, ChromaDB, Pinecone, Weaviate, Azure AI Search.

**Vector Search**
Trouver les vecteurs les plus proches (embeddings les plus similaires) d'un vecteur de requête en utilisant des métriques comme la similarité cosinus ou la distance L2.

---

## W

**Webhook**
Un point de terminaison HTTP qui reçoit des événements d'un service externe. Les extensions GitHub Copilot utilisent des webhooks pour recevoir des messages de chat et retourner des réponses.

---

## Acronymes courants

| Acronyme | Nom complet |
|----------|-------------|
| AI | Artificial Intelligence (Intelligence artificielle) |
| API | Application Programming Interface (Interface de programmation applicative) |
| BM25 | Best Match 25 (algorithme de scoring par mots-clés) |
| CE | Conformité Européenne (certification de sécurité) |
| CLI | Command Line Interface (Interface en ligne de commande) |
| CV | Computer Vision (Vision par ordinateur) |
| DI | Dependency Injection (Injection de dépendances) |
| DSL | Domain-Specific Language (Langage spécifique au domaine) |
| GPT | Generative Pre-trained Transformer (Transformeur génératif pré-entraîné) |
| JSON | JavaScript Object Notation |
| JWT | JSON Web Token |
| LLM | Large Language Model (Grand modèle de langage) |
| MCP | Model Context Protocol (Protocole de contexte de modèle) |
| ML | Machine Learning (Apprentissage automatique) |
| NLP | Natural Language Processing (Traitement du langage naturel) |
| RAG | Retrieval Augmented Generation (Génération augmentée par récupération) |
| RLS | Row Level Security (Sécurité au niveau des lignes) |
| RRF | Reciprocal Rank Fusion (Fusion de rang réciproque) |
| SDK | Software Development Kit (Kit de développement logiciel) |
| SK | Semantic Kernel |
| SQL | Structured Query Language (Langage de requête structuré) |

---

*Un terme manque ? [Ouvrez une issue](https://github.com/lcarli/AI-LearningHub/issues/new) ou soumettez une PR !*
