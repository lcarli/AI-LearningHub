---
tags: [github-copilot, free, vscode, agentic]
---
# Lab 045: GitHub Copilot Workspace

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> <a href="../paths/copilot/">🤖 GitHub Copilot</a></span>
  <span><strong>Time:</strong> ~30 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> — GitHub Copilot account required</span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.



## What You'll Learn

- What GitHub Copilot Workspace is and how it differs from Copilot Chat
- How to trigger Workspace from a GitHub issue
- The Workspace flow: **Specification → Plan → Implementation**
- How to review, edit, and refine the plan before code is generated
- How to iterate on the implementation with natural language
- When to use Workspace vs. Copilot Agent Mode vs. regular Copilot Chat

---

## Introduction

**GitHub Copilot Workspace** is an agentic coding experience built into GitHub.com. You start with a **GitHub issue** (a bug report, feature request, or task), and Workspace takes you through an end-to-end journey:

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

Unlike Copilot Chat (which helps you in your editor), Workspace works in the browser and can read your entire repository to understand context.

!!! info "Workspace vs. Copilot Chat vs. Agent Mode"
    | | Copilot Chat | Agent Mode (VS Code) | Workspace |
    |--|-------------|---------------------|-----------|
    | **Where** | IDE sidebar | VS Code editor | github.com browser |
    | **Trigger** | Manual chat | Manual prompt | GitHub Issue |
    | **Scope** | Current file/selection | Entire workspace | Entire repository |
    | **Plan step** | ❌ | ❌ | ✅ Explicit plan you review |
    | **Best for** | Line-by-line help | Multi-file tasks | Issue-driven development |

---

## Prerequisites

- GitHub Copilot subscription (Copilot Free includes limited Workspace access)
- A GitHub repository with code (you can fork the OutdoorGear sample or use any repo)
- No local setup needed — runs entirely in the browser

---

## Step 1: Create a Practice Repository

If you don't have a Python project to work with, fork the OutdoorGear starter:

1. Go to [github.com/lcarli/AI-LearningHub](https://github.com/lcarli/AI-LearningHub)
2. Fork the repo
3. In your fork, navigate to `docs/docs/en/labs/lab-018/` — this has the OutdoorGear product functions from Lab 018

Alternatively, create a minimal Python project:

```bash
mkdir outdoorgear-api && cd outdoorgear-api
git init
# Create a simple products.py file and push to GitHub
```

---

## Step 2: Create a GitHub Issue

1. In your repository, click **Issues** → **New issue**
2. Use this template:

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

3. Submit the issue — note the issue number (e.g., `#1`)

---

## Step 3: Open in Copilot Workspace

From your issue page:
1. Click the **▾** dropdown next to **"Open a branch"** (or look for the Copilot icon)
2. Click **"Open in Copilot Workspace"**

   Or navigate directly: `github.com/YOUR_ORG/YOUR_REPO/issues/1/workspace`

!!! tip "Alternative entry point"
    You can also open Workspace from the Copilot icon (✨) at the top right of any issue page.

---

## Step 4: Review the Specification

Workspace analyzes your issue and generates a **specification** — a description of what needs to be built, expressed as natural language statements.

Example specification Workspace might generate:
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

**Your turn:** Read the specification carefully. Does it match what the issue asked for? If not, click **Edit** and refine it. This is the most important step — a clear specification leads to better code.

!!! warning "Don't skip the spec review"
    The specification is the foundation for everything that follows. Vague or incorrect specs produce poor code. Spend 2-3 minutes here.

---

## Step 5: Review and Edit the Plan

After you accept the specification, Workspace generates a **plan** — a list of specific file changes:

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

**Editing the plan:** Click any step and use natural language to modify it:
- "Also add type hints to all new functions"
- "Use a list instead of a dict for REVIEWS storage"
- "Add a DELETE endpoint for removing a review"

---

## Step 6: Generate the Implementation

Click **"Implement"** to generate the code changes.

Workspace will show you a diff for each planned change. Review each file:

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

## Step 7: Iterate with Natural Language

After seeing the generated code, you can request changes without re-reading all the code:

In the Workspace chat, type:
- "The submit_review function should also check that the product_id exists before storing the review"
- "Add a `helpful_votes` integer field to the Review dataclass, defaulting to 0"
- "Change the REVIEWS store to use a class with proper encapsulation"

Workspace will update the plan and regenerate only the affected parts.

---

## Step 8: Create the Pull Request

When satisfied with the implementation:

1. Click **"Create pull request"**
2. Workspace pre-fills the PR title and body with:
   - Link to the original issue
   - Summary of changes
   - List of files modified
   - Test results (if tests ran)
3. Review the PR on GitHub as normal
4. Request code review from teammates

---

## Workspace vs. Copilot Agent Mode — Choosing the Right Tool

| Situation | Use |
|-----------|-----|
| Working from a formal GitHub issue | **Workspace** — issue provides clear context |
| Quick multi-file refactor in VS Code | **Agent Mode** — faster, no browser switch |
| Issue requires understanding many files | **Workspace** — better cross-repo context |
| Exploratory coding, no issue | **Agent Mode** or **Copilot Chat** |
| Need a reviewable plan before coding | **Workspace** — explicit plan step |
| Bug fix with clear repro steps | Either works well |

---

## 🧠 Knowledge Check

??? question "1. What is the purpose of the Specification step in Copilot Workspace?"
    The specification translates the GitHub issue (which is written for humans) into **precise, testable statements** about what the code should do when complete. It catches ambiguities before any code is written — much cheaper to fix a misunderstanding in the spec than in the implementation.

??? question "2. Why is it important to review and edit the Plan before clicking Implement?"
    The plan determines which files will be created or modified and what changes will be made. If the plan is wrong (missing files, wrong approach, incorrect scope), the generated code will be wrong too. Editing the plan with natural language is much faster than editing generated code afterwards.

??? question "3. What is the main advantage of Workspace over asking Copilot Chat to 'implement this issue'?"
    Workspace provides a **structured, reviewable process** with explicit Spec and Plan steps that you can review and edit before any code is generated. Copilot Chat goes directly to code without these review points, making it harder to catch misunderstandings early. Workspace also has better full-repository context.

---

## Summary

Copilot Workspace transforms a GitHub issue into a pull request through a structured, reviewable process:

1. **Issue** → provides the requirement
2. **Specification** → defines what "done" looks like in precise terms
3. **Plan** → lists exact file changes (reviewable, editable)
4. **Implementation** → generates the code
5. **Pull Request** → ready for team review

The key insight: Workspace is not just code generation — it's **agentic issue resolution** where you stay in control at each step.

---

## Next Steps

- **Agentic coding in VS Code:** → [Lab 016 — Copilot Agent Mode](lab-016-copilot-agent-mode.md)
- **Build a custom Copilot Extension:** → [Lab 041 — Custom GitHub Copilot Extension](lab-041-copilot-extension.md)
- **Automate code review with CI/CD:** → [Lab 037 — CI/CD for AI Agents](lab-037-cicd-github-actions.md)
