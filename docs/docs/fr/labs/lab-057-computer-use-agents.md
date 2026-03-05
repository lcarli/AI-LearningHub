---
tags: [computer-use, automation, anthropic, desktop, python, safety]
---
# Lab 057 : Agents utilisant l'ordinateur — Automatisation du bureau

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Durée :</strong> ~90 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise un jeu de données de benchmark ; API Anthropic optionnelle</span>
</div>

## Ce que vous apprendrez

- Ce que sont les **agents utilisant l'ordinateur** — une IA qui interagit avec un bureau comme le ferait un humain (capture d'écran → raisonnement → clic/saisie)
- La **boucle capture d'écran–action** : l'agent capture une image de l'écran, identifie les éléments d'interface et exécute des actions souris/clavier
- Comment exécuter des agents dans un **bac à sable Docker** pour les isoler du système hôte
- Concevoir des **garde-fous de sécurité** — listes blanches de domaines, invites de confirmation d'action et limites de débit
- Analyser des **benchmarks d'automatisation de bureau** pour comprendre où les agents utilisant l'ordinateur réussissent et échouent

## Introduction

L'automatisation traditionnelle repose sur des API, des scripts ou des bots RPA qui interagissent avec des interfaces structurées. Mais que se passe-t-il lorsque l'application n'a **pas d'API** ? Les applications de bureau anciennes, les terminaux mainframe et les logiciels client lourd n'exposent souvent qu'une interface graphique.

Les **agents utilisant l'ordinateur** résolvent ce problème en opérant l'ordinateur comme le ferait un humain. L'agent capture une **image de l'écran** actuel, l'envoie à un modèle de vision-langage (comme l'outil `computer_20251124` d'Anthropic), reçoit une action structurée (déplacer la souris, cliquer, saisir du texte), l'exécute et recommence. Cette boucle capture d'écran → action permet à l'agent d'interagir avec *n'importe quelle* application disposant d'une interface visuelle.

### Le scénario

Vous êtes **ingénieur en automatisation** chez OutdoorGear Inc. L'entreprise utilise un système de gestion des stocks ancien — une application Windows client lourd sans API et sans projet de modernisation. La direction souhaite automatiser les tâches répétitives comme le remplissage de formulaires de frais, la génération de rapports et la navigation dans le système ERP.

Votre mission est d'évaluer si les agents utilisant l'ordinateur peuvent gérer ces tâches de manière fiable et sécurisée, en utilisant un jeu de données de benchmark de **10 tâches de bureau et de navigateur**.

!!! info "Aucun agent en direct requis"
    Ce lab analyse un **jeu de données de benchmark pré-enregistré** de résultats de tâches d'utilisation de l'ordinateur. Vous n'avez pas besoin d'une clé API Anthropic ni d'un agent en cours d'exécution — toute l'analyse se fait localement avec pandas. Si vous avez accès à l'API, vous pouvez optionnellement étendre le lab pour exécuter des tâches en direct.

## Prérequis

| Exigence | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| Bibliothèque `pandas` | Opérations sur les DataFrames |
| (Optionnel) Clé API Anthropic | Pour des expériences d'utilisation de l'ordinateur en direct |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-057/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|------|-------------|----------|
| `broken_safety.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-057/broken_safety.py) |
| `desktop_tasks.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-057/desktop_tasks.csv) |

---

## Étape 1 : Comprendre l'utilisation de l'ordinateur

Les agents utilisant l'ordinateur suivent une boucle simple mais puissante :

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Screenshot  │────▶│  Vision LLM  │────▶│   Action     │
│  (pixels)    │     │  (reason)    │     │  (click/type)│
└─────────────┘     └──────────────┘     └──────────────┘
       ▲                                        │
       └────────────────────────────────────────┘
                    repeat until done
```

Les composants clés :

| Composant | Description |
|-----------|-------------|
| **Capture d'écran** | Capture l'écran actuel sous forme d'image (PNG) |
| **Modèle de vision** | Analyse la capture d'écran pour identifier les éléments d'interface et décider de l'action suivante |
| **Exécuteur d'actions** | Traduit la sortie du modèle en événements souris/clavier au niveau du système d'exploitation |
| **Bac à sable** | Conteneur Docker ou machine virtuelle qui isole l'agent du système hôte |

L'outil `computer_20251124` d'Anthropic offre trois capacités :

1. **Capture d'écran** — prend une photo de l'écran actuel
2. **Contrôle de la souris** — déplacer, cliquer, double-cliquer, glisser
3. **Saisie clavier** — saisir du texte, appuyer sur des combinaisons de touches

!!! tip "Pourquoi des captures d'écran ?"
    Contrairement au web scraping traditionnel (qui lit le HTML/DOM), les agents utilisant l'ordinateur voient l'écran en *pixels*. Cela signifie qu'ils peuvent interagir avec n'importe quelle interface visuelle — applications de bureau, bureaux à distance, émulateurs de terminal, voire des jeux — sans avoir besoin d'accéder au code sous-jacent ou au DOM.

---

## Étape 2 : Charger le jeu de données de benchmark

Le jeu de données contient **10 tâches** qu'un agent utilisant l'ordinateur a tentées, couvrant des scénarios de bureau et de navigateur :

```python
import pandas as pd

tasks = pd.read_csv("lab-057/desktop_tasks.csv")
print(f"Total tasks: {len(tasks)}")
print(f"Task types: {sorted(tasks['app_type'].unique())}")
print(f"Difficulty levels: {sorted(tasks['difficulty'].unique())}")
print(f"\nDataset preview:")
print(tasks[["task_id", "task_description", "app_type", "completed", "safety_risk"]].to_string(index=False))
```

**Sortie attendue :**

```
Total tasks: 10
Task types: ['browser', 'desktop']
Difficulty levels: ['easy', 'hard', 'medium']
```

| task_id | task_description | app_type | completed | safety_risk |
|---------|-----------------|----------|-----------|-------------|
| T01 | Open calculator and compute 15 × 23 | desktop | True | low |
| T02 | Create a new text file on the desktop | desktop | True | low |
| T03 | Open browser and search for hiking boots | browser | True | low |
| ... | ... | ... | ... | ... |
| T10 | Navigate a multi-step checkout process | browser | False | high |

---

## Étape 3 : Analyser les taux de complétion

Calculez les taux de complétion globaux et par niveau de difficulté :

```python
completed = tasks["completed"].sum()
total = len(tasks)
rate = (completed / total) * 100
print(f"Completed: {completed}/{total}")
print(f"Completion rate: {rate:.0f}%")

print(f"\nBy difficulty:")
for diff in ["easy", "medium", "hard"]:
    subset = tasks[tasks["difficulty"] == diff]
    diff_rate = (subset["completed"].sum() / len(subset)) * 100
    print(f"  {diff}: {subset['completed'].sum()}/{len(subset)} = {diff_rate:.0f}%")
```

**Sortie attendue :**

```
Completed: 7/10
Completion rate: 70%

By difficulty:
  easy: 2/2 = 100%
  medium: 4/4 = 100%
  hard: 1/4 = 25%
```

!!! tip "Observation"
    L'agent gère les tâches **faciles et moyennes** de manière fiable (100%) mais peine avec les **tâches difficiles** (25%). Les tâches difficiles impliquent des flux de travail à plusieurs étapes, du contenu dynamique ou des opérations sensibles en matière de sécurité — autant de défis pour la navigation basée sur les captures d'écran.

---

## Étape 4 : Analyse des risques de sécurité

Identifiez les tâches présentant un risque de sécurité élevé :

```python
print("Safety risk distribution:")
print(tasks["safety_risk"].value_counts().sort_index())

high_risk = tasks[tasks["safety_risk"] == "high"]
print(f"\nHigh-risk tasks: {len(high_risk)}")
print(high_risk[["task_id", "task_description", "completed"]].to_string(index=False))
```

**Sortie attendue :**

```
Safety risk distribution:
high      2
low       6
medium    2

High-risk tasks: 2
```

| task_id | task_description | completed |
|---------|-----------------|-----------|
| T08 | Log into a web application using credentials | False |
| T10 | Navigate a multi-step checkout process | False |

Les deux tâches à haut risque ont **échoué**, ce qui est en réalité un bon résultat — cela signifie que l'agent n'a pas réussi à effectuer des actions potentiellement dangereuses sans garde-fous appropriés.

!!! warning "Pourquoi ces tâches sont à haut risque"
    - **T08 (Connexion avec des identifiants)** : L'agent devrait lire les mots de passe depuis un gestionnaire de mots de passe — un risque de sécurité significatif si l'agent est compromis ou si le bac à sable est violé.
    - **T10 (Processus de paiement)** : Finaliser un achat avec de vraies informations de paiement pourrait avoir des conséquences financières si l'agent fait des erreurs.

---

## Étape 5 : Comparaison des tâches bureau vs navigateur

Comparez les performances de l'agent sur les tâches de bureau par rapport aux tâches de navigateur :

```python
print("Performance by app type:")
for app in ["desktop", "browser"]:
    subset = tasks[tasks["app_type"] == app]
    rate = (subset["completed"].sum() / len(subset)) * 100
    avg_time = subset[subset["completed"] == True]["time_sec"].mean()
    avg_actions = subset[subset["completed"] == True]["actions"].mean()
    print(f"\n  {app.upper()}:")
    print(f"    Tasks: {len(subset)}")
    print(f"    Completed: {subset['completed'].sum()}/{len(subset)} ({rate:.0f}%)")
    print(f"    Avg time (completed): {avg_time:.1f}s")
    print(f"    Avg actions (completed): {avg_actions:.1f}")
```

**Sortie attendue :**

```
Performance by app type:

  DESKTOP:
    Tasks: 5
    Completed: 4/5 (80%)
    Avg time (completed): 20.5s
    Avg actions (completed): 8.0

  BROWSER:
    Tasks: 5
    Completed: 3/5 (60%)
    Avg time (completed): 26.0s
    Avg actions (completed): 10.7
```

!!! tip "Observation"
    Les tâches de bureau ont un taux de réussite plus élevé (80% vs 60%) et nécessitent en moyenne moins d'actions. Les tâches de navigateur tendent à impliquer plus de contenu dynamique et une navigation complexe, ce qui les rend plus difficiles pour les agents basés sur les captures d'écran.

---

## Étape 6 : Conception des garde-fous de sécurité

Sur la base de l'analyse du benchmark, concevez des garde-fous pour le déploiement en production :

### Garde-fous recommandés

| Garde-fou | Objectif | Implémentation |
|-----------|---------|----------------|
| **Liste blanche de domaines** | Restreindre les applications/sites auxquels l'agent peut accéder | Fichier de configuration listant les noms d'applications et URLs approuvés |
| **Confirmation d'action** | Exiger l'approbation humaine pour les actions à haut risque | Demander confirmation avant les clics sur des boutons comme « Soumettre », « Acheter », « Supprimer » |
| **Limite de durée de session** | Empêcher les agents incontrôlés | Arrêter l'agent après N minutes d'inactivité |
| **Journalisation des captures d'écran** | Piste d'audit de chaque action | Enregistrer chaque capture d'écran avec horodatage et action effectuée |
| **Isolation des identifiants** | Ne jamais exposer les mots de passe à l'agent | Utiliser des variables d'environnement ou des références de coffre-fort, jamais de mots de passe visibles à l'écran |

### Matrice de décision des garde-fous

```python
print("Guardrail recommendations by risk level:")
for _, task in tasks.iterrows():
    guardrails = []
    if task["safety_risk"] == "high":
        guardrails = ["domain_allowlist", "action_confirmation", "human_review"]
    elif task["safety_risk"] == "medium":
        guardrails = ["domain_allowlist", "screenshot_logging"]
    else:
        guardrails = ["screenshot_logging"]
    print(f"  {task['task_id']} ({task['safety_risk']}): {', '.join(guardrails)}")
```

!!! warning "Le bac à sable Docker est essentiel"
    **N'exécutez jamais un agent utilisant l'ordinateur sur votre machine hôte.** Utilisez toujours un conteneur Docker ou une machine virtuelle. Si l'agent interprète mal une capture d'écran et clique sur « Tout supprimer » au lieu de « Tout sélectionner », les dégâts sont contenus dans le bac à sable. L'implémentation de référence d'Anthropic utilise un conteneur Docker avec un affichage virtuel (Xvfb) précisément pour cette raison.

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-057/broken_safety.py` contient **3 bugs** dans les fonctions d'analyse de sécurité. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-057/broken_safety.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Calcul du taux de complétion | Le dénominateur devrait être le nombre total de tâches, pas le nombre de tâches complétées |
| Test 2 | Comptage des tâches à haut risque | Devrait vérifier `"high"`, pas `"medium"` |
| Test 3 | Temps moyen pour les tâches complétées | Doit filtrer les tâches complétées avant de calculer la moyenne |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `🎉 All 3 tests passed`, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quelles capacités l'outil `computer_20251124` d'Anthropic fournit-il ?"

    - A) Uniquement la saisie clavier pour taper des commandes
    - B) Capture d'écran, contrôle de la souris et saisie clavier
    - C) Accès direct au DOM et analyse HTML
    - D) Intégration API avec les applications de bureau

    ??? success "✅ Révéler la réponse"
        **Correct : B) Capture d'écran, contrôle de la souris et saisie clavier**

        L'outil `computer_20251124` offre trois capacités principales : (1) capturer des images de l'écran actuel, (2) contrôler la souris (déplacer, cliquer, glisser) et (3) envoyer des entrées clavier (saisir du texte, appuyer sur des combinaisons de touches). Il n'accède *pas* au DOM ni aux API des applications — il opère uniquement via l'interface visuelle.

??? question "**Q2 (Choix multiple) :** Quel est l'objectif principal de l'exécution d'un agent utilisant l'ordinateur dans un bac à sable Docker ?"

    - A) Améliorer la résolution des captures d'écran de l'agent
    - B) Réduire les coûts d'API en regroupant les requêtes
    - C) Isoler l'agent du système hôte et contenir les dommages potentiels
    - D) Permettre à l'agent d'exécuter plusieurs tâches en parallèle

    ??? success "✅ Révéler la réponse"
        **Correct : C) Isoler l'agent du système hôte et contenir les dommages potentiels**

        Un bac à sable Docker (ou une machine virtuelle) crée une frontière entre l'agent et votre système réel. Si l'agent interprète mal une capture d'écran et effectue une action non intentionnelle — comme supprimer des fichiers ou cliquer sur le mauvais bouton — les dommages sont contenus dans le bac à sable et n'affectent pas votre machine hôte, vos fichiers ou vos comptes.

??? question "**Q3 (Exécuter le lab) :** Quel est le taux global de complétion des tâches ?"

    Chargez [📥 `desktop_tasks.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-057/desktop_tasks.csv) et calculez `completed.sum() / total`.

    ??? success "✅ Révéler la réponse"
        **70%**

        7 tâches sur 10 ont été complétées avec succès. Les 3 tâches échouées (T07, T08, T10) étaient toutes de difficulté **difficile** — l'agent a eu du mal avec les flux de travail complexes à plusieurs étapes et les opérations sensibles en matière de sécurité.

??? question "**Q4 (Exécuter le lab) :** Combien de tâches à haut risque y a-t-il dans le jeu de données ?"

    Filtrez les tâches où `safety_risk == "high"` et comptez-les.

    ??? success "✅ Révéler la réponse"
        **2**

        Les tâches T08 (Se connecter à une application web en utilisant des identifiants d'un gestionnaire de mots de passe) et T10 (Naviguer dans un processus de paiement à plusieurs étapes sur un site e-commerce) sont classées comme à haut risque. Les deux impliquent des opérations sensibles — gestion d'identifiants et transactions financières — où les erreurs de l'agent pourraient avoir des conséquences graves.

??? question "**Q5 (Exécuter le lab) :** Quel est le nombre moyen d'actions pour les tâches complétées uniquement ?"

    Filtrez avec `completed == True`, puis calculez `actions.mean()`.

    ??? success "✅ Révéler la réponse"
        **≈ 9.1**

        Tâches complétées : T01(5) + T02(7) + T03(6) + T04(12) + T05(9) + T06(14) + T09(11) = **64 actions** sur **7 tâches**. Moyenne = 64 ÷ 7 ≈ **9,14 actions par tâche complétée**.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Concept d'utilisation de l'ordinateur | Boucle capture d'écran → action : capturer l'écran, raisonner avec un LLM de vision, exécuter souris/clavier |
| Analyse de benchmark | Taux de complétion de 70% ; tâches faciles/moyennes fiables, tâches difficiles problématiques |
| Risques de sécurité | Les tâches à haut risque (identifiants, paiements) nécessitent des garde-fous supplémentaires |
| Bureau vs navigateur | Les tâches de bureau ont un meilleur taux de réussite (80%) que les tâches de navigateur (60%) |
| Conception des garde-fous | Listes blanches de domaines, confirmation d'action, bac à sable Docker, isolation des identifiants |
| Bac à sable Docker | Couche d'isolation essentielle — n'exécutez jamais d'agents utilisant l'ordinateur sur votre hôte |

---

## Prochaines étapes

- **[Lab 058](lab-058-browser-automation-cua.md)** — Agents d'automatisation de navigateur avec OpenAI CUA
- Explorez l'[implémentation de référence pour l'utilisation de l'ordinateur](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use) d'Anthropic pour la configuration d'un agent en direct
