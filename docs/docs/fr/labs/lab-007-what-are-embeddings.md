---
tags: [free, beginner, no-account-needed, embeddings, rag]
---
# Lab 007 : Que sont les embeddings ?

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/rag/">📚 RAG</a> · <a href="../paths/semantic-kernel/">🧠 Semantic Kernel</a></span>
  <span><strong>Durée :</strong> ~15 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Aucun compte requis</span>
</div>

## Ce que vous apprendrez

- Ce qu'est un embedding (un vecteur / une liste de nombres)
- Comment le texte est projeté dans un espace de haute dimension
- Ce que signifie la **similarité cosinus** et pourquoi elle est importante
- Pourquoi les embeddings sont au cœur de la recherche sémantique, du RAG et de la mémoire d'agent
- Quels modèles d'embedding utiliser et quand

---

## Introduction

Les embeddings sont le moteur derrière la recherche sémantique, le RAG et la mémoire vectorielle des agents IA. Une fois que vous comprenez ce qu'ils sont, beaucoup de « magie » dans les systèmes IA devient évidente.

L'idée clé est simple : **convertir n'importe quel morceau de texte en une liste de nombres (un vecteur) de sorte que les textes similaires produisent des vecteurs similaires.**

---

## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-007/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `embedding_explorer.py` | Script d'exercices interactifs | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-007/embedding_explorer.py) |

---

## Partie 1 : Le texte comme un point dans l'espace

Imaginez une carte 2D où chaque mot est placé en fonction de son sens :

![Espace d'Embedding 2D](../../assets/diagrams/embedding-space-2d.svg)

Les mots ayant des sens similaires se regroupent. « Dog » est proche de « Cat » et « Pet ». « Python » se regroupe près de « Code » et « Programming » — pas près de « Snake » (dans un corpus orienté code).

Les vrais modèles d'embedding n'utilisent pas 2 dimensions — ils en utilisent **1 536** (OpenAI) ou **3 072**. Mais le principe est le même : sens similaire = point proche dans l'espace.

??? question "🤔 Vérifiez votre compréhension"
    Pourquoi les modèles d'embedding utilisent-ils 1 536 dimensions au lieu de seulement 2 ou 3 ?

    ??? success "Réponse"
        Le langage humain a une complexité énorme — synonymes, contexte, ton, sens spécifique au domaine. Deux ou trois dimensions ne peuvent pas capturer toutes ces nuances. Les **dimensions élevées** permettent au modèle d'encoder simultanément de nombreux aspects différents du sens, de sorte que des distinctions subtiles (comme « Python le langage » vs « python le serpent ») peuvent être représentées comme des directions différentes dans l'espace vectoriel.

---

## Partie 2 : À quoi ressemble réellement un embedding

Lorsque vous vectorisez le texte `"waterproof hiking boots"`, vous obtenez en retour quelque chose comme :

```python
[0.023, -0.157, 0.842, 0.001, -0.334, 0.711, ..., 0.089]
# ↑ 1,536 numbers for text-embedding-3-small
```

Chaque nombre encode un aspect du sens — mais il n'y a pas d'interprétation lisible par l'humain des dimensions individuelles. Le sens réside dans les *relations* entre les vecteurs.

---

## Partie 3 : Mesurer la similarité — Distance cosinus

Pour comparer deux vecteurs, nous utilisons la **similarité cosinus** : l'angle entre eux.

```
Vector A ("waterproof hiking boots")
      ↗

Vector B ("weatherproof trekking shoes")  ← small angle → very similar
      ↗ (almost same direction)

Vector C ("chocolate birthday cake")      ← large angle → very different
→  (completely different direction)
```

La similarité cosinus va de **-1 à 1** :
- `1.0` = sens identique
- `0.0` = sans rapport
- `-1.0` = sens opposé

En pratique, la plupart des documents similaires obtiennent un score entre **0,7 et 0,95**.

??? question "🤔 Vérifiez votre compréhension"
    Deux textes ont une similarité cosinus de 0,05. Que vous dit cela sur leur relation ?

    ??? success "Réponse"
        Une similarité cosinus de 0,05 signifie que les textes sont **essentiellement sans rapport** — leurs vecteurs pointent dans des directions presque perpendiculaires. Sur l'échelle de -1 à 1, un score proche de 0 indique aucune connexion sémantique significative. Les documents similaires obtiennent typiquement un score entre 0,7 et 0,95.

---

```python
# Simplified cosine similarity
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# "king" - "man" + "woman" ≈ "queen"  (the famous word2vec example)
similarity = cosine_similarity(embed("king"), embed("queen"))
# → ~0.89 (very similar)

similarity = cosine_similarity(embed("king"), embed("pizza"))
# → ~0.12 (unrelated)
```

---

## Partie 4 : Où les embeddings sont utilisés dans les systèmes d'agents

### 1. Recherche sémantique (RAG)
```
User query: "something to keep rain out while hiking"
         ↓ embed
[0.023, -0.157, ...]
         ↓ compare with all document vectors
Matches: "waterproof hiking jacket" (0.91)
         "rain-resistant trekking gear" (0.88)
         "chocolate cake recipe" (0.08) ← filtered out
```

### 2. Mémoire d'agent (Semantic Kernel / LangChain)
La mémoire à long terme de l'agent stocke les interactions passées sous forme d'embeddings. Quand l'utilisateur mentionne un sujet, l'agent récupère les souvenirs sémantiquement pertinents :

```
User: "Let's continue our discussion about the camping budget"
         ↓ embed query
Retrieves: previous conversation about camping (0.87 similarity)
Not: unrelated conversation about software (0.12 similarity)
```

### 3. Détection de doublons
```
"How do I return a product?" (0.94 similarity)
"What's your return policy?"
→ Detected as duplicates → merge/deduplicate FAQs
```

### 4. Regroupement / Catégorisation
Regroupez automatiquement des documents par sens sans catégories prédéfinies.

---

## Partie 5 : Modèles d'embedding

| Modèle | Dimensions | Contexte | Coût | Idéal pour |
|-------|-----------|---------|------|---------|
| `text-embedding-3-small` (OpenAI) | 1 536 | 8 191 tokens | Faible | La plupart des cas d'usage |
| `text-embedding-3-large` (OpenAI) | 3 072 | 8 191 tokens | Plus élevé | Meilleure précision |
| `text-embedding-ada-002` (OpenAI) | 1 536 | 8 191 tokens | Faible | Hérité |
| `nomic-embed-text` (Ollama) | 768 | 8 192 tokens | **Gratuit (local)** | Hors ligne/privé |
| `mxbai-embed-large` (Ollama) | 1 024 | 512 tokens | **Gratuit (local)** | Production locale |

??? question "🤔 Vérifiez votre compréhension"
    Votre système RAG a ingéré tous les documents avec `text-embedding-3-small`. Vous passez ensuite à `text-embedding-3-large` pour les requêtes. Le système fonctionnera-t-il toujours correctement ?

    ??? success "Réponse"
        **Non.** Les vecteurs de modèles d'embedding différents sont **incompatibles** — ils projettent dans des espaces vectoriels différents avec des dimensions différentes (1 536 vs 3 072). Les comparer produirait des scores de similarité sans signification. Vous devez **toujours utiliser le même modèle** pour l'ingestion et les requêtes, ou re-vectoriser tous les documents avec le nouveau modèle.

!!! tip "Utilisez text-embedding-3-small via GitHub Models (gratuit)"
    Dans les labs L200 de ce hub, nous utilisons `text-embedding-3-small` via l'API GitHub Models — gratuit, sans carte de crédit, même qualité qu'Azure OpenAI payant.

---

## Partie 6 : Propriétés clés et pièges

### ✅ Les embeddings capturent le sens entre les langues
```
embed("waterproof jacket") ≈ embed("veste imperméable")  # French
```
Les modèles multilingues fonctionnent entre les langues — les requêtes dans une langue peuvent trouver des documents dans une autre.

### ⚠️ Les embeddings sont spécifiques au modèle
Les vecteurs de `text-embedding-3-small` ne sont **pas comparables** aux vecteurs de `nomic-embed-text`. Ne mélangez jamais les modèles dans le même magasin vectoriel.

### ⚠️ Les embeddings ne capturent pas bien les correspondances exactes
```
embed("SKU-12345") may not match embed("product SKU-12345")
```
Pour les identifiants exacts, codes ou mots-clés → utilisez la recherche par mots-clés/BM25 en complément des embeddings (recherche hybride).

### ⚠️ Le texte long perd en détail
Vectoriser un document de 10 pages en un seul vecteur perd le sens détaillé. C'est pourquoi nous **découpons** d'abord, puis vectorisons chaque morceau séparément.

---

## 📁 Pratique : Explorateur d'embeddings

Ce lab inclut un script Python qui vous permet de **voir les embeddings en action** en utilisant le niveau gratuit de GitHub Models.

```
lab-007/
└── embedding_explorer.py   ← Cosine similarity demo with OutdoorGear products
```

**Prérequis :** Python 3.9+ et un token GitHub (gratuit)

```bash
# Install dependencies
pip install openai

# Set your GitHub token
export GITHUB_TOKEN=<your_PAT>    # Linux/macOS
set GITHUB_TOKEN=<your_PAT>       # Windows

# Run the explorer
python lab-007/embedding_explorer.py
```

**Ce que vous verrez :**

1. **Recherche sémantique :** Trouver des produits correspondant à « lightweight tent for solo hiking » sans correspondance de mots-clés
2. **Sémantique vs mots-clés :** Comparer comment la recherche par mots-clés manque « something to sleep in the cold » tandis que la recherche sémantique trouve le sac de couchage
3. **Matrice de similarité :** Voir que deux descriptions de tentes obtiennent un score de similarité plus élevé entre elles qu'une tente vs un sac de couchage

Cela illustre directement pourquoi le RAG fonctionne : l'embedding d'une *question* et l'embedding de son *document de réponse* atterrissent proches l'un de l'autre dans l'espace vectoriel.

---

## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Deux descriptions de produits ont une similarité cosinus de 0,95. Que signifie cela ?"

    - A) Ce sont des produits complètement sans rapport
    - B) Ils partagent 95 % des mêmes mots
    - C) Ils sont sémantiquement très similaires — leurs représentations vectorielles pointent dans quasiment la même direction
    - D) Un document est 95 % plus long que l'autre

    ??? success "✅ Voir la réponse"
        **Correct : C**

        La similarité cosinus mesure l'*angle* entre deux vecteurs, pas le chevauchement de mots. Un score de 0,95 signifie que les vecteurs pointent dans quasiment la même direction — les textes sont sémantiquement très similaires. En pratique : des produits de même catégorie comme deux tentes obtiennent ~0,90–0,96 ; des produits sans rapport (tente vs sac à dos) obtiennent ~0,70–0,82 ; du texte complètement sans rapport obtient < 0,5.

??? question "**Q2 (Choix multiple) :** Votre système RAG utilise `text-embedding-3-small` pour l'ingestion des documents mais `text-embedding-3-large` pour l'embedding des requêtes. Que va-t-il se passer ?"

    - A) Les requêtes seront plus lentes mais plus précises
    - B) Les scores de similarité seront sans signification — vous comparez des vecteurs d'espaces différents
    - C) Le système normalisera automatiquement les vecteurs pour les rendre compatibles
    - D) Les performances s'améliorent car le plus grand modèle fournit une compréhension plus riche des requêtes

    ??? success "✅ Voir la réponse"
        **Correct : B — Les vecteurs de modèles différents sont incompatibles**

        Chaque modèle d'embedding projette le texte dans son propre espace de haute dimension unique. `text-embedding-3-small` produit des vecteurs à 1 536 dimensions ; `text-embedding-3-large` produit des vecteurs à 3 072 dimensions. Même si vous les forciez à la même dimension, les significations numériques sont complètement différentes. Vous obtiendriez des scores de similarité aléatoires. **Utilisez toujours le même modèle pour l'ingestion et les requêtes.**

??? question "**Q3 (Exécutez le lab) :** Exécutez `python lab-007/embedding_explorer.py`. Dans la sortie de la matrice de similarité, quels deux produits (autres qu'un produit comparé à lui-même) ont le score de similarité cosinus le PLUS ÉLEVÉ entre eux ?"

    Exécutez le script et regardez la section matrice de similarité à la fin de la sortie.

    ??? success "✅ Voir la réponse"
        **P001 (TrailBlazer Tent 2P) et P003 (TrailBlazer Solo)**

        Les deux sont des tentes de randonnée 3 saisons avec des descriptions très similaires — même catégorie, même saison, mêmes matériaux de construction. Leurs descriptions partagent le plus de chevauchement sémantique dans le catalogue. Score typique : **~0,93–0,97**. En comparaison, une tente vs un sac de couchage obtient un score beaucoup plus bas (~0,75–0,85) car ils servent des usages différents bien que les deux soient du matériel de camping.

---

## Résumé

| Concept | Point clé |
|---------|-------------|
| **Embedding** | Une liste de ~1 536 nombres représentant le sens du texte |
| **Similarité cosinus** | Mesure l'angle entre les vecteurs ; plus proche = plus similaire |
| **Recherche sémantique** | Trouver du contenu pertinent par le sens, pas les mots exacts |
| **Spécifique au modèle** | Ne jamais mélanger des vecteurs de modèles d'embedding différents |
| **Découpage d'abord** | Vectoriser les morceaux, pas les documents entiers |
| **Option gratuite** | `text-embedding-3-small` via GitHub Models ou `nomic-embed-text` via Ollama |

---

## Prochaines étapes

- **Voir les embeddings dans une application RAG :** → [Lab 022 — RAG avec GitHub Models + pgvector](lab-022-rag-github-models-pgvector.md)
- **Exécuter des embeddings localement et gratuitement :** → [Lab 015 — Ollama LLM locaux](lab-015-ollama-local-llms.md)
- **Utiliser les embeddings dans Semantic Kernel :** → [Lab 023 — SK Plugins, Mémoire et Planificateurs](lab-023-sk-plugins-memory.md)