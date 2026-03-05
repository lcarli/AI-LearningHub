---
tags: [on-device, phi-silica, windows-ai, npu, edge-ai, csharp]
---
# Lab 062 : Agents sur appareil avec Phi Silica — Windows AI APIs

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~90 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des données de benchmark simulées (aucun matériel NPU requis)</span>
</div>

## Ce que vous apprendrez

- Comment les **Windows AI APIs** permettent l'inférence sur appareil en utilisant le Neural Processing Unit (NPU)
- Ce qu'est **Phi Silica** — un modèle optimisé pour le matériel NPU Windows
- Comparer la latence **NPU vs cloud** pour les compétences d'agent (résumer, classifier, réécrire, text_to_table)
- Gérer l'**indisponibilité du NPU** de manière élégante avec des stratégies de repli vers le cloud
- Mesurer les **taux de correspondance de qualité** entre l'inférence sur appareil et cloud
- Construire des agents qui fonctionnent en **mode hors-ligne prioritaire** avec une dégradation intelligente

---

## Introduction

L'IA basée sur le cloud est puissante, mais elle nécessite une connectivité internet, introduit de la latence et envoie les données hors de l'appareil. Les **Windows AI APIs** avec **Phi Silica** apportent l'inférence directement au NPU (Neural Processing Unit) — un accélérateur IA dédié intégré aux appareils Windows modernes.

L'inférence sur appareil signifie : zéro latence réseau, confidentialité totale des données, capacité hors-ligne et aucun coût par token. Le compromis est que toutes les tâches ne peuvent pas s'exécuter sur le NPU, et la qualité peut différer de celle des modèles cloud. Ce lab mesure exactement où l'inférence sur appareil excelle et où vous avez besoin d'un repli vers le cloud.

### Le benchmark

Vous analyserez **15 tâches** réparties en 4 catégories, comparant le NPU (Phi Silica) vs l'inférence cloud :

| Catégorie | Nombre | Exemple |
|-----------|--------|---------|
| **Résumer** | 4 | Transcription de réunion, article, fil d'e-mails, document de politique |
| **Classifier** | 4 | Sentiment, intention, priorité, détection de langue |
| **Réécrire** | 4 | Ajustement du ton, simplification, formalisation, traduction |
| **Text-to-table** | 3 | Extraire des données structurées à partir de texte non structuré |

---

## Prérequis

```bash
pip install pandas
```

Ce lab analyse des résultats de benchmark pré-calculés — aucun matériel NPU, SDK Windows AI ou chaîne d'outils C# requis. Pour exécuter une inférence en direct sur appareil, vous auriez besoin d'un Copilot+ PC avec NPU et les Windows AI APIs.

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-062/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|---------|-------------|-------------|
| `broken_ondevice.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-062/broken_ondevice.py) |
| `ondevice_tasks.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-062/ondevice_tasks.csv) |

---

## Partie 1 : Comprendre l'inférence sur appareil

### Étape 1 : Architecture du NPU

Le Neural Processing Unit (NPU) est un accélérateur IA dédié conçu pour des opérations matricielles efficaces :

```
Cloud Inference:
  App → [Network] → [Cloud GPU] → [Network] → Response
  Latency: ~800-1200ms

NPU Inference (Phi Silica):
  App → [Local NPU] → Response
  Latency: ~50-120ms
```

Concepts clés :

| Concept | Description |
|---------|-------------|
| **NPU** | Neural Processing Unit — matériel IA dédié dans les processeurs modernes |
| **Phi Silica** | Modèle de Microsoft optimisé pour l'exécution sur le NPU Windows |
| **Windows AI APIs** | API au niveau système pour l'inférence IA sur appareil |
| **Vérification de disponibilité** | API pour vérifier la disponibilité du NPU avant de tenter l'inférence |
| **Repli élégant** | Stratégie de repli vers le cloud lorsque le NPU est indisponible |

!!! info "Phi Silica vs Phi-4 Mini"
    Phi Silica est spécifiquement optimisé pour le matériel NPU Windows — ce n'est pas simplement un modèle plus petit, mais un modèle conçu pour l'architecture du NPU. Phi-4 Mini (Lab 061) s'exécute via ONNX Runtime sur CPU/GPU. Les deux offrent une inférence sur appareil mais ciblent des chemins matériels différents.

---

## Partie 2 : Charger les données du benchmark

### Étape 2 : Charger [📥 `ondevice_tasks.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-062/ondevice_tasks.csv)

Le jeu de données de benchmark contient les résultats de l'exécution de 15 tâches via l'inférence NPU et cloud :

```python
# ondevice_analysis.py
import pandas as pd

bench = pd.read_csv("lab-062/ondevice_tasks.csv")

print(f"Tasks: {len(bench)}")
print(f"Categories: {bench['category'].unique().tolist()}")
print(bench[["task_id", "category", "description", "npu_available"]].to_string(index=False))
```

**Sortie attendue :**

```
Tasks: 15
Categories: ['summarize', 'classify', 'rewrite', 'text_to_table']

task_id      category                      description  npu_available
    T01     summarize          Meeting transcript summary           True
    T02     summarize                    Article digest           True
    T03     summarize              Email thread summary           True
    T04     summarize                Policy doc summary           True
    T05      classify              Sentiment analysis           True
    T06      classify                Intent detection           True
    T07      classify              Priority assignment           True
    T08      classify             Language detection           True
    T09       rewrite                 Tone adjustment           True
    T10       rewrite                  Simplification           True
    T11       rewrite                  Formalization           True
    T12       rewrite    Translation (EN→ES snippet)          False
    T13 text_to_table      Invoice data extraction           True
    T14 text_to_table      Resume parsing to table           True
    T15 text_to_table  Schedule extraction to table           True
```

---

## Partie 3 : Disponibilité du NPU

### Étape 3 : Vérifier la disponibilité du NPU pour chaque tâche

```python
# NPU availability
available = bench["npu_available"].sum()
unavailable = len(bench) - available
print(f"NPU available: {available}/{len(bench)}")
print(f"NPU unavailable: {unavailable}")

# Which tasks have no NPU support?
no_npu = bench[bench["npu_available"] == False]
print("\nTasks without NPU support:")
print(no_npu[["task_id", "category", "description"]].to_string(index=False))
```

**Sortie attendue :**

```
NPU available: 14/15
NPU unavailable: 1

Tasks without NPU support:
task_id category                   description
    T12  rewrite  Translation (EN→ES snippet)
```

!!! warning "Limitation du NPU"
    La traduction (T12) n'est pas disponible sur le NPU — Phi Silica est optimisé pour les tâches en anglais et ne prend pas en charge la traduction entre langues sur l'appareil. Votre agent doit détecter cela et effectuer un repli vers l'inférence cloud.

---

## Partie 4 : Analyse de la correspondance de qualité

### Étape 4 : Comparer la qualité NPU vs cloud

```python
# Quality match for NPU-available tasks only
npu_tasks = bench[bench["npu_available"] == True]
quality_match = npu_tasks["quality_match"].sum()
total_available = len(npu_tasks)
match_rate = quality_match / total_available * 100

print(f"Quality match (NPU-available tasks): {quality_match}/{total_available} = {match_rate:.0f}%")

# Which NPU-available tasks have quality mismatch?
mismatches = npu_tasks[npu_tasks["quality_match"] == False]
print("\nQuality mismatches (NPU available but lower quality):")
print(mismatches[["task_id", "category", "description"]].to_string(index=False))
```

**Sortie attendue :**

```
Quality match (NPU-available tasks): 13/14 = 93%

Quality mismatches (NPU available but lower quality):
task_id      category              description
    T04     summarize  Policy doc summary
```

!!! info "Aperçu de la qualité"
    93 % des tâches disponibles sur le NPU correspondent à la qualité cloud. La seule non-correspondance est T04 (résumé de document de politique) — un document complexe qui pousse les limites de contexte du modèle sur appareil. Pour 13 des 14 tâches disponibles, la qualité NPU est indiscernable de celle du cloud.

```python
# Quality by category (NPU-available tasks only)
print("\nQuality match by category:")
for cat in npu_tasks["category"].unique():
    cat_data = npu_tasks[npu_tasks["category"] == cat]
    matches = cat_data["quality_match"].sum()
    total = len(cat_data)
    print(f"  {cat:>13}: {matches}/{total}")
```

**Sortie attendue :**

```
Quality match by category:
      summarize: 3/4
       classify: 4/4
        rewrite: 3/3
  text_to_table: 3/3
```

---

## Partie 5 : Comparaison de la latence

### Étape 5 : Latence NPU vs cloud

```python
# Average NPU latency (available tasks only)
npu_tasks = bench[bench["npu_available"] == True]
npu_avg = npu_tasks["npu_latency_ms"].mean()
cloud_avg = npu_tasks["cloud_latency_ms"].mean()
speedup = cloud_avg / npu_avg

print(f"NPU avg latency:   {npu_avg:.1f}ms")
print(f"Cloud avg latency: {cloud_avg:.1f}ms")
print(f"Speedup:           {speedup:.0f}×")
```

**Sortie attendue :**

```
NPU avg latency:   83.1ms
Cloud avg latency: 874.3ms
Speedup:           10×
```

```python
# Per-task latency comparison
print("\nPer-task latency (NPU-available only):")
for _, row in npu_tasks.iterrows():
    print(f"  {row['task_id']} ({row['category']:>13}): "
          f"NPU={row['npu_latency_ms']:.0f}ms  "
          f"Cloud={row['cloud_latency_ms']:.0f}ms")
```

!!! info "Avantage de latence"
    L'inférence NPU prend en moyenne 83,1ms — plus de **10× plus rapide** que le cloud à 874,3ms. C'est même plus rapide que l'ONNX Runtime sur CPU (82,3ms du Lab 061) parce que le NPU est conçu spécifiquement pour les charges de travail IA. Pour des expériences d'agent en temps réel, cette latence inférieure à 100ms permet des interactions véritablement réactives.

---

## Partie 6 : Stratégie de repli élégant

### Étape 6 : Implémenter la logique de repli

Le modèle correct pour les agents sur appareil est : **vérifier la disponibilité → tenter le NPU → repli vers le cloud** :

```csharp
// C# — Windows AI API pattern
async Task<string> RunAgentSkill(string input, SkillType skill)
{
    // 1. Check NPU readiness for this skill
    var readiness = await PhiSilicaModel.CheckReadinessAsync(skill);

    if (readiness == AIReadiness.Available)
    {
        // 2. Run on NPU
        return await PhiSilicaModel.InferAsync(input, skill);
    }
    else
    {
        // 3. Fall back to cloud
        Console.WriteLine($"NPU unavailable for {skill}, falling back to cloud");
        return await CloudModel.InferAsync(input, skill);
    }
}
```

!!! warning "Anti-modèle : pas de vérification de disponibilité"
    Ne supposez jamais que le NPU est disponible. Appelez toujours `CheckReadinessAsync()` en premier. Certaines tâches (comme la traduction) ne sont pas prises en charge sur l'appareil, et la disponibilité du NPU peut changer en fonction du matériel et de l'état des pilotes.

```python
# Simulate fallback strategy
print("Fallback strategy simulation:")
for _, row in bench.iterrows():
    if row["npu_available"]:
        engine = "NPU"
        latency = row["npu_latency_ms"]
    else:
        engine = "CLOUD (fallback)"
        latency = row["cloud_latency_ms"]
    print(f"  {row['task_id']}: {engine:>20} → {latency:.0f}ms")
```

---

## Partie 7 : Cadre décisionnel

### Étape 7 : Quand utiliser l'inférence sur appareil

| Scénario | Recommandé | Pourquoi |
|----------|-----------|----------|
| **Fonctionnement hors-ligne** | NPU | Pas d'internet requis |
| **Données sensibles en matière de confidentialité** | NPU | Les données ne quittent jamais l'appareil |
| **UX d'agent en temps réel** | NPU | Latence inférieure à 100ms |
| **Traduction** | Cloud | Le NPU ne prend pas en charge la traduction entre langues |
| **Documents complexes** | Cloud (ou NPU avec repli) | Le NPU peut avoir des écarts de qualité sur les entrées complexes |
| **Traitement par lots** | NPU | Zéro coût par token à grande échelle |

```python
# Summary dashboard
print("""
╔══════════════════════════════════════════════════════╗
║   On-Device Benchmark — Phi Silica (NPU) vs Cloud   ║
╠══════════════════════════════════════════════════════╣
║  Metric                    NPU         Cloud        ║
║  ─────────────────         ───         ─────        ║
║  Tasks supported           14/15       15/15        ║
║  Quality match (avail.)    93%         baseline     ║
║  Avg latency               83.1ms      874.3ms     ║
║  Speedup                   10×+        baseline     ║
║  Privacy                   Full        Data sent    ║
║  Offline capable           Yes         No           ║
╠══════════════════════════════════════════════════════╣
║  Strategy: NPU-first with cloud fallback            ║
║  Check readiness → attempt NPU → fall back if needed║
╚══════════════════════════════════════════════════════╝
""")
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-062/broken_ondevice.py` contient **3 bugs** dans les fonctions d'analyse sur appareil. Exécutez les auto-tests :

```bash
python lab-062/broken_ondevice.py
```

Vous devriez voir **3 tests échoués** :

| Test | Ce qu'il vérifie | Indice |
|------|-----------------|--------|
| Test 1 | Comptage de disponibilité du NPU | Quelle colonne représente la disponibilité — `npu_available` ou `quality_match` ? |
| Test 2 | Calcul de l'accélération | Le ratio est-il `npu / cloud` ou `cloud / npu` ? |
| Test 3 | Filtre de correspondance de qualité | Filtrez-vous par `npu_available == True` avant de vérifier la qualité ? |

Corrigez les 3 bugs et relancez jusqu'à voir `🎉 All 3 tests passed`.

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quel est le principal avantage de l'inférence basée sur le NPU avec Phi Silica ?"

    - A) Une meilleure précision que tous les modèles cloud
    - B) Inférence rapide sans connectivité internet
    - C) Prise en charge de toutes les langues et modalités
    - D) Taille de fenêtre de contexte illimitée

    ??? success "✅ Révéler la réponse"
        **Correct : B) Inférence rapide sans connectivité internet**

        Le NPU permet une inférence sur appareil à environ 83ms en moyenne — pas d'aller-retour réseau, pas de dépendance à internet et confidentialité totale des données. Il ne prétend pas avoir une meilleure précision que les modèles cloud (la correspondance de qualité est de 93 %), et il a des limitations (par exemple, pas de support de traduction). L'avantage clé est la combinaison de vitesse, de confidentialité et de capacité hors-ligne.

??? question "**Q2 (Choix multiple) :** Quel est le modèle correct pour gérer l'indisponibilité du NPU dans un agent en production ?"

    - A) Planter avec un message d'erreur indiquant à l'utilisateur de mettre à niveau son matériel
    - B) Toujours utiliser l'inférence cloud pour éviter les problèmes de NPU
    - C) Vérifier la disponibilité du NPU d'abord, puis effectuer un repli vers le cloud si indisponible
    - D) Réessayer l'inférence NPU 10 fois avant d'abandonner

    ??? success "✅ Révéler la réponse"
        **Correct : C) Vérifier la disponibilité du NPU d'abord, puis effectuer un repli vers le cloud si indisponible**

        Le modèle correct est : vérifier la disponibilité → tenter le NPU → repli vers le cloud. Cela garantit que l'agent fonctionne sur toutes les configurations matérielles et pour tous les types de tâches. Certaines tâches (comme la traduction) ne sont jamais disponibles sur le NPU, et la disponibilité matérielle peut varier. Un repli élégant offre la meilleure expérience utilisateur — rapide sur l'appareil quand c'est possible, cloud fiable quand c'est nécessaire.

??? question "**Q3 (Exécuter le lab) :** Combien de tâches ont le NPU indisponible ?"

    Calculez `(bench["npu_available"] == False).sum()`.

    ??? success "✅ Révéler la réponse"
        **1 tâche (T12 — Traduction)**

        Seule T12 (Traduction EN→ES snippet) n'a pas de support NPU. Toutes les 14 autres tâches — résumer, classifier, réécrire et text_to_table — peuvent s'exécuter sur le NPU via Phi Silica. Cela signifie que 93 % des tâches du benchmark peuvent s'exécuter entièrement sur l'appareil.

??? question "**Q4 (Exécuter le lab) :** Quel est le taux de correspondance de qualité pour les tâches disponibles sur le NPU ?"

    Filtrez par `npu_available == True`, puis calculez `quality_match.sum() / len(filtered) * 100`.

    ??? success "✅ Révéler la réponse"
        **93 % (13/14)**

        Sur les 14 tâches où le NPU est disponible, 13 produisent une qualité qui correspond à l'inférence cloud — un taux de correspondance de 93 %. La seule non-correspondance est T04 (résumé de document de politique), où le document complexe dépasse la capacité de contexte effective du modèle sur appareil. Pour la grande majorité des tâches, la qualité sur appareil est indiscernable de celle du cloud.

??? question "**Q5 (Exécuter le lab) :** Quelle est la latence moyenne du NPU pour les tâches disponibles ?"

    Filtrez par `npu_available == True`, puis calculez `npu_latency_ms.mean()`.

    ??? success "✅ Révéler la réponse"
        **83,1ms**

        La latence moyenne du NPU sur les 14 tâches disponibles est de 83,1ms. Comparé à la moyenne cloud de 874,3ms, cela représente une accélération de plus de 10×. Une latence inférieure à 100ms permet des interactions d'agent en temps réel — l'utilisateur perçoit la réponse comme instantanée. Cet avantage de latence est l'argument le plus fort en faveur de l'inférence sur appareil dans les expériences d'agent interactives.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|------------------------|
| Windows AI APIs | API au niveau système pour l'inférence NPU sur appareil |
| Phi Silica | Modèle optimisé pour le matériel NPU Windows |
| Disponibilité du NPU | 14/15 tâches prises en charge ; la traduction nécessite un repli vers le cloud |
| Correspondance de qualité | 93 % des tâches disponibles sur le NPU correspondent à la qualité cloud |
| Latence | NPU moy. 83,1ms vs cloud 874,3ms — plus de 10× plus rapide |
| Modèle de repli | Vérifier la disponibilité → NPU → repli vers le cloud |

---

## Prochaines étapes

- **[Lab 061](lab-061-slm-phi4-mini.md)** — SLM avec Phi-4 Mini (inférence locale sur CPU/GPU via ONNX Runtime)
- **[Lab 063](lab-063-agent-identity-entra.md)** — Identité des agents avec Entra (sécuriser les agents qui accèdent aux ressources cloud)
- **[Lab 043](lab-043-multimodal-agents.md)** — Agents multimodaux (étendre les capacités des agents au-delà du texte)