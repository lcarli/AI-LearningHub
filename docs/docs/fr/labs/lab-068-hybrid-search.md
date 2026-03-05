---
tags: [search, rag, bm25, vector, semantic-ranker, python]
---
# Lab 068 : Recherche hybride — Vecteurs + BM25 + Ranker sémantique

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Résultats de recherche pré-calculés (aucun Azure AI Search requis)</span>
</div>

## Ce que vous apprendrez

- Les différences entre la recherche **BM25** (mots-clés), **vectorielle** (sémantique) et **hybride**
- Comment le **Reciprocal Rank Fusion (RRF)** combine les scores BM25 et vectoriels
- Comment un **ranker sémantique** (cross-encoder reranker) améliore la précision
- Mesurer la qualité de la recherche avec des métriques de **rappel** et de **précision**
- Comparer les stratégies de recherche à l'aide d'un **jeu de données de benchmark**
- Identifier quels types de requêtes bénéficient le plus de l'hybride + reranking

!!! abstract "Prérequis"
    Complétez d'abord le **[Lab 009 : Génération augmentée par la recherche](lab-009-rag-basic.md)**. Ce lab suppose une familiarité avec la recherche basée sur les embeddings et les concepts de base de la recherche.

## Introduction

Les pipelines RAG dépendent de la qualité de la recherche — si vous récupérez les mauvais segments, même le meilleur LLM produira de mauvaises réponses. La recherche moderne combine plusieurs stratégies pour maximiser le rappel et la précision :

| Stratégie | Fonctionnement | Forces | Faiblesses |
|-----------|---------------|--------|------------|
| **BM25** | Correspondance par mots-clés TF-IDF | Correspondances exactes, termes rares | Pas de compréhension sémantique |
| **Vectorielle** | Similarité cosinus sur les embeddings | Similarité sémantique, synonymes | Manque les mots-clés exacts |
| **Hybride (RRF)** | Combine BM25 + vecteurs via fusion de rangs | Le meilleur des deux mondes | Latence plus élevée |
| **Hybride + Rerank** | Hybride + reranking par cross-encoder | Résultats de la plus haute qualité | Latence et coût les plus élevés |

### Le scénario

Vous avez **20 requêtes de recherche** avec des documents pertinents connus (vérité terrain). Chaque requête a été exécutée avec les quatre stratégies, avec le rappel et la précision enregistrés. Votre mission : analyser quelle stratégie offre la meilleure qualité de recherche et comprendre quand chaque approche excelle.

---

## Prérequis

| Exigence | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| pandas | Analyser les données de comparaison de recherche |

`ash
pip install pandas
`

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier lab-068/ de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| roken_search.py | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-068/broken_search.py) |
| search_comparison.csv | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-068/search_comparison.csv) |

---

## Étape 1 : Comprendre les stratégies de recherche

Chaque stratégie de recherche traite les requêtes différemment :

`
Query → ┬─ [BM25 Index]      → keyword matches   ─┐
        │                                          ├─ [RRF Fusion] → Hybrid Results
        └─ [Vector Index]     → semantic matches   ─┘                      ↓
                                                                  [Semantic Ranker]
                                                                         ↓
                                                               Hybrid + Rerank Results
`

Métriques clés :

1. **Rappel** — Quelle fraction des documents pertinents a été récupérée ? (plus élevé = moins de manques)
2. **Précision** — Quelle fraction des documents récupérés est pertinente ? (plus élevé = moins de bruit)
3. **Score RRF** — Le Reciprocal Rank Fusion combine les classements : 1/(k + rank) sommé à travers les stratégies
4. **Score de reranking** — Score de pertinence cross-encoder appliqué aux résultats hybrides

!!! info "Pourquoi l'hybride bat les deux"
    BM25 excelle pour les correspondances exactes de mots-clés (« error code 0x8004 ») tandis que la recherche vectorielle excelle pour le sens sémantique (« l'application plante au démarrage »). La recherche hybride fusionne les deux — capturant les correspondances exactes que la recherche vectorielle manque ET les correspondances sémantiques que BM25 manque. Le ranker sémantique réordonne ensuite les résultats en utilisant un modèle cross-encoder plus coûteux mais plus précis.

---

## Étape 2 : Charger et explorer les résultats de recherche

Le jeu de données contient **20 requêtes** avec les résultats des quatre stratégies :

`python
import pandas as pd

results = pd.read_csv("lab-068/search_comparison.csv")
print(f"Total queries: {len(results)}")
print(f"Search strategies: {sorted(results.columns)}")
print(f"\nFirst 5 queries:")
print(results[["query_id", "query_text", "bm25_recall", "vector_recall",
               "hybrid_recall", "hybrid_rerank_recall"]].head().to_string(index=False))
`

**Résultat attendu :**

`
Total queries: 20
`

---

## Étape 3 : Comparaison du rappel

Comparez le rappel à travers les quatre stratégies :

`python
print("Average Recall by Strategy:")
print(f"  BM25:            {results['bm25_recall'].mean():.2f}")
print(f"  Vector:          {results['vector_recall'].mean():.2f}")
print(f"  Hybrid:          {results['hybrid_recall'].mean():.2f}")
print(f"  Hybrid + Rerank: {results['hybrid_rerank_recall'].mean():.2f}")

perfect_recall = results[results["hybrid_rerank_recall"] == 1.0]
print(f"\nQueries with perfect hybrid+rerank recall: {len(perfect_recall)} / {len(results)}")
`

**Résultat attendu :**

`
Average Recall by Strategy:
  BM25:            0.47
  Vector:          0.62
  Hybrid:          0.85
  Hybrid + Rerank: 1.00
`

!!! tip "Aperçu clé"
    Hybride + Rerank atteint un rappel parfait (1,00) — chaque document pertinent est récupéré pour chaque requête. BM25 seul récupère moins de la moitié des documents pertinents en moyenne. Cela démontre pourquoi les pipelines RAG modernes devraient utiliser la recherche hybride avec reranking autant que possible.

---

## Étape 4 : Analyse de la précision

Le rappel sans précision signifie récupérer trop de bruit. Analysez la précision :

`python
print("Average Precision by Strategy:")
print(f"  BM25:            {results['bm25_precision'].mean():.2f}")
print(f"  Vector:          {results['vector_precision'].mean():.2f}")
print(f"  Hybrid:          {results['hybrid_precision'].mean():.2f}")
print(f"  Hybrid + Rerank: {results['hybrid_rerank_precision'].mean():.2f}")
`

**Résultat attendu :**

`
Average Precision by Strategy:
  BM25:            0.40
  Vector:          0.48
  Hybrid:          0.52
  Hybrid + Rerank: 0.57
`

!!! warning "Compromis précision vs rappel"
    Même hybride + rerank n'atteint qu'une précision moyenne de 0,57 — ce qui signifie que 43 % des documents récupérés ne sont pas pertinents. Un rappel élevé garantit qu'aucun document pertinent n'est manqué, mais le LLM doit filtrer le bruit du contexte. Envisagez d'utiliser un seuil de reranking plus strict pour améliorer la précision au détriment d'un certain rappel.

---

## Étape 5 : Analyse au niveau des requêtes

Identifiez quelles requêtes bénéficient le plus de la recherche hybride :

`python
results["hybrid_lift"] = results["hybrid_rerank_recall"] - results["bm25_recall"]
biggest_lift = results.sort_values("hybrid_lift", ascending=False).head(5)
print("Queries with biggest recall lift (hybrid+rerank vs BM25):")
print(biggest_lift[["query_id", "query_text", "bm25_recall", "hybrid_rerank_recall", "hybrid_lift"]]
      .to_string(index=False))
`

Les requêtes avec le plus grand gain sont généralement de nature sémantique — paraphrases, synonymes ou requêtes conceptuelles où la correspondance par mots-clés de BM25 échoue mais la similarité vectorielle réussit.

---

## Étape 6 : Moteur de recommandation de stratégie de recherche

Construisez une recommandation basée sur l'analyse :

`python
summary = f"""
╔════════════════════════════════════════════════════════╗
║     Hybrid Search — Strategy Comparison Report         ║
╠════════════════════════════════════════════════════════╣
║ Queries Evaluated:           {len(results):>5}                     ║
║ BM25 Avg Recall:             {results['bm25_recall'].mean():>5.2f}                     ║
║ Vector Avg Recall:           {results['vector_recall'].mean():>5.2f}                     ║
║ Hybrid Avg Recall:           {results['hybrid_recall'].mean():>5.2f}                     ║
║ Hybrid+Rerank Avg Recall:    {results['hybrid_rerank_recall'].mean():>5.2f}                     ║
║ Hybrid+Rerank Avg Precision: {results['hybrid_rerank_precision'].mean():>5.2f}                     ║
╚════════════════════════════════════════════════════════╝
"""
print(summary)
`

---

## 🐛 Exercice de correction de bugs

Le fichier lab-068/broken_search.py contient **3 bugs** dans la manière dont il calcule les métriques de recherche :

`ash
python lab-068/broken_search.py
`

| Test | Ce qu'il vérifie | Indice |
|------|-----------------|--------|
| Test 1 | Calcul du rappel moyen | Devrait utiliser mean(), pas sum() |
| Test 2 | Nom de la colonne de précision | Devrait utiliser hybrid_rerank_precision, pas hybrid_precision |
| Test 3 | Comparaison du rappel | Devrait comparer hybrid_rerank_recall >= bm25_recall, pas <= |

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Que fait le Reciprocal Rank Fusion (RRF) dans la recherche hybride ?"

    - A) Il remplace l'index vectoriel par un index de mots-clés
    - B) Il combine les classements de plusieurs stratégies de recherche en un classement unifié unique
    - C) Il entraîne un nouveau modèle d'embedding sur la requête
    - D) Il réduit le nombre de documents dans l'index

    ??? success "✅ Révéler la réponse"
        **Correct : B) Il combine les classements de plusieurs stratégies de recherche en un classement unifié unique**

        Le RRF fusionne les classements de résultats de BM25 et de la recherche vectorielle en utilisant la formule 1/(k + rank) sommée à travers les stratégies. Les documents bien classés par les deux stratégies sont renforcés, tandis que les documents bien classés par une seule stratégie apparaissent quand même. Cela produit un classement unifié qui capture à la fois la pertinence par mots-clés et sémantique.

??? question "**Q2 (Choix multiple) :** Pourquoi un ranker sémantique (cross-encoder) améliore-t-il les résultats par rapport à la recherche hybride seule ?"

    - A) Il est plus rapide que BM25
    - B) Il re-score chaque candidat en encodant conjointement la requête et le document ensemble, capturant des signaux de pertinence plus profonds
    - C) Il supprime parfaitement tous les documents non pertinents
    - D) Il génère de nouveaux documents pour combler les lacunes

    ??? success "✅ Révéler la réponse"
        **Correct : B) Il re-score chaque candidat en encodant conjointement la requête et le document ensemble, capturant des signaux de pertinence plus profonds**

        Un cross-encoder prend à la fois la requête et un document candidat en entrée et produit un score de pertinence. Contrairement aux bi-encodeurs (utilisés pour la recherche vectorielle), les cross-encodeurs capturent des interactions fines entre les tokens de la requête et du document. C'est plus précis mais trop coûteux pour l'appliquer à l'index entier — il est donc utilisé comme reranker sur les top-N résultats hybrides.

??? question "**Q3 (Exécuter le lab) :** Quel est le rappel moyen de la stratégie hybride + rerank ?"

    Calculez esults['hybrid_rerank_recall'].mean().

    ??? success "✅ Révéler la réponse"
        **1,00 (rappel parfait)**

        Hybride + rerank atteint un rappel parfait sur les 20 requêtes, ce qui signifie que chaque document pertinent est récupéré pour chaque requête. C'est une amélioration significative par rapport à BM25 seul (0,47) et démontre la valeur de combiner la recherche par mots-clés et sémantique avec le reranking par cross-encoder.

??? question "**Q4 (Exécuter le lab) :** Quel est le rappel moyen de la recherche BM25 seule ?"

    Calculez esults['bm25_recall'].mean().

    ??? success "✅ Révéler la réponse"
        **0,47 de rappel moyen**

        BM25 récupère moins de la moitié des documents pertinents en moyenne. C'est parce que BM25 repose sur la correspondance de mots-clés et ne peut pas gérer les synonymes, paraphrases ou requêtes conceptuelles. Par exemple, une requête sur « plantage d'application » manquerait les documents qui discutent de « défaillances logicielles » ou « instabilité du système ».

??? question "**Q5 (Exécuter le lab) :** Quelle est la précision moyenne de la stratégie hybride + rerank ?"

    Calculez esults['hybrid_rerank_precision'].mean().

    ??? success "✅ Révéler la réponse"
        **0,57 de précision moyenne**

        Bien que hybride + rerank atteigne un rappel parfait, sa précision est de 0,57 — ce qui signifie que 43 % des documents récupérés ne sont pas pertinents. C'est le compromis rappel-précision : maximiser le rappel garantit qu'aucun document pertinent n'est manqué, mais inclut du bruit. Le LLM doit être suffisamment robuste pour ignorer le contexte non pertinent lors de la génération des réponses.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|------------------------|
| Recherche BM25 | Recherche par mots-clés utilisant le scoring TF-IDF |
| Recherche vectorielle | Recherche sémantique utilisant la similarité cosinus des embeddings |
| Recherche hybride | Combinaison de BM25 + vecteurs via Reciprocal Rank Fusion |
| Ranker sémantique | Reranking par cross-encoder pour un classement de résultats de meilleure qualité |
| Rappel et précision | Mesure de la qualité de la recherche avec des métriques complémentaires |
| Sélection de stratégie | Choisir la bonne stratégie de recherche en fonction des caractéristiques des requêtes |

---

## Prochaines étapes

- **[Lab 009](lab-009-rag-basic.md)** — Les bases du RAG (schémas fondamentaux de recherche)
- **[Lab 067](lab-067-graphrag.md)** — GraphRAG (synthèse inter-documents avec graphes de connaissances)
- **[Lab 065](lab-065-purview-dspm-ai.md)** — Purview DSPM for AI (gouvernance pour les pipelines de recherche)