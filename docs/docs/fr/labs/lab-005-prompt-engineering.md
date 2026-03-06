---
tags: [free, beginner, no-account-needed, prompt-engineering]
---
# Lab 005 : Ingénierie de prompts

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~25 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Aucun compte requis (les exemples utilisent le playground GitHub Models)</span>
</div>

## Ce que vous apprendrez

- L'anatomie d'un prompt : messages système, utilisateur, assistant
- Les techniques fondamentales : zero-shot, few-shot, chaîne de pensée, prompting par rôle
- Comment écrire des **prompts système** efficaces pour les agents IA
- Les schémas d'échec courants — et comment les corriger
- Des modèles pratiques utilisables immédiatement

---

## Introduction

L'ingénierie de prompts est la pratique de concevoir des entrées pour les LLM qui produisent de manière fiable les sorties souhaitées. C'est en partie un art, en partie une science — et la compétence la plus impactante pour construire de bons agents IA.

Un prompt bien conçu peut transformer une réponse médiocre en une réponse excellente sans changer de modèle. Un prompt système mal conçu fera que votre agent se comportera mal, quelle que soit la puissance du modèle.

!!! tip "Essayez ces exemples en direct"
    Ouvrez le [GitHub Models Playground](https://github.com/marketplace/models) dans un onglet de navigateur et testez chaque exemple au fur et à mesure de votre lecture. C'est gratuit avec un compte GitHub.

---

## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-005/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `prompt_challenges.py` | Script d'exercices interactifs | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-005/prompt_challenges.py) |

---

## Partie 1 : Anatomie d'un prompt

Chaque appel d'API LLM comporte jusqu'à trois types de messages :

```
┌──────────────────────────────────────────────┐
│  SYSTEM MESSAGE                              │
│  "You are a helpful assistant for Zava,      │
│   a DIY retail company..."                   │
│  (Persistent instructions — defines behavior)│
├──────────────────────────────────────────────┤
│  USER MESSAGE                                │
│  "What are your top-selling products         │
│   in the camping category?"                  │
│  (The human's input)                         │
├──────────────────────────────────────────────┤
│  ASSISTANT MESSAGE (optional)                │
│  "The top-selling camping products are..."   │
│  (Prior model responses — for few-shot or    │
│   continued conversations)                   │
└──────────────────────────────────────────────┘
```

### Le message système

Le message système est la partie la plus importante de la conception d'un agent. Il :

- Définit le **personnage et le rôle** de l'agent
- Établit les **règles de comportement** (« ne jamais inventer de données »)
- Spécifie le **format de sortie** (Markdown, JSON, tableaux)
- Fournit le **contexte métier** que le modèle n'aurait pas autrement
- Gère les **cas limites** (« si on pose des questions hors périmètre, dire... »)

??? question "🤔 Vérifiez votre compréhension"
    Quels sont les trois rôles de messages dans un appel d'API LLM, et lequel est invisible pour l'utilisateur final ?

    ??? success "Réponse"
        Les trois rôles sont **system**, **user** et **assistant**. Le **message système** est invisible pour les utilisateurs finaux — il est défini par le développeur et définit le personnage, les règles, le périmètre et le comportement de l'agent. L'utilisateur voit ses propres messages et les réponses de l'assistant.

---

## Partie 2 : Techniques fondamentales

### Zero-Shot

Demandez directement sans exemples. Fonctionne pour les tâches simples et bien définies.

```
Classify this customer review as Positive, Neutral, or Negative.

Review: "The tent arrived on time but the zipper broke after one use."
```

**Quand l'utiliser :** Classification simple, extraction, résumé.

---

### Few-Shot

Fournissez des exemples avant votre question réelle. Améliore considérablement la cohérence.

```
Classify customer reviews as Positive, Neutral, or Negative.

Review: "Great quality, arrived fast!" → Positive
Review: "It's okay, nothing special." → Neutral
Review: "Completely broken on arrival." → Negative

Review: "The tent arrived on time but the zipper broke after one use." →
```

**Quand l'utiliser :** Toute tâche où vous voulez un format, un ton ou un schéma de classification spécifique.

!!! tip "Règle de base"
    2 à 5 exemples suffisent généralement. Plus de 10 aide rarement et coûte plus de tokens.

---

### Chaîne de pensée (CoT)

Demandez au modèle de réfléchir étape par étape avant de donner la réponse finale. Améliore la précision pour les tâches de raisonnement.

**Sans CoT :**
```
Q: A store sells 3 tents for $249 each and gives a 15% group discount.
   What is the total?
A: $635.55
```
*(Peut être faux — calcul précipité)*

**Avec CoT :**
```
Q: A store sells 3 tents for $249 each and gives a 15% group discount.
   What is the total? Think step by step.

A: 
Step 1: 3 tents × $249 = $747
Step 2: 15% discount = $747 × 0.15 = $112.05
Step 3: Total = $747 - $112.05 = $634.95
Final answer: $634.95
```

**Comment déclencher la CoT :**
- « Think step by step »
- « Let's work through this »
- « Explain your reasoning before answering »

**Quand l'utiliser :** Maths, logique, raisonnement multi-étapes, débogage, décisions complexes.

??? question "🤔 Vérifiez votre compréhension"
    Pourquoi ajouter « Think step by step » à un prompt mathématique améliore-t-il la précision, même si le modèle a les mêmes connaissances dans les deux cas ?

    ??? success "Réponse"
        Le prompting par chaîne de pensée force le modèle à **générer des étapes de raisonnement intermédiaires** avant de produire une réponse finale. Cela réduit les erreurs car le modèle peut détecter des erreurs dans les étapes précédentes. Sans CoT, le modèle peut « se précipiter » vers une réponse finale et sauter des calculs critiques.

??? question "🤔 Vérifiez votre compréhension"
    Quand choisiriez-vous le prompting few-shot plutôt que le zero-shot ?

    ??? success "Réponse"
        Utilisez le **few-shot** quand vous avez besoin d'un **format, ton ou schéma de classification spécifique** que le modèle pourrait ne pas déduire des instructions seules. Fournir 2 à 5 exemples améliore considérablement la cohérence. Le zero-shot fonctionne pour les tâches simples et bien définies où le modèle peut déduire le format de sortie attendu.

---

### Prompting par rôle

Donnez au modèle un personnage à adopter. Change le ton, le vocabulaire et le niveau de détail.

```
You are a senior PostgreSQL database engineer with 15 years of experience.
Review this query for performance issues and suggest improvements:

SELECT * FROM sales WHERE store_id = 5 ORDER BY sale_date;
```

vs.

```
Review this query for performance issues:

SELECT * FROM sales WHERE store_id = 5 ORDER BY sale_date;
```

Le prompt par rôle produit des retours plus détaillés et de niveau expert.

---

### Sortie structurée

Forcez le modèle à répondre dans un format spécifique — JSON, tableau Markdown, liste à puces.

```
Extract the product details from this text and return as JSON.
Do not include any explanation — return only the JSON object.

Text: "The ProTrek X200 hiking boots are available in sizes 7-13,
       priced at $189.99, and come in black and brown."

Expected format:
{
  "name": string,
  "sizes": [number],
  "price": number,
  "colors": [string]
}
```

!!! tip "Utilisez le mode JSON lorsqu'il est disponible"
    La plupart des API prennent en charge `response_format: { type: "json_object" }` qui force une sortie JSON valide et élimine les erreurs d'analyse.

---

### Chaînage de prompts

Décomposez les tâches complexes en une séquence de prompts plus petits. Chaque sortie alimente le suivant.

```
Step 1: Extract key facts from the sales report → JSON
Step 2: Feed JSON to "write an executive summary" prompt → Text
Step 3: Feed summary to "translate to Spanish" prompt → Final output
```

C'est plus fiable que de demander à un seul prompt de tout faire.

---

## Partie 3 : Écrire des prompts système pour agents

Pour les agents IA (utilisés dans tous les labs à partir de L100+), le prompt système est la **constitution de l'agent**. Voici une structure éprouvée :

```markdown
## Role
You are [name], a [role] for [company/context].
Your tone is [professional/friendly/technical].

## Capabilities
You can:
- [capability 1]
- [capability 2]
Use ONLY the tools provided to you. Never invent data.

## Rules
- [Rule 1: always do X]
- [Rule 2: never do Y]
- [Rule 3: when Z happens, respond with...]

## Output Format
- Default: Markdown tables
- Charts: only when explicitly requested
- Language: respond in the same language the user writes in

## Scope
Only answer questions about [domain].
For out-of-scope questions, say: "I can only help with [domain]."
```

### Exemple concret : Zava Sales Agent (de l'atelier de ce dépôt)

```markdown
You are Zava, a sales analysis agent for Zava DIY Retail (Washington State).
Your tone is professional and friendly. Use emojis sparingly.

## Data Rules
- Always fetch table schemas before querying (get_multiple_table_schemas())
- Apply LIMIT 20 to all SELECT queries
- Use exact table and column names from the schema
- Never invent, estimate, or assume data

## Financial Calendar
- Financial year (FY) starts July 1
- Q1=Jul–Sep, Q2=Oct–Dec, Q3=Jan–Mar, Q4=Apr–Jun

## Visualizations
- Generate charts ONLY when user uses words: "chart", "graph", "visualize", "show as"
- Always save as PNG and provide download link

## Scope
Only answer questions about Zava sales data.
If asked about anything else, say you're specialized for Zava sales analysis.
```

---

## Partie 4 : Schémas d'échec courants — et corrections

### ❌ Le prompt vague

```
# Bad
"Summarize this."

# Good
"Summarize this sales report in 3 bullet points.
 Each bullet should be ≤20 words.
 Focus on: total revenue, top product, and key trend."
```

**Règle :** Soyez explicite sur le format, la longueur et l'angle.

---

### ❌ Le prompt contradictoire

```
# Bad (contradicts itself)
"Be concise but include all the details."

# Good
"Summarize in 100 words. Prioritize: revenue numbers and top-performing stores."
```

**Règle :** Quand l'espace est limité, dites au modèle quoi prioriser.

---

### ❌ Pas d'exemples négatifs

```
# Bad (doesn't stop hallucination)
"Answer questions about our product catalog."

# Good
"Answer questions about our product catalog.
 If you don't have a product in your data, say 'I don't have that product in the catalog.'
 Never guess or suggest alternatives you haven't verified."
```

**Règle :** Définissez toujours ce que l'agent doit faire quand il *ne peut pas* répondre.

---

### ❌ Surcharge d'instructions

```
# Bad (27 rules, contradictory, hard to follow)
"Be helpful. Be concise. Be detailed. Use tables. Use bullet points.
 Always explain. Never explain. Answer in English. Answer in Portuguese..."

# Good
"Use Markdown tables for data. Use bullet points for lists.
 Default to the user's language."
```

**Règle :** 5 à 10 règles claires surpassent 30 règles vagues.

---

### ❌ Oublier les cas limites

Demandez-vous toujours : « Que se passe-t-il si l'utilisateur pose une question hors périmètre ? Et si des données manquent ? Et si la question est ambiguë ? »

Construisez des règles pour ces cas explicitement.

---

## Partie 5 : Modèles de référence rapide

### Prompt d'extraction

```
Extract the following fields from the text below.
Return as JSON. If a field is not found, use null.

Fields: name, price, category, availability

Text:
"""
{text}
"""
```

### Prompt de classification

```
Classify the following support ticket into one of these categories:
[Billing, Shipping, Returns, Technical, Other]

Return only the category name. No explanation.

Ticket: "{ticket_text}"
```

### Prompt de résumé

```
Summarize the following in {n} bullet points.
Each bullet: one key insight, ≤15 words.
Audience: {audience}

Text:
"""
{text}
"""
```

### Modèle de prompt système pour agent

```
## Role
You are {agent_name}, a {role} for {company}.
Tone: {tone}.

## Capabilities
You have access to these tools: {tools}
Only use verified tool outputs. Never invent data.

## Rules
- {rule_1}
- {rule_2}

## Output Format
{format_instructions}

## Scope
{scope_definition}
For out-of-scope questions: "{out_of_scope_response}"
```

??? question "🤔 Vérifiez votre compréhension"
    Pourquoi est-il important que le prompt système d'un agent définisse ce que l'agent doit faire quand il *ne peut pas* répondre à une question ?

    ??? success "Réponse"
        Sans instruction de repli explicite, le LLM tentera de répondre quand même — souvent en **hallucinant** une réponse plausible mais incorrecte. Définir le comportement hors périmètre (par ex., « dire 'Je ne peux aider qu'avec X' ») empêche l'agent d'inventer des données et fixe des attentes claires pour l'utilisateur.

---

## Partie 6 : 🧪 Défis interactifs — Corrigez les prompts

Lire sur les prompts est bien. **Les écrire et les exécuter** est mieux.

Ces 4 défis vous donnent des **prompts cassés ou vagues** qui produisent de mauvais résultats. Votre mission : les améliorer jusqu'à ce que la sortie corresponde à la cible.

### Installation (5 minutes, gratuit)

```bash
pip install openai
export GITHUB_TOKEN=your_github_token   # github.com → Settings → Developer Settings → Tokens
```

Exécutez le fichier de défis que vous avez téléchargé dans la section [📦 Fichiers d'Appui](#-supporting-files) en haut de ce lab :

```bash
python lab-005/prompt_challenges.py
```

### Ce que chaque défi teste

| # | Ce qui est cassé | Technique à appliquer |
|---|---------------|--------------------|
| **1** | Prompt utilisateur vague, pas d'instruction de format | Format de sortie spécifique |
| **2** | Pas de structure, probablement de la prose au lieu de JSON | Sortie structurée |
| **3** | Question directe sans étapes de raisonnement | Chaîne de pensée |
| **4** | Pas de garde-fous de périmètre → produits hallucinés | Contrôle de périmètre |

### Comment travailler chaque défi

1. Exécutez `python prompt_challenges.py` et lisez le **résultat du ❌ MAUVAIS PROMPT**
2. Éditez les variables `IMPROVED_SYSTEM_*` ou `IMPROVED_USER_*` en bas de chaque défi
3. Relancez et comparez avec la description de la **Cible** dans les commentaires
4. Continuez à itérer jusqu'à ce que votre sortie corresponde

!!! tip "Il n'y a pas de réponse unique"
    L'objectif est d'obtenir une sortie qui respecte les spécifications de la cible. La façon dont vous formulez le prompt est libre — comparez les approches avec un collègue !

---

## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Vous construisez un agent qui doit résoudre un problème mathématique multi-étapes. Quelle technique de prompting améliorera le plus la précision ?"

    - A) Prompting zero-shot
    - B) Prompting par rôle (par ex., « Vous êtes un mathématicien »)
    - C) Prompting par chaîne de pensée (par ex., « Réfléchissez étape par étape »)
    - D) Prompting de sortie structurée

    ??? success "✅ Voir la réponse"
        **Correct : C — Prompting par chaîne de pensée**

        La chaîne de pensée (CoT) force le modèle à raisonner à travers des étapes intermédiaires avant de produire une réponse finale. Cela réduit considérablement les erreurs sur les problèmes de maths, de logique et multi-étapes. « Think step by step » ou montrer des exemples few-shot avec un raisonnement explicite déclenchent tous deux la CoT. Le zero-shot fonctionne pour les tâches simples ; le prompting par rôle aide pour le ton/expertise ; la sortie structurée aide pour le formatage.

??? question "**Q2 (Choix multiple) :** Lequel des trois rôles de conversation l'UTILISATEUR ne voit-il jamais directement lorsqu'il interagit avec un agent ?"

    - A) user
    - B) assistant
    - C) system
    - D) function

    ??? success "✅ Voir la réponse"
        **Correct : C — system**

        Le message `system` est la « constitution » de l'agent — il définit le personnage, les règles, le périmètre et le comportement. Il est défini par le développeur et n'est pas visible pour les utilisateurs finaux dans l'interface de chat. Le rôle `user` contient les entrées de l'humain. Le rôle `assistant` contient les réponses précédentes du modèle (incluses dans les appels API suivants pour maintenir le contexte).

??? question "**Q3 (Choix multiple) :** Votre agent OutdoorGear continue de dire des choses comme « La tente TrailBlazer pèse probablement environ 1,5 kg » alors que le poids exact est dans la base de données. Quelle règle de prompt système est la meilleure correction ?"

    - A) « You are a helpful OutdoorGear assistant. »
    - B) « Never invent, estimate, or assume data. Only use outputs from the tools provided to you. If the product is not found, say: 'I don't have that information in our catalog.' »
    - C) « Think step by step before answering. »
    - D) « Always respond in JSON format. »

    ??? success "✅ Voir la réponse"
        **Correct : B**

        La clé est deux instructions qui fonctionnent ensemble : (1) l'interdiction d'inventer/estimer des données, et (2) une phrase de repli explicite pour quand les données ne sont pas disponibles. Sans le repli, le modèle inventera une réponse plutôt que de ne rien dire. Les règles d'ancrage + le comportement de repli ensemble empêchent les hallucinations dans les agents utilisant des outils.

---

## Résumé

| Technique | Idéale pour |
|-----------|---------|
| **Zero-shot** | Tâches simples et claires |
| **Few-shot** | Format ou classification cohérents |
| **Chaîne de pensée** | Raisonnement, maths, problèmes multi-étapes |
| **Prompting par rôle** | Réponses de niveau expert |
| **Sortie structurée** | JSON, tableaux, données analysables |
| **Chaînage de prompts** | Flux de travail complexes multi-étapes |

**La règle d'or :** Soyez spécifique sur *ce que vous voulez*, *quel format*, et *quoi faire quand les choses tournent mal*.

---

## Prochaines étapes

Vous êtes maintenant prêt à construire votre premier lab pratique :

→ **[Lab 010 — GitHub Copilot premiers pas](lab-010-github-copilot-first-steps.md)** — Appliquez vos compétences de prompting dans VS Code  
→ **[Lab 013 — GitHub Models](lab-013-github-models.md)** — Exécutez vos propres prompts via API gratuitement  
→ **[Lab 014 — SK Hello Agent](lab-014-sk-hello-agent.md)** — Écrivez un prompt système pour un agent Semantic Kernel
