---
tags: [copilot-studio, teams, free-trial, no-code]
---
# Lab 011 : Copilot Studio — Premier agent

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/agent-builder-teams/">Agent Builder — Teams</a></span>
  <span><strong>Durée :</strong> ~30 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Essai gratuit</span> — Essai gratuit de Microsoft Copilot Studio (pas de carte bancaire pendant les 30 premiers jours)</span>
</div>

## Ce que vous apprendrez

- Naviguer dans le canevas de **Copilot Studio** (créateur d'agents sans code / low-code)
- Créer un agent de questions-réponses à partir d'une source de connaissances (document FAQ)
- Tester votre agent dans le panneau de test intégré
- Publier l'agent sur **Microsoft Teams**
- Comprendre les sujets, les déclencheurs et le comportement de repli

---

## Introduction

Microsoft Copilot Studio est une plateforme graphique low-code permettant de créer des agents d'IA conversationnelle sans écrire de code. Vous définissez des **sujets** (flux de conversation), connectez des **sources de connaissances** et publiez sur Teams, des sites web ou d'autres canaux en quelques minutes.

Ce lab construit un agent de service client pour l'entreprise fictive **OutdoorGear Inc.**, basé sur une FAQ produit.

---

## Prérequis

- Compte Microsoft (gratuit sur account.microsoft.com)
- Essai Copilot Studio : [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com) → Démarrer l'essai gratuit
- Microsoft Teams (l'édition personnelle gratuite fonctionne)

!!! tip "Pas de carte bancaire nécessaire"
    L'essai gratuit de Copilot Studio dure 30 jours et ne nécessite pas de coordonnées de paiement.

---

## Exercice du lab

### Étape 1 : Créer un nouveau Copilot

1. Accédez à [copilotstudio.microsoft.com](https://copilotstudio.microsoft.com)
2. Connectez-vous avec votre compte Microsoft
3. Cliquez sur **Créer** → **Nouvel agent**
4. Remplissez :
   - **Nom :** `OutdoorGear Assistant`
   - **Description :** `Customer service agent for OutdoorGear Inc. — answers product and policy questions`
   - **Instructions :** `You are a friendly customer service agent for OutdoorGear Inc. Answer questions about products, return policies, shipping, and warranties. Be concise and helpful.`
5. Cliquez sur **Créer**

### Étape 2 : Ajouter une source de connaissances

1. Dans le panneau de gauche, cliquez sur **Connaissances**
2. Cliquez sur **Ajouter des connaissances** → **Site web public ou fichier**
3. Entrez cette URL (notre FAQ d'exemple) :
   ```
   https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json
   ```
   Ou cliquez sur **Charger un fichier** et collez d'abord ce contenu dans un fichier `.txt`.

!!! tip "Utilisation de knowledge-base.json"
    Le fichier `data/knowledge-base.json` contient 42 documents incluant des guides produits, des politiques de retour, des FAQ et des informations d'expédition — le tout pré-formaté pour le RAG.

### Étape 3 : Tester les connaissances intégrées

1. Cliquez sur **Tester** dans le coin supérieur droit
2. Dans le panneau de discussion, essayez ces questions :
   - `What is your return policy?`
   - `Do you have waterproof boots?`
   - `How long does shipping take?`
3. L'agent devrait répondre à partir de la source de connaissances et citer l'endroit où il a trouvé la réponse

### Étape 4 : Créer un sujet personnalisé

Les sujets personnalisés vous permettent de remplacer les réponses IA par des flux déterministes pour des intentions spécifiques.

1. Cliquez sur **Sujets** dans le panneau de gauche
2. Cliquez sur **Ajouter un sujet** → **À partir de zéro**
3. Nommez-le : `Order Status`
4. Sous **Phrases de déclenchement**, ajoutez :
   - `Where is my order`
   - `Track my order`
   - `Order status`
   - `What happened to my order`
5. Ajoutez un nœud **Message** :
   ```
   To check your order status, please visit our order portal at outdoorgear.com/orders or call 1-800-OUTDOOR. Have your order number ready!
   ```
6. Ajoutez un nœud **Fin de conversation**
7. Cliquez sur **Enregistrer**

### Étape 5 : Tester le sujet personnalisé

Dans le panneau de test, tapez : `Where is my order?`

L'agent devrait utiliser le flux de votre sujet personnalisé, et non le repli IA. Remarquez comment les sujets déterministes ont la priorité sur les réponses génératives de l'IA.

### Étape 6 : Publier sur Teams

1. Cliquez sur **Publier** dans le panneau de gauche
2. Cliquez sur **Publier** pour mettre l'agent en ligne
3. Cliquez sur **Canaux** → **Microsoft Teams**
4. Cliquez sur **Activer Teams**
5. Cliquez sur **Ouvrir l'agent** — cela ouvre un lien profond
6. Dans Teams, cliquez sur **Ajouter** pour installer l'agent en tant qu'application
7. Commencez à discuter avec votre OutdoorGear Assistant dans Teams !

---

## Architecture de Copilot Studio

```
┌─────────────────────────────────────────┐
│          Copilot Studio                 │
│                                         │
│  ┌─────────────┐   ┌─────────────────┐  │
│  │   Topics    │   │  Generative AI  │  │
│  │ (no-code    │   │  (knowledge +   │  │
│  │  flows)     │   │   LLM fallback) │  │
│  └──────┬──────┘   └────────┬────────┘  │
│         │   Topic match?    │           │
│         │ ◄─────────────────┘           │
│         ▼                               │
│     User message                        │
└─────────────────────────────────────────┘
         │
         ▼
  Channels: Teams, Web, Slack, ...
```

**Ordre de priorité :**
1. Sujets personnalisés (correspondance exacte des déclencheurs) → déterministe
2. Sujets système intégrés (escalade, repli)
3. Réponses génératives de l'IA à partir des sources de connaissances

---

## Quand utiliser Copilot Studio vs le code professionnel

| Copilot Studio | Code professionnel (SK/MCP) |
|----------------|-------------------|
| Utilisateurs métier, sans code | Développeurs |
| Prototypage rapide | Logique complexe |
| Intégration Teams/SharePoint | Intégrations personnalisées |
| Flux basés sur une interface graphique | Contrôle programmatique |
| Personnalisation limitée | Flexibilité totale |

---

## Étapes suivantes

- **Teams AI Library (bot Teams code-first) :** → [Lab 024 — Teams AI Library](lab-024-teams-ai-library.md)
- **Ajouter des outils MCP à Copilot Studio :** → [Lab 012 — Qu'est-ce que MCP ?](lab-012-what-is-mcp.md)
