---
tags: [free, beginner, no-account-needed, awareness]
---
# Lab 002 : Panorama des agents IA 2025

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~20 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Aucun compte requis</span>
</div>

## Ce que vous apprendrez

- L'écosystème Microsoft des agents IA en un coup d'œil
- Quand utiliser chaque plateforme : Copilot Studio, Microsoft Foundry, Semantic Kernel, Teams AI Library, AutoGen
- Comment MCP s'intègre dans tout cela
- Le spectre du no-code au pro-code

---

## Introduction

L'écosystème Microsoft propose plusieurs façons complémentaires de créer des agents IA. Cela peut être déroutant — faut-il utiliser Copilot Studio ou Foundry ? Semantic Kernel ou LangChain ? MCP ou des appels API directs ?

Ce lab vous fournit une **carte du paysage** pour faire des choix éclairés.

---

## Le spectre : No-Code → Pro-Code

![Spectre No-Code à Pro-Code](../../assets/diagrams/nocode-procode-spectrum.svg)

Il n'y a pas de « meilleur » côté — cela dépend de votre cas d'usage, des compétences de votre équipe et de vos exigences de gouvernance.

---

## Comparaison des plateformes

### 🤖 GitHub Copilot

| | |
|---|---|
| **Ce que c'est** | Assistant de codage IA intégré à votre IDE et à GitHub |
| **Idéal pour** | Développeurs individuels, productivité du codage |
| **Capacité d'agent** | Copilot Chat, GitHub Models, Copilot Extensions |
| **Compétence requise** | Faible (chat) à Élevée (extensions) |
| **Coût** | Niveau gratuit disponible |

### 🎨 Copilot Studio (Low-Code)

| | |
|---|---|
| **Ce que c'est** | Le créateur d'agents no-code/low-code de Microsoft |
| **Idéal pour** | Analystes métier, utilisateurs M365, agents Teams |
| **Capacité d'agent** | Flux de sujets, connecteurs, actions personnalisées, Azure OpenAI |
| **Compétence requise** | Faible — aucun codage requis |
| **Coût** | Inclus dans de nombreuses licences M365 ; essai gratuit disponible |

### 🏭 Microsoft Foundry Agent Service

| | |
|---|---|
| **Ce que c'est** | Runtime d'agent géré sur Azure |
| **Idéal pour** | Agents en production, échelle entreprise |
| **Capacité d'agent** | Appel d'outils, Code Interpreter, serveurs MCP, évaluation |
| **Compétence requise** | Moyenne — SDK Python ou C# |
| **Coût** | Abonnement Azure (niveau gratuit pour le prototypage) |

### 🧠 Semantic Kernel

| | |
|---|---|
| **Ce que c'est** | SDK d'agent open-source (Python / C# / Java) |
| **Idéal pour** | Développeurs souhaitant contrôler le code avec la pile Microsoft |
| **Capacité d'agent** | Plugins, mémoire vectorielle, planificateurs, multi-agent |
| **Compétence requise** | Moyenne — expérience Python ou C# |
| **Coût** | Gratuit (open-source) ; les coûts LLM dépendent du backend |

### ⚙️ AutoGen

| | |
|---|---|
| **Ce que c'est** | Framework multi-agent open-source de Microsoft Research |
| **Idéal pour** | Flux de travail multi-agents complexes, recherche, orchestration |
| **Capacité d'agent** | Conversations imbriquées, humain dans la boucle, exécution de code |
| **Compétence requise** | Élevée — Python, concepts avancés d'agents |
| **Coût** | Gratuit (open-source) ; coûts LLM |

### 👥 Teams AI Library

| | |
|---|---|
| **Ce que c'est** | SDK pour créer des bots Teams alimentés par l'IA |
| **Idéal pour** | Applications natives Teams, collaboration en entreprise |
| **Capacité d'agent** | IA conversationnelle dans les canaux Teams, accès aux données M365 |
| **Compétence requise** | Moyenne — Node.js ou C# |
| **Coût** | SDK gratuit ; nécessite un tenant M365 |

??? question "🤔 Vérifiez votre compréhension"
    Quelle est la différence clé entre Copilot Studio et Semantic Kernel en termes de public cible ?

    ??? success "Réponse"
        **Copilot Studio** est conçu pour les **développeurs citoyens et analystes métier** qui ont besoin d'un outil de création d'agents no-code/low-code. **Semantic Kernel** est conçu pour les **développeurs professionnels** (Python/C#) qui souhaitent un contrôle total du code sur la logique de l'agent, les plugins et la mémoire.

---

## Où s'intègre MCP ?

**Model Context Protocol (MCP)** n'est pas une plateforme — c'est un **standard de connecteur**. Pensez-y comme le USB-C des outils IA : une interface standard unique que tout agent peut utiliser pour se connecter à n'importe quelle source de données ou outil.

![Où s'intègre MCP](../../assets/diagrams/mcp-fit-overview.svg)

MCP fonctionne avec **toutes les plateformes ci-dessus** — et aussi avec Claude Desktop, OpenAI et tout autre hôte compatible MCP.

??? question "🤔 Vérifiez votre compréhension"
    MCP est décrit comme « USB-C pour les outils IA ». Quel problème spécifique cette analogie met-elle en évidence que MCP résout ?

    ??? success "Réponse"
        MCP résout le **problème d'intégration N×M**. Sans MCP, connecter 5 agents à 5 outils nécessite 25 intégrations personnalisées. Avec MCP comme standard universel, chaque outil publie un serveur MCP et chaque agent compatible MCP peut s'y connecter — réduisant les intégrations à N+M.

---

## Aide-mémoire de décision

| Situation | Outil recommandé |
|-----------|-----------------|
| « Je veux un agent dans Teams pour mon équipe, sans coder » | Copilot Studio |
| « Je veux ajouter l'IA à mon extension VS Code » | VS Code Chat Participant API |
| « Je veux un agent en production adossé à Azure, avec monitoring » | Microsoft Foundry Agent Service |
| « Je veux écrire du code Python/C# pour construire un agent sophistiqué » | Semantic Kernel |
| « Je veux que plusieurs agents IA collaborent sur des tâches complexes » | AutoGen |
| « Je veux connecter mon outil/API existant à n'importe quel agent IA » | Construire un serveur MCP |
| « Je veux juste expérimenter gratuitement avec des LLM » | GitHub Models |

??? question "🤔 Vérifiez votre compréhension"
    Un développeur veut construire un système où un agent « chercheur », un agent « rédacteur » et un agent « réviseur » collaborent pour produire un rapport. Quel outil Microsoft est le mieux adapté ?

    ??? success "Réponse"
        **AutoGen.** Il est spécifiquement conçu pour orchestrer **plusieurs agents spécialisés** qui collaborent sur des tâches complexes via des conversations imbriquées. Semantic Kernel excelle dans la construction d'agents individuels sophistiqués, tandis qu'AutoGen excelle dans la coordination multi-agent.

---

## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Vous êtes un développeur citoyen sans expérience en codage. Vous devez créer un chatbot Teams qui répond aux questions de politique RH depuis SharePoint. Quel outil devriez-vous choisir ?"

    - A) AutoGen
    - B) Semantic Kernel
    - C) Copilot Studio
    - D) Microsoft Foundry Agent Service

    ??? success "✅ Voir la réponse"
        **Correct : C — Copilot Studio**

        Copilot Studio est l'option **no-code/low-code** conçue pour les développeurs citoyens et les professionnels IT. Il s'intègre nativement avec Teams et Microsoft 365, peut pointer vers SharePoint comme source de connaissances, et ne nécessite aucun code. AutoGen et Semantic Kernel nécessitent des compétences de développement Python/C#. Foundry est pour les développeurs construisant des backends personnalisés.

??? question "**Q2 (Choix multiple) :** Que résout MCP (Model Context Protocol) dans l'écosystème des agents IA ?"

    - A) Il fournit un créateur visuel d'agents sans codage
    - B) Il optimise l'utilisation des tokens LLM pour réduire les coûts d'API
    - C) Il définit un standard universel pour que tout agent puisse se connecter à n'importe quel outil/source de données via une interface commune
    - D) Il gère l'authentification et le contrôle d'accès basé sur les rôles pour les agents

    ??? success "✅ Voir la réponse"
        **Correct : C**

        MCP est décrit comme « USB-C pour les outils IA » — un standard de connecteur universel. Sans MCP, connecter 5 agents à 5 outils nécessite 25 intégrations personnalisées. Avec MCP, chaque outil publie un serveur MCP et chaque agent compatible MCP peut l'utiliser. Il résout le problème d'intégration N×M dans tout l'écosystème.

??? question "**Q3 (Choix multiple) :** Quelle est la différence principale entre Semantic Kernel et AutoGen ?"

    - A) Semantic Kernel est open-source ; AutoGen est propriétaire Microsoft
    - B) Semantic Kernel construit des agents individuels sophistiqués avec des plugins ; AutoGen orchestre plusieurs agents spécialisés collaborant sur des tâches complexes
    - C) AutoGen ne fonctionne qu'avec GPT-4o ; Semantic Kernel prend en charge n'importe quel LLM
    - D) Semantic Kernel est uniquement pour Python ; AutoGen prend en charge Python et C#

    ??? success "✅ Voir la réponse"
        **Correct : B**

        **Semantic Kernel** excelle dans la construction d'un agent unique très capable — avec des plugins, de la mémoire, des planificateurs et une utilisation structurée des outils. **AutoGen** excelle dans l'orchestration de *plusieurs* agents — un agent chercheur, un agent rédacteur, un agent réviseur — chacun effectuant une sous-tâche spécialisée et passant les résultats entre eux. Les deux sont open-source et prennent en charge plusieurs LLM.

---

## Résumé

L'écosystème Microsoft dispose d'outils pour **chaque niveau de compétence et cas d'usage** — du Copilot Studio no-code à AutoGen pro-code. MCP est le connecteur universel qui fonctionne avec tous. Dans le prochain lab, nous vous aiderons à choisir le bon outil pour votre situation spécifique.

---

## Prochaines étapes

→ **[Lab 003 : Choisir le bon outil](lab-003-choosing-the-right-tool.md)**
