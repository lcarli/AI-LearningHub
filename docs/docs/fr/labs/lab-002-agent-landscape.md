---
tags: [free, beginner, no-account-needed, awareness]
---
# Laboratoire 002 : Paysage des agents IA 2025

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Temps :</strong> ~20 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Aucun compte requis</span>
</div>

## Ce que vous apprendrez

- L'écosystème des agents IA de Microsoft en un coup d'œil
- Quand utiliser chaque plateforme : Copilot Studio, Microsoft Foundry, Semantic Kernel, Teams AI Library, AutoGen
- Comment MCP s'intègre dans tout cela
- Le spectre du no-code au pro-code

---

## Introduction

L'écosystème Microsoft offre plusieurs façons de construire des agents IA qui se chevauchent. Cela peut être déroutant : devez-vous utiliser Copilot Studio ou Foundry ? Semantic Kernel ou LangChain ? MCP ou appels API directs ?

Ce laboratoire vous fournit une **carte du paysage** afin que vous puissiez faire des choix éclairés.

---

## Le Spectre : No-Code → Pro-Code

![Spectre No-Code à Pro-Code](../../assets/diagrams/nocode-procode-spectrum.svg)

Il n'y a pas de "meilleur" extrême — cela dépend de votre cas d'utilisation, des compétences de l'équipe et des exigences de gouvernance.

---

## Comparaison des plateformes

### 🤖 GitHub Copilot

| | |
|---|---|
| **Ce que c'est** | Assistant de codage IA intégré dans votre IDE et GitHub |
| **Idéal pour** | Développeurs individuels, productivité de codage |
| **Capacité de l'agent** | Copilot Chat, GitHub Models, Copilot Extensions |
| **Compétence requise** | Faible (chat) à Élevée (extensions) |
| **Coût** | Niveau gratuit disponible |

### 🎨 Copilot Studio (Low-Code)

| | |
|---|---|
| **Ce que c'est** | Constructeur d'agents sans code/low-code de Microsoft |
| **Idéal pour** | Analystes commerciaux, utilisateurs de M365, agents Teams |
| **Capacité de l'agent** | Flux de sujets, connecteurs, actions personnalisées, Azure OpenAI |
| **Compétence requise** | Faible — aucune programmation requise |
| **Coût** | Inclus avec de nombreuses licences M365 ; essai gratuit disponible |

### 🏭 Service d'agent Microsoft Foundry

| | |
|---|---|
| **Ce que c'est** | Exécution d'agent gérée sur Azure |
| **Idéal pour** | Agents de production, échelle d'entreprise |
| **Capacité de l'agent** | Appel d'outils, interpréteur de code, serveurs MCP, évaluation |
| **Compétence requise** | Moyenne — SDK Python ou C# |
| **Coût** | Abonnement Azure (niveau gratuit pour le prototypage) |

### 🧠 Semantic Kernel

| | |
|---|---|
| **Ce que c'est** | SDK d'agent open-source (Python / C# / Java) |
| **Idéal pour** | Développeurs qui souhaitent un contrôle total du code avec la pile Microsoft |
| **Capacité de l'agent** | Plugins, mémoire vectorielle, planificateurs, multi-agent |
| **Compétence requise** | Moyenne — expérience en Python ou C# |
| **Coût** | Gratuit (open-source) ; les coûts LLM dépendent du backend |

### ⚙️ AutoGen

| | |
|---|---|
| **Ce que c'est** | Cadre multi-agent open-source de Microsoft Research |
| **Idéal pour** | Flux de travail multi-agent complexes, recherche, orchestration |
| **Capacité de l'agent** | Conversations imbriquées, humain dans la boucle, exécution de code |
| **Compétence requise** | Élevée — Python, concepts avancés d'agent |
| **Coût** | Gratuit (open-source) ; coûts LLM |

### 👥 Teams AI Library

| | |
|---|---|
| **Ce que c'est** | SDK pour construire des bots Teams alimentés par IA |
| **Idéal pour** | Applications natives Teams, collaboration d'entreprise |
| **Capacité de l'agent** | IA conversationnelle dans les canaux Teams, accès aux données M365 |
| **Compétence requise** | Moyenne — Node.js ou C# |
| **Coût** | SDK gratuit ; nécessite un locataire M365 |

??? question "🤔 Vérifiez votre compréhension"
    Quelle est la principale différence entre Copilot Studio et Semantic Kernel en termes d'utilisateurs ?

    ??? success "Réponse"
        **Copilot Studio** est conçu pour **les développeurs citoyens et les analystes commerciaux** qui ont besoin d'un constructeur d'agents sans code/low-code. **Semantic Kernel** est conçu pour **les développeurs professionnels** (Python/C#) qui souhaitent un contrôle total du code sur la logique des agents, les plugins et la mémoire.

---

## Où s'intègre MCP ?

**Model Context Protocol (MCP)** n'est pas une plateforme — c'est une **norme de connecteur**. Pensez-y comme au USB-C des outils IA : une interface standard unique que tout agent peut utiliser pour se connecter à n'importe quelle source de données ou outil.

![Où s'intègre MCP](../../assets/diagrams/mcp-fit-overview.svg)

MCP fonctionne avec **toutes les plateformes ci-dessus** — et aussi avec Claude Desktop, OpenAI, et tout autre hôte compatible MCP.

??? question "🤔 Vérifiez votre compréhension"
    MCP est décrit comme "USB-C pour les outils IA". Quel problème spécifique cette analogie met-elle en évidence que MCP résout ?

    ??? success "Réponse"
        MCP résout le **problème d'intégration N×M**. Sans MCP, connecter 5 agents à 5 outils nécessite 25 intégrations personnalisées. Avec MCP comme norme universelle, chaque outil publie un serveur MCP et chaque agent compatible MCP peut s'y connecter — réduisant les intégrations à N+M.

---

## Fiche de décision

| Situation | Outil recommandé |
|-----------|-----------------|
| "Je veux un agent dans Teams pour mon équipe, sans codage" | Copilot Studio |
| "Je veux ajouter de l'IA à mon extension VS Code" | API Participant Chat de VS Code |
| "Je veux un agent de production soutenu par Azure, avec surveillance" | Service d'agent Microsoft Foundry |
| "Je veux écrire du code Python/C# pour construire un agent sophistiqué" | Semantic Kernel |
| "Je veux plusieurs agents IA collaborant sur des tâches complexes" | AutoGen |
| "Je veux connecter mon outil/API existant à n'importe quel agent IA" | Construire un serveur MCP |
| "Je veux juste expérimenter avec des LLM gratuitement" | GitHub Models |

??? question "🤔 Vérifiez votre compréhension"
    Un développeur souhaite construire un système où un agent "chercheur", un agent "rédacteur" et un agent "réviseur" collaborent à la production d'un rapport. Quel outil Microsoft est le mieux adapté pour cela ?

    ??? success "Réponse"
        **AutoGen.** Il est spécifiquement conçu pour orchestrer **plusieurs agents spécialisés** qui collaborent sur des tâches complexes à travers des conversations imbriquées. Semantic Kernel excelle à construire des agents sophistiqués uniques, tandis qu'AutoGen excelle dans la coordination multi-agents.

---

## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Vous êtes un développeur citoyen sans expérience en codage. Vous devez construire un chatbot Teams qui répond aux questions sur les politiques RH à partir de SharePoint. Quel outil devriez-vous choisir ?"

    - A) AutoGen
    - B) Semantic Kernel
    - C) Copilot Studio
    - D) Service d'agent Microsoft Foundry

    ??? success "✅ Révéler la réponse"
        **Correct : C — Copilot Studio**

        Copilot Studio est l'option **sans code/low-code** conçue pour les développeurs citoyens et les professionnels de l'IT. Il s'intègre nativement avec Teams et Microsoft 365, peut pointer vers SharePoint comme source de connaissances, et ne nécessite aucun code. AutoGen et Semantic Kernel nécessitent des compétences en développement Python/C#. Foundry est destiné aux développeurs construisant des backends personnalisés.

??? question "**Q2 (Choix multiple) :** Que résout MCP (Model Context Protocol) dans l'écosystème des agents IA ?"

    - A) Il fournit un constructeur GUI pour les agents sans codage
    - B) Il optimise l'utilisation des tokens LLM pour réduire les coûts API
    - C) Il définit une norme universelle afin que tout agent puisse se connecter à n'importe quel outil/source de données via une interface commune
    - D) Il gère l'authentification et le contrôle d'accès basé sur les rôles pour les agents

    ??? success "✅ Révéler la réponse"
        **Correct : C**

        MCP est décrit comme "USB-C pour les outils IA" — une norme de plug universelle. Sans MCP, connecter 5 agents à 5 outils nécessite 25 intégrations personnalisées. Avec MCP, chaque outil publie un serveur MCP et chaque agent compatible MCP peut l'utiliser. Cela résout le problème d'intégration N×M dans l'ensemble de l'écosystème.

??? question "**Q3 (Choix multiple) :** Quelle est la principale différence entre Semantic Kernel et AutoGen ?"

    - A) Semantic Kernel est open-source ; AutoGen est propriétaire de Microsoft
    - B) Semantic Kernel construit des agents sophistiqués uniques avec des plugins ; AutoGen orchestre plusieurs agents spécialisés collaborant sur des tâches complexes
    - C) AutoGen ne fonctionne qu'avec GPT-4o ; Semantic Kernel prend en charge n'importe quel LLM
    - D) Semantic Kernel est uniquement pour Python ; AutoGen prend en charge Python et C#

    ??? success "✅ Révéler la réponse"
        **Correct : B**

        **Semantic Kernel** excelle à construire un agent profondément capable — avec des plugins, de la mémoire, des planificateurs et une utilisation structurée des outils. **AutoGen** excelle à orchestrer *plusieurs* agents — un agent chercheur, un agent rédacteur, un agent réviseur — chacun effectuant une sous-tâche spécialisée et passant les résultats entre eux. Les deux sont open-source et prennent en charge plusieurs LLM.

---

## Résumé

L'écosystème Microsoft dispose d'outils pour **tous les niveaux de compétence et cas d'utilisation** — du Copilot Studio sans code à l'AutoGen pro-code. MCP est le connecteur universel qui fonctionne à travers tous ces outils. Dans le prochain laboratoire, nous vous aiderons à choisir l'outil adapté à votre situation spécifique.

---

## Prochaines étapes

→ **[Laboratoire 003 : Choisir le bon outil](lab-003-choosing-the-right-tool.md)**