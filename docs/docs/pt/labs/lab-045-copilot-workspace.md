---
tags: [github-copilot, free, vscode, agentic]
---
# Lab 045: GitHub Copilot Workspace

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/copilot/">🤖 GitHub Copilot</a></span>
  <span><strong>Tempo:</strong> ~30 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-github">GitHub Free</span> — Conta do GitHub Copilot necessária</span>
</div>

## O que Você Vai Aprender

- O que é o GitHub Copilot Workspace e como ele difere do Copilot Chat
- Como acionar o Workspace a partir de uma issue do GitHub
- O fluxo do Workspace: **Especificação → Plano → Implementação**
- Como revisar, editar e refinar o plano antes do código ser gerado
- Como iterar na implementação com linguagem natural
- Quando usar Workspace vs. Copilot Agent Mode vs. Copilot Chat regular
- Como acionar o Workspace a partir de uma issue do GitHub
- O fluxo do Workspace: **Especificação → Plano → Implementação**
- Como revisar, editar e refinar o plano antes do código ser gerado
- Como iterar na implementação com linguagem natural
- Quando usar Workspace vs. Copilot Agent Mode vs. Copilot Chat regular

---

## Introdução

O **GitHub Copilot Workspace** é uma experiência de codificação agêntica integrada ao GitHub.com. Você começa com uma **issue do GitHub** (um relatório de bug, solicitação de recurso ou tarefa), e o Workspace leva você por uma jornada de ponta a ponta:

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

Ao contrário do Copilot Chat (que ajuda você no seu editor), o Workspace funciona no navegador e pode ler todo o seu repositório para entender o contexto.

!!! info "Workspace vs. Copilot Chat vs. Agent Mode"
    | | Copilot Chat | Agent Mode (VS Code) | Workspace |
    |--|-------------|---------------------|-----------|
    | **Onde** | Barra lateral da IDE | Editor do VS Code | Navegador github.com |
    | **Gatilho** | Chat manual | Prompt manual | Issue do GitHub |
    | **Escopo** | Arquivo/seleção atual | Workspace inteiro | Repositório inteiro |
    | **Etapa de plano** | ❌ | ❌ | ✅ Plano explícito que você revisa |
    | **Melhor para** | Ajuda linha por linha | Tarefas multi-arquivo | Desenvolvimento orientado por issues |

---

## Pré-requisitos

- Assinatura do GitHub Copilot (Copilot Free inclui acesso limitado ao Workspace)
- Um repositório GitHub com código (você pode fazer fork do exemplo OutdoorGear ou usar qualquer repositório)
- Nenhuma configuração local necessária — roda inteiramente no navegador

---

## Passo 1: Criar um Repositório de Prática

Se você não tem um projeto Python para trabalhar, faça fork do starter OutdoorGear:

1. Acesse [github.com/lcarli/AI-LearningHub](https://github.com/lcarli/AI-LearningHub)
2. Faça fork do repositório
3. No seu fork, navegue até `docs/docs/en/labs/lab-018/` — aqui estão as funções de produto do OutdoorGear do Lab 018

Alternativamente, crie um projeto Python mínimo:

```bash
mkdir outdoorgear-api && cd outdoorgear-api
git init
# Create a simple products.py file and push to GitHub
```

---

## Passo 2: Criar uma Issue no GitHub

1. No seu repositório, clique em **Issues** → **New issue**
2. Use este template:

**Título:** `Add product review functionality to the OutdoorGear API`

**Corpo:**
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

3. Envie a issue — anote o número da issue (ex.: `#1`)

---

## Passo 3: Abrir no Copilot Workspace

Na página da sua issue:
1. Clique no dropdown **▾** ao lado de **"Open a branch"** (ou procure o ícone do Copilot)
2. Clique em **"Open in Copilot Workspace"**

   Ou navegue diretamente: `github.com/YOUR_ORG/YOUR_REPO/issues/1/workspace`

!!! tip "Ponto de entrada alternativo"
    Você também pode abrir o Workspace pelo ícone do Copilot (✨) no canto superior direito de qualquer página de issue.

---

## Passo 4: Revisar a Especificação

O Workspace analisa sua issue e gera uma **especificação** — uma descrição do que precisa ser construído, expressa como declarações em linguagem natural.

Exemplo de especificação que o Workspace pode gerar:
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

**Sua vez:** Leia a especificação cuidadosamente. Ela corresponde ao que a issue pediu? Se não, clique em **Edit** e refine-a. Este é o passo mais importante — uma especificação clara leva a um código melhor.

!!! warning "Não pule a revisão da especificação"
    A especificação é a base para tudo que vem depois. Especificações vagas ou incorretas produzem código ruim. Gaste 2-3 minutos aqui.

---

## Passo 5: Revisar e Editar o Plano

Depois que você aceita a especificação, o Workspace gera um **plano** — uma lista de alterações específicas em arquivos:

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

**Editando o plano:** Clique em qualquer etapa e use linguagem natural para modificá-la:
- "Also add type hints to all new functions"
- "Use a list instead of a dict for REVIEWS storage"
- "Add a DELETE endpoint for removing a review"

---

## Passo 6: Gerar a Implementação

Clique em **"Implement"** para gerar as alterações de código.

O Workspace mostrará um diff para cada alteração planejada. Revise cada arquivo:

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

## Passo 7: Iterar com Linguagem Natural

Depois de ver o código gerado, você pode solicitar alterações sem reler todo o código:

No chat do Workspace, digite:
- "The submit_review function should also check that the product_id exists before storing the review"
- "Add a `helpful_votes` integer field to the Review dataclass, defaulting to 0"
- "Change the REVIEWS store to use a class with proper encapsulation"

O Workspace atualizará o plano e regenerará apenas as partes afetadas.

---

## Passo 8: Criar o Pull Request

Quando estiver satisfeito com a implementação:

1. Clique em **"Create pull request"**
2. O Workspace preenche automaticamente o título e corpo do PR com:
   - Link para a issue original
   - Resumo das alterações
   - Lista de arquivos modificados
   - Resultados de testes (se os testes rodaram)
3. Revise o PR no GitHub normalmente
4. Solicite revisão de código dos colegas de equipe

---

## Workspace vs. Copilot Agent Mode — Escolhendo a Ferramenta Certa

| Situação | Use |
|----------|-----|
| Trabalhando a partir de uma issue formal do GitHub | **Workspace** — a issue fornece contexto claro |
| Refatoração rápida multi-arquivo no VS Code | **Agent Mode** — mais rápido, sem troca de navegador |
| A issue requer entender muitos arquivos | **Workspace** — melhor contexto cross-repo |
| Codificação exploratória, sem issue | **Agent Mode** ou **Copilot Chat** |
| Precisa de um plano revisável antes de codificar | **Workspace** — etapa de plano explícita |
| Correção de bug com passos de reprodução claros | Ambos funcionam bem |

---

## 🧠 Verificação de Conhecimento

??? question "1. Qual é o propósito da etapa de Especificação no Copilot Workspace?"
    A especificação traduz a issue do GitHub (que é escrita para humanos) em **declarações precisas e testáveis** sobre o que o código deve fazer quando concluído. Ela captura ambiguidades antes que qualquer código seja escrito — é muito mais barato corrigir um mal-entendido na especificação do que na implementação.

??? question "2. Por que é importante revisar e editar o Plano antes de clicar em Implementar?"
    O plano determina quais arquivos serão criados ou modificados e quais alterações serão feitas. Se o plano estiver errado (arquivos faltando, abordagem errada, escopo incorreto), o código gerado também estará errado. Editar o plano com linguagem natural é muito mais rápido do que editar código gerado depois.

??? question "3. Qual é a principal vantagem do Workspace em relação a pedir ao Copilot Chat para 'implementar esta issue'?"
    O Workspace fornece um **processo estruturado e revisável** com etapas explícitas de Especificação e Plano que você pode revisar e editar antes que qualquer código seja gerado. O Copilot Chat vai direto para o código sem esses pontos de revisão, tornando mais difícil detectar mal-entendidos cedo. O Workspace também tem melhor contexto de repositório completo.

---

## Resumo

O Copilot Workspace transforma uma issue do GitHub em um pull request através de um processo estruturado e revisável:

1. **Issue** → fornece o requisito
2. **Especificação** → define como "pronto" se parece em termos precisos
3. **Plano** → lista as alterações exatas nos arquivos (revisável, editável)
4. **Implementação** → gera o código
5. **Pull Request** → pronto para revisão da equipe

O insight principal: o Workspace não é apenas geração de código — é **resolução agêntica de issues** onde você mantém o controle em cada etapa.

---

## Próximos Passos

- **Codificação agêntica no VS Code:** → [Lab 016 — Copilot Agent Mode](lab-016-copilot-agent-mode.md)
- **Construir uma extensão personalizada do Copilot:** → [Lab 041 — Custom GitHub Copilot Extension](lab-041-copilot-extension.md)
- **Automatizar revisão de código com CI/CD:** → [Lab 037 — CI/CD for AI Agents](lab-037-cicd-github-actions.md)
