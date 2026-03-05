---
tags: [caching, cost-optimization, anthropic, google, openai, python]
---
# Lab 071 : Mise en cache du contexte — Réduire les coûts pour les agents traitant de grands documents

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des données de benchmark simulées</span>
</div>

## Ce que vous apprendrez

- Ce qu'est la **mise en cache du contexte** et comment les fournisseurs (Anthropic, Google, OpenAI) l'implémentent
- Comment les succès de cache réduisent le **temps jusqu'au premier token (TTFT)** et le **coût par requête**
- Analyser un fichier CSV de benchmark pour quantifier les économies de latence et de coût sur 3 fournisseurs
- Identifier quand la mise en cache offre le meilleur retour sur investissement pour les charges de travail d'agents sur grands documents
- Construire un **rapport de performance du cache** comparant l'économie des succès et des échecs de cache

## Introduction

Lorsqu'un agent traite le même document de 100 000 tokens sur plusieurs tours, vous payez ces tokens d'entrée à chaque fois — sauf si vous utilisez la **mise en cache du contexte**. Les trois principaux fournisseurs offrent désormais des mécanismes de mise en cache :

| Fournisseur | Fonctionnalité | Fonctionnement |
|-------------|---------------|----------------|
| **Anthropic** | Prompt Caching | Points de rupture de cache dans les messages système/utilisateur ; tokens en cache facturés à 10 % du prix d'entrée |
| **Google** | Context Caching | Création explicite du cache via l'API ; tokens en cache facturés à 25 % du prix d'entrée |
| **OpenAI** | Automatic Caching | Correspondance automatique de préfixe pour les prompts ≥1024 tokens ; tokens en cache facturés à 50 % du prix d'entrée |

### Le scénario

Vous êtes un **ingénieur de plateforme IA** dans une entreprise de technologie juridique. Votre agent de révision de contrats traite des documents de 150 000 à 200 000 tokens. Chaque contrat nécessite 3 à 5 questions de suivi sur le même document. La direction veut savoir : _« Combien d'argent et de latence pouvons-nous économiser en activant la mise en cache du contexte ? »_

Vous disposez d'un **jeu de données de benchmark** (\cache_benchmark.csv\) avec 15 requêtes sur 3 fournisseurs — un mélange de succès et d'échecs de cache. Votre mission : analyser les données et construire un rapport d'économies.

!!! info "Données simulées"
    Ce lab utilise un fichier CSV de benchmark simulé pour que tout le monde puisse suivre sans clés API. La structure des données et les ratios de coûts reflètent le comportement réel de mise en cache décrit dans la documentation de chaque fournisseur.

## Prérequis

| Exigence | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| \pandas\ | Manipulation des données |

\\\ash
pip install pandas
\\\

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier \lab-071/\ de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| \roken_cache.py\ | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-071/broken_cache.py) |
| \cache_benchmark.csv\ | Jeu de données de benchmark | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-071/cache_benchmark.csv) |

---

## Étape 1 : Comprendre les mécanismes de mise en cache du contexte

Avant d'analyser les données, comprenez les concepts clés :

| Concept | Définition |
|---------|-----------|
| **Échec de cache** | Première requête — contexte complet envoyé au modèle, aucune donnée en cache n'existe |
| **Succès de cache** | Requête suivante — contexte trouvé en cache, traitement d'entrée réduit |
| **TTFT** | Temps jusqu'au premier token — rapidité avec laquelle le modèle commence à répondre |
| **Coût d'entrée** | Coût facturé lorsque le contexte N'EST PAS en cache (plein tarif) |
| **Coût en cache** | Coût facturé lorsque le contexte EST en cache (tarif réduit) |

### Aperçu clé

Les succès de cache font économiser de l'argent de deux manières :

1. **Coût de tokens inférieur** — les tokens en cache sont facturés à une fraction du prix d'entrée
2. **Latence inférieure** — le modèle n'a pas besoin de retraiter l'intégralité du contexte, donc le TTFT diminue drastiquement

---

## Étape 2 : Charger et explorer les données de benchmark

Le jeu de données contient **15 requêtes** sur 3 fournisseurs. Commencez par le charger :

\\\python
import pandas as pd

df = pd.read_csv("lab-071/cache_benchmark.csv")

print(f"Total requests: {len(df)}")
print(f"Providers: {df['provider'].unique().tolist()}")
print(f"Cache statuses: {df['cache_status'].value_counts().to_dict()}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nFirst 5 rows:\n{df.head()}")
\\\

**Résultat attendu :**

\\\
Total requests: 15
Providers: ['anthropic', 'google', 'openai']
Cache statuses: {'hit': 9, 'miss': 6}
\\\

Explorez les données par fournisseur :

\\\python
summary = df.groupby("provider").agg(
    requests=("request_id", "count"),
    hits=("cache_status", lambda x: (x == "hit").sum()),
    misses=("cache_status", lambda x: (x == "miss").sum()),
    avg_tokens=("context_tokens", "mean"),
).reset_index()
print(summary)
\\\

---

## Étape 3 : Analyser l'impact sur la latence — Comparaison du TTFT

Le plus grand bénéfice visible pour l'utilisateur de la mise en cache est la **réduction de latence**. Comparez le TTFT pour les succès vs les échecs de cache :

\\\python
hits = df[df["cache_status"] == "hit"]
misses = df[df["cache_status"] == "miss"]

avg_hit_ttft = hits["ttft_ms"].mean()
avg_miss_ttft = misses["ttft_ms"].mean()
speedup = avg_miss_ttft / avg_hit_ttft

print(f"Avg TTFT (cache hit):  {avg_hit_ttft:.0f} ms")
print(f"Avg TTFT (cache miss): {avg_miss_ttft:.0f} ms")
print(f"Speedup factor:        {speedup:.1f}x faster with cache")
\\\

**Résultat attendu :**

\\\
Avg TTFT (cache hit):  217 ms
Avg TTFT (cache miss): 2583 ms
Speedup factor:        11.9x faster with cache
\\\

Détaillez par fournisseur :

\\\python
ttft_by_provider = df.groupby(["provider", "cache_status"])["ttft_ms"].mean().unstack()
ttft_by_provider["speedup"] = ttft_by_provider["miss"] / ttft_by_provider["hit"]
print(ttft_by_provider.round(0))
\\\

!!! tip "Aperçu"
    Les succès de cache sont environ **10 à 15 fois plus rapides** chez tous les fournisseurs. Pour un agent traitant des questions de suivi sur un grand document, cela signifie des réponses en moins d'une seconde au lieu de 2 à 3 secondes d'attente par tour.

---

## Étape 4 : Analyser les économies de coûts

Calculez maintenant l'impact financier. Chaque ligne a \input_cost_usd\ (facturé lors d'un échec) et \cached_cost_usd\ (facturé lors d'un succès) :

\\\python
total_miss_cost = misses["input_cost_usd"].sum()
total_hit_cost = hits["cached_cost_usd"].sum()
savings = total_miss_cost - total_hit_cost

print(f"Total cost (cache misses): \")
print(f"Total cost (cache hits):   \")
print(f"Total savings:             \")
print(f"Savings ratio:             {savings / total_miss_cost * 100:.0f}%")
\\\

**Résultat attendu :**

\\\
Total cost (cache misses): \.80
Total cost (cache hits):   \.36
Total savings:             \.44
Savings ratio:             80%
\\\

Détaillez par fournisseur :

\\\python
cost_by_provider = []
for provider, group in df.groupby("provider"):
    miss_cost = group[group["cache_status"] == "miss"]["input_cost_usd"].sum()
    hit_cost = group[group["cache_status"] == "hit"]["cached_cost_usd"].sum()
    cost_by_provider.append({
        "Provider": provider,
        "Miss Cost": f"\",
        "Hit Cost": f"\",
        "Savings": f"\",
    })

print(pd.DataFrame(cost_by_provider).to_string(index=False))
\\\

---

## Étape 5 : Calculer le taux de succès du cache et les métriques de ROI

\\\python
hit_rate = len(hits) / len(df) * 100
cost_per_request_with_cache = (total_miss_cost + total_hit_cost) / len(df)
cost_per_request_without_cache = total_miss_cost / len(misses)

print(f"Overall cache hit rate:          {hit_rate:.0f}%")
print(f"Avg cost/request (with cache):   \")
print(f"Avg cost/request (without cache):\")
\\\

### Projection des économies annuelles

\\\python
daily_requests = 500
annual_requests = daily_requests * 365
annual_savings = (savings / len(df)) * annual_requests

print(f"\nProjected annual savings at {daily_requests} requests/day:")
print(f"  \")
\\\

!!! warning "Considérations réelles"
    Les taux de succès du cache dépendent des modèles d'utilisation. Les questions de suivi séquentielles sur le même document obtiennent des taux de succès proches de 100 %. Les requêtes diverses et sans rapport peuvent avoir 0 % de succès. Dimensionnez vos estimations d'économies en fonction des modèles de conversation réels de votre agent.

---

## Étape 6 : Construire le rapport de performance du cache

Combinez toute l'analyse dans un rapport de synthèse :

\\\python
report = f"""# 📊 Context Caching Benchmark Report

## Overview
| Metric | Value |
|--------|-------|
| Total Requests | {len(df)} |
| Cache Hits | {len(hits)} ({hit_rate:.0f}%) |
| Cache Misses | {len(misses)} |
| Providers Tested | {', '.join(df['provider'].unique())} |

## Latency Impact
| Metric | Value |
|--------|-------|
| Avg TTFT (hit) | {avg_hit_ttft:.0f} ms |
| Avg TTFT (miss) | {avg_miss_ttft:.0f} ms |
| Speedup | {speedup:.1f}x |

## Cost Impact
| Metric | Value |
|--------|-------|
| Total Miss Cost | \ |
| Total Hit Cost | \ |
| Total Savings | \ |
| Savings Rate | {savings / total_miss_cost * 100:.0f}% |

## Recommendation
Enable context caching for all large-document agent workflows.
Expected ROI: {savings / total_miss_cost * 100:.0f}% cost reduction, {speedup:.0f}x latency improvement.
"""

print(report)

with open("lab-071/cache_report.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-071/cache_report.md")
\\\

---

## 🐛 Exercice de correction de bugs

Le fichier \lab-071/broken_cache.py\ contient **3 bugs** qui produisent des métriques de mise en cache incorrectes. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

\\\ash
python lab-071/broken_cache.py
\\\

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|-----------------|--------|
| Test 1 | TTFT moyen en cache | Devrait moyenner le TTFT des succès, pas des échecs |
| Test 2 | Économies totales de coût | Devrait être la somme des coûts d'entrée des échecs moins la somme des coûts en cache des succès |
| Test 3 | Taux de succès du cache | Devrait compter les succès / total, pas les échecs / total |

Corrigez les 3 bugs, puis relancez. Quand vous voyez \All passed!\, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quel est le principal avantage de la mise en cache du contexte pour les conversations multi-tours d'un agent ?"

    - A) Elle améliore la précision du raisonnement du modèle
    - B) Elle réduit les coûts des tokens d'entrée et le temps jusqu'au premier token sur un contexte répété
    - C) Elle permet au modèle de se souvenir des conversations précédentes de manière permanente
    - D) Elle augmente la taille maximale de la fenêtre de contexte

    ??? success "✅ Révéler la réponse"
        **Correct : B) Elle réduit les coûts des tokens d'entrée et le temps jusqu'au premier token sur un contexte répété**

        La mise en cache du contexte stocke les tokens d'entrée précédemment traités pour qu'ils n'aient pas besoin d'être renvoyés et retraités. Cela réduit à la fois le coût (les tokens en cache sont facturés avec une remise) et la latence (le TTFT diminue drastiquement car le modèle saute la relecture du contexte en cache).

??? question "**Q2 (Choix multiple) :** Quel fournisseur facture le tarif le plus bas pour les tokens en cache par rapport au plein tarif d'entrée ?"

    - A) OpenAI (50 % du prix d'entrée)
    - B) Google (25 % du prix d'entrée)
    - C) Anthropic (10 % du prix d'entrée)
    - D) Tous les fournisseurs facturent le même tarif en cache

    ??? success "✅ Révéler la réponse"
        **Correct : C) Anthropic (10 % du prix d'entrée)**

        La mise en cache de prompts d'Anthropic facture les tokens en cache à seulement 10 % du prix d'entrée standard, ce qui en fait la remise la plus agressive. Google facture 25 % et OpenAI facture 50 %. Cependant, les modèles de tarification changent — vérifiez toujours la documentation la plus récente.

??? question "**Q3 (Exécuter le lab) :** Quel est le TTFT moyen pour les **succès** de cache sur tous les fournisseurs ?"

    Exécutez l'analyse de l'étape 3 sur [📥 \cache_benchmark.csv\](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-071/cache_benchmark.csv) et vérifiez les résultats.

    ??? success "✅ Révéler la réponse"
        **217 ms**

        Les 9 requêtes avec succès de cache ont des TTFT de 180, 175, 190, 220, 210, 230, 250, 240 et 260 ms. La moyenne est (180+175+190+220+210+230+250+240+260) ÷ 9 = **217 ms** (arrondi).

??? question "**Q4 (Exécuter le lab) :** Quel est le TTFT moyen pour les **échecs** de cache sur tous les fournisseurs ?"

    Exécutez l'analyse de l'étape 3 pour le découvrir.

    ??? success "✅ Révéler la réponse"
        **2583 ms**

        Les 6 requêtes avec échec de cache ont des TTFT de 2800, 2750, 3200, 3100, 1800 et 1850 ms. La moyenne est (2800+2750+3200+3100+1800+1850) ÷ 6 = **2583 ms** (arrondi).

??? question "**Q5 (Exécuter le lab) :** Quelles sont les économies totales de coût (coûts des échecs moins coûts des succès) sur les 15 requêtes ?"

    Exécutez l'analyse de l'étape 4 pour le calculer.

    ??? success "✅ Révéler la réponse"
        **1,44 \$**

        Coûts totaux d'entrée des échecs = 0,45 \$ + 0,45 \$ + 0,20 \$ + 0,20 \$ + 0,25 \$ + 0,25 \$ = **1,80 \$**. Coûts totaux en cache des succès = 0,045 \$×3 + 0,05 \$×3 + 0,025 \$×3 = 0,135 \$ + 0,15 \$ + 0,075 \$ = **0,36 \$**. Économies = 1,80 \$ − 0,36 \$ = **1,44 \$**.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|------------------------|
| Mise en cache du contexte | Stocke les tokens d'entrée traités pour éviter de les renvoyer lors des requêtes suivantes |
| Impact sur le TTFT | Les succès de cache réduisent le TTFT d'environ 12x (de ~2,6 s à ~217 ms) |
| Économies de coûts | 80 % de réduction des coûts sur les requêtes en cache chez tous les fournisseurs |
| Comparaison des fournisseurs | Anthropic (10 %), Google (25 %), OpenAI (50 %) de remise sur les tokens en cache |
| Analyse du ROI | Comment projeter les économies en fonction du volume de requêtes et des taux de succès |
| Méthodologie de benchmark | Structurer des expériences de cache avec suivi des succès/échecs |

---

## Prochaines étapes

- **[Lab 038](lab-038-cost-optimization.md)** — Optimisation des coûts IA (stratégies de coûts plus larges au-delà de la mise en cache)
- **[Lab 019](lab-019-streaming-responses.md)** — Réponses en streaming (optimisation complémentaire de la latence)
- **[Lab 033](lab-033-agent-observability.md)** — Observabilité des agents (surveiller les taux de succès du cache en production)
- **[Lab 072](lab-072-structured-outputs.md)** — Sorties structurées (JSON garanti pour des pipelines d'agents efficaces en coûts)