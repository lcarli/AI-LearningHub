---
tags: [declarative-agents, m365-copilot, teams, manifest, low-code]
---
# Lab 069 : Agents déclaratifs pour Microsoft 365 Copilot

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Manifeste simulé (aucune licence M365 Copilot requise)</span>
</div>

## Ce que vous apprendrez

- Ce que sont les **agents déclaratifs** et comment ils étendent Microsoft 365 Copilot
- Définir le comportement d'un agent via un **manifeste JSON** sans écrire de code
- Configurer des **sources de connaissances** (SharePoint, connecteurs Graph, fichiers)
- Ajouter des **plugins API** pour donner à votre agent des capacités personnalisées
- Configurer des **amorces de conversation** pour des interactions utilisateur guidées
- Valider et résoudre les problèmes de configuration des manifestes

!!! abstract "Prérequis"
    Une familiarité avec les concepts de **Microsoft 365 Copilot** est recommandée. Aucune expérience en programmation n'est requise — les agents déclaratifs sont configurés entièrement via des manifestes JSON.

## Introduction

Les **agents déclaratifs** vous permettent de personnaliser le comportement de Microsoft 365 Copilot sans écrire de code. Au lieu de construire un agent personnalisé de zéro, vous définissez un manifeste JSON qui spécifie :

- **Instructions** — Prompt système qui façonne le persona et le comportement de l'agent
- **Sources de connaissances** — Où l'agent récupère les informations (sites SharePoint, connecteurs Graph, fichiers importés)
- **Plugins API** — API externes que l'agent peut appeler pour effectuer des actions
- **Amorces de conversation** — Prompts prédéfinis qui guident les utilisateurs vers les capacités de l'agent

| Composant | Objectif | Exemple |
|-----------|---------|---------|
| **Instructions** | Définir le persona, le ton et les limites | « Vous êtes un assistant RH. Répondez uniquement aux questions liées aux RH. » |
| **Sources de connaissances** | Ancrer les réponses dans les données organisationnelles | Site SharePoint avec les politiques de l'entreprise |
| **Plugins API** | Permettre des actions au-delà du chat | Soumettre des demandes de congés via l'API RH |
| **Amorces de conversation** | Guider les utilisateurs vers des interactions productives | « Quelle est la politique de congés de l'entreprise ? » |

### Le scénario

Vous construisez un **assistant RH d'entreprise** en tant qu'agent déclaratif pour Microsoft 365 Copilot. L'agent doit répondre aux questions sur les politiques de l'entreprise, aider les employés à soumettre des demandes de congés et fournir des conseils d'intégration. Vous examinerez un fichier manifeste, comprendrez chaque composant et validerez la configuration.

---

## Prérequis

| Exigence | Raison |
|---|---|
| Python 3.10+ | Exécuter les scripts de validation |
| `json` (intégré) | Analyser les fichiers manifestes |

Aucun package supplémentaire requis — le module `json` est inclus avec Python.

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-069/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `broken_manifest.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-069/broken_manifest.py) |
| `declarative_agent.json` | Fichier de configuration / données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-069/declarative_agent.json) |

---

## Étape 1 : Comprendre l'architecture des agents déclaratifs

Les agents déclaratifs se situent entre l'utilisateur et Microsoft 365 Copilot, personnalisant son comportement :

```
User → [Teams / M365 App] → [Declarative Agent Manifest]
                                      ↓
                             [Instructions] → Persona + Boundaries
                             [Knowledge]    → SharePoint, Graph, Files
                             [Plugins]      → API Actions
                             [Starters]     → Guided Conversations
                                      ↓
                            Microsoft 365 Copilot → Response
```

Principes clés :

1. **Aucun code requis** — Toute la configuration est en JSON
2. **Connaissances ciblées** — L'agent n'accède qu'aux sources spécifiées
3. **Actions par plugins** — L'agent peut appeler des API pour effectuer des tâches
4. **Garde-fous** — Les instructions définissent ce que l'agent doit et ne doit pas faire

!!! info "Agents déclaratifs vs agents personnalisés"
    Les agents déclaratifs étendent Copilot — ils héritent de ses capacités de raisonnement, de sécurité et d'ancrage. Les agents personnalisés (construits avec Bot Framework ou Copilot Studio) sont autonomes et nécessitent plus d'efforts de développement mais offrent une plus grande flexibilité pour les workflows complexes.

---

## Étape 2 : Charger et explorer le manifeste

Chargez le manifeste de l'agent déclaratif et examinez sa structure :

```python
import json

with open("lab-069/declarative_agent.json", "r") as f:
    manifest = json.load(f)

print(f"Agent Name: {manifest['name']}")
print(f"Description: {manifest['description']}")
print(f"\nTop-level keys: {list(manifest.keys())}")
print(f"Instructions length: {len(manifest['instructions'])} characters")
```

**Attendu :**

```
Agent Name: HR Assistant
Description: A declarative agent for answering HR policy questions and managing time-off requests.
```

---

## Étape 3 : Analyse des sources de connaissances

Examinez les sources de connaissances configurées pour l'agent :

```python
knowledge = manifest["knowledge_sources"]
print(f"Number of knowledge sources: {len(knowledge)}")
for i, source in enumerate(knowledge):
    print(f"\n  Source {i+1}:")
    print(f"    Type: {source['type']}")
    print(f"    Name: {source['name']}")
    print(f"    Description: {source['description']}")
```

**Attendu :**

```
Number of knowledge sources: 3
```

!!! tip "Connaissances ciblées"
    Chaque source de connaissances limite ce à quoi l'agent peut accéder. En spécifiant exactement 3 sources (par ex. un site SharePoint pour les politiques, un connecteur Graph pour les données organisationnelles, un fichier importé pour le guide des avantages), l'agent est ancré dans des informations organisationnelles vérifiées et ne peut pas accéder aux données hors de son périmètre.

---

## Étape 4 : Configuration des plugins API

Examinez les plugins API disponibles pour l'agent :

```python
plugins = manifest["api_plugins"]
print(f"Number of API plugins: {len(plugins)}")
for plugin in plugins:
    print(f"\n  Plugin: {plugin['name']}")
    print(f"  Description: {plugin['description']}")
    print(f"  Endpoint: {plugin['endpoint']}")
    print(f"  Operations: {[op['name'] for op in plugin['operations']]}")
```

**Attendu :**

```
Number of API plugins: 1
```

!!! warning "Sécurité des plugins"
    Les plugins API permettent à l'agent d'effectuer des actions — soumettre des demandes, mettre à jour des enregistrements ou interroger des systèmes externes. Chaque plugin devrait utiliser l'authentification OAuth 2.0 et être limité aux permissions minimales requises. Validez toujours que les points de terminaison des plugins sont internes et de confiance.

---

## Étape 5 : Amorces de conversation

Examinez les amorces de conversation qui guident les utilisateurs :

```python
starters = manifest["conversation_starters"]
print(f"Number of conversation starters: {len(starters)}")
for i, starter in enumerate(starters):
    print(f"\n  Starter {i+1}: {starter['text']}")
    print(f"    Category: {starter.get('category', 'general')}")
```

**Attendu :**

```
Number of conversation starters: 4
```

Les amorces de conversation apparaissent comme des suggestions cliquables lorsque les utilisateurs interagissent pour la première fois avec l'agent. Elles guident les utilisateurs vers les capacités principales de l'agent et réduisent le problème du « prompt vide ».

---

## Étape 6 : Validation du manifeste

Validez le manifeste pour la complétude et les problèmes courants :

```python
required_fields = ["name", "description", "instructions", "knowledge_sources",
                   "api_plugins", "conversation_starters"]
missing = [f for f in required_fields if f not in manifest]
print(f"Missing required fields: {missing if missing else 'None'}")

# Validation checks
checks = {
    "Has name": bool(manifest.get("name")),
    "Has description": bool(manifest.get("description")),
    "Has instructions": len(manifest.get("instructions", "")) > 50,
    "Knowledge sources > 0": len(manifest.get("knowledge_sources", [])) > 0,
    "Conversation starters > 0": len(manifest.get("conversation_starters", [])) > 0,
}

print("\nValidation Results:")
for check, passed in checks.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"  {status} — {check}")

print(f"\nOverall: {'All checks passed' if all(checks.values()) else 'Some checks failed'}")
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-069/broken_manifest.py` contient **3 bugs** dans la façon dont il valide le manifeste :

```bash
python lab-069/broken_manifest.py
```

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Nombre de sources de connaissances | Devrait lire depuis `knowledge_sources`, pas `data_sources` |
| Test 2 | Validation des plugins | Devrait vérifier `api_plugins`, pas `extensions` |
| Test 3 | Extraction du texte des amorces | Devrait accéder à `starter['text']`, pas `starter['prompt']` |

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quel est le principal avantage des agents déclaratifs par rapport aux agents construits sur mesure ?"

    - A) Ils sont plus rapides à l'inférence
    - B) Ils ne nécessitent aucun code — toute la configuration est définie dans un manifeste JSON
    - C) Ils peuvent accéder à n'importe quelle source de données sans restrictions
    - D) Ils fonctionnent uniquement en local

    ??? success "✅ Révéler la réponse"
        **Correct : B) Ils ne nécessitent aucun code — toute la configuration est définie dans un manifeste JSON**

        Les agents déclaratifs étendent Microsoft 365 Copilot en configurant le comportement via un manifeste JSON. Cela inclut les instructions (prompt système), les sources de connaissances, les plugins API et les amorces de conversation. Aucune programmation n'est requise, les rendant accessibles aux non-développeurs tout en fournissant des capacités d'agent ciblées et gouvernées.

??? question "**Q2 (Choix multiple) :** Pourquoi les sources de connaissances ciblées sont-elles importantes pour les agents déclaratifs ?"

    - A) Elles rendent l'agent plus rapide
    - B) Elles garantissent que l'agent n'accède qu'à des données vérifiées et autorisées — empêchant l'hallucination à partir de sources non ancrées
    - C) Elles sont requises par le store d'applications Teams
    - D) Elles réduisent la taille du fichier manifeste

    ??? success "✅ Révéler la réponse"
        **Correct : B) Elles garantissent que l'agent n'accède qu'à des données vérifiées et autorisées — empêchant l'hallucination à partir de sources non ancrées**

        En listant explicitement les sources de connaissances (sites SharePoint, connecteurs Graph, fichiers), l'agent est ancré dans les données organisationnelles. Il ne peut pas accéder aux données hors de son périmètre, réduisant le risque d'hallucination et assurant la conformité avec les politiques d'accès aux données. C'est un avantage clé de gouvernance des agents déclaratifs.

??? question "**Q3 (Exécutez le lab) :** Combien de sources de connaissances sont configurées dans le manifeste ?"

    Chargez le JSON du manifeste et vérifiez `len(manifest['knowledge_sources'])`.

    ??? success "✅ Révéler la réponse"
        **3 sources de connaissances**

        L'agent Assistant RH a 3 sources de connaissances configurées, lui fournissant un accès ciblé aux politiques de l'entreprise, aux données organisationnelles et aux informations sur les avantages des employés. Chaque source est explicitement déclarée dans le manifeste.

??? question "**Q4 (Exécutez le lab) :** Combien de plugins API sont configurés ?"

    Vérifiez `len(manifest['api_plugins'])`.

    ??? success "✅ Révéler la réponse"
        **1 plugin API**

        L'agent a 1 plugin API configuré, lui permettant d'effectuer des actions comme la soumission de demandes de congés via une API RH. Les plugins API permettent aux agents déclaratifs d'aller au-delà du chat et d'effectuer de vraies actions au nom des utilisateurs.

??? question "**Q5 (Exécutez le lab) :** Combien d'amorces de conversation sont définies ?"

    Vérifiez `len(manifest['conversation_starters'])`.

    ??? success "✅ Révéler la réponse"
        **4 amorces de conversation**

        Le manifeste définit 4 amorces de conversation qui apparaissent comme des suggestions cliquables lorsque les utilisateurs interagissent pour la première fois avec l'agent. Elles guident les utilisateurs vers les capacités principales de l'agent — poser des questions sur les politiques de congés, soumettre des demandes de congés, vérifier les avantages et obtenir de l'aide pour l'intégration.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Agents déclaratifs | Étendre M365 Copilot via la configuration d'un manifeste JSON |
| Instructions | Définir le persona, le ton et les limites comportementales |
| Sources de connaissances | Restreindre l'accès de l'agent aux données organisationnelles vérifiées |
| Plugins API | Permettre aux agents d'effectuer des actions via des API externes |
| Amorces de conversation | Guider les utilisateurs vers des interactions productives |
| Validation du manifeste | Vérifier la complétude et l'exactitude de la configuration de l'agent |

---

## Prochaines étapes

- **[Lab 070](lab-070-agent-ux-patterns.md)** — Patterns UX des agents (concevoir des interactions d'agent efficaces)
- **[Lab 066](lab-066-copilot-studio-governance.md)** — Gouvernance Copilot Studio (gouverner les déploiements d'agents)
- **[Lab 008](lab-008-responsible-ai.md)** — IA responsable (principes fondamentaux de gouvernance)