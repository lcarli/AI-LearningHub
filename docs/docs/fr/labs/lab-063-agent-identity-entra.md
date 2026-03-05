---
tags: [security, entra-id, obo, identity, oauth, enterprise]
---
# Lab 063 : Identité des agents — Flux Entra OBO & moindre privilège

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~75 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des données de scénarios simulées (aucun tenant Entra requis)</span>
</div>

## Ce que vous apprendrez

- Comment le **flux OAuth 2.0 On-Behalf-Of (OBO)** transmet l'identité de l'utilisateur à travers une chaîne d'agents
- La différence entre les **permissions déléguées** (agir en tant qu'utilisateur) et les **permissions d'application** (agir en tant qu'application)
- Identifier les **violations de conformité** dans les configurations de permissions des agents
- Appliquer les **principes du moindre privilège** à la conception de l'identité des agents
- Implémenter des **portes de validation humaine (human-in-the-loop)** pour les actions d'agents à haut risque
- Analyser un **jeu de données de 15 scénarios** à travers 4 agents pour évaluer la posture de sécurité

---

## Introduction

Lorsque les agents accèdent aux ressources d'entreprise — lire les e-mails, interroger des bases de données, modifier SharePoint — ils ont besoin d'une identité. **La manière** dont ils s'authentifient détermine la posture de sécurité de l'ensemble de votre système.

Le **flux On-Behalf-Of (OBO)** garantit que les agents agissent avec l'identité et les permissions de l'utilisateur, en maintenant le principe du moindre privilège. L'alternative — **client_credentials** (permissions d'application) — donne à l'agent sa propre identité avec un accès potentiellement large, contournant l'autorisation au niveau de l'utilisateur.

Ce lab analyse 15 scénarios réels pour montrer pourquoi OBO est le choix par défaut et quand client_credentials crée des risques de conformité.

### Les scénarios

Vous examinerez **15 scénarios** à travers **4 agents**, chacun avec des configurations de permissions différentes :

| Agent | Description | Scénarios |
|-------|-------------|-----------|
| **MailAgent** | Lit et envoie des e-mails au nom des utilisateurs | 4 |
| **FileAgent** | Accède aux fichiers SharePoint et OneDrive | 4 |
| **CalendarAgent** | Gère les événements de calendrier et la planification | 4 |
| **AdminAgent** | Effectue des opérations d'annuaire et de conformité | 3 |

---

## Prérequis

```bash
pip install pandas
```

Ce lab analyse des données de scénarios pré-calculées — aucun tenant Entra ID, abonnement Azure ou enregistrement d'application requis. Pour implémenter les flux OBO en production, vous auriez besoin d'un tenant Entra ID avec des enregistrements d'applications.

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-063/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|---------|-------------|-------------|
| `broken_identity.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-063/broken_identity.py) |
| `identity_scenarios.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-063/identity_scenarios.csv) |

---

## Partie 1 : Comprendre le flux OBO

### Étape 1 : OBO vs client_credentials

Les deux principaux flux d'authentification pour les agents :

```
OBO Flow (Delegated — Recommended):
  User → [Auth] → Agent → [OBO token exchange] → Resource API
  Agent acts AS the user — user's permissions apply

Client Credentials (Application — Use with caution):
  Agent → [App secret/cert] → Resource API
  Agent acts AS ITSELF — app permissions apply (often broader)
```

Concepts clés :

| Concept | Description |
|---------|-------------|
| **OBO (On-Behalf-Of)** | L'agent échange le jeton utilisateur contre un jeton d'API en aval, préservant l'identité de l'utilisateur |
| **Permissions déléguées** | L'agent agit en tant qu'utilisateur connecté — limité à l'accès propre de l'utilisateur |
| **Permissions d'application** | L'agent agit en son propre nom — peut accéder aux données de tous les utilisateurs (ex. : lire TOUTES les boîtes mail) |
| **Moindre privilège** | N'accorder que les permissions minimales nécessaires pour la tâche |
| **Human-in-the-loop** | Exiger l'approbation explicite de l'utilisateur pour les actions à haut risque |

!!! warning "Pourquoi OBO est important"
    Avec client_credentials, un MailAgent pourrait lire les e-mails de **tous les utilisateurs** — pas seulement ceux de l'utilisateur demandeur. OBO garantit que l'agent ne peut accéder qu'à ce que l'utilisateur lui-même peut accéder. C'est la différence entre un outil contrôlé et une faille de sécurité.

---

## Partie 2 : Charger les données de scénarios

### Étape 2 : Charger [📥 `identity_scenarios.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-063/identity_scenarios.csv)

Le jeu de données de scénarios contient 15 configurations d'identité à travers 4 agents :

```python
# identity_analysis.py
import pandas as pd

scenarios = pd.read_csv("lab-063/identity_scenarios.csv")

print(f"Scenarios: {len(scenarios)}")
print(f"Agents: {scenarios['agent'].unique().tolist()}")
print(f"Auth flows: {scenarios['auth_flow'].unique().tolist()}")
print(scenarios[["scenario_id", "agent", "auth_flow", "risk_level", "compliant"]].to_string(index=False))
```

**Sortie attendue :**

```
Scenarios: 15
Agents: ['MailAgent', 'FileAgent', 'CalendarAgent', 'AdminAgent']
Auth flows: ['obo', 'client_credentials']

scenario_id          agent          auth_flow risk_level  compliant
        S01      MailAgent                obo        low       True
        S02      MailAgent                obo        low       True
        S03      MailAgent                obo     medium       True
        S04      MailAgent                obo     medium       True
        S05      MailAgent  client_credentials   critical      False
        S06      FileAgent                obo        low       True
        S07      FileAgent  client_credentials   critical      False
        S08      FileAgent                obo     medium       True
        S09      FileAgent                obo        low       True
        S10   CalendarAgent  client_credentials   critical      False
        S11   CalendarAgent                obo        low       True
        S12   CalendarAgent                obo     medium       True
        S13      AdminAgent                obo       high       True
        S14      AdminAgent  client_credentials       high      False
        S15      AdminAgent                obo     medium       True
```

---

## Partie 3 : Analyse de conformité

### Étape 3 : Identifier les violations de conformité

```python
# Compliance violations
violations = scenarios[scenarios["compliant"] == False]
print(f"Compliance violations: {len(violations)}/{len(scenarios)}")
print("\nViolation details:")
print(violations[["scenario_id", "agent", "auth_flow", "risk_level", "description"]].to_string(index=False))
```

**Sortie attendue :**

```
Compliance violations: 4/15

Violation details:
scenario_id          agent          auth_flow risk_level                                          description
        S05      MailAgent  client_credentials   critical  Read all users' mail with app-level permissions
        S07      FileAgent  client_credentials   critical  Access all SharePoint sites without user context
        S10   CalendarAgent  client_credentials   critical  Modify any user's calendar without delegation
        S14      AdminAgent  client_credentials       high  Directory read with app permissions instead of OBO
```

!!! warning "Constatation critique"
    Les 4 violations de conformité utilisent **client_credentials** — pas OBO. Trois sont à risque critique (S05, S07, S10) car elles accordent un accès large aux données de tous les utilisateurs. Le schéma est clair : client_credentials sans restriction de portée crée des violations de conformité.

```python
# Verify: do all violations use client_credentials?
violation_flows = violations["auth_flow"].unique().tolist()
print(f"\nAuth flows in violations: {violation_flows}")
print(f"All violations use client_credentials: {violation_flows == ['client_credentials']}")
```

**Sortie attendue :**

```
Auth flows in violations: ['client_credentials']
All violations use client_credentials: True
```

---

## Partie 4 : Analyse du niveau de risque

### Étape 4 : Analyser la distribution des risques

```python
# Risk level distribution
print("Risk level distribution:")
for level in ["low", "medium", "high", "critical"]:
    count = len(scenarios[scenarios["risk_level"] == level])
    if count > 0:
        print(f"  {level:>8}: {count}")

# Critical-risk scenarios
critical = scenarios[scenarios["risk_level"] == "critical"]
print(f"\nCritical-risk scenarios: {len(critical)}")
print(critical[["scenario_id", "agent", "auth_flow", "description"]].to_string(index=False))
```

**Sortie attendue :**

```
Risk level distribution:
      low: 5
   medium: 4
     high: 3
 critical: 3

Critical-risk scenarios: 3
scenario_id          agent          auth_flow                                          description
        S05      MailAgent  client_credentials  Read all users' mail with app-level permissions
        S07      FileAgent  client_credentials  Access all SharePoint sites without user context
        S10   CalendarAgent  client_credentials  Modify any user's calendar without delegation
```

!!! info "Schéma de risque"
    Les 3 scénarios à risque critique impliquent des agents avec **client_credentials accédant aux données utilisateur** (e-mails, fichiers, calendrier) sans contexte utilisateur. Le scénario client_credentials de l'AdminAgent (S14) est à haut risque mais pas critique car les lectures d'annuaire sont moins sensibles que l'accès aux données individuelles des utilisateurs.

---

## Partie 5 : Analyse du flux OBO

### Étape 5 : Taux d'adoption OBO

```python
# OBO vs client_credentials
obo_count = len(scenarios[scenarios["auth_flow"] == "obo"])
total = len(scenarios)
obo_pct = obo_count / total * 100

print(f"OBO flow: {obo_count}/{total} = {obo_pct:.1f}%")
print(f"Client credentials: {total - obo_count}/{total} = {(total - obo_count)/total*100:.1f}%")

# OBO by agent
print("\nOBO usage by agent:")
for agent in scenarios["agent"].unique():
    agent_data = scenarios[scenarios["agent"] == agent]
    agent_obo = len(agent_data[agent_data["auth_flow"] == "obo"])
    agent_total = len(agent_data)
    print(f"  {agent:>15}: {agent_obo}/{agent_total} OBO")
```

**Sortie attendue :**

```
OBO flow: 11/15 = 73.3%
Client credentials: 4/15 = 26.7%

OBO usage by agent:
      MailAgent: 4/5 OBO
      FileAgent: 3/4 OBO
  CalendarAgent: 2/4 OBO
     AdminAgent: 2/3 OBO
```

73,3 % des scénarios utilisent OBO — c'est bien, mais les 26,7 % utilisant client_credentials représentent **toutes** les violations de conformité. Chaque agent a au moins un scénario client_credentials qui devrait être révisé.

---

## Partie 6 : Stratégie de remédiation

### Étape 6 : Corriger les violations de conformité

Pour chaque violation, la remédiation consiste à passer de client_credentials à OBO :

| Scénario | Actuel | Correction | Notes |
|----------|--------|------------|-------|
| S05 | L'application lit tous les e-mails | OBO — lire uniquement les e-mails de l'utilisateur demandeur | Élimine l'accès aux données inter-utilisateurs |
| S07 | L'application accède à tout SharePoint | OBO — accéder uniquement aux sites autorisés de l'utilisateur | Respecte les permissions des sites |
| S10 | L'application modifie n'importe quel calendrier | OBO — modifier uniquement le calendrier propre de l'utilisateur | Empêche la modification inter-utilisateurs |
| S14 | Lecture d'annuaire par l'application | OBO — lecture d'annuaire en tant qu'utilisateur | Limite la portée à la vue d'annuaire de l'utilisateur |

```python
# Compliance improvement after remediation
compliant_count = scenarios["compliant"].sum()
total = len(scenarios)
print(f"Current compliance: {compliant_count}/{total} = {compliant_count/total*100:.1f}%")
print(f"After remediation:  {total}/{total} = 100.0%")
print(f"\nAction: Convert {total - compliant_count} client_credentials scenarios to OBO")
```

### Étape 7 : Human-in-the-loop pour les actions à haut risque

Même avec OBO, certaines actions justifient une approbation explicite de l'utilisateur :

```python
# High-risk + medium scenarios that should have human-in-the-loop
hitl_candidates = scenarios[scenarios["risk_level"].isin(["high", "critical", "medium"])]
print(f"Scenarios needing human-in-the-loop review: {len(hitl_candidates)}")
print(hitl_candidates[["scenario_id", "agent", "risk_level", "description"]].to_string(index=False))
```

!!! info "Défense en profondeur"
    OBO + moindre privilège + human-in-the-loop forment trois couches de défense. OBO garantit la bonne identité. Le moindre privilège limite ce que cette identité peut faire. Le human-in-the-loop ajoute une étape de confirmation pour les actions sensibles — même si l'agent a la permission, l'utilisateur approuve explicitement.

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-063/broken_identity.py` contient **3 bugs** dans les fonctions d'analyse d'identité. Exécutez les auto-tests :

```bash
python lab-063/broken_identity.py
```

Vous devriez voir **3 tests échoués** :

| Test | Ce qu'il vérifie | Indice |
|------|-------------------|--------|
| Test 1 | Nombre de violations de conformité | Comptez-vous `compliant == True` au lieu de `compliant == False` ? |
| Test 2 | Nombre de risques critiques | Filtrez-vous sur `risk_level == "high"` au lieu de `risk_level == "critical"` ? |
| Test 3 | Pourcentage OBO | Filtrez-vous sur `auth_flow == "client_credentials"` au lieu de `auth_flow == "obo"` ? |

Corrigez les 3 bugs et relancez jusqu'à voir `🎉 All 3 tests passed`.

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quel est l'objectif du flux OAuth 2.0 On-Behalf-Of (OBO) ?"

    - A) Donner aux agents leur propre identité indépendante avec un accès administrateur complet
    - B) Transmettre l'identité de l'utilisateur à travers la chaîne d'agents pour que l'agent agisse en tant qu'utilisateur
    - C) Contourner entièrement l'authentification pour une exécution plus rapide des agents
    - D) Créer un nouveau compte utilisateur pour chaque instance d'agent

    ??? success "✅ Révéler la réponse"
        **Correct : B) Transmettre l'identité de l'utilisateur à travers la chaîne d'agents pour que l'agent agisse en tant qu'utilisateur**

        Le flux OBO échange le jeton de l'utilisateur contre un jeton d'API en aval, préservant l'identité et les permissions de l'utilisateur. L'agent agit **en tant que** l'utilisateur — il ne peut accéder qu'à ce que l'utilisateur peut accéder. C'est le fondement de l'identité d'agent à moindre privilège : l'agent hérite de la portée d'autorisation de l'utilisateur, et non d'une portée large au niveau de l'application.

??? question "**Q2 (Choix multiple) :** Quelle est la différence clé entre les permissions déléguées et les permissions d'application ?"

    - A) Les permissions déléguées sont plus rapides ; les permissions d'application sont plus précises
    - B) Les permissions déléguées agissent en tant qu'utilisateur connecté ; les permissions d'application agissent en tant que l'application elle-même
    - C) Les permissions déléguées ne nécessitent aucune authentification ; les permissions d'application nécessitent OAuth
    - D) Il n'y a pas de différence pratique — elles sont interchangeables

    ??? success "✅ Révéler la réponse"
        **Correct : B) Les permissions déléguées agissent en tant qu'utilisateur connecté ; les permissions d'application agissent en tant que l'application elle-même**

        Avec les **permissions déléguées** (OBO), l'agent agit en tant qu'utilisateur — il peut lire les e-mails propres de l'utilisateur mais pas ceux des autres utilisateurs. Avec les **permissions d'application** (client_credentials), l'agent agit en son propre nom avec un accès au niveau de l'application — il pourrait lire les e-mails de TOUS les utilisateurs. Cette distinction est critique : les 4 violations de conformité dans le benchmark utilisent des permissions d'application là où des permissions déléguées auraient dû être utilisées.

??? question "**Q3 (Exécuter le lab) :** Combien de violations de conformité existent dans les 15 scénarios ?"

    Calculez `(scenarios["compliant"] == False).sum()`.

    ??? success "✅ Révéler la réponse"
        **4 violations (S05, S07, S10, S14)**

        Quatre scénarios sont non conformes : S05 (MailAgent lit les e-mails de tous les utilisateurs), S07 (FileAgent accède à tout SharePoint), S10 (CalendarAgent modifie n'importe quel calendrier), et S14 (AdminAgent lecture d'annuaire avec permissions d'application). Les quatre utilisent client_credentials au lieu d'OBO, accordant un accès plus large que nécessaire.

??? question "**Q4 (Exécuter le lab) :** Combien de scénarios sont classés comme risque critique ?"

    Calculez `(scenarios["risk_level"] == "critical").sum()`.

    ??? success "✅ Révéler la réponse"
        **3 scénarios (S05, S07, S10)**

        Trois scénarios sont à risque critique : S05 (MailAgent), S07 (FileAgent) et S10 (CalendarAgent). Les trois impliquent des agents utilisant client_credentials pour accéder aux données utilisateur (e-mails, fichiers, calendrier) sans contexte utilisateur. S14 (AdminAgent) est à haut risque mais pas critique car les lectures d'annuaire sont moins sensibles que l'accès aux données personnelles individuelles des utilisateurs.

??? question "**Q5 (Exécuter le lab) :** Quel pourcentage de scénarios utilise le flux OBO ?"

    Calculez `(scenarios["auth_flow"] == "obo").sum() / len(scenarios) * 100`.

    ??? success "✅ Révéler la réponse"
        **73,3 % (11/15)**

        11 des 15 scénarios utilisent OBO — une solide majorité, mais les 4 restants (26,7 %) utilisant client_credentials représentent toutes les violations de conformité. Le chemin de remédiation est clair : convertir les 4 scénarios client_credentials en OBO, portant la conformité de 73,3 % à 100 %. Chaque agent (MailAgent, FileAgent, CalendarAgent, AdminAgent) a au moins un scénario nécessitant une conversion.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-------------------------|
| Flux OBO | Transmet l'identité de l'utilisateur à travers la chaîne d'agents — l'agent agit en tant qu'utilisateur |
| Déléguées vs Application | Déléguées = portée utilisateur ; Application = portée à l'échelle de l'application |
| Conformité | 4/15 violations — toutes provenant de client_credentials, pas d'OBO |
| Niveaux de risque | 3 scénarios à risque critique — tous client_credentials accédant aux données utilisateur |
| Adoption OBO | 73,3 % OBO — les 26,7 % client_credentials causent toutes les violations |
| Remédiation | Convertir client_credentials en OBO ; ajouter le human-in-the-loop pour le haut risque |

---

## Prochaines étapes

- **[Lab 062](lab-062-ondevice-phi-silica.md)** — Agents on-device avec Phi Silica (confidentialité via l'inférence sur appareil)
- **[Lab 061](lab-061-slm-phi4-mini.md)** — SLMs avec Phi-4 Mini (une autre approche de l'IA axée sur la confidentialité)
- **[Lab 042](lab-042-enterprise-rag.md)** — RAG d'entreprise (application des contrôles d'identité à la récupération de données)
