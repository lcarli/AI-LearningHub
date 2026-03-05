---
tags: [free, beginner, no-account-needed, rag]
---
# Lab 006 : Qu'est-ce que le RAG ?

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/rag/">📚 RAG</a></span>
  <span><strong>Durée :</strong> ~20 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Aucun compte requis</span>
</div>

## Ce que vous apprendrez

- Pourquoi les LLM ont besoin de connaissances externes (et pourquoi les données d'entraînement seules ne suffisent pas)
- Le pipeline RAG complet : ingestion → découpage → embedding → stockage → récupération → génération
- La différence entre la **recherche par mots-clés**, la **recherche sémantique** et la **recherche hybride**
- Quand utiliser le RAG vs l'affinage vs simplement une plus grande fenêtre de contexte
- Des architectures RAG du monde réel

---

## Introduction

Imaginez que vous avez construit un agent IA pour votre entreprise. Il répond aux questions magnifiquement — jusqu'à ce qu'un utilisateur demande un produit lancé le mois dernier, ou une politique mise à jour la semaine dernière.

Le LLM ne sait pas. Ses données d'entraînement ont une date de coupure. Et même si l'information existait dans les données d'entraînement, le modèle peut ne pas l'avoir mémorisée avec précision.

**RAG (Génération Augmentée par la Récupération)** résout ce problème en connectant le LLM à vos propres connaissances à jour au moment de la requête — sans ré-entraîner le modèle.

![Pipeline RAG](../../assets/diagrams/rag-pipeline.svg)

---

## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-006/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `faq_backpacks.txt` | Fichier de base de connaissances FAQ | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-006/faq_backpacks.txt) |
| `faq_clothing.txt` | Fichier de base de connaissances FAQ | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-006/faq_clothing.txt) |
| `faq_footwear.txt` | Fichier de base de connaissances FAQ | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-006/faq_footwear.txt) |
| `faq_sleeping_bags.txt` | Fichier de base de connaissances FAQ | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-006/faq_sleeping_bags.txt) |
| `faq_tents.txt` | Fichier de base de connaissances FAQ | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-006/faq_tents.txt) |

---

## Partie 1 : Le problème fondamental

Les LLM ont deux limitations de connaissances :

| Limitation | Description | Exemple |
|-----------|-------------|---------|
| **Date de coupure** | Les connaissances s'arrêtent à une date | « Que s'est-il passé la semaine dernière ? » |
| **Données privées** | N'a jamais vu vos documents | « Quelle est notre politique de remboursement ? » |
| **Risque d'hallucination** | Peut confabuler en cas d'incertitude | Invente une réponse plausible mais fausse |

La solution naïve — « mettre tous vos documents dans le prompt » — ne passe pas à l'échelle. Un manuel de 500 pages représente environ 375 000 tokens. La plupart des LLM plafonnent à 128 000 tokens, et même s'ils ne le faisaient pas, vous paieriez pour tous ces tokens à chaque requête.

**La réponse du RAG :** Ne récupérer que les morceaux *pertinents*, exactement quand vous en avez besoin.

---

## Partie 2 : Le pipeline RAG

Le RAG comporte deux phases distinctes :

### Phase 1 — Ingestion (exécutée une fois, ou de façon programmée)

```
Your documents (PDFs, Word, web pages, databases...)
         │
         ▼
    1. LOAD       ── Read content from source
         │
         ▼
    2. CHUNK      ── Split into overlapping segments (~512 tokens each)
         │
         ▼
    3. EMBED      ── Convert each chunk to a vector (list of numbers)
         │
         ▼
    4. STORE      ── Save chunks + vectors in a vector database
                     (pgvector, Azure AI Search, Chroma, Pinecone...)
```

### Phase 2 — Récupération + Génération (exécutée à chaque requête)

```
User asks: "What is the return policy for outdoor equipment?"
         │
         ▼
    5. EMBED QUERY ── Convert user question to a vector
         │
         ▼
    6. SEARCH     ── Find the most similar chunks in the vector DB
                     (cosine similarity / vector distance)
         │
         ▼
    7. AUGMENT    ── Inject retrieved chunks into the prompt:
                     "Answer based on these documents: [chunks]"
         │
         ▼
    8. GENERATE   ── LLM answers, grounded in real data
         │
         ▼
    User gets: "Our return policy for outdoor equipment allows returns
               within 30 days with original receipt..."
```

??? question "🤔 Vérifiez votre compréhension"
    Dans le pipeline RAG, quelle est la différence entre la **phase d'ingestion** et la **phase de récupération**, et à quelle fréquence chacune s'exécute-t-elle ?

    ??? success "Réponse"
        La **phase d'ingestion** (Charger → Découper → Vectoriser → Stocker) s'exécute **une fois** (ou de façon programmée) pour préparer vos documents. La **phase de récupération** (Vectoriser la requête → Rechercher → Augmenter → Générer) s'exécute **à chaque requête utilisateur** pour trouver les morceaux pertinents et générer une réponse. L'ingestion est un processus par lots ; la récupération est en temps réel.

---

## Partie 3 : Stratégies de découpage

La façon dont vous découpez les documents est extrêmement importante.

| Stratégie | Comment | Idéale pour |
|----------|-----|---------|
| **Taille fixe** | Découper tous les N tokens | Simple, rapide, fonctionne pour la plupart des cas |
| **Phrase/paragraphe** | Découper aux limites naturelles | Meilleure préservation du contexte |
| **Sémantique** | Découper quand le sujet change | Meilleure qualité, plus complexe |
| **Récursive** | Essayer paragraphe → phrase → mot | Bon défaut pour le contenu mixte |

**Le chevauchement est important.** Si vous découpez exactement à 512 tokens, les informations pertinentes qui chevauchent une limite sont perdues. Ajoutez un chevauchement de 50 à 100 tokens entre les morceaux.

```
Chunk 1: tokens 1–512
Chunk 2: tokens 462–974   ← 50-token overlap
Chunk 3: tokens 924–1436  ← 50-token overlap
```

??? question "🤔 Vérifiez votre compréhension"
    Pourquoi est-il important d'ajouter un **chevauchement** entre les morceaux lors du découpage des documents ?

    ??? success "Réponse"
        Sans chevauchement, les informations pertinentes qui chevauchent une limite de morceau sont **réparties entre deux morceaux** et peuvent être perdues lors de la récupération. Ajouter un chevauchement de 50 à 100 tokens garantit que le contexte aux bords est préservé dans les deux morceaux adjacents, améliorant la qualité de la récupération.

---

## Partie 4 : Types de recherche

### Recherche par mots-clés (BM25)
Recherche traditionnelle — correspond aux mots exacts. Rapide, interprétable, mais manque les synonymes et l'intention.

```
Query: "waterproof jacket"
Finds: documents containing exactly "waterproof" and "jacket"
Misses: "rain-resistant coat", "weatherproof outerwear"
```

### Recherche sémantique (vectorielle)
Compare le sens, pas les mots. Trouve du contenu conceptuellement similaire.

```
Query: "waterproof jacket"
Finds: "rain-resistant coat", "all-weather outerwear", "waterproof jacket"
Based on: vector similarity in embedding space
```

### Recherche hybride (BM25 + vectorielle)
Le meilleur des deux mondes — combine les scores par mots-clés et sémantiques.

```
Final score = α × keyword_score + (1-α) × semantic_score
```

La plupart des systèmes RAG en production utilisent la recherche hybride car elle gère à la fois les recherches exactes (« SKU-12345 ») et les requêtes sémantiques (« quelque chose pour camper sous la pluie »).

??? question "🤔 Vérifiez votre compréhension"
    Un utilisateur cherche « rain-resistant coat » mais le document ne contient que l'expression « waterproof jacket ». La recherche par mots-clés le trouvera-t-elle ? La recherche sémantique ? Pourquoi ?

    ??? success "Réponse"
        **La recherche par mots-clés ne le trouvera pas** — il n'y a pas de mots correspondants entre « rain-resistant coat » et « waterproof jacket ». **La recherche sémantique le trouvera** car elle compare le sens via la similarité vectorielle, pas les mots exacts. Les deux expressions ont des significations très similaires et auront des représentations vectorielles similaires. C'est pourquoi la recherche hybride (combinant les deux) est préférée en production.

---

## Partie 5 : RAG vs Affinage vs Grand contexte

Une question courante : « Pourquoi ne pas simplement affiner le modèle sur mes données ? »

| Approche | Coût | Fraîcheur | Idéale pour |
|----------|------|-----------|---------|
| **RAG** | Faible | ✅ Temps réel | Données dynamiques, documents, Q&R |
| **Affinage** | Élevé | ❌ Statique | Ton, style, vocabulaire métier |
| **Grand contexte** | Moyen | ✅ Par requête | Petits jeux de données qui tiennent dans le contexte |
| **RAG + Affinage** | Élevé | ✅ Temps réel | Systèmes de production nécessitant les deux |

**Règle de base :** Utilisez le RAG pour les *connaissances* (faits, documents). Utilisez l'affinage pour le *comportement* (ton, style, format). Ils sont complémentaires, pas en concurrence.

---

## Partie 6 : Métriques de qualité RAG

Un système RAG peut échouer à deux endroits :

| Échec | Symptôme | Correction |
|---------|---------|-----|
| **Mauvaise récupération** | Les morceaux récupérés ne sont pas pertinents | Meilleur découpage, recherche hybride, re-classement |
| **Mauvaise génération** | Le LLM ignore ou mal utilise le contenu récupéré | Prompt système plus fort, obligation de citation |

Métriques clés utilisées dans le [Lab 035](lab-035-agent-evaluation.md) et le [Lab 042](lab-042-enterprise-rag.md) :

- **Ancrage** : La réponse est-elle étayée par les documents récupérés ?
- **Pertinence** : Les morceaux récupérés sont-ils réellement pertinents par rapport à la question ?
- **Cohérence** : La réponse est-elle bien structurée et lisible ?
- **Fidélité** : La réponse reste-t-elle fidèle au matériel source ?

---

## Architectures RAG du monde réel

### RAG basique
```
User → Embed query → Vector search → Augment prompt → LLM → Answer
```

### RAG agentique (couvert dans le Lab 026)
```
User → Agent decides: search? what query? how many chunks?
     → Multiple targeted searches
     → Agent synthesizes results
     → Answer with citations
```

### RAG correctif
```
User → Retrieve → Grade relevance → If poor: web search fallback
     → Augment → Generate → Self-check → Answer
```

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Que signifie RAG, et quel problème résout-il principalement ?"

    - A) Recursive Augmented Graph — il résout les problèmes de raisonnement multi-étapes
    - B) Retrieval-Augmented Generation — il ancre les réponses LLM dans des données privées ou à jour sans ré-entraînement
    - C) Randomized Agent Generation — il rend les réponses des agents moins déterministes
    - D) Ranked Answer Generation — il améliore le classement des résultats de recherche

    ??? success "✅ Voir la réponse"
        **Correct : B — Retrieval-Augmented Generation**

        Le RAG connecte le LLM à vos propres connaissances au moment de la requête. Au lieu que le modèle se fie aux données d'entraînement (qui ont une date de coupure et n'incluent pas vos documents privés), le RAG récupère les morceaux les plus pertinents de votre magasin de données et les inclut dans le prompt. Aucun ré-entraînement nécessaire.

??? question "**Q2 (Choix multiple) :** Dans le pipeline d'ingestion RAG, quelle étape vient immédiatement AVANT le stockage des vecteurs dans la base de données ?"

    - A) Le découpage
    - B) Le chargement des documents
    - C) La génération des embeddings
    - D) Le re-classement sémantique

    ??? success "✅ Voir la réponse"
        **Correct : C — La génération des embeddings**

        L'ordre d'ingestion est : **Charger → Découper → Vectoriser → Stocker**. Vous chargez d'abord les documents bruts, les découpez en morceaux plus petits (~512 tokens avec chevauchement), *puis* convertissez chaque morceau en un vecteur d'embedding à l'aide du modèle d'embedding, et enfin stockez ces vecteurs dans la base de données vectorielle. Le re-classement sémantique est une étape de récupération, pas d'ingestion.

??? question "**Q3 (Exécutez le lab) :** Ouvrez le fichier `lab-006/faq_tents.txt`. Combien de paires Q&R contient-il, et quel est le sujet de la DERNIÈRE question ?"

    Ouvrez `lab-006/faq_tents.txt` et comptez les paires Q&R. La dernière question commence par « Q: ».

    ??? success "✅ Voir la réponse"
        **5 paires Q&R. La dernière question est : « Can I use a 2-person tent solo? »**

        [📥 `faq_tents.txt`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-006/faq_tents.txt) contient exactement 5 paires Q&R couvrant : le choix d'une tente de randonnée solo, 3 saisons vs 4 saisons, l'imperméabilisation, les matériaux des arceaux, et l'utilisation d'une tente 2P en solo. C'est le type de base de connaissances qu'un système RAG ingérerait — chaque paire Q&R est un morceau naturel pour l'embedding.

---

## Résumé

| Concept | Point clé |
|---------|-------------|
| **Pourquoi le RAG** | Les LLM ne connaissent pas vos données ni les événements récents — le RAG corrige cela |
| **Ingestion** | Charger → Découper → Vectoriser → Stocker (exécuté une fois) |
| **Récupération** | Vectoriser la requête → Recherche vectorielle → Top-k morceaux |
| **Découpage** | La taille + le chevauchement comptent ; ~512 tokens avec 50 tokens de chevauchement |
| **Recherche** | L'hybride (mots-clés + sémantique) surpasse chacune seule |
| **Évaluation** | Mesurer l'ancrage et la pertinence — tant pour la récupération que pour la génération |

---

## Prochaines étapes

- **Comprendre les vecteurs d'embedding :** → [Lab 007 — Que sont les embeddings ?](lab-007-what-are-embeddings.md)
- **Construire une application RAG gratuitement :** → [Lab 022 — RAG avec GitHub Models + pgvector](lab-022-rag-github-models-pgvector.md)
- **RAG en production sur Azure :** → [Lab 031 — Recherche sémantique pgvector sur Azure](lab-031-pgvector-semantic-search.md)
