---
tags: [foundry-local, local-inference, free, ollama-alternative, python]
---
# Lab 078 : Foundry Local — Exécuter des modèles IA hors ligne

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~45 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Fonctionne entièrement sur du matériel local</span>
</div>

## Ce que vous apprendrez

- Ce qu'est **Foundry Local** et comment il permet l'inférence de modèles IA hors ligne
- Comment installer et exécuter des modèles avec `winget` et le CLI `foundry`
- Comment l'**API compatible OpenAI** fait de Foundry Local un remplacement direct
- Analyser un **catalogue de modèles** de 8 modèles — en comparant tailles, exigences matérielles et qualité
- Identifier le **plus petit modèle** et quels modèles supportent l'inférence **CPU uniquement**

## Introduction

**Foundry Local** est le runtime d'inférence locale de Microsoft qui vous permet d'exécuter des modèles IA entièrement sur votre propre matériel — sans cloud, sans clés API, sans internet requis. C'est une alternative gratuite à Ollama, optimisée pour Windows avec l'accélération GPU DirectML.

### Installation

```bash
winget install Microsoft.FoundryLocal
```

### Exécuter un modèle

```bash
foundry model run phi-4-mini
```

Cela télécharge le modèle (si nécessaire) et démarre un serveur local avec une **API compatible OpenAI** à `http://localhost:5273` :

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:5273/v1", api_key="not-needed")

response = client.chat.completions.create(
    model="phi-4-mini",
    messages=[{"role": "user", "content": "Explain quantum computing in 2 sentences."}]
)
print(response.choices[0].message.content)
```

### Le scénario

Vous êtes un **ingénieur DevOps** évaluant Foundry Local pour des déploiements en environnement isolé (hors ligne). Vous disposez d'un catalogue de **8 modèles** (`foundry_models.csv`) avec la taille, les exigences matérielles et les benchmarks de qualité. Votre mission : analyser le catalogue, trouver le meilleur modèle pour différents profils matériels et construire une recommandation de déploiement.

!!! info "Données simulées"
    Ce lab utilise un fichier CSV de catalogue de modèles simulé. Les noms et tailles des modèles sont représentatifs des modèles disponibles dans le catalogue de Foundry Local début 2026.

## Prérequis

| Exigence | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| Bibliothèque `pandas` | Manipulation des données |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-078/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `broken_foundry_local.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-078/broken_foundry_local.py) |
| `foundry_models.csv` | Catalogue de 8 modèles avec tailles, matériel et scores de qualité | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-078/foundry_models.csv) |

---

## Étape 1 : Comprendre le catalogue de modèles

Chaque modèle du catalogue possède ces attributs :

| Colonne | Description |
|--------|-----------|
| **model_name** | Identifiant du modèle (ex. : `phi-4-mini`, `qwen2.5-0.5b`) |
| **size_gb** | Taille de téléchargement en gigaoctets |
| **parameters** | Nombre de paramètres du modèle (ex. : `3.8B`, `0.5B`) |
| **hardware** | Matériel requis : `cpu_only`, `gpu_recommended` ou `gpu_required` |
| **quality_score** | Score de qualité benchmark (0.0–1.0) |
| **use_case** | Cas d'usage principal : `chat`, `coding`, `embedding` ou `general` |
| **quantization** | Niveau de quantification : `q4`, `q8` ou `fp16` |

---

## Étape 2 : Charger et explorer le catalogue

```python
import pandas as pd

df = pd.read_csv("lab-078/foundry_models.csv")

print(f"Total models: {len(df)}")
print(f"Hardware requirements: {df['hardware'].value_counts().to_dict()}")
print(f"Use cases: {df['use_case'].value_counts().to_dict()}")
print(f"\nFull catalog:")
print(df[["model_name", "size_gb", "parameters", "hardware", "quality_score"]].to_string(index=False))
```

**Sortie attendue :**

```
Total models: 8
Hardware requirements: {'gpu_recommended': 4, 'cpu_only': 2, 'gpu_required': 2}
Use cases: {'chat': 3, 'coding': 2, 'general': 2, 'embedding': 1}
```

---

## Étape 3 : Trouver le plus petit modèle

```python
smallest = df.loc[df["size_gb"].idxmin()]
largest = df.loc[df["size_gb"].idxmax()]

print(f"Smallest model: {smallest['model_name']} ({smallest['size_gb']} GB)")
print(f"  Parameters: {smallest['parameters']}")
print(f"  Hardware: {smallest['hardware']}")
print(f"  Quality: {smallest['quality_score']}")

print(f"\nLargest model: {largest['model_name']} ({largest['size_gb']} GB)")
print(f"  Parameters: {largest['parameters']}")
print(f"  Hardware: {largest['hardware']}")
print(f"  Quality: {largest['quality_score']}")

print(f"\nSize range: {smallest['size_gb']} GB – {largest['size_gb']} GB")
```

**Sortie attendue :**

```
Smallest model: qwen2.5-0.5b (0.4 GB)
  Parameters: 0.5B
  Hardware: cpu_only
  Quality: 0.52
```

!!! tip "Déploiement en périphérie"
    **qwen2.5-0.5b** avec seulement **0.4 Go** est idéal pour les appareils en périphérie, les passerelles IoT ou les machines avec un stockage minimal. Malgré sa petite taille, il gère raisonnablement bien les tâches de base de conversation et de résumé.

---

## Étape 4 : Identifier les modèles CPU uniquement

Pour les machines isolées sans GPU :

```python
cpu_models = df[df["hardware"] == "cpu_only"]
print(f"CPU-only models: {len(cpu_models)}\n")
for _, row in cpu_models.iterrows():
    print(f"  {row['model_name']:>20s}  size={row['size_gb']}GB  quality={row['quality_score']}  use_case={row['use_case']}")
```

```python
# Compare CPU-only vs GPU models
gpu_models = df[df["hardware"] != "cpu_only"]
print(f"\nCPU-only avg quality: {cpu_models['quality_score'].mean():.2f}")
print(f"GPU models avg quality: {gpu_models['quality_score'].mean():.2f}")
print(f"Quality gap: {(gpu_models['quality_score'].mean() - cpu_models['quality_score'].mean()) * 100:.1f}pp")
```

!!! warning "Compromis qualité"
    Les modèles CPU uniquement sont plus petits et fonctionnent partout, mais leurs scores de qualité sont généralement inférieurs à ceux des modèles GPU. Pour les cas d'usage en production nécessitant une haute précision, préférez les modèles recommandés GPU avec au moins 4 Go de VRAM.

---

## Étape 5 : Analyser par cas d'usage

```python
print("Models by use case:\n")
for use_case, group in df.groupby("use_case"):
    print(f"  {use_case.upper()} ({len(group)} models):")
    for _, row in group.iterrows():
        print(f"    {row['model_name']:>20s}  {row['size_gb']}GB  quality={row['quality_score']}")
    print()

# Best model per use case
print("Best model per use case (by quality):")
for use_case, group in df.groupby("use_case"):
    best = group.loc[group["quality_score"].idxmax()]
    print(f"  {use_case:>10s}: {best['model_name']} (quality={best['quality_score']}, size={best['size_gb']}GB)")
```

---

## Étape 6 : Construire la recommandation de déploiement

```python
report = f"""# 📋 Foundry Local Deployment Recommendation

## Catalog Summary
| Metric | Value |
|--------|-------|
| Total Models | {len(df)} |
| CPU-Only | {len(cpu_models)} |
| GPU Recommended | {len(df[df['hardware'] == 'gpu_recommended'])} |
| GPU Required | {len(df[df['hardware'] == 'gpu_required'])} |
| Smallest | {smallest['model_name']} ({smallest['size_gb']} GB) |
| Largest | {largest['model_name']} ({largest['size_gb']} GB) |

## Hardware Profiles

### Profile A: Edge Device (CPU only, 2 GB storage)
"""

for _, row in cpu_models.iterrows():
    report += f"- **{row['model_name']}** — {row['size_gb']} GB, quality {row['quality_score']}\n"

report += f"""
### Profile B: Developer Laptop (GPU, 16 GB storage)
"""

for _, row in df[df["hardware"] == "gpu_recommended"].iterrows():
    report += f"- **{row['model_name']}** — {row['size_gb']} GB, quality {row['quality_score']}\n"

report += f"""
### Profile C: Workstation (High-end GPU, 64 GB storage)
"""

for _, row in df[df["hardware"] == "gpu_required"].iterrows():
    report += f"- **{row['model_name']}** — {row['size_gb']} GB, quality {row['quality_score']}\n"

print(report)

with open("lab-078/deployment_recommendation.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-078/deployment_recommendation.md")
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-078/broken_foundry_local.py` contient **3 bugs** qui produisent une analyse de modèles incorrecte. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-078/broken_foundry_local.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Nom du plus petit modèle | Devrait trouver le min de `size_gb`, pas le max |
| Test 2 | Nombre de modèles CPU uniquement | Devrait filtrer `hardware == "cpu_only"`, pas `"gpu_required"` |
| Test 3 | Nombre total de modèles | Devrait utiliser `len(df)`, pas une valeur codée en dur |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `All passed!`, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Qu'est-ce qui différencie Foundry Local des services IA cloud ?"

    - A) Il ne prend en charge que les modèles Microsoft
    - B) Il exécute les modèles IA entièrement sur du matériel local sans internet requis
    - C) Il nécessite un abonnement Azure
    - D) Il ne fonctionne que sous Linux

    ??? success "✅ Révéler la réponse"
        **Correct : B) Il exécute les modèles IA entièrement sur du matériel local sans internet requis**

        Foundry Local est un runtime d'inférence locale — les modèles sont téléchargés une fois et fonctionnent entièrement hors ligne. Il utilise une API compatible OpenAI, en faisant un remplacement direct des endpoints cloud. Pas de clés API, pas d'internet, pas de coûts par token.

??? question "**Q2 (Choix multiple) :** Pourquoi Foundry Local utilise-t-il une API compatible OpenAI ?"

    - A) Il est développé par OpenAI
    - B) Il permet un remplacement direct — le code existant qui appelle les API OpenAI fonctionne sans modification
    - C) OpenAI exige que tous les moteurs d'inférence utilisent leur format d'API
    - D) Il n'exécute que des modèles OpenAI

    ??? success "✅ Révéler la réponse"
        **Correct : B) Il permet un remplacement direct — le code existant qui appelle les API OpenAI fonctionne sans modification**

        En exposant le même format d'endpoint `/v1/chat/completions`, Foundry Local permet aux développeurs de passer du cloud à l'inférence locale en changeant uniquement la `base_url`. Tous les SDK, outils et frameworks existants qui parlent le format d'API OpenAI fonctionnent immédiatement.

??? question "**Q3 (Exécutez le lab) :** Quel est le plus petit modèle du catalogue et quelle est sa taille ?"

    Exécutez l'analyse de l'étape 3 sur [📥 `foundry_models.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-078/foundry_models.csv) pour trouver le plus petit modèle.

    ??? success "✅ Révéler la réponse"
        **qwen2.5-0.5b à 0.4 Go**

        Le plus petit modèle du catalogue est **qwen2.5-0.5b** avec seulement **0.4 Go** de taille de téléchargement et 0.5B de paramètres. Il fonctionne en CPU uniquement et atteint un score de qualité de 0.52 — adapté aux conversations de base et aux déploiements en périphérie.

??? question "**Q4 (Exécutez le lab) :** Combien de modèles supportent l'inférence CPU uniquement ?"

    Exécutez l'analyse de l'étape 4 pour filtrer les modèles avec `hardware == "cpu_only"`.

    ??? success "✅ Révéler la réponse"
        **2 modèles**

        Seuls **2 modèles** supportent l'inférence CPU uniquement. Ce sont les plus petits modèles du catalogue, optimisés avec une quantification agressive (q4) pour fonctionner sans accélération GPU. Ils sont idéaux pour les appareils en périphérie et les environnements isolés.

??? question "**Q5 (Exécutez le lab) :** Combien de modèles au total sont disponibles dans le catalogue Foundry Local ?"

    Chargez le CSV et vérifiez le nombre total de lignes.

    ??? success "✅ Révéler la réponse"
        **8 modèles**

        Le catalogue Foundry Local comprend **8 modèles** répartis en 4 cas d'usage : chat (3), coding (2), general (2) et embedding (1). Les exigences matérielles vont de CPU uniquement à GPU requis.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Foundry Local | Runtime d'inférence locale de Microsoft — gratuit, hors ligne, sans clés API |
| Installation | `winget install Microsoft.FoundryLocal` + `foundry model run` |
| Compatibilité OpenAI | Remplacement direct via `http://localhost:5273/v1` |
| Catalogue de modèles | 8 modèles de 0.4 Go à plusieurs Go, CPU à GPU requis |
| Plus petit modèle | qwen2.5-0.5b à 0.4 Go — fonctionne en CPU, idéal pour la périphérie |
| Profils matériels | CPU uniquement (2 modèles), GPU recommandé (4), GPU requis (2) |

---

## Prochaines étapes

- **[Lab 074](lab-074-foundry-agent-service.md)** — Foundry Agent Service (déployer des agents utilisant des modèles Foundry)
- **[Lab 071](lab-071-context-caching.md)** — Mise en cache du contexte (optimiser l'inférence locale avec la mise en cache des prompts)
- **[Lab 038](lab-038-cost-optimization.md)** — Optimisation des coûts IA (comparer les coûts d'inférence locale vs. cloud)
- **[Lab 076](lab-076-microsoft-agent-framework.md)** — Microsoft Agent Framework (utiliser Foundry Local comme backend d'inférence pour les agents MAF)
