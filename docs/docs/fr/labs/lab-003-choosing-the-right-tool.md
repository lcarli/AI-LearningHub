---
tags: [free, beginner, no-account-needed, awareness]
---
# Lab 003 : Choisir le bon outil

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~15 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Aucun compte requis</span>
</div>

## Ce que vous apprendrez

- Un cadre de décision pratique pour choisir votre outil d'agent IA
- Comprendre les compromis clés (contrôle vs simplicité, coût vs puissance)
- Des parcours d'apprentissage suggérés en fonction de votre rôle et de vos objectifs

---

## Introduction

Après avoir examiné le paysage dans le [Lab 002](lab-002-agent-landscape.md), la question naturelle est : **par où commencer ?**

Utilisez l'organigramme de décision et les guides par rôle ci-dessous pour trouver votre chemin.

---

## Organigramme de décision

![Organigramme de décision](../../assets/diagrams/decision-flowchart.svg)

??? question "🤔 Vérifiez votre compréhension"
    Selon l'organigramme de décision, quel outil devriez-vous utiliser si votre objectif principal est de connecter une base de données ou une API existante aux agents IA ?

    ??? success "Réponse"
        Vous devriez **construire un serveur MCP**. MCP (Model Context Protocol) fournit un standard de connecteur universel pour que tout agent IA compatible MCP puisse accéder à votre outil ou source de données via une interface commune.

---

## Par rôle

### 🎯 Analyste métier / Utilisateur avancé
**Objectif :** Automatiser les flux de travail, créer des agents sans écrire de code.

Parcours recommandé :
1. [Lab 001](lab-001-what-are-ai-agents.md) → [Lab 011](lab-011-copilot-studio-first-agent.md) → [Lab 024](lab-024-teams-ai-library.md)

**Outils :** Copilot Studio, Power Automate, M365 Copilot

---

### 👨‍💻 Développeur (Python / C#)
**Objectif :** Écrire des agents en code, intégrer avec les systèmes existants.

Parcours recommandé :
1. [Lab 013](lab-013-github-models.md) → [Lab 014](lab-014-sk-hello-agent.md) → [Lab 020](lab-020-mcp-server-python.md) → [Lab 030](lab-030-foundry-agent-mcp.md)

**Outils :** Semantic Kernel, Microsoft Foundry, MCP

---

### 🔌 Ingénieur intégration / Plateforme
**Objectif :** Exposer les systèmes existants (bases de données, API) aux agents IA.

Parcours recommandé :
1. [Lab 012](lab-012-what-is-mcp.md) → [Lab 020](lab-020-mcp-server-python.md) → [Lab 031](lab-031-pgvector-semantic-search.md) → [Lab 032](lab-032-row-level-security.md)

**Outils :** MCP, PostgreSQL + pgvector, Row Level Security

---

### 🏗️ Architecte solution / Ingénieur senior
**Objectif :** Concevoir des systèmes multi-agents de production avec gouvernance et observabilité.

Parcours recommandé :
1. [Lab 030](lab-030-foundry-agent-mcp.md) → [Lab 033](lab-033-agent-observability.md) → [Lab 034](lab-034-multi-agent-sk.md) → [Lab 040](lab-040-autogen-multi-agent.md)

**Outils :** Foundry, Semantic Kernel, AutoGen, App Insights

---

### 🎓 Étudiant / Apprenant
**Objectif :** Comprendre les agents IA et construire quelque chose de concret, gratuitement.

Parcours recommandé :
1. [Lab 001](lab-001-what-are-ai-agents.md) → [Lab 002](lab-002-agent-landscape.md) → [Lab 013](lab-013-github-models.md) → [Lab 014](lab-014-sk-hello-agent.md) → [Lab 022](lab-022-rag-github-models-pgvector.md)

**Outils :** GitHub Models, Semantic Kernel — tout est gratuit !

??? question "🤔 Vérifiez votre compréhension"
    Un architecte solution doit concevoir un système multi-agents de production avec observabilité et gouvernance. Quelle combinaison d'outils ce lab recommande-t-il ?

    ??? success "Réponse"
        **Foundry, Semantic Kernel, AutoGen et App Insights.** Le parcours d'apprentissage recommandé est : Foundry Agent MCP → Observabilité des agents → Multi-Agent SK → AutoGen Multi-Agent. Cela couvre le runtime géré, la logique d'agent, l'orchestration multi-agent et le monitoring.

??? question "🤔 Vérifiez votre compréhension"
    Que signifie « plus de contrôle = plus de responsabilité » dans le compromis contrôle vs simplicité ?

    ??? success "Réponse"
        Les outils pro-code comme AutoGen et Semantic Kernel vous donnent une **flexibilité totale** sur la logique de l'agent, mais vous devez gérer plus de choses vous-même — gestion des erreurs, déploiement, sécurité, mise à l'échelle. Les outils no-code comme Copilot Studio sont **plus rapides à construire** mais moins personnalisables. Le bon choix dépend des compétences de votre équipe et de vos exigences.

---

## Les deux compromis clés

![Contrôle vs Simplicité, Gratuit vs Payant](../../assets/diagrams/tradeoffs-control-cost.svg)

Plus de contrôle = plus de flexibilité + plus de responsabilité.  
Plus de simplicité = plus rapide à construire + moins personnalisable.

??? question "🤔 Vérifiez votre compréhension"
    Un étudiant sans abonnement Azure et sans budget peut-il quand même construire un agent IA fonctionnel en utilisant les outils de ce hub ?

    ??? success "Réponse"
        **Oui !** GitHub Models et Semantic Kernel sont entièrement gratuits. Les labs conceptuels L50 et les labs L100–L200 utilisant GitHub Models ne nécessitent aucun abonnement Azure. Les étudiants peuvent construire de vrais agents, exécuter des serveurs MCP localement et apprendre le cycle complet de développement d'agents à coût zéro.

### 2. Gratuit vs. Payant

Le SVG ci-dessus inclut la comparaison complète Gratuit vs. Payant. Commencez gratuit → ajoutez Azure uniquement quand vous avez besoin de fonctionnalités de production.

---

## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Un développeur veut construire une extension VS Code qui répond à `@mybot` dans GitHub Copilot Chat. Quel outil/API devrait-il utiliser ?"

    - A) Copilot Studio
    - B) VS Code Chat Participant API (Lab 025)
    - C) Microsoft Foundry Agent Service
    - D) Azure Bot Service

    ??? success "✅ Voir la réponse"
        **Correct : B — VS Code Chat Participant API**

        La Chat Participant API enregistre un participant `@yourextension` directement dans l'interface Copilot Chat de VS Code. Elle s'exécute entièrement dans VS Code — pas d'abonnement Azure, pas de serveur requis. Copilot Studio est pour les agents Teams/M365 sans code. Foundry est pour les agents hébergés côté serveur avec une échelle cloud complète.

??? question "**Q2 (Choix multiple) :** Quel facteur est LE PLUS important lorsqu'on choisit entre Copilot Studio et Semantic Kernel ?"

    - A) Le langage de programmation que vous préférez (Python vs C#)
    - B) Si vous avez besoin d'un déploiement cloud ou local
    - C) Votre rôle et le niveau de contrôle du code dont vous avez besoin — développeur citoyen vs développeur professionnel
    - D) Le fournisseur de LLM (OpenAI vs Anthropic)

    ??? success "✅ Voir la réponse"
        **Correct : C**

        L'axe de décision principal est le **contrôle du code vs la rapidité**. Copilot Studio cible les développeurs citoyens et les professionnels IT qui ont besoin d'un agent fonctionnel rapidement sans code. Semantic Kernel cible les développeurs professionnels qui ont besoin d'un contrôle total sur la logique, les schémas d'outils, les modèles de mémoire et le comportement en production. Les deux prennent en charge plusieurs LLM et le déploiement cloud.

??? question "**Q3 (Choix multiple) :** Le principe du « moindre privilège » stipule que votre agent ne doit avoir accès qu'à ce dont il a besoin — rien de plus. Lequel des choix suivants viole le moindre privilège ?"

    - A) Un agent de recherche de produits qui peut appeler `search_products()` et `get_product_details()`
    - B) Un agent de service client avec un accès en lecture seule à la base de données
    - C) Un agent de suivi de commandes avec des identifiants administrateur complets sur la base de données des commandes
    - D) Un agent météo qui ne peut appeler que l'API météo publique

    ??? success "✅ Voir la réponse"
        **Correct : C — Les identifiants administrateur complets violent le moindre privilège**

        Un agent de suivi de commandes n'a besoin que de *lire* les enregistrements de commandes. Lui donner des identifiants administrateur signifie qu'une attaque par injection de prompt ou une erreur logique pourrait supprimer des commandes, modifier des prix ou accéder à toutes les données clients. La bonne configuration est un utilisateur de base de données en lecture seule limité aux tables spécifiques dont l'agent a besoin. Les options A, B et D respectent toutes correctement le moindre privilège.

---

## Résumé

Il n'y a pas un seul « bon » outil — cela dépend de votre rôle, de vos objectifs et de vos contraintes. La bonne nouvelle : **tout dans ce hub commence gratuitement**, et vous pouvez toujours monter en niveau. Le cadre de décision ci-dessus vous oriente vers le chemin le plus efficace.

---

## Prochaines étapes

Choisissez votre parcours et lancez-vous !

- **Parcours no-code :** → [Lab 011 — Copilot Studio](lab-011-copilot-studio-first-agent.md)
- **Parcours développeur (gratuit) :** → [Lab 013 — GitHub Models](lab-013-github-models.md)
- **Parcours MCP :** → [Lab 012 — Qu'est-ce que MCP ?](lab-012-what-is-mcp.md)
- **Parcours Azure complet :** → [Lab 030 — Foundry + MCP](lab-030-foundry-agent-mcp.md)
- **Vous voulez d'abord comprendre les LLM ?** → [Lab 004 — Comment fonctionnent les LLM](lab-004-how-llms-work.md)
