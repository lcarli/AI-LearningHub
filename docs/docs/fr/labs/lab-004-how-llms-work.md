---
tags: [free, beginner, no-account-needed, llm]
---
# Lab 004 : Comment fonctionnent les LLM

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~20 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Aucun compte requis</span>
</div>

## Ce que vous apprendrez

- Ce qu'est vraiment un Grand Modèle de Langage (LLM) sous le capot
- Comment fonctionne l'entraînement : pré-entraînement, affinage, RLHF
- Ce que signifient en pratique les tokens, les fenêtres de contexte et la température
- Pourquoi les LLM hallucinent — et comment atténuer ce phénomène
- La différence entre les modèles : GPT-4o, Phi-4, Llama, Claude

---

## Introduction

Vous avez probablement utilisé ChatGPT ou GitHub Copilot. Mais que se passe-t-il réellement lorsque vous tapez un message et recevez une réponse ? Comprendre la mécanique des LLM fait de vous un bien meilleur constructeur d'agents — vous saurez *pourquoi* certains prompts fonctionnent, *pourquoi* les agents font des erreurs, et *comment* concevoir en tenant compte de leurs limitations.

---

## Partie 1 : Qu'est-ce qu'un Grand Modèle de Langage ?

Un LLM est un réseau neuronal entraîné à **prédire le prochain token** à partir d'une séquence de tokens.

C'est tout. Tout le reste — raisonnement, génération de code, résumé, discussion — est une capacité émergente qui apparaît en faisant cela *à grande échelle* sur *d'énormes quantités de texte*.

### Tokens

Un **token** est l'unité de base qu'un LLM traite. C'est environ ¾ d'un mot (environ 4 caractères).

![Tokenisation](../../assets/diagrams/tokenization.svg)

!!! info "Pourquoi les tokens comptent pour les agents"
    - Les fenêtres de contexte sont mesurées en tokens, pas en mots
    - Les coûts d'API sont facturés par token
    - Les longs documents doivent être découpés pour tenir dans la fenêtre de contexte

### La boucle de prédiction

Lorsque vous envoyez un message, le LLM :

1. Convertit votre texte en une séquence d'identifiants de tokens
2. Les fait passer à travers des milliards d'opérations mathématiques (couches de transformeur)
3. Produit une distribution de probabilité sur l'ensemble du vocabulaire (~100 000 tokens)
4. Échantillonne le prochain token en fonction de cette distribution
5. L'ajoute à la séquence et reprend à l'étape 2

![Boucle de prédiction du LLM](../../assets/diagrams/llm-prediction-loop.svg)

Le LLM ne « connaît » pas les faits — il a appris des **schémas statistiques** à partir de texte. Quand il dit « Paris », c'est parce que « Paris » suit presque toujours cette phrase dans ses données d'entraînement.

??? question "🤔 Vérifiez votre compréhension"
    Un LLM répond correctement « La capitale de la France est Paris. » Le modèle *connaît-il* ce fait comme un humain ?

    ??? success "Réponse"
        Non. Le LLM a appris des **schémas statistiques** à partir de ses données d'entraînement — « Paris » suit presque toujours « La capitale de la France est » dans le texte sur lequel il a été entraîné. Il prédit le token le plus probable suivant, pas des faits vérifiés. C'est pourquoi les LLM peuvent aussi produire avec assurance des réponses fausses (hallucinations).

---

## Partie 2 : Entraîner un LLM

### Étape 1 — Pré-entraînement

Le modèle lit des **trillions de tokens** provenant d'internet, de livres, de code et d'articles scientifiques. Il apprend la structure du langage, des faits, des schémas de raisonnement et des connaissances générales purement en prédisant le prochain token.

```
Training data: Wikipedia + books + GitHub + web pages + ...
Goal: minimize prediction error across all that text
Result: a "base model" that can complete text
```

**GPT-4o, Llama 3, Phi-4** commencent tous comme modèles de base.

### Étape 2 — Affinage par instructions (SFT)

Le modèle de base est entraîné sur des **exemples de conversations** — des paires (prompt, réponse idéale). Cela lui apprend à être utile, à suivre des instructions et à répondre de manière conversationnelle.

### Étape 3 — RLHF (Apprentissage par renforcement à partir de retours humains)

Des évaluateurs humains comparent des paires de réponses et choisissent la meilleure. Un **modèle de récompense** est entraîné sur ces préférences. Le LLM est ensuite affiné pour maximiser le score du modèle de récompense.

C'est pourquoi ChatGPT semble plus poli et aligné qu'un modèle de base brut.

![Pipeline d'entraînement du LLM](../../assets/diagrams/llm-training-pipeline.svg)

??? question "🤔 Vérifiez votre compréhension"
    Quel est le but du RLHF (Apprentissage par renforcement à partir de retours humains) dans l'entraînement des LLM, et pourquoi le pré-entraînement seul ne peut-il pas atteindre le même résultat ?

    ??? success "Réponse"
        Le RLHF aligne le modèle avec les **préférences humaines** — rendant les réponses plus utiles, sûres et conversationnelles. Le pré-entraînement enseigne uniquement au modèle à prédire le prochain token à partir de schémas textuels. Sans RLHF, le modèle pourrait produire des réponses techniquement correctes mais inutiles, dangereuses ou mal formatées.

---

## Partie 3 : Paramètres clés

### Fenêtre de contexte

La **fenêtre de contexte** est la quantité de texte que le modèle peut « voir » en même temps — sa mémoire de travail.

| Modèle | Fenêtre de contexte |
|-------|---------------|
| GPT-4o | 128 000 tokens (~96 000 mots) |
| GPT-4o-mini | 128 000 tokens |
| Phi-4 | 16 000 tokens |
| Llama 3.3 70B | 128 000 tokens |
| Claude 3.5 Sonnet | 200 000 tokens |

![Comparaison des fenêtres de contexte](../../assets/diagrams/context-window.svg)

!!! warning "Fenêtre de contexte ≠ mémoire illimitée"
    Le modèle lit la *totalité* de la fenêtre de contexte à chaque requête. Un contexte plus long = plus lent + plus cher. Les agents utilisent le RAG et la synthèse pour gérer les conversations longues.

### Température

La **température** contrôle le degré d'aléatoire de la sortie.

![Comparaison de la température](../../assets/diagrams/temperature-comparison.svg)

```python
# Deterministic (good for structured data extraction)
response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.0,
    messages=[...]
)

# Creative (good for ideas/drafts)
response = client.chat.completions.create(
    model="gpt-4o",
    temperature=0.8,
    messages=[...]
)
```

### Top-p (échantillonnage par noyau)

Une alternative à la température. N'échantillonne que dans le plus petit ensemble de tokens dont la probabilité cumulée dépasse `top_p`.

- `top_p=0.1` → très conservateur
- `top_p=0.9` → permet des sorties diversifiées

??? question "🤔 Vérifiez votre compréhension"
    Vous construisez un agent qui génère des requêtes SQL à partir du langage naturel. Devriez-vous utiliser une température haute ou basse, et pourquoi ?

    ??? success "Réponse"
        Utilisez une **température basse (0.0)**. Les requêtes SQL doivent être déterministes et syntaxiquement correctes. Une température élevée introduit de l'aléatoire qui pourrait produire du SQL invalide ou incohérent. Pour les tâches de sortie structurée comme la génération de code, l'extraction de données et le SQL, préférez toujours temperature=0.

---

## Partie 4 : Pourquoi les LLM hallucinent

![Causes et solutions des hallucinations](../../assets/diagrams/hallucination-causes.svg)

L'hallucination (génération d'informations fausses formulées avec assurance) se produit parce que :

1. **Le modèle prédit du texte probable, pas du texte vrai.** Une réponse plausible peut obtenir un score plus élevé que « Je ne sais pas. »
2. **Les données d'entraînement ont des lacunes et du bruit.** Si le web dit quelque chose de faux assez souvent, le modèle l'a appris.
3. **Pas de mémoire externe.** Le modèle ne « vérifie » pas les faits — il génère à partir de schémas.

### Comment les agents atténuent les hallucinations

| Technique | Comment elle aide |
|-----------|-------------|
| **RAG** | Fournir au modèle de vrais documents à citer au lieu de se fier aux données d'entraînement |
| **Appel d'outils** | Laisser le modèle appeler des API/bases de données pour des données en temps réel |
| **Température basse** | Réduire la créativité quand la précision compte |
| **Règles du prompt système** | « Ne jamais inventer de données ; utiliser uniquement les sorties des outils » |
| **Sortie structurée** | Forcer le modèle à produire un schéma JSON — plus facile à valider |
| **Évaluation** | Mesurer automatiquement l'ancrage, la cohérence et la factualité |

---

## Partie 5 : Choisir un modèle

Toutes les tâches n'ont pas besoin de GPT-4o. Choisir le bon modèle économise de l'argent et réduit la latence.

| Modèle | Idéal pour | Vitesse | Coût |
|-------|---------|-------|------|
| **GPT-4o** | Raisonnement complexe, long contexte, multimodal | Moyen | $$$ |
| **GPT-4o-mini** | La plupart des tâches quotidiennes | Rapide | $ |
| **Phi-4** (Microsoft) | Sur appareil, faible coût, étonnamment capable | Très rapide | Gratuit (local) |
| **Llama 3.3 70B** | Open-source, auto-hébergé, tâches volumineuses | Moyen | Gratuit (auto-hébergé) |
| **o1 / o3** | Maths, code, raisonnement multi-étapes approfondi | Lent | $$$$ |

!!! tip "Commencez économique, montez en gamme si nécessaire"
    Commencez avec `gpt-4o-mini` ou `Phi-4`. N'upgrader vers `gpt-4o` ou `o1` que si la tâche l'exige clairement.

---

## Partie 6 : L'architecture Transformer (simplifiée)

Vous n'avez pas besoin de comprendre les mathématiques, mais connaître l'intuition clé aide :

**L'auto-attention** est la magie. Pour chaque token, le modèle calcule combien d'« attention » accorder à chaque autre token du contexte.

![Mécanisme d'auto-attention](../../assets/diagrams/self-attention.svg)

C'est pourquoi les LLM comprennent si bien le contexte — chaque mot est interprété en relation avec chaque autre mot.

??? question "🤔 Vérifiez votre compréhension"
    Dans la phrase « La rive au bord de la rivière était escarpée », comment le mécanisme d'auto-attention aide-t-il le modèle à comprendre que « rive » fait référence au bord de la rivière et non à une institution financière ?

    ??? success "Réponse"
        L'auto-attention calcule combien d'« attention » chaque token doit accorder à chaque autre token. En traitant « rive », le modèle prête fortement attention à « rivière » — la relation contextuelle entre ces mots oriente l'interprétation vers la **rive de la rivière** plutôt que vers une institution financière. Chaque mot est interprété en relation avec chaque autre mot du contexte.

---

## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Environ combien de tokens contient la phrase *'Hello world'* ?"

    - A) 1 token
    - B) 2 tokens
    - C) 6 tokens
    - D) 10 tokens

    ??? success "✅ Voir la réponse"
        **Correct : B — 2 tokens**

        « Hello » est 1 token et « world » est 1 token. En règle générale, 1 token ≈ 4 caractères ≈ ¾ d'un mot. Un document de 1 000 mots représente environ 1 300 tokens. Cela importe tant pour le coût (les API facturent par token) que pour les limites de la fenêtre de contexte (GPT-4o a une fenêtre de contexte de 128K tokens).

??? question "**Q2 (Choix multiple) :** Vous appelez un LLM pour de l'extraction de données structurées (par ex., analyser du JSON à partir d'un e-mail client). Quel réglage de température est le plus approprié ?"

    - A) temperature = 1.5 (haute créativité)
    - B) temperature = 0.8 (créativité modérée)
    - C) temperature = 0.0 (déterministe)
    - D) temperature = 2.0 (aléatoire maximal)

    ??? success "✅ Voir la réponse"
        **Correct : C — temperature = 0.0**

        Quand la précision et la reproductibilité comptent plus que la créativité, utilisez `temperature=0`. Cela fait que le modèle choisit toujours le prochain token le plus probable — donc la même entrée produit toujours la même sortie. Pour l'écriture créative : utilisez 0.7–1.0. Pour l'extraction de données, la génération SQL ou le formatage d'arguments d'outils : utilisez 0.

??? question "**Q3 (Choix multiple) :** Un LLM affirme avec assurance qu'une ville fictive au Brésil a une population de 2,3 millions. Cette ville n'existe pas. Quelle est la cause principale ?"

    - A) La fenêtre de contexte du modèle était trop petite
    - B) La température était trop élevée
    - C) Le modèle prédit du texte vraisemblable plutôt que des faits vérifiés — il a fait de la correspondance de motifs avec des villes réelles similaires
    - D) Le prompt système était absent

    ??? success "✅ Voir la réponse"
        **Correct : C — Les LLM prédisent du texte vraisemblable, pas du texte factuel**

        Les LLM sont entraînés à prédire le prochain token qui est *statistiquement probable* étant donné le contexte. Une ville inventée qui ressemble à de vraies villes dans le schéma (« São Paulo a 12M, Rio a 6M... ») amène le modèle à générer une réponse plausible mais fabriquée. C'est une hallucination. Le remède est le RAG ou l'appel d'outils — forcer le modèle à chercher les faits plutôt qu'à les prédire.

---

## Résumé

| Concept | Point clé |
|---------|-------------|
| **Tokens** | ~4 caractères chacun ; les fenêtres de contexte et les coûts sont mesurés en tokens |
| **Prédiction** | Les LLM prédisent le prochain token — le raisonnement est émergent, pas programmé |
| **Entraînement** | Pré-entraînement → affinage → RLHF produit des assistants utiles |
| **Température** | 0 = déterministe ; plus élevé = plus créatif |
| **Fenêtre de contexte** | La mémoire de travail du modèle ; ne persiste pas entre les requêtes |
| **Hallucination** | Causée par la correspondance de motifs, pas la vérification de faits — atténuée avec des outils + RAG |

---

## Prochaines étapes

→ **[Lab 005 — Ingénierie de prompts](lab-005-prompt-engineering.md)** — Maintenant que vous savez comment fonctionnent les LLM, apprenez à écrire des prompts qui produisent de manière fiable le résultat souhaité.
