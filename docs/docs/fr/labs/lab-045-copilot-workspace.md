---
tags: [github-copilot, free, vscode, agentic]
---
# Lab 045 : GitHub Copilot Workspace

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/copilot/">🤖 GitHub Copilot</a></span>
  <span><strong>Durée :</strong> ~30 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-github">GitHub Free</span> — Compte GitHub Copilot requis</span>
</div>

## Ce que vous apprendrez

- Ce qu'est GitHub Copilot Workspace et en quoi il diffère de Copilot Chat
- Comment déclencher Workspace à partir d'une issue GitHub
- Le flux Workspace : **Spécification → Plan → Implémentation**
- Comment examiner, modifier et affiner le plan avant la génération du code
- Comment itérer sur l'implémentation en langage naturel
- Quand utiliser Workspace vs. Copilot Agent Mode vs. Copilot Chat standard

---

## Introduction

**GitHub Copilot Workspace** est une expérience de codage agentique intégrée à GitHub.com. Vous commencez avec une **issue GitHub** (un rapport de bug, une demande de fonctionnalité ou une tâche), et Workspace vous guide à travers un parcours de bout en bout :

```
GitHub Issue
    ↓
Specification (what does "done" look like?)
    ↓
Plan (which files to change, in what order, why)
    ↓
Implementation (actual code changes)
    ↓
Pull Request
```

Contrairement à Copilot Chat (qui vous aide dans votre éditeur), Workspace fonctionne dans le navigateur et peut lire l'intégralité de votre dépôt pour comprendre le contexte.

!!! info "Workspace vs. Copilot Chat vs. Agent Mode"
    | | Copilot Chat | Agent Mode (VS Code) | Workspace |
    |--|-------------|---------------------|-----------|
    | **Où** | Barre latérale de l'IDE | Éditeur VS Code | Navigateur github.com |
    | **Déclencheur** | Chat manuel | Prompt manuel | Issue GitHub |
    | **Portée** | Fichier/sélection en cours | Espace de travail complet | Dépôt complet |
    | **Étape de plan** | ❌ | ❌ | ✅ Plan explicite que vous examinez |
    | **Idéal pour** | Aide ligne par ligne | Tâches multi-fichiers | Développement piloté par les issues |

---

## Prérequis

- Abonnement GitHub Copilot (Copilot Free inclut un accès limité à Workspace)
- Un dépôt GitHub avec du code (vous pouvez forker l'exemple OutdoorGear ou utiliser n'importe quel dépôt)
- Aucune configuration locale nécessaire — fonctionne entièrement dans le navigateur

---

## Étape 1 : Créer un dépôt de pratique

Si vous n'avez pas de projet Python avec lequel travailler, forkez le projet de démarrage OutdoorGear :

1. Accédez à [github.com/lcarli/AI-LearningHub](https://github.com/lcarli/AI-LearningHub)
2. Forkez le dépôt
3. Dans votre fork, naviguez vers `docs/docs/en/labs/lab-018/` — il contient les fonctions produit OutdoorGear du Lab 018

Sinon, créez un projet Python minimal :

```bash
mkdir outdoorgear-api && cd outdoorgear-api
git init
# Create a simple products.py file and push to GitHub
```

---

## Étape 2 : Créer une issue GitHub

1. Dans votre dépôt, cliquez sur **Issues** → **New issue**
2. Utilisez ce modèle :

**Title:** `Add product review functionality to the OutdoorGear API`

**Body:**
```
## Feature Request

### Problem
Currently, customers can search and view products, but there's no way 
to read or submit product reviews through the API.

### Desired Behavior
The API should support:
- GET /products/{id}/reviews — list all reviews for a product
- POST /products/{id}/reviews — submit a new review (rating 1-5, comment)
- GET /products/{id}/rating — get average rating for a product

### Acceptance Criteria
- [ ] Review model with fields: id, product_id, user_id, rating (1-5), comment, created_at
- [ ] In-memory storage is sufficient (no database needed for this task)
- [ ] Proper validation: rating must be 1-5, comment must be non-empty
- [ ] Unit tests for the new functions
- [ ] Type hints on all new functions
```

3. Soumettez l'issue — notez le numéro de l'issue (par exemple, `#1`)

---

## Étape 3 : Ouvrir dans Copilot Workspace

Depuis la page de votre issue :
1. Cliquez sur le menu déroulant **▾** à côté de **"Open a branch"** (ou cherchez l'icône Copilot)
2. Cliquez sur **"Open in Copilot Workspace"**

   Ou naviguez directement : `github.com/YOUR_ORG/YOUR_REPO/issues/1/workspace`

!!! tip "Point d'entrée alternatif"
    Vous pouvez également ouvrir Workspace depuis l'icône Copilot (✨) en haut à droite de n'importe quelle page d'issue.

---

## Étape 4 : Examiner la spécification

Workspace analyse votre issue et génère une **spécification** — une description de ce qui doit être construit, exprimée sous forme d'énoncés en langage naturel.

Exemple de spécification que Workspace pourrait générer :
```
The OutdoorGear API needs a review system. When implemented:

1. A Review data class will exist with fields: id, product_id, user_id, 
   rating (integer 1-5), comment (non-empty string), and created_at (datetime)

2. An in-memory reviews store will maintain reviews indexed by product_id

3. Three new functions will be available:
   - get_product_reviews(product_id) → returns list of Review objects
   - submit_review(product_id, user_id, rating, comment) → validates and stores review
   - get_average_rating(product_id) → returns float or None if no reviews

4. Unit tests cover: valid review submission, invalid rating (0 and 6), 
   empty comment, retrieving reviews for unknown product
```

**À vous :** Lisez attentivement la spécification. Correspond-elle à ce que l'issue demandait ? Si non, cliquez sur **Edit** et affinez-la. C'est l'étape la plus importante — une spécification claire conduit à un meilleur code.

!!! warning "Ne sautez pas la revue de la spécification"
    La spécification est le fondement de tout ce qui suit. Des spécifications vagues ou incorrectes produisent du code médiocre. Passez 2 à 3 minutes ici.

---

## Étape 5 : Examiner et modifier le plan

Après avoir accepté la spécification, Workspace génère un **plan** — une liste de modifications de fichiers spécifiques :

```
Plan:
1. MODIFY products.py
   - Add Review dataclass with fields: id, product_id, user_id, rating, comment, created_at
   - Add REVIEWS dict to store reviews in memory
   - Add get_product_reviews() function
   - Add submit_review() function with validation
   - Add get_average_rating() function

2. CREATE tests/test_reviews.py
   - Test: submit valid review → stored successfully
   - Test: submit review with rating=0 → raises ValueError
   - Test: submit review with rating=6 → raises ValueError  
   - Test: submit empty comment → raises ValueError
   - Test: get_product_reviews for unknown product → returns empty list
   - Test: get_average_rating with no reviews → returns None
   - Test: get_average_rating with 3 reviews → returns correct average
```

**Modifier le plan :** Cliquez sur n'importe quelle étape et utilisez le langage naturel pour la modifier :
- « Ajoutez aussi des annotations de type à toutes les nouvelles fonctions »
- « Utilisez une liste au lieu d'un dict pour le stockage REVIEWS »
- « Ajoutez un endpoint DELETE pour supprimer un avis »

---

## Étape 6 : Générer l'implémentation

Cliquez sur **"Implement"** pour générer les modifications de code.

Workspace vous montrera un diff pour chaque modification planifiée. Examinez chaque fichier :

```python
# Example generated code in products.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class Review:
    product_id: str
    user_id: str
    rating: int  # 1-5
    comment: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)


# In-memory store: product_id → list of reviews
REVIEWS: dict[str, list[Review]] = {}


def get_product_reviews(product_id: str) -> list[Review]:
    """Return all reviews for a product. Returns empty list if none exist."""
    return REVIEWS.get(product_id, [])


def submit_review(product_id: str, user_id: str, rating: int, comment: str) -> Review:
    """Submit a new review. Raises ValueError for invalid input."""
    if not 1 <= rating <= 5:
        raise ValueError(f"Rating must be between 1 and 5, got {rating}")
    if not comment or not comment.strip():
        raise ValueError("Comment cannot be empty")
    
    review = Review(
        product_id=product_id,
        user_id=user_id,
        rating=rating,
        comment=comment.strip()
    )
    
    if product_id not in REVIEWS:
        REVIEWS[product_id] = []
    REVIEWS[product_id].append(review)
    
    return review


def get_average_rating(product_id: str) -> Optional[float]:
    """Return average rating for a product, or None if no reviews."""
    reviews = get_product_reviews(product_id)
    if not reviews:
        return None
    return round(sum(r.rating for r in reviews) / len(reviews), 2)
```

---

## Étape 7 : Itérer en langage naturel

Après avoir vu le code généré, vous pouvez demander des modifications sans relire tout le code :

Dans le chat de Workspace, tapez :
- « La fonction submit_review devrait aussi vérifier que le product_id existe avant de stocker l'avis »
- « Ajoutez un champ entier `helpful_votes` à la dataclass Review, avec une valeur par défaut de 0 »
- « Changez le stockage REVIEWS pour utiliser une classe avec une encapsulation appropriée »

Workspace mettra à jour le plan et ne regénérera que les parties concernées.

---

## Étape 8 : Créer la pull request

Lorsque vous êtes satisfait de l'implémentation :

1. Cliquez sur **"Create pull request"**
2. Workspace pré-remplit le titre et le corps de la PR avec :
   - Lien vers l'issue d'origine
   - Résumé des modifications
   - Liste des fichiers modifiés
   - Résultats des tests (si des tests ont été exécutés)
3. Examinez la PR sur GitHub comme d'habitude
4. Demandez une revue de code à vos coéquipiers

---

## Workspace vs. Copilot Agent Mode — Choisir le bon outil

| Situation | Utiliser |
|-----------|-----|
| Travail à partir d'une issue GitHub formelle | **Workspace** — l'issue fournit un contexte clair |
| Refactoring rapide multi-fichiers dans VS Code | **Agent Mode** — plus rapide, pas de changement de navigateur |
| L'issue nécessite la compréhension de nombreux fichiers | **Workspace** — meilleur contexte inter-dépôt |
| Codage exploratoire, sans issue | **Agent Mode** ou **Copilot Chat** |
| Besoin d'un plan révisable avant de coder | **Workspace** — étape de plan explicite |
| Correction de bug avec des étapes de reproduction claires | Les deux fonctionnent bien |

---

## 🧠 Quiz de connaissances

??? question "1. Quel est l'objectif de l'étape Spécification dans Copilot Workspace ?"
    La spécification traduit l'issue GitHub (qui est écrite pour les humains) en **énoncés précis et testables** sur ce que le code doit faire une fois terminé. Elle détecte les ambiguïtés avant qu'un seul ligne de code ne soit écrite — il est bien moins coûteux de corriger un malentendu dans la spécification que dans l'implémentation.

??? question "2. Pourquoi est-il important d'examiner et de modifier le plan avant de cliquer sur Implement ?"
    Le plan détermine quels fichiers seront créés ou modifiés et quelles modifications seront apportées. Si le plan est incorrect (fichiers manquants, mauvaise approche, portée incorrecte), le code généré sera également incorrect. Modifier le plan en langage naturel est bien plus rapide que de modifier le code généré après coup.

??? question "3. Quel est le principal avantage de Workspace par rapport à demander à Copilot Chat d'« implémenter cette issue » ?"
    Workspace fournit un **processus structuré et révisable** avec des étapes explicites de spécification et de plan que vous pouvez examiner et modifier avant la génération de code. Copilot Chat passe directement au code sans ces points de contrôle, ce qui rend plus difficile la détection précoce des malentendus. Workspace dispose également d'un meilleur contexte sur l'ensemble du dépôt.

---

## Résumé

Copilot Workspace transforme une issue GitHub en pull request à travers un processus structuré et révisable :

1. **Issue** → fournit l'exigence
2. **Spécification** → définit ce que signifie « terminé » en termes précis
3. **Plan** → liste les modifications exactes des fichiers (révisable, modifiable)
4. **Implémentation** → génère le code
5. **Pull Request** → prête pour la revue de l'équipe

L'idée clé : Workspace n'est pas qu'un générateur de code — c'est une **résolution agentique des issues** où vous gardez le contrôle à chaque étape.

---

## Prochaines étapes

- **Codage agentique dans VS Code :** → [Lab 016 — Copilot Agent Mode](lab-016-copilot-agent-mode.md)
- **Créer une extension Copilot personnalisée :** → [Lab 041 — Extension GitHub Copilot personnalisée](lab-041-copilot-extension.md)
- **Automatiser la revue de code avec CI/CD :** → [Lab 037 — CI/CD pour agents IA](lab-037-cicd-github-actions.md)
