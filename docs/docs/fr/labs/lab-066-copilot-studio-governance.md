---
tags: [copilot-studio, governance, dlp, power-platform, enterprise]
---
# Lab 066 : Gouvernance d'entreprise avec Copilot Studio

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~75 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Données simulées (aucune licence Copilot Studio requise)</span>
</div>

## Ce que vous apprendrez

- Comment **auditer les agents Copilot Studio** à travers un locataire Power Platform
- Appliquer des **stratégies DLP** sur les connecteurs et les flux de données des agents
- Détecter les **agents non gouvernés** créés en dehors des environnements gérés par l'IT
- Appliquer la **sécurité au niveau de l'environnement** pour isoler les agents de production
- Identifier les **lacunes de conformité** entre les agents développés par les utilisateurs métier et ceux gérés par l'IT
- Créer un **tableau de bord de gouvernance** résumant la posture des agents

!!! abstract "Prérequis"
    Complétez d'abord le **[Lab 065 : Purview DSPM for AI](lab-065-purview-dspm-ai.md)**. Ce lab suppose une familiarité avec les concepts de gouvernance des données et les fondamentaux des stratégies DLP.

## Introduction

Lorsque les organisations adoptent **Microsoft Copilot Studio**, les développeurs citoyens et les développeurs professionnels créent des agents à travers la Power Platform. Sans gouvernance adéquate, les agents prolifèrent sans contrôle — se connectant à des sources de données sensibles, contournant les stratégies DLP et fonctionnant sans piste d'audit.

**La gouvernance d'entreprise de Copilot Studio** répond à ces défis :

- Quels agents existent et qui les a créés ?
- Les agents respectent-ils les **stratégies DLP** organisationnelles ?
- Les agents fonctionnent-ils dans des **environnements gérés** ou des bacs à sable personnels ?
- Quels agents ont **échoué aux analyses de sécurité** ?

| Capacité de gouvernance | Ce qu'elle fait | Exemple |
|------------------------|----------------|---------|
| **Inventaire des agents** | Catalogue tous les agents du locataire | 12 agents dans 4 environnements |
| **Application DLP** | Évalue l'utilisation des connecteurs par rapport aux règles DLP | Bloquer les agents utilisant des API externes non approuvées |
| **Analyse de sécurité** | Détecte les mauvaises configurations et vulnérabilités | Agent exposant une base de connaissances interne sans authentification |
| **Isolation des environnements** | Sépare les agents dev/test/prod | Agents de production verrouillés dans les environnements gérés par l'IT |
| **Gouvernance des créateurs** | Suit les agents créés par les utilisateurs métier vs l'IT | Signaler les agents développés par les utilisateurs métier non révisés |

### Le scénario

Vous êtes un **administrateur Power Platform** chargé d'auditer tous les agents Copilot Studio de votre locataire. L'organisation compte **12 agents** créés par différentes équipes. Certains ont été créés par l'IT, d'autres par des développeurs citoyens. Votre mission : identifier les agents non gouvernés, signaler les violations DLP et produire un rapport de gouvernance.

---

## Prérequis

| Exigence | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| `pandas` | Analyser les données d'inventaire des agents |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-066/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `broken_governance.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-066/broken_governance.py) |
| `studio_agents.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-066/studio_agents.csv) |

---

## Étape 1 : Comprendre la gouvernance de Copilot Studio

La gouvernance de Copilot Studio fonctionne à travers plusieurs couches :

```
Tenant Admin Center → Environment Management → DLP Policies → Agent Inventory
                                                                     ↓
Governance Report ← Security Scan ← Connector Audit ←──────── Agent Config
```

Chaque agent est évalué selon :

1. **Classification de l'environnement** — L'agent est-il dans un environnement géré ou par défaut ?
2. **Conformité aux stratégies DLP** — L'agent utilise-t-il uniquement des connecteurs approuvés ?
3. **Statut de l'analyse de sécurité** — L'agent a-t-il réussi les vérifications de sécurité automatisées ?
4. **Type de créateur** — A-t-il été créé par l'IT ou par un développeur citoyen ?

!!! info "Agents citoyens vs agents gérés par l'IT"
    Les agents développés par les citoyens sont créés par des utilisateurs métier à l'aide d'outils low-code. Bien qu'ils accélèrent l'innovation, ils manquent souvent de revues de sécurité, de gestion d'erreurs appropriée et de contrôles de conformité. La gouvernance garantit que ces agents respectent les mêmes standards que ceux gérés par l'IT.

---

## Étape 2 : Charger et explorer l'inventaire des agents

Le jeu de données contient **12 agents Copilot Studio** à travers le locataire :

```python
import pandas as pd

agents = pd.read_csv("lab-066/studio_agents.csv")
print(f"Total agents: {len(agents)}")
print(f"Environments: {sorted(agents['environment'].unique())}")
print(f"Creator types: {sorted(agents['creator_type'].unique())}")
print(f"\nAgents per environment:")
print(agents.groupby("environment")["agent_id"].count().sort_values(ascending=False))
```

**Résultat attendu :**

```
Total agents: 12
Environments: ['Default', 'Development', 'Production', 'Sandbox']
Creator types: ['citizen', 'it_managed']
```

---

## Étape 3 : Vérification de la conformité aux stratégies DLP

Identifiez les agents qui violent les stratégies DLP :

```python
dlp_violations = agents[agents["dlp_compliant"] == False]
print(f"DLP non-compliant agents: {len(dlp_violations)}")
print(dlp_violations[["agent_id", "agent_name", "environment", "creator_type", "connector_count"]]
      .to_string(index=False))
```

**Résultat attendu :**

```
DLP non-compliant agents: 4
```

!!! warning "Risque lié aux connecteurs"
    Les agents non conformes utilisent généralement des connecteurs qui accèdent à des API externes ou à des sources de données en dehors de la liste approuvée de l'organisation. Chaque connecteur non approuvé représente un chemin potentiel d'exfiltration de données.

---

## Étape 4 : Analyse des scans de sécurité

Vérifiez quels agents ont échoué aux analyses de sécurité :

```python
failed_scans = agents[agents["security_scan"] == "failed"]
print(f"Failed security scans: {len(failed_scans)}")
print(failed_scans[["agent_id", "agent_name", "creator_type", "environment"]].to_string(index=False))

unprotected = agents[agents["authentication"] == "none"]
print(f"\nAgents without authentication: {len(unprotected)}")
print(unprotected[["agent_id", "agent_name", "environment"]].to_string(index=False))
```

**Résultat attendu :**

```
Failed security scans: 3

Agents without authentication: 3
```

!!! danger "Agents non protégés"
    Les agents sans authentification sont accessibles publiquement. N'importe quel utilisateur — ou attaquant externe — peut interagir avec eux. Ces agents doivent être immédiatement sécurisés ou désactivés.

---

## Étape 5 : Gouvernance des développeurs citoyens

Analysez la répartition entre les agents développés par les citoyens et ceux gérés par l'IT :

```python
citizen = agents[agents["creator_type"] == "citizen"]
it_managed = agents[agents["creator_type"] == "it_managed"]
print(f"Citizen-created agents: {len(citizen)}")
print(f"IT-managed agents: {len(it_managed)}")
print(f"\nCitizen agents by environment:")
print(citizen.groupby("environment")["agent_id"].count().sort_values(ascending=False))

citizen_noncompliant = citizen[citizen["dlp_compliant"] == False]
print(f"\nCitizen agents violating DLP: {len(citizen_noncompliant)}")
```

**Résultat attendu :**

```
Citizen-created agents: 8
IT-managed agents: 4
```

!!! tip "Aperçu de gouvernance"
    Les développeurs citoyens ont créé 8 agents sur 12 (67 %). Bien que cela démontre une forte adoption, les agents citoyens sont plus susceptibles de présenter des violations DLP et des échecs aux analyses de sécurité. Envisagez de mettre en place des workflows de révision obligatoires pour les agents créés par les citoyens avant qu'ils n'atteignent la production.

---

## Étape 6 : Tableau de bord de gouvernance

Combinez toutes les conclusions dans un résumé de gouvernance :

```python
dashboard = f"""
╔════════════════════════════════════════════════════════╗
║     Copilot Studio Governance Report                   ║
╠════════════════════════════════════════════════════════╣
║ Total Agents:                {len(agents):>5}                     ║
║ Citizen-Created:             {len(citizen):>5}                     ║
║ IT-Managed:                  {len(it_managed):>5}                     ║
║ DLP Non-Compliant:           {len(dlp_violations):>5}                     ║
║ Failed Security Scans:       {len(failed_scans):>5}                     ║
║ No Authentication:           {len(unprotected):>5}                     ║
║ Production Agents:           {len(agents[agents['environment'] == 'Production']):>5}                     ║
╚════════════════════════════════════════════════════════╝
"""
print(dashboard)
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-066/broken_governance.py` contient **3 bugs** dans la manière dont il analyse les données de gouvernance :

```bash
python lab-066/broken_governance.py
```

| Test | Ce qu'il vérifie | Indice |
|------|-----------------|--------|
| Test 1 | Nombre de violations DLP | Devrait filtrer `dlp_compliant == False`, pas `True` |
| Test 2 | Nombre d'agents citoyens | Devrait filtrer `creator_type == "citizen"`, pas `"it_managed"` |
| Test 3 | Pourcentage de scans échoués | Devrait filtrer `security_scan == "failed"`, pas `"passed"` |

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quel est le principal risque des agents Copilot Studio non gouvernés ?"

    - A) Ils consomment trop de ressources de calcul
    - B) Ils peuvent accéder à des données sensibles sans contrôles DLP, authentification ni pistes d'audit
    - C) Ils ralentissent la Power Platform
    - D) Ils empêchent l'IT de créer de nouveaux agents

    ??? success "✅ Révéler la réponse"
        **Correct : B) Ils peuvent accéder à des données sensibles sans contrôles DLP, authentification ni pistes d'audit**

        Les agents non gouvernés contournent les politiques de sécurité organisationnelles. Ils peuvent se connecter à des sources de données sensibles en utilisant des connecteurs non approuvés, fonctionner sans authentification et manquer de journalisation d'audit — créant des lacunes de conformité et des risques d'exfiltration de données.

??? question "**Q2 (Choix multiple) :** Pourquoi l'isolation des environnements est-elle importante pour la gouvernance de Copilot Studio ?"

    - A) Cela fait fonctionner les agents plus rapidement
    - B) Cela sépare les agents de développement, de test et de production pour appliquer différentes politiques de sécurité par étape du cycle de vie
    - C) Cela réduit les coûts de licence
    - D) Cela n'est nécessaire que pour les agents à code personnalisé

    ??? success "✅ Révéler la réponse"
        **Correct : B) Cela sépare les agents de développement, de test et de production pour appliquer différentes politiques de sécurité par étape du cycle de vie**

        L'isolation des environnements garantit que les agents expérimentaux dans les environnements bac à sable ne peuvent pas accéder aux données de production, et que les agents de production respectent des exigences plus strictes en matière de DLP, d'authentification et de révision. Sans isolation, le prototype d'un développeur citoyen pourrait accidentellement se connecter à des bases de données de production.

??? question "**Q3 (Exécuter le lab) :** Combien d'agents ont échoué aux analyses de sécurité ?"

    Filtrez le DataFrame des agents pour `security_scan == "failed"` et comptez les lignes.

    ??? success "✅ Révéler la réponse"
        **3 agents ont échoué aux analyses de sécurité**

        Ces agents présentaient des mauvaises configurations telles que l'absence d'authentification, des bases de connaissances internes exposées ou l'utilisation de connecteurs non approuvés. Les scans échoués nécessitent une remédiation immédiate avant que les agents puissent être promus en production.

??? question "**Q4 (Exécuter le lab) :** Combien d'agents n'ont pas d'authentification configurée ?"

    Filtrez pour `authentication == "none"` et comptez.

    ??? success "✅ Révéler la réponse"
        **3 agents n'ont pas d'authentification**

        Les agents sans authentification sont accessibles publiquement, ce qui signifie que toute personne disposant de l'URL du point de terminaison peut interagir avec eux. C'est une faille de sécurité critique qui doit être résolue en configurant Azure AD ou d'autres fournisseurs d'identité.

??? question "**Q5 (Exécuter le lab) :** Combien d'agents ont été créés par des développeurs citoyens ?"

    Filtrez pour `creator_type == "citizen"` et comptez.

    ??? success "✅ Révéler la réponse"
        **8 agents ont été créés par des développeurs citoyens**

        Les développeurs citoyens ont créé 8 des 12 agents au total (67 %). Bien que le développement citoyen accélère l'innovation, ces agents nécessitent une révision de gouvernance supplémentaire pour garantir la conformité DLP, une authentification appropriée et la réussite des analyses de sécurité avant le déploiement en production.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|------------------------|
| Inventaire des agents | Cataloguer et auditer tous les agents Copilot Studio à travers le locataire |
| Application DLP | Détecter les agents utilisant des connecteurs et sources de données non approuvés |
| Analyses de sécurité | Identifier les agents avec des scans de sécurité échoués et des mauvaises configurations |
| Isolation des environnements | Séparer dev/test/prod pour appliquer des politiques adaptées au cycle de vie |
| Gouvernance des créateurs | Suivre la création d'agents citoyens vs gérés par l'IT et les taux de conformité |
| Tableaux de bord de gouvernance | Créer des rapports de synthèse pour les parties prenantes exécutives et de conformité |

---

## Prochaines étapes

- **[Lab 065](lab-065-purview-dspm-ai.md)** — Purview DSPM for AI (gouvernance complémentaire des données)
- **[Lab 064](lab-064-securing-mcp-apim.md)** — Sécurisation de MCP avec APIM (sécurité au niveau de l'infrastructure)
- **[Lab 008](lab-008-responsible-ai.md)** — IA responsable (principes fondamentaux de gouvernance)