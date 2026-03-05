---
tags: [free, beginner, no-account-needed, awareness]
---
# Lab 001 : Que sont les agents IA ?

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~15 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Aucun compte requis</span>
</div>

## Ce que vous apprendrez

- Ce qu'est (et n'est pas) un agent IA
- Les quatre propriétés fondamentales d'un agent : **perception, mémoire, raisonnement, action**
- Comment les agents diffèrent des chatbots simples et des logiciels traditionnels
- Des exemples concrets d'agents IA

---

## Introduction

Le mot « agent » est omniprésent dans l'IA en ce moment — mais que signifie-t-il réellement ?

Un **agent IA** est un logiciel qui utilise un Grand Modèle de Langage (LLM) comme moteur de raisonnement pour **poursuivre un objectif de manière autonome**, en décidant *quoi faire* et *quels outils appeler* à chaque étape — sans que vous ayez à pré-programmer chaque chemin possible.

Le mot clé est **autonome** : l'agent ne se contente pas de répondre à une question. Il planifie, agit, observe le résultat et s'ajuste.

---

## Les quatre propriétés d'un agent

### 1. 🔍 Perception
L'agent reçoit une entrée — un message utilisateur, un fichier, une réponse d'API, un événement.

### 2. 🧠 Mémoire
L'agent stocke des informations entre les échanges :
- **Court terme (fenêtre de contexte) :** la conversation en cours
- **Long terme (base vectorielle / BDD) :** faits, historique, documents récupérés

### 3. 💡 Raisonnement
Le LLM décide *quoi faire ensuite* : répondre directement, appeler un outil, poser une question de clarification, ou décomposer l'objectif en sous-étapes.

### 4. ⚡ Action
L'agent *fait quelque chose* : appeler une API, interroger une base de données, écrire un fichier, envoyer un e-mail, déclencher un autre agent.

![Boucle de l'agent IA — Percevoir, Raisonner, Agir, Observer](../../assets/diagrams/agent-loop-cycle.svg)

??? question "🤔 Vérifiez votre compréhension"
    Dans la boucle de l'agent, que se passe-t-il après que l'agent **agit** (par ex., appelle une API) ?

    ??? success "Réponse"
        L'agent **observe** le résultat — la sortie de l'outil est réinjectée dans le contexte afin que le LLM puisse raisonner sur les nouvelles informations et décider de l'étape suivante. Cela ferme la boucle : percevoir → raisonner → agir → observer → raisonner à nouveau.

---

## Agent vs. Chatbot vs. Logiciel traditionnel

| | Logiciel traditionnel | Chatbot | Agent IA |
|---|---|---|---|
| **Logique définie par** | Développeur | Développeur | LLM (à l'exécution) |
| **Gère les situations nouvelles** | ❌ Uniquement ce qui est codé | ⚠️ Dans les limites des modèles appris | ✅ S'adapte dynamiquement |
| **Utilise des outils** | ✅ Codé en dur | ⚠️ Limité | ✅ Découvre et appelle des outils |
| **Raisonnement multi-étapes** | ❌ | ❌ | ✅ |
| **Prévisibilité** | ✅ Très prévisible | ✅ Plutôt prévisible | ⚠️ Moins prévisible |

!!! tip "Quand NE PAS utiliser un agent"
    Les agents sont puissants mais complexes. Utilisez un **simple appel LLM** pour des questions-réponses en un seul tour. N'utilisez un **agent** que lorsque la tâche nécessite un raisonnement multi-étapes, l'utilisation d'outils ou une prise de décision dynamique.

??? question "🤔 Vérifiez votre compréhension"
    Un chatbot traditionnel suit un arbre de décision pré-programmé. En quoi un agent IA diffère-t-il lorsqu'il rencontre une situation que le développeur n'avait pas anticipée ?

    ??? success "Réponse"
        Un agent IA utilise le LLM pour **s'adapter dynamiquement à l'exécution** — il raisonne sur la nouvelle situation et décide quoi faire, même si ce scénario exact n'a jamais été codé. Un chatbot traditionnel ne peut gérer que ce qui a été explicitement programmé.

??? question "🤔 Vérifiez votre compréhension"
    Quand devriez-vous utiliser un simple appel LLM au lieu de construire un agent IA complet ?

    ??? success "Réponse"
        Utilisez un simple appel LLM pour les tâches de **questions-réponses en un seul tour** qui ne nécessitent ni raisonnement multi-étapes, ni utilisation d'outils, ni prise de décision dynamique. Les agents ajoutent de la complexité et ne doivent être utilisés que lorsque la tâche nécessite véritablement de l'autonomie.

---

## Exemples concrets

| Agent | Ce qu'il fait |
|-------|-------------|
| **GitHub Copilot** | Lit votre code, suggère des complétions, discute, exécute des commandes |
| **Zava Sales Agent** *(l'atelier de ce dépôt)* | Interroge PostgreSQL, génère des graphiques, interprète les tendances de ventes |
| **Microsoft 365 Copilot** | Lit les e-mails, le calendrier, les fichiers, rédige des réponses, résume les réunions |
| **Agent de recherche AutoGen** | Génère des sous-agents pour chercher, synthétiser et rédiger un rapport |

??? question "🤔 Vérifiez votre compréhension"
    Laquelle des quatre propriétés fondamentales d'un agent (perception, mémoire, raisonnement, action) est principalement responsable de la décision de l'agent sur *quoi faire ensuite* ?

    ??? success "Réponse"
        **Le raisonnement.** Le LLM utilise le raisonnement pour décider de l'étape suivante — répondre directement, appeler un outil, poser une question de clarification ou décomposer l'objectif en sous-étapes. La perception gère les entrées, la mémoire stocke le contexte, et l'action exécute la décision.

---

## Termes clés

| Terme | Définition |
|------|-----------|
| **LLM** | Grand Modèle de Langage — le cerveau IA (par ex., GPT-4o, Phi-4) |
| **Outil / Fonction** | Une fonction que le LLM peut appeler (par ex., `search_database`, `send_email`) |
| **Fenêtre de contexte** | La « mémoire de travail » du LLM — tout ce qu'il peut voir en même temps |
| **Prompt** | Les instructions + le contexte envoyés au LLM |
| **Token** | L'unité que les LLM traitent — environ ¾ d'un mot |
| **Ancrage** | Connecter les réponses de l'agent à des données réelles et vérifiées |

---

## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Laquelle des propositions suivantes décrit le mieux un agent IA ?"

    - A) Un chatbot qui suit un arbre de décision pré-programmé
    - B) Un modèle d'apprentissage automatique affiné sur les données de votre entreprise
    - C) Un logiciel qui utilise un LLM pour poursuivre un objectif de manière autonome, en décidant quoi faire et quels outils appeler à chaque étape
    - D) Un système de correspondance de mots-clés basé sur des règles qui redirige les utilisateurs vers des FAQ

    ??? success "✅ Voir la réponse"
        **Correct : C**

        Un agent IA utilise un LLM comme *moteur de raisonnement* pour décider de manière autonome quoi faire à chaque étape — y compris quels outils appeler, quand boucler et quand s'arrêter. L'option A décrit un chatbot traditionnel. L'option B est de l'affinage (modifie le comportement du modèle, pas la structure de l'agent). L'option D est un système classique de routage NLP.

??? question "**Q2 (Choix multiple) :** Dans la boucle percevoir → raisonner → agir → observer, quel est le rôle de l'étape « observer » ?"

    - A) L'agent reformule la requête utilisateur initiale avant de raisonner
    - B) L'agent reçoit le résultat d'une action et le réintègre au contexte pour l'étape de raisonnement suivante
    - C) L'agent appelle le LLM pour générer une réponse finale
    - D) L'agent sauvegarde la conversation dans la mémoire à long terme

    ??? success "✅ Voir la réponse"
        **Correct : B**

        Après que l'agent *agit* (appelle un outil, exécute du code, interroge une base de données), il *observe* le résultat — la sortie de l'outil est ajoutée à l'historique des messages. Cela ferme la boucle : le LLM dispose désormais de nouvelles informations pour raisonner à l'étape suivante. La boucle continue jusqu'à ce que l'agent décide qu'il a suffisamment d'éléments pour répondre.

??? question "**Q3 (Choix multiple) :** Laquelle des propositions suivantes N'EST PAS l'une des quatre propriétés fondamentales d'un agent IA ?"

    - A) Perception
    - B) Compilation
    - C) Mémoire
    - D) Action

    ??? success "✅ Voir la réponse"
        **Correct : B — La compilation n'est pas une propriété fondamentale d'un agent**

        Les quatre propriétés fondamentales sont la **Perception** (reçoit les entrées), la **Mémoire** (conserve le contexte), le **Raisonnement** (utilise le LLM pour décider de l'étape suivante) et l'**Action** (appelle des outils/API/code). La compilation est un concept de langage de programmation, pas une partie de l'architecture d'agent.

---

## Résumé

Un agent IA est un système alimenté par un LLM qui **perçoit, mémorise, raisonne et agit** pour atteindre un objectif. Il diffère du logiciel traditionnel car la logique n'est pas codée en dur — le LLM décide à l'exécution. Cette flexibilité est puissante, mais nécessite une conception soignée des instructions et des outils.

---

## Prochaines étapes

→ **[Lab 002 : Panorama des agents IA 2025](lab-002-agent-landscape.md)** — Comparez tous les outils et plateformes disponibles aujourd'hui.
