---
tags: [voice, realtime-api, webrtc, azure-openai, multimodal, python]
---
# Lab 059 : Agents vocaux avec GPT Realtime API

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~75 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise un jeu de données de sessions (Azure OpenAI optionnel)</span>
</div>

## Ce que vous apprendrez

- Comment le **GPT-4o Realtime API** permet des conversations vocales en duplex intégral avec une latence d'environ 100 ms
- Connecter des clients via **WebRTC** pour un streaming audio natif au navigateur à faible latence
- Gérer les **interruptions (barge-in)** — permettre aux utilisateurs d'intervenir pendant que l'agent parle encore
- Intégrer le **RAG avec l'audio en temps réel** pour que l'agent récupère des données produit en cours de conversation
- Analyser les **métriques des sessions vocales** : percentiles de latence, sentiment et distribution linguistique
- Évaluer le **support multilingue** (en, es, fr) dans un déploiement unique d'agent vocal

---

## Introduction

Les agents vocaux passent du mode traditionnel de prise de parole alternée — où l'utilisateur parle, attend, puis l'agent répond — à la **conversation en temps réel**. Le GPT-4o Realtime API traite l'entrée vocale et génère une sortie vocale simultanément, permettant un dialogue naturel en va-et-vient avec une latence inférieure à 100 ms.

**OutdoorGear** souhaite un assistant vocal pour les demandes de renseignements sur les produits. Les clients appellent, posent des questions sur l'équipement, et l'agent répond avec les détails du produit — le tout en temps réel. Le système doit gérer les interruptions avec élégance (un client peut dire « attendez, en fait… » en pleine réponse), prendre en charge plusieurs langues et récupérer les informations produit depuis un pipeline RAG à la volée.

### Vue d'ensemble de l'architecture

```
┌──────────┐   WebRTC    ┌────────────────────┐   REST/WS   ┌───────────┐
│  Browser  │◄──────────►│  Realtime API      │◄───────────►│  RAG      │
│  (mic +   │  audio     │  (GPT-4o-realtime) │  tool calls │  (product │
│  speaker) │  stream    │  • VAD             │             │   search) │
└──────────┘             │  • Barge-in        │             └───────────┘
                         │  • Turn detection  │
                         └────────────────────┘
```

Concepts clés :

| Concept | Description |
|---------|-------------|
| **Realtime API** | Point de terminaison voix-vers-voix en duplex intégral — pas de pipeline STT/TTS séparé |
| **WebRTC** | Protocole natif au navigateur pour le streaming audio/vidéo à faible latence |
| **VAD (Voice Activity Detection)** | Détecte quand l'utilisateur commence/arrête de parler |
| **Barge-in** | L'utilisateur peut interrompre l'agent en pleine réponse ; l'agent s'arrête et écoute |
| **Détection de tour côté serveur** | L'API décide quand le tour de parole de l'utilisateur est terminé |

---

## Prérequis

```bash
pip install pandas
```

Ce lab analyse des données de session pré-enregistrées — aucune clé API ni abonnement Azure requis. Pour construire un agent vocal en direct, vous auriez besoin d'une ressource Azure OpenAI avec le modèle `gpt-4o-realtime-preview` déployé.

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-059/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|------|-------------|----------|
| `broken_voice.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-059/broken_voice.py) |
| `voice_sessions.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-059/voice_sessions.csv) |

---

## Partie 1 : Comprendre l'architecture du Realtime API

### Étape 1 : En quoi le Realtime API diffère de Chat Completions

L'API Chat Completions standard suit un modèle requête-réponse : envoyer du texte, recevoir du texte. Le Realtime API est fondamentalement différent :

| Fonctionnalité | Chat Completions | Realtime API |
|---------|-----------------|--------------|
| Entrée | Texte (JSON) | Flux audio (PCM/WebRTC) |
| Sortie | Texte (JSON) | Flux audio + transcription textuelle |
| Latence | 500–2000 ms | ~100 ms (P50) |
| Duplex | Semi-duplex (requête → réponse) | Duplex intégral (simultané) |
| Interruption | Non supportée | Barge-in supporté |
| Protocole | HTTP REST | WebSocket / WebRTC |

La latence cible d'environ 100 ms rend les conversations vocales naturelles — comparable aux appels téléphoniques entre humains.

---

## Partie 2 : Charger et explorer les données des sessions vocales

### Étape 2 : Charger [📥 `voice_sessions.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-059/voice_sessions.csv)

OutdoorGear a enregistré **15 sessions vocales** lors d'un test pilote de leur intégration du Realtime API. Chaque session capture une interaction client :

```python
# voice_analysis.py
import pandas as pd

sessions = pd.read_csv("lab-059/voice_sessions.csv")
print(f"Total sessions: {len(sessions)}")
print(f"Columns: {list(sessions.columns)}")
print(sessions.head())
```

**Sortie attendue :**

```
Total sessions: 15
Columns: ['session_id', 'scenario', 'duration_sec', 'latency_p50_ms',
           'latency_p95_ms', 'interruptions', 'turns', 'sentiment',
           'model', 'rag_used', 'language']
```

Le jeu de données inclut :

| Colonne | Description |
|--------|-------------|
| `session_id` | Identifiant unique de session (S01–S15) |
| `scenario` | Type d'interaction : product_inquiry, order_status, complaint, return_request, faq |
| `duration_sec` | Durée totale de la session en secondes |
| `latency_p50_ms` | Latence médiane de réponse en millisecondes |
| `latency_p95_ms` | 95e percentile de latence de réponse |
| `interruptions` | Nombre de fois où l'utilisateur a interrompu l'agent |
| `turns` | Nombre total de tours de conversation |
| `sentiment` | Sentiment global de la session : positive, neutral, negative |
| `model` | Modèle utilisé (`gpt-4o-realtime`) |
| `rag_used` | Si le RAG a été invoqué pendant la session |
| `language` | Langue de la session : en, es, fr |

---

## Partie 3 : Analyse de la latence

### Étape 3 : Mesurer la latence de réponse à travers les sessions

La latence est la métrique la plus critique pour les agents vocaux — tout ce qui dépasse 200 ms donne une impression de lenteur.

```python
# Latency statistics
avg_p50 = sessions["latency_p50_ms"].mean()
avg_p95 = sessions["latency_p95_ms"].mean()

print(f"Average P50 latency: {avg_p50:.1f} ms")
print(f"Average P95 latency: {avg_p95:.1f} ms")
print(f"Min P50: {sessions['latency_p50_ms'].min()} ms")
print(f"Max P50: {sessions['latency_p50_ms'].max()} ms")

# Sessions exceeding 200ms at P95
slow = sessions[sessions["latency_p95_ms"] > 200]
print(f"\nSessions with P95 > 200ms: {len(slow)}")
print(slow[["session_id", "scenario", "latency_p95_ms"]])
```

**Sortie attendue :**

```
Average P50 latency: 89.3 ms
Average P95 latency: 187.5 ms
Min P50: 75 ms
Max P50: 110 ms

Sessions with P95 > 200ms: 4
  session_id       scenario  latency_p95_ms
       S06  return_request             210
       S09       complaint             240
       S12  return_request             215
       S14       complaint             255
```

!!! info "Observation sur la latence"
    Le P50 moyen de 89,3 ms est bien en dessous de la cible de 100 ms. Cependant, les sessions de réclamation et de retour ont systématiquement une latence plus élevée — probablement parce qu'elles déclenchent des recherches RAG plus longues et un raisonnement plus complexe.

---

## Partie 4 : Analyse du sentiment

### Étape 4 : Analyser la distribution du sentiment des sessions

```python
# Sentiment breakdown
sentiment_counts = sessions["sentiment"].value_counts()
print("Sentiment Distribution:")
print(sentiment_counts)
print(f"\nPositive: {sentiment_counts.get('positive', 0)} sessions")
print(f"Neutral:  {sentiment_counts.get('neutral', 0)} sessions")
print(f"Negative: {sentiment_counts.get('negative', 0)} sessions")

# Which sessions are negative?
negative = sessions[sessions["sentiment"] == "negative"]
print(f"\nNegative sessions:")
print(negative[["session_id", "scenario", "duration_sec", "interruptions"]])
```

**Sortie attendue :**

```
Sentiment Distribution:
positive    8
negative    4
neutral     3

Positive: 8 sessions (S01, S04, S05, S07, S10, S11, S13, S15)
Neutral:  3 sessions (S02, S08, S12)
Negative: 4 sessions (S03, S06, S09, S14)

Negative sessions:
  session_id       scenario  duration_sec  interruptions
       S03       complaint           120              3
       S06  return_request            65              1
       S09       complaint            90              4
       S14       complaint           105              5
```

!!! warning "Tendance observée"
    Les 4 sessions négatives sont toutes des réclamations ou des demandes de retour. Trois des quatre ont 3+ interruptions — les clients frustrés interrompent plus fréquemment.

---

## Partie 5 : Modèles d'utilisation du RAG

### Étape 5 : Analyser quelles sessions utilisent le RAG

```python
# RAG usage
rag_used = sessions[sessions["rag_used"] == True]
rag_not_used = sessions[sessions["rag_used"] == False]

print(f"RAG used: {len(rag_used)}/{len(sessions)} sessions ({len(rag_used)/len(sessions)*100:.0f}%)")
print(f"RAG not used: {len(rag_not_used)} sessions")
print(f"\nSessions without RAG:")
print(rag_not_used[["session_id", "scenario", "sentiment"]])

# Compare latency: RAG vs no-RAG
print(f"\nAvg P50 with RAG:    {rag_used['latency_p50_ms'].mean():.1f} ms")
print(f"Avg P50 without RAG: {rag_not_used['latency_p50_ms'].mean():.1f} ms")
```

**Sortie attendue :**

```
RAG used: 12/15 sessions (80%)
RAG not used: 3 sessions

Sessions without RAG:
  session_id scenario sentiment
       S05      faq  positive
       S10      faq  positive
       S15      faq  positive

Avg P50 with RAG:    92.6 ms
Avg P50 without RAG: 76.3 ms
```

!!! info "Observation sur le RAG"
    Les 3 sessions sans RAG sont toutes des scénarios FAQ — des questions simples qui ne nécessitent pas de recherche dans la base de données produit. Les sessions FAQ sont aussi les plus courtes (15–20 secondes) et ont la latence la plus faible.

---

## Partie 6 : Modèles d'interruption

### Étape 6 : Analyser le comportement de barge-in

Le barge-in désigne le moment où un utilisateur interrompt l'agent en pleine réponse. C'est une capacité clé du Realtime API — sans elle, les agents vocaux semblent robotiques.

```python
# Interruption analysis
print("Interruptions per session:")
print(sessions[["session_id", "scenario", "interruptions", "sentiment"]].to_string(index=False))

# Correlation between interruptions and sentiment
avg_interruptions = sessions.groupby("sentiment")["interruptions"].mean()
print(f"\nAvg interruptions by sentiment:")
print(avg_interruptions)

# Sessions with most interruptions
high_interrupt = sessions[sessions["interruptions"] >= 3]
print(f"\nHigh-interruption sessions (≥3):")
print(high_interrupt[["session_id", "scenario", "interruptions", "sentiment"]])
```

**Sortie attendue :**

```
Avg interruptions by sentiment:
negative    3.25
neutral     0.67
positive    0.63

High-interruption sessions (≥3):
  session_id   scenario  interruptions sentiment
       S03  complaint              3  negative
       S09  complaint              4  negative
       S14  complaint              5  negative
```

!!! info "Observation sur le barge-in"
    Les sessions négatives ont en moyenne 3,25 interruptions contre 0,63 pour les sessions positives. Un nombre élevé d'interruptions est un signal fort de frustration du client — un agent pourrait détecter cela en temps réel et escalader vers un agent humain.

---

## Partie 7 : Support multilingue

### Étape 7 : Analyser la distribution linguistique

```python
# Language breakdown
lang_counts = sessions["language"].value_counts()
print("Language Distribution:")
print(lang_counts)

# Performance by language
for lang in sessions["language"].unique():
    lang_sessions = sessions[sessions["language"] == lang]
    print(f"\n{lang.upper()}: {len(lang_sessions)} sessions, "
          f"avg P50={lang_sessions['latency_p50_ms'].mean():.1f}ms, "
          f"avg sentiment: {lang_sessions['sentiment'].mode().iloc[0]}")
```

**Sortie attendue :**

```
Language Distribution:
en    13
es     1
fr     1

EN: 13 sessions, avg P50=90.2ms, avg sentiment: positive
ES: 1 sessions, avg P50=82.0ms, avg sentiment: positive
FR: 1 sessions, avg P50=87.0ms, avg sentiment: positive
```

Le Realtime API prend en charge plusieurs langues nativement — le même modèle gère l'anglais, l'espagnol et le français sans déploiements séparés.

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-059/broken_voice.py` contient **3 bugs** dans les fonctions d'analyse des sessions vocales. Exécutez les auto-tests :

```bash
python lab-059/broken_voice.py
```

Vous devriez voir **3 tests échoués** :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Calcul de la latence P95 moyenne | Quelle colonne de latence devriez-vous utiliser ? |
| Test 2 | Nombre de sessions à sentiment négatif | Filtrez-vous la bonne valeur de sentiment ? |
| Test 3 | Taux d'utilisation du RAG en pourcentage | Quel devrait être le dénominateur ? |

Corrigez les 3 bugs et relancez jusqu'à voir `🎉 All 3 tests passed`.

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quelle est la latence de réponse cible du GPT-4o Realtime API ?"

    - A) ~500 ms — suffisamment rapide pour la plupart des applications vocales
    - B) ~100 ms — comparable à la latence de conversation entre humains
    - C) ~10 ms — quasi instantané pour le jeu en temps réel
    - D) ~1000 ms — acceptable pour le traitement vocal par lots

    ??? success "✅ Révéler la réponse"
        **Correct : B) ~100 ms**

        Le Realtime API cible une latence P50 d'environ 100 ms, comparable aux pauses naturelles dans la conversation humaine. À cette vitesse, les interactions vocales semblent fluides et naturelles. Les données de session confirment cela — le P50 moyen sur 15 sessions est de 89,3 ms.

??? question "**Q2 (Choix multiple) :** Que signifie « barge-in » dans le contexte des agents vocaux ?"

    - A) L'agent interrompt l'utilisateur pour fournir des informations urgentes
    - B) L'utilisateur peut interrompre l'agent en pleine réponse et l'agent s'arrête pour écouter
    - C) Plusieurs utilisateurs peuvent rejoindre la même session vocale simultanément
    - D) L'agent change de langue en cours de conversation

    ??? success "✅ Révéler la réponse"
        **Correct : B) L'utilisateur peut interrompre l'agent en pleine réponse et l'agent s'arrête pour écouter**

        Le barge-in est une fonctionnalité essentielle de la conversation vocale naturelle. Quand un utilisateur dit « attendez, en fait… » pendant que l'agent parle encore, l'agent arrête immédiatement sa réponse en cours et traite la nouvelle entrée. Sans le barge-in, les utilisateurs doivent attendre que l'agent finisse — créant une expérience frustrante et robotique.

??? question "**Q3 (Exécuter le lab) :** Quelle est la latence P95 moyenne sur l'ensemble des 15 sessions vocales ?"

    Calculez `sessions["latency_p95_ms"].mean()`.

    ??? success "✅ Révéler la réponse"
        **187,5 ms**

        Les valeurs P95 vont de 150 ms (S10, une session FAQ) à 255 ms (S14, une réclamation). La moyenne sur les 15 sessions est (170+185+195+180+155+210+165+175+240+150+178+215+188+255+152) / 15 = **187,5 ms**. Quatre sessions dépassent le seuil de 200 ms — toutes sont des réclamations ou des demandes de retour.

??? question "**Q4 (Exécuter le lab) :** Combien de sessions ont un sentiment négatif ?"

    Filtrez `sessions[sessions["sentiment"] == "negative"]` et comptez.

    ??? success "✅ Révéler la réponse"
        **4 sessions**

        Les sessions S03, S06, S09 et S14 ont un sentiment négatif. Les quatre sont soit des réclamations (S03, S09, S14) soit des demandes de retour (S06). Ces sessions ont aussi la latence et le nombre d'interruptions les plus élevés, suggérant une corrélation entre la frustration du client et les performances du système dans les scénarios complexes.

??? question "**Q5 (Exécuter le lab) :** Quel pourcentage de sessions utilise le RAG ?"

    Calculez `(sessions avec rag_used == True) / nombre total de sessions * 100`.

    ??? success "✅ Révéler la réponse"
        **80% (12 sur 15)**

        12 des 15 sessions utilisent le RAG. Les 3 sessions sans RAG (S05, S10, S15) sont toutes des scénarios FAQ — des questions simples auxquelles le modèle répond à partir de ses données d'entraînement sans avoir besoin de recherches dans la base de données produit. Les sessions FAQ ont aussi la latence la plus faible, confirmant que le RAG ajoute un surcoût de latence mesurable (mais faible).

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Realtime API | Voix-vers-voix en duplex intégral avec une latence d'environ 100 ms |
| WebRTC | Protocole natif au navigateur pour le streaming audio à faible latence |
| Barge-in | Les utilisateurs peuvent interrompre en pleine réponse pour un flux de conversation naturel |
| RAG + Voix | 80% des sessions utilisent le RAG ; les sessions FAQ le contournent pour une latence plus faible |
| Sentiment | Les sessions négatives corrèlent avec les réclamations, la latence élevée et les interruptions |
| Multilingue | Le même modèle gère en, es, fr sans déploiements séparés |

---

## Prochaines étapes

- **[Lab 043](lab-043-multimodal-agents.md)** — Agents multimodaux avec GPT-4o Vision (modalité complémentaire)
- **[Lab 060](lab-060-reasoning-models.md)** — Modèles de raisonnement : Chain-of-Thought avec o3 et DeepSeek R1
- **[Lab 019](lab-019-streaming-responses.md)** — Réponses en streaming (concepts fondamentaux du streaming)
