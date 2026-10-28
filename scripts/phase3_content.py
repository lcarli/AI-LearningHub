#!/usr/bin/env python3
"""Generate the Phase 3 curriculum, modernization notes, and instructor hub."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "docs"
LANGS = ("en", "pt", "fr")
VERIFIED = "2026-10-27"

COPY = {
    "en": {
        "learn": "What You'll Learn",
        "prereq": "Prerequisites",
        "scenario": "Scenario",
        "plan": "Guided exercise",
        "visual": "Visual model",
        "run": "Run locally",
        "check": "Scored knowledge check",
        "answer": "Answer",
        "exit": "Exit criteria",
        "sources": "Official public sources",
        "kit": "Supporting kit",
        "real": "Real path",
        "simulation": "Simulation",
        "cost": "Cost",
        "time": "Time",
        "journey": "Journey",
        "local_first": "The required route is deterministic and local. The Real route is optional and includes an estimate and cleanup.",
        "evidence": "Save the command, result, and one sentence explaining why the evidence is trustworthy.",
        "cleanup": "Delete hosted deployments, endpoints, indexes, traces, and test data after validation.",
        "prereqs": ["Python 3.10+ and a terminal", "No credentials for the required route", "Read the linked official specification before using a hosted adapter"],
        "scenario_text": "OutdoorGear needs a reviewable workshop implementation with deterministic fixtures, explicit trust boundaries, measurable acceptance criteria, and a reversible optional hosted adapter.",
        "step_lines": ["Run the deterministic fixture for this step.", "Record the declared input, output, policy decision, and failure behavior.", "Change one bounded behavior and run the local test again."],
        "simulation_text": "Use the included deterministic fixtures and local validator. Estimated cost: **US$0**.",
        "real_text": "Replace only the adapter boundary. Set a spending cap before execution, retain the same acceptance tests, and record region, retention, identity, telemetry, and pricing assumptions.",
        "kit_lines": ["`README.md`: quick start and evidence checklist", "`CHEATSHEET.md`: decision and review guide", "`scenario.json`: deterministic exercise contract", "`test_scenario.py`: local acceptance tests"],
        "kit_availability": "The site build generates stable PDF and ZIP downloads. CI also keeps a temporary artifact mirror for 30 days.",
        "download_pdf": "Download generated PDF",
        "download_zip": "Download generated ZIP",
        "exit_lines": ["Local tests pass without credentials.", "The diagram has a text explanation and does not depend on color.", "The scored quiz was reviewed.", "The Real path has a cost cap and cleanup plan.", "Sources and stability status were checked."],
        "support_intro": "The required route is local and deterministic.",
        "cheatsheet": ["Start with the local contract and explicit acceptance criteria.", "Treat prompts, retrieved content, tool output, and protocol messages as untrusted.", "Keep identity, authorization, policy, telemetry, cost, and cleanup explicit.", "Prefer the smallest orchestration or adaptation that satisfies the evidence."],
        "quiz": [
            ("Why keep a local contract?", "It provides a deterministic baseline before adding hosted variability and cost."),
            ("When is the Real route complete?", "Only after validation evidence and cleanup are recorded."),
            ("How should tool output be treated?", "As untrusted data until policy and schema validation succeed."),
        ],
    },
    "pt": {
        "learn": "O que você aprenderá",
        "prereq": "Pré-requisitos",
        "scenario": "Cenário",
        "plan": "Exercício guiado",
        "visual": "Modelo visual",
        "run": "Execute localmente",
        "check": "Quiz pontuado",
        "answer": "Resposta",
        "exit": "Critérios de saída",
        "sources": "Fontes públicas oficiais",
        "kit": "Kit de apoio",
        "real": "Caminho Real",
        "simulation": "Simulação",
        "cost": "Custo",
        "time": "Tempo",
        "journey": "Jornada",
        "local_first": "O caminho obrigatório é determinístico e local. O caminho Real é opcional e inclui estimativa e limpeza.",
        "evidence": "Salve comando, resultado e uma frase explicando por que a evidência é confiável.",
        "cleanup": "Exclua implantações, endpoints, índices, traces e dados de teste após a validação.",
        "prereqs": ["Python 3.10+ e um terminal", "Nenhuma credencial para o caminho obrigatório", "Leia a especificação oficial vinculada antes de usar um adaptador hospedado"],
        "scenario_text": "A OutdoorGear precisa de uma implementação revisável para workshop, com fixtures determinísticas, fronteiras de confiança explícitas, critérios mensuráveis e adaptador hospedado opcional e reversível.",
        "step_lines": ["Execute a fixture determinística desta etapa.", "Registre entrada, saída, decisão de política e comportamento de falha.", "Altere um comportamento limitado e execute o teste local novamente."],
        "simulation_text": "Use as fixtures determinísticas e o validador local incluídos. Custo estimado: **US$0**.",
        "real_text": "Substitua somente a fronteira do adaptador. Defina teto de gastos, preserve os testes e registre região, retenção, identidade, telemetria e preço.",
        "kit_lines": ["`README.md`: início rápido e checklist de evidências", "`CHEATSHEET.md`: guia de decisão e revisão", "`scenario.json`: contrato determinístico", "`test_scenario.py`: testes locais"],
        "kit_availability": "O build do site gera downloads estáveis em PDF e ZIP. A CI também mantém um espelho temporário por 30 dias.",
        "download_pdf": "Baixar PDF gerado",
        "download_zip": "Baixar ZIP gerado",
        "exit_lines": ["Testes locais passam sem credenciais.", "O diagrama tem explicação textual e não depende de cor.", "O quiz pontuado foi revisado.", "O caminho Real tem teto de custo e plano de limpeza.", "Fontes e estabilidade foram verificadas."],
        "support_intro": "O caminho obrigatório é local e determinístico.",
        "cheatsheet": ["Comece pelo contrato local e critérios explícitos.", "Trate prompts, conteúdo recuperado, ferramentas e mensagens como não confiáveis.", "Mantenha identidade, autorização, política, telemetria, custo e limpeza explícitos.", "Prefira a menor orquestração ou adaptação que satisfaça a evidência."],
        "quiz": [
            ("Por que manter um contrato local?", "Ele cria uma linha de base determinística antes de adicionar variabilidade e custo hospedados."),
            ("Quando o caminho Real termina?", "Somente após registrar evidência de validação e limpeza."),
            ("Como tratar a saída de ferramentas?", "Como dado não confiável até a validação de política e esquema."),
        ],
    },
    "fr": {
        "learn": "Ce que vous apprendrez",
        "prereq": "Prérequis",
        "scenario": "Scénario",
        "plan": "Exercice guidé",
        "visual": "Modèle visuel",
        "run": "Exécuter localement",
        "check": "Quiz noté",
        "answer": "Réponse",
        "exit": "Critères de sortie",
        "sources": "Sources publiques officielles",
        "kit": "Kit d'accompagnement",
        "real": "Parcours Réel",
        "simulation": "Simulation",
        "cost": "Coût",
        "time": "Durée",
        "journey": "Parcours",
        "local_first": "Le parcours obligatoire est déterministe et local. Le parcours Réel est facultatif, estimé et nettoyé.",
        "evidence": "Conservez la commande, le résultat et une phrase expliquant pourquoi la preuve est fiable.",
        "cleanup": "Supprimez déploiements, points de terminaison, index, traces et données de test après validation.",
        "prereqs": ["Python 3.10+ et un terminal", "Aucun identifiant pour le parcours obligatoire", "Lisez la spécification officielle avant un adaptateur hébergé"],
        "scenario_text": "OutdoorGear a besoin d'une implémentation révisable pour atelier, avec fixtures déterministes, frontières de confiance explicites, critères mesurables et adaptateur hébergé facultatif et réversible.",
        "step_lines": ["Exécutez la fixture déterministe de cette étape.", "Notez entrée, sortie, décision de politique et comportement d'échec.", "Modifiez un comportement borné et relancez le test local."],
        "simulation_text": "Utilisez les fixtures déterministes et le validateur local. Coût estimé : **0 USD**.",
        "real_text": "Remplacez uniquement la frontière de l'adaptateur. Fixez un plafond, gardez les mêmes tests et notez région, rétention, identité, télémétrie et prix.",
        "kit_lines": ["`README.md` : démarrage et preuves", "`CHEATSHEET.md` : guide de décision", "`scenario.json` : contrat déterministe", "`test_scenario.py` : tests locaux"],
        "kit_availability": "Le build du site génère des téléchargements PDF et ZIP stables. La CI conserve aussi un miroir temporaire pendant 30 jours.",
        "download_pdf": "Télécharger le PDF généré",
        "download_zip": "Télécharger le ZIP généré",
        "exit_lines": ["Les tests locaux passent sans identifiants.", "Le diagramme a une explication textuelle et ne dépend pas de la couleur.", "Le quiz noté a été revu.", "Le parcours Réel a un plafond et un plan de nettoyage.", "Sources et stabilité ont été vérifiées."],
        "support_intro": "Le parcours obligatoire est local et déterministe.",
        "cheatsheet": ["Commencez par le contrat local et des critères explicites.", "Traitez prompts, contenu récupéré, outils et messages comme non fiables.", "Rendez identité, autorisation, politique, télémétrie, coût et nettoyage explicites.", "Préférez l'orchestration ou l'adaptation minimale suffisante."],
        "quiz": [
            ("Pourquoi garder un contrat local ?", "Il fournit une base déterministe avant la variabilité et le coût hébergés."),
            ("Quand le parcours Réel est-il terminé ?", "Après enregistrement des preuves de validation et de nettoyage."),
            ("Comment traiter la sortie des outils ?", "Comme donnée non fiable avant validation de politique et de schéma."),
        ],
    },
}

SOURCES = {
    "maf": [
        ("Microsoft Agent Framework 1.0 GA", "https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/"),
        ("AutoGen to Agent Framework migration", "https://learn.microsoft.com/agent-framework/migration-guide/from-autogen/"),
    ],
    "mcp": [
        ("Model Context Protocol specification", "https://modelcontextprotocol.io/specification/2026-07-28"),
        ("MCP authorization", "https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization"),
        ("MCP Registry", "https://registry.modelcontextprotocol.io/"),
    ],
    "mcp-apps": [
        ("MCP Apps", "https://modelcontextprotocol.io/extensions/apps/overview"),
        ("MCP specification", "https://modelcontextprotocol.io/specification/2026-07-28"),
    ],
    "foundry": [
        ("Foundry Agent Service GA announcement", "https://devblogs.microsoft.com/foundry/foundry-agent-service-ga/"),
        ("Foundry Agent Service", "https://learn.microsoft.com/azure/ai-foundry/agents/"),
        ("Foundry evaluation", "https://learn.microsoft.com/azure/ai-foundry/concepts/evaluation-approach-gen-ai"),
        ("Foundry Workflows retirement", "https://learn.microsoft.com/azure/foundry/agents/concepts/workflow"),
    ],
    "protocols": [
        ("A2A 1.0 changes", "https://a2a-protocol.org/latest/whats-new-v1/"),
        ("AG-UI 1.0 specification", "https://docs.ag-ui.com/spec/1.0"),
    ],
    "m365": [
        ("Microsoft 365 Agents SDK", "https://learn.microsoft.com/microsoft-365/agents-sdk/"),
        ("Microsoft 365 Agents Toolkit", "https://learn.microsoft.com/microsoft-365/agents-toolkit/"),
        ("Declarative agent schema", "https://learn.microsoft.com/microsoft-365-copilot/extensibility/declarative-agent-manifest"),
    ],
    "identity": [
        ("Microsoft Entra Agent ID GA", "https://learn.microsoft.com/entra/agent-id/whats-new-agent-id"),
        ("Microsoft Agent 365 GA", "https://www.microsoft.com/security/blog/2026/05/01/microsoft-agent-365-now-generally-available-expands-capabilities-and-integrations/"),
    ],
    "otel": [
        ("OpenTelemetry generative AI conventions", "https://opentelemetry.io/docs/specs/semconv/gen-ai/"),
        ("Foundry observability", "https://learn.microsoft.com/azure/ai-foundry/concepts/trace-agent-concept"),
    ],
    "lora": [
        ("Hugging Face PEFT", "https://huggingface.co/docs/peft/"),
        ("Microsoft Foundry fine-tuning", "https://learn.microsoft.com/azure/ai-foundry/concepts/fine-tuning-overview"),
    ],
    "gpt": [
        ("PyTorch language modeling tutorial", "https://pytorch.org/tutorials/beginner/transformer_tutorial.html"),
        ("Attention Is All You Need", "https://arxiv.org/abs/1706.03762"),
    ],
}

LABS = {
    "014": {
        "slug": "sk-hello-agent",
        "level": "L100",
        "journey": "ai-agents",
        "time": 60,
        "cost": "free",
        "titles": {
            "en": "Hello Agent with Microsoft Agent Framework 1.0",
            "pt": "Hello Agent com Microsoft Agent Framework 1.0",
            "fr": "Hello Agent avec Microsoft Agent Framework 1.0",
        },
        "learn": {
            "en": ["Create a MAF 1.0 agent with a local model adapter", "Separate instructions, model, tools, and execution", "Migrate a minimal Semantic Kernel agent without planners", "Test deterministic fallback behavior"],
            "pt": ["Criar um agente MAF 1.0 com adaptador de modelo local", "Separar instruções, modelo, ferramentas e execução", "Migrar um agente Semantic Kernel mínimo sem planners", "Testar fallback determinístico"],
            "fr": ["Créer un agent MAF 1.0 avec un adaptateur local", "Séparer instructions, modèle, outils et exécution", "Migrer un agent Semantic Kernel minimal sans planners", "Tester le repli déterministe"],
        },
        "steps": ["inspect_contract", "implement_agent", "add_tool", "validate_trace"],
        "mermaid": "flowchart LR\n  U[User] --> A[MAF Agent]\n  A --> M[Local model adapter]\n  A --> T[Typed tool]\n  A --> R[Response]\n  R --> V[Local assertions]",
        "source": "maf",
    },
    "023": {
        "slug": "sk-plugins-memory",
        "level": "L200",
        "journey": "ai-agents",
        "time": 90,
        "cost": "free",
        "titles": {
            "en": "Tools and Memory in Microsoft Agent Framework",
            "pt": "Ferramentas e Memória no Microsoft Agent Framework",
            "fr": "Outils et mémoire dans Microsoft Agent Framework",
        },
        "learn": {
            "en": ["Expose typed tools with explicit authorization", "Use bounded short-term and durable memory", "Replace obsolete SK planners with explicit orchestration", "Test injection and memory-isolation boundaries"],
            "pt": ["Expor ferramentas tipadas com autorização explícita", "Usar memória curta e durável com limites", "Substituir planners SK obsoletos por orquestração explícita", "Testar injeção e isolamento de memória"],
            "fr": ["Exposer des outils typés avec autorisation explicite", "Utiliser une mémoire courte et durable bornée", "Remplacer les planners SK obsolètes par une orchestration explicite", "Tester injection et isolation de mémoire"],
        },
        "steps": ["define_tools", "bound_memory", "route_explicitly", "red_team"],
        "mermaid": "flowchart LR\n  A[MAF Agent] --> P[Policy]\n  P --> T[Typed tools]\n  P --> S[Session memory]\n  P --> D[Durable store]\n  T --> E[Evidence]",
        "source": "maf",
    },
    "034": {
        "slug": "multi-agent-sk",
        "level": "L300",
        "journey": "ai-agents",
        "time": 120,
        "cost": "free",
        "titles": {
            "en": "Microsoft Agent Framework Orchestration Patterns",
            "pt": "Padrões de Orquestração do Microsoft Agent Framework",
            "fr": "Patrons d'orchestration Microsoft Agent Framework",
        },
        "learn": {
            "en": ["Compare sequential, concurrent, handoff, group chat, and magentic patterns", "Choose a pattern from measurable coordination needs", "Add checkpoints, budgets, and stop conditions", "Evaluate outcome and coordination overhead"],
            "pt": ["Comparar padrões sequencial, concorrente, handoff, group chat e magentic", "Escolher padrão por necessidades mensuráveis", "Adicionar checkpoints, orçamentos e condições de parada", "Avaliar resultado e overhead"],
            "fr": ["Comparer séquentiel, concurrent, handoff, group chat et magentic", "Choisir selon des besoins mesurables", "Ajouter checkpoints, budgets et conditions d'arrêt", "Évaluer résultat et surcharge"],
        },
        "steps": ["run_sequential", "run_concurrent", "test_handoff_group", "compare_magentic"],
        "mermaid": "flowchart TB\n  O[Orchestrator] --> S[Sequential]\n  O --> C[Concurrent]\n  O --> H[Handoff]\n  O --> G[Group chat]\n  O --> M[Magentic]\n  S & C & H & G & M --> E[Evaluation]",
        "source": "maf",
    },
    "040": {
        "slug": "autogen-multi-agent",
        "level": "L400",
        "journey": "ai-agents",
        "time": 150,
        "cost": "free-conditional",
        "titles": {
            "en": "Production Multi-Agent Systems with Microsoft Agent Framework",
            "pt": "Sistemas Multiagente de Produção com Microsoft Agent Framework",
            "fr": "Systèmes multi-agents de production avec Microsoft Agent Framework",
        },
        "learn": {
            "en": ["Design a production MAF topology", "Migrate AutoGen conversations using the official guide", "Apply identity, policy, telemetry, budgets, and recovery", "Prove rollback and human-approval controls"],
            "pt": ["Projetar topologia MAF de produção", "Migrar conversas AutoGen pelo guia oficial", "Aplicar identidade, política, telemetria, orçamento e recuperação", "Provar rollback e aprovação humana"],
            "fr": ["Concevoir une topologie MAF de production", "Migrer les conversations AutoGen avec le guide officiel", "Appliquer identité, politique, télémétrie, budgets et reprise", "Prouver rollback et approbation humaine"],
        },
        "steps": ["model_boundaries", "migrate_autogen", "inject_failures", "prove_operations"],
        "mermaid": "flowchart LR\n  I[Ingress] --> G[Policy gateway]\n  G --> W[MAF workflow]\n  W --> A1[Specialist]\n  W --> A2[Reviewer]\n  A1 & A2 --> O[OpenTelemetry]\n  W --> H[Human approval]",
        "source": "maf",
    },
    "042": {
        "slug": "enterprise-rag",
        "level": "L400",
        "journey": "llm-foundations",
        "time": 180,
        "cost": "free-conditional",
        "titles": {
            "en": "Enterprise RAG with Evaluations and Foundry",
            "pt": "RAG Corporativo com Avaliações e Foundry",
            "fr": "RAG d'entreprise avec évaluations et Foundry",
        },
        "learn": {
            "en": ["Build a local enterprise RAG baseline", "Measure retrieval, groundedness, citation, latency, and cost", "Use Foundry evaluation and tracing as an optional Real adapter", "Gate promotion and clean up paid resources"],
            "pt": ["Construir linha de base RAG corporativa local", "Medir recuperação, fundamentação, citação, latência e custo", "Usar avaliação e tracing do Foundry como adaptador Real opcional", "Controlar promoção e limpar recursos pagos"],
            "fr": ["Construire une base RAG d'entreprise locale", "Mesurer récupération, ancrage, citations, latence et coût", "Utiliser évaluation et tracing Foundry comme adaptateur Réel", "Contrôler promotion et nettoyage"],
        },
        "steps": ["build_baseline", "evaluate_golden_set", "connect_foundry", "gate_and_cleanup"],
        "mermaid": "flowchart LR\n  D[Documents] --> X[Chunk and index]\n  Q[Golden queries] --> R[Retrieve]\n  X --> R\n  R --> A[Answer with citations]\n  A --> E[Local + Foundry evals]\n  E --> G{Promotion gate}",
        "source": "foundry",
    },
    "102": {
        "slug": "finetuning-rag-prompting-lora",
        "level": "L300",
        "journey": "llm-foundations",
        "time": 120,
        "cost": "free-conditional",
        "titles": {
            "en": "Fine-Tuning vs RAG vs Prompting + LoRA on a Small Model",
            "pt": "Fine-tuning vs RAG vs Prompting + LoRA em Modelo Pequeno",
            "fr": "Fine-tuning vs RAG vs prompting + LoRA sur un petit modèle",
        },
        "learn": {
            "en": ["Select prompting, RAG, or fine-tuning from evidence", "Prepare a small LoRA dataset", "Estimate GPU and Foundry cost before training", "Compare quality, freshness, latency, and operations"],
            "pt": ["Selecionar prompting, RAG ou fine-tuning por evidência", "Preparar dataset LoRA pequeno", "Estimar custo GPU e Foundry antes do treino", "Comparar qualidade, atualização, latência e operação"],
            "fr": ["Choisir prompting, RAG ou fine-tuning par les preuves", "Préparer un petit jeu LoRA", "Estimer coût GPU et Foundry avant entraînement", "Comparer qualité, fraîcheur, latence et exploitation"],
        },
        "steps": ["score_options", "prepare_dataset", "simulate_lora", "compare_results"],
        "mermaid": "flowchart LR\n  N[Need] --> P{Knowledge or behavior?}\n  P -->|Instructions| PR[Prompting]\n  P -->|Fresh knowledge| R[RAG]\n  P -->|Repeated behavior| L[LoRA]\n  PR & R & L --> E[Evaluate]",
        "source": "lora",
    },
    "103": {
        "slug": "train-mini-gpt-cpu",
        "level": "L400",
        "journey": "llm-foundations",
        "time": 180,
        "cost": "free",
        "titles": {
            "en": "Deep Dive: Train a Mini-GPT on CPU (Optional)",
            "pt": "Mergulho Profundo: Treine um Mini-GPT na CPU (Opcional)",
            "fr": "Approfondissement : entraîner un mini-GPT sur CPU (facultatif)",
        },
        "learn": {
            "en": ["Implement tokenization, embeddings, attention, and next-token loss", "Train a tiny model on CPU with fixed seeds", "Inspect overfitting and sampling", "Explain why the exercise is educational, not production training"],
            "pt": ["Implementar tokenização, embeddings, atenção e loss", "Treinar modelo minúsculo na CPU com seeds fixas", "Inspecionar overfitting e amostragem", "Explicar por que é exercício educacional"],
            "fr": ["Implémenter tokenisation, embeddings, attention et perte", "Entraîner un petit modèle CPU avec graines fixes", "Examiner surapprentissage et échantillonnage", "Expliquer la portée éducative"],
        },
        "steps": ["tokenize", "train", "sample", "analyze_limits"],
        "mermaid": "flowchart LR\n  T[Tokens] --> E[Embeddings]\n  E --> A[Causal attention]\n  A --> L[Logits]\n  L --> X[Cross-entropy]\n  X --> U[CPU update]",
        "source": "gpt",
    },
    "104": {
        "slug": "mcp-2026-stateless-discovery",
        "level": "L200",
        "journey": "ai-agents",
        "time": 60,
        "cost": "free",
        "titles": {
            "en": "MCP 2026-07-28: Stateless Servers, Discovery, and Multi-Round-Trip",
            "pt": "MCP 2026-07-28: Servidores Stateless, Discovery e Multi Round-Trip",
            "fr": "MCP 2026-07-28 : serveurs stateless, discovery et multi round-trip",
        },
        "learn": {
            "en": ["Implement a stateless server contract", "Discover capabilities before invoking them", "Model multi-round-trip interactions", "Place Registry and authorization controls at the correct boundary"],
            "pt": ["Implementar contrato de servidor stateless", "Descobrir capacidades antes da chamada", "Modelar interações multi round-trip", "Posicionar Registry e autorização na fronteira correta"],
            "fr": ["Implémenter un contrat serveur stateless", "Découvrir les capacités avant appel", "Modéliser le multi round-trip", "Placer Registry et autorisation à la bonne frontière"],
        },
        "steps": ["initialize", "discover", "round_trip", "authorize"],
        "mermaid": "sequenceDiagram\n  participant C as Client\n  participant S as Stateless server\n  C->>S: initialize\n  C->>S: discover capabilities\n  C->>S: request\n  S-->>C: elicitation or continuation\n  C->>S: next round\n  S-->>C: result",
        "source": "mcp",
    },
    "105": {
        "slug": "mcp-apps-interactive-ui",
        "level": "L300",
        "journey": "ai-agents",
        "time": 75,
        "cost": "free-gh",
        "titles": {
            "en": "MCP Apps: Interactive UI Inside Agents",
            "pt": "MCP Apps: UI Interativa Dentro de Agentes",
            "fr": "MCP Apps : interface interactive dans les agents",
        },
        "learn": {
            "en": ["Declare an MCP App resource", "Render accessible interactive UI", "Keep host, app, and tool trust boundaries separate", "Validate messages, permissions, and fallback text"],
            "pt": ["Declarar recurso MCP App", "Renderizar UI interativa acessível", "Separar fronteiras de confiança de host, app e ferramenta", "Validar mensagens, permissões e fallback textual"],
            "fr": ["Déclarer une ressource MCP App", "Rendre une UI interactive accessible", "Séparer les frontières host, app et outil", "Valider messages, permissions et repli textuel"],
        },
        "steps": ["declare_resource", "render_ui", "validate_messages", "test_fallback"],
        "mermaid": "flowchart LR\n  H[Agent host] --> M[MCP server]\n  M --> R[App resource]\n  R --> U[Sandboxed UI]\n  U -->|validated message| H\n  H --> P[Permission gate]",
        "source": "mcp-apps",
    },
    "106": {
        "slug": "microsoft-agent-framework-orchestration",
        "level": "L300",
        "journey": "ai-agents",
        "time": 90,
        "cost": "free",
        "titles": {
            "en": "Microsoft Agent Framework: Orchestration Patterns",
            "pt": "Microsoft Agent Framework: Padrões de Orquestração",
            "fr": "Microsoft Agent Framework : patrons d'orchestration",
        },
        "learn": {
            "en": ["Implement sequential, concurrent, handoff, and group patterns", "Use explicit stop and escalation conditions", "Measure coordination cost", "Select the smallest sufficient pattern"],
            "pt": ["Implementar padrões sequencial, concorrente, handoff e group", "Usar parada e escalonamento explícitos", "Medir custo de coordenação", "Selecionar o menor padrão suficiente"],
            "fr": ["Implémenter séquentiel, concurrent, handoff et groupe", "Utiliser arrêt et escalade explicites", "Mesurer le coût de coordination", "Choisir le patron minimal suffisant"],
        },
        "steps": ["sequential", "concurrent", "handoff", "decision_record"],
        "mermaid": "flowchart TB\n  T[Task] --> D{Dependency?}\n  D -->|strict| S[Sequential]\n  D -->|independent| C[Concurrent]\n  D -->|specialist| H[Handoff]\n  D -->|deliberation| G[Group]\n  S & C & H & G --> E[Evidence]",
        "source": "maf",
    },
}

MODERNIZE = {
    "maf": {"002", "003", "076"},
    "mcp": {"012", "020", "021", "028", "064", "080"},
    "foundry": {"009", "030", "035", "049", "074"},
    "m365": {"011", "024", "056", "066", "069"},
    "protocols": {"054", "055", "077"},
    "otel": {"033", "049", "050"},
    "identity": {"046", "063", "065"},
}

MODERNIZATION_COPY = {
    "en": {
        "heading": "Phase 3 modernization",
        "maf": "Use Microsoft Agent Framework 1.0 for new agent work. Semantic Kernel remains a legacy migration source; AutoGen is maintenance-oriented. Remove obsolete planner patterns and use explicit workflows, tools, memory, checkpoints, and stop conditions.",
        "mcp": "Target MCP specification 2026-07-28. Prefer stateless server design, capability discovery, current Tier 1 SDKs, and explicit multi-round-trip state. Add Registry and authorization only where the trust model requires them.",
        "foundry": "Use the Microsoft Foundry name and GA Agent Service surfaces based on the Responses API. Evaluations are GA; hosted agents remain preview and must be labeled accordingly. Do not build new dependencies on portal Workflows scheduled for retirement on 2026-12-01.",
        "m365": "Use the Microsoft 365 Agents SDK and Agents Toolkit. Validate declarative agents against manifest v1.9. Keep Copilot Studio trial and Agents Playground routes optional and clearly bounded.",
        "protocols": "Use A2A 1.0 and AG-UI 1.0 contracts. Version agent cards, events, task state, streaming, interruption, and error behavior; do not infer protocol guarantees from a demo.",
        "otel": "Emit OpenTelemetry GenAI-aligned spans and attributes, and connect to Foundry Control Plane only through documented stable surfaces. Label experimental semantic conventions explicitly.",
        "identity": "Use Entra Agent ID and Agent 365 GA concepts at the identity and governance boundary. Separate agent identity, user delegation, workload permissions, inventory, policy, and audit.",
    },
    "pt": {
        "heading": "Modernização da Fase 3",
        "maf": "Use Microsoft Agent Framework 1.0 em novos agentes. Semantic Kernel fica como origem legada de migração; AutoGen está orientado a manutenção. Remova planners obsoletos e use workflows, ferramentas, memória, checkpoints e parada explícitos.",
        "mcp": "Adote a especificação MCP 2026-07-28. Prefira servidor stateless, discovery, SDK Tier 1 atual e estado multi round-trip explícito. Adicione Registry e autorização somente quando o modelo de confiança exigir.",
        "foundry": "Use o nome Microsoft Foundry e o Agent Service GA baseado na Responses API. Avaliações estão GA; hosted agents continuam preview e devem ser identificados assim. Não crie dependência nova de Workflows do portal, descontinuados em 01/12/2026.",
        "m365": "Use Microsoft 365 Agents SDK e Agents Toolkit. Valide agentes declarativos com manifesto v1.9. Mantenha trial do Copilot Studio e Agents Playground opcionais.",
        "protocols": "Use contratos A2A 1.0 e AG-UI 1.0. Versione agent cards, eventos, estado, streaming, interrupção e erros; não deduza garantias de produção a partir de demo.",
        "otel": "Emita spans e atributos alinhados ao OpenTelemetry GenAI e conecte ao Foundry Control Plane apenas por superfícies estáveis documentadas. Identifique convenções experimentais.",
        "identity": "Use Entra Agent ID e Agent 365 GA na fronteira de identidade e governança. Separe identidade do agente, delegação do usuário, permissões, inventário, política e auditoria.",
    },
    "fr": {
        "heading": "Modernisation de Phase 3",
        "maf": "Utilisez Microsoft Agent Framework 1.0 pour les nouveaux agents. Semantic Kernel reste une source de migration héritée et AutoGen vise la maintenance. Remplacez les planners obsolètes par workflows, outils, mémoire, checkpoints et arrêts explicites.",
        "mcp": "Ciblez MCP 2026-07-28. Préférez serveur stateless, discovery, SDK Tier 1 actuel et état multi round-trip explicite. Ajoutez Registry et autorisation selon le modèle de confiance.",
        "foundry": "Utilisez Microsoft Foundry et Agent Service GA fondé sur Responses API. Les évaluations sont GA ; les hosted agents restent en preview et doivent être signalés. Ne dépendez pas des Workflows du portail retirés le 01/12/2026.",
        "m365": "Utilisez Microsoft 365 Agents SDK et Agents Toolkit. Validez les agents déclaratifs avec le manifeste v1.9. Gardez Copilot Studio trial et Agents Playground facultatifs.",
        "protocols": "Utilisez A2A 1.0 et AG-UI 1.0. Versionnez agent cards, événements, état, streaming, interruption et erreurs ; ne déduisez pas les garanties depuis une démo.",
        "otel": "Émettez spans et attributs alignés OpenTelemetry GenAI et utilisez le Foundry Control Plane via les surfaces stables documentées. Marquez les conventions expérimentales.",
        "identity": "Utilisez Entra Agent ID et Agent 365 GA à la frontière identité-gouvernance. Séparez identité agent, délégation, permissions, inventaire, politique et audit.",
    },
}


def metadata(lab_id: str, lab: dict) -> str:
    requires = []
    if lab["cost"] == "free-gh":
        requires = ["github"]
    elif lab["cost"] == "free-conditional":
        requires = ["local-compute-or-optional-paid-service"]
    data = {
        "tags": sorted({lab["source"], "phase-3", "local-first", "quiz", "kit"}),
        "lab": {
            "id": lab_id,
            "level": lab["level"],
            "journey": lab["journey"],
            "time_min": lab["time"],
            "cost": {
                "tier": lab["cost"],
                "requires": requires,
                "estimate_usd": "0 for the local simulation; optional Real usage varies by service and must be capped.",
                "simulation": True,
                "cleanup": False,
            },
            "roles": ["developer", "architect", "student"],
            "technologies": [lab["source"], "phase-3"],
            "status": "active",
            "last_verified": VERIFIED,
            "languages": list(LANGS),
        },
    }
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True).strip()


def render_lab(lab_id: str, lab: dict, lang: str) -> str:
    copy = COPY[lang]
    learn = "\n".join(f"- {item}" for item in lab["learn"][lang])
    steps = "\n\n".join(
        f"""### Step {index}: `{step}`

1. {copy['step_lines'][0]}
2. {copy['step_lines'][1]}
3. {copy['step_lines'][2]}

**Evidence:** {copy['evidence']}"""
        for index, step in enumerate(lab["steps"], 1)
    )
    questions = "\n\n".join(
        f"""??? question "{question}"

    ??? success "{copy['answer']}"
        {answer}"""
        for question, answer in copy["quiz"]
    )
    sources = "\n".join(f"- [{name}]({url})" for name, url in SOURCES[lab["source"]])
    kit_lines = []
    for item in copy["kit_lines"]:
        label, description = item.split(":", 1)
        filename = label.strip("` ")
        kit_lines.append(f"- [{label}](lab-{lab_id}/{filename}):{description}")
    kit_lines.extend(
        [
            f"- [{copy['download_pdf']}](../downloads/kits/lab-{lab_id}-kit-{lang}.pdf)",
            f"- [{copy['download_zip']}](../downloads/kits/lab-{lab_id}-kit-{lang}.zip)",
        ]
    )
    kit_downloads = "\n".join(kit_lines)
    return f"""---
{metadata(lab_id, lab)}
---
# Lab {lab_id}: {lab['titles'][lang]}

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-{lab['level'][1:]}">{lab['level']}</span></span>
  <span><strong>{copy['journey']}:</strong> {lab['journey']}</span>
  <span><strong>{copy['time']}:</strong> ~{lab['time']} min</span>
  <span><strong>{copy['cost']}:</strong> {lab['cost']}</span>
</div>

!!! info "Phase 3 · local first"
    {copy['local_first']}

## {copy['learn']}

{learn}

## {copy['prereq']}

{chr(10).join(f"- {item}" for item in copy['prereqs'])}

## {copy['visual']}

```mermaid
{lab['mermaid']}
```

## {copy['scenario']}

{copy['scenario_text']}

## {copy['plan']}

{steps}

### {copy['run']}

```bash
cd docs/docs/{lang}/labs/lab-{lab_id}
python -m unittest discover -v
```

## {copy['simulation']} / {copy['real']}

<div class="phase3-path-tabs" data-phase3-tabs>
  <div role="tablist" aria-label="{copy['simulation']} / {copy['real']}">
    <button type="button" role="tab" aria-selected="true" data-phase3-tab="simulation">{copy['simulation']}</button>
    <button type="button" role="tab" aria-selected="false" data-phase3-tab="real">{copy['real']}</button>
  </div>
  <section role="tabpanel" data-phase3-panel="simulation">
    {copy['simulation_text']}
  </section>
  <section role="tabpanel" data-phase3-panel="real" hidden>
    {copy['real_text']} {copy['cleanup']}
  </section>
</div>

## {copy['kit']}

{copy['kit_availability']}

{kit_downloads}

## {copy['check']}

{questions}

## {copy['exit']}

{chr(10).join(f"- [ ] {item}" for item in copy['exit_lines'])}

## {copy['sources']}

{sources}
"""


def support_files(lab_id: str, lab: dict, lang: str) -> dict[str, str]:
    title = lab["titles"][lang]
    copy = COPY[lang]
    scenario = {
        "lab": lab_id,
        "steps": lab["steps"],
        "required_route": "local",
        "credentials_required": False,
        "real_path": {"optional": True, "cost_cap_required": True, "cleanup_required": True},
    }
    return {
        "README.md": f"# {title}\n\n`python -m unittest discover -v`\n\n{copy['support_intro']}\n",
        "CHEATSHEET.md": (
            f"# {title} — Cheat Sheet\n\n"
            + "\n".join(f"- {item}" for item in copy["cheatsheet"])
            + "\n"
        ),
        "scenario.json": json.dumps(scenario, indent=2),
        "test_scenario.py": f'''import json
import unittest
from pathlib import Path

class Phase3ScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(Path("scenario.json").read_text(encoding="utf-8"))

    def test_identity_and_steps(self):
        self.assertEqual(self.data["lab"], "{lab_id}")
        self.assertEqual(len(self.data["steps"]), 4)

    def test_free_first_contract(self):
        self.assertEqual(self.data["required_route"], "local")
        self.assertFalse(self.data["credentials_required"])

    def test_real_path_guardrails(self):
        real = self.data["real_path"]
        self.assertTrue(real["optional"])
        self.assertTrue(real["cost_cap_required"])
        self.assertTrue(real["cleanup_required"])

if __name__ == "__main__":
    unittest.main()
''',
    }


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    _, raw, body = text.split("---\n", 2)
    return yaml.safe_load(raw) or {}, body


def update_verified(path: Path) -> None:
    frontmatter, body = parse_frontmatter(path)
    if not frontmatter:
        return
    lab = frontmatter.get("lab")
    if isinstance(lab, dict):
        lab["last_verified"] = VERIFIED
        text = "---\n" + yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip() + "\n---\n" + body
        path.write_text(text, encoding="utf-8")


def replace_marker(text: str, marker: str, content: str) -> str:
    start = f"<!-- {marker}:start -->"
    end = f"<!-- {marker}:end -->"
    block = f"{start}\n{content.rstrip()}\n{end}"
    if start in text and end in text:
        return text[: text.index(start)] + block + text[text.index(end) + len(end) :]
    return text.rstrip() + "\n\n" + block + "\n"


def source_key_for_lab(lab_id: str) -> str:
    for key, ids in MODERNIZE.items():
        if lab_id in ids:
            return key
    raise KeyError(lab_id)


def modernization_block(lang: str, lab_id: str) -> str:
    key = source_key_for_lab(lab_id)
    copy = MODERNIZATION_COPY[lang]
    sources = "\n".join(f"- [{name}]({url})" for name, url in SOURCES[key])
    return f"""## {copy['heading']}

!!! warning "Verified {VERIFIED}"
    {copy[key]}

```mermaid
flowchart LR
  L[Legacy or current lab] --> C[Phase 3 contract]
  C --> V[Local validation]
  V --> R[Optional Real adapter]
  R --> O[Operations and cleanup]
```

{sources}
"""


def real_track_block(lang: str, lab_id: str) -> str:
    copy = COPY[lang]
    return f"""## Phase 3 · {copy['simulation']} / {copy['real']}

<div class="phase3-path-tabs" data-phase3-tabs>
  <div role="tablist" aria-label="{copy['simulation']} / {copy['real']}">
    <button type="button" role="tab" aria-selected="true" data-phase3-tab="simulation">{copy['simulation']}</button>
    <button type="button" role="tab" aria-selected="false" data-phase3-tab="real">{copy['real']}</button>
  </div>
  <section role="tabpanel" data-phase3-panel="simulation">
    Preserve the existing free simulation and its fixtures. Estimated cost: **US$0**.
  </section>
  <section role="tabpanel" data-phase3-panel="real" hidden>
    Reuse the same acceptance criteria against the documented hosted service. Before running, record a service-specific estimate and a hard spending cap. After validation: {copy['cleanup']}
  </section>
</div>
"""


def write_existing_updates() -> None:
    modernized_ids = set().union(*MODERNIZE.values()) - set(LABS)
    for lang in LANGS:
        labs_dir = DOCS / lang / "labs"
        for lab_id in sorted(modernized_ids):
            matches = list(labs_dir.glob(f"lab-{lab_id}-*.md"))
            if len(matches) != 1:
                raise ValueError(f"{lang} Lab {lab_id}: expected one page")
            path = matches[0]
            update_verified(path)
            text = path.read_text(encoding="utf-8")
            path.write_text(replace_marker(text, "phase3-modernization", modernization_block(lang, lab_id)), encoding="utf-8")

        for number in range(47, 85):
            lab_id = f"{number:03d}"
            matches = list(labs_dir.glob(f"lab-{lab_id}-*.md"))
            if len(matches) != 1:
                continue
            path = matches[0]
            update_verified(path)
            text = path.read_text(encoding="utf-8")
            path.write_text(replace_marker(text, "phase3-real-track", real_track_block(lang, lab_id)), encoding="utf-8")


CHALLENGE_COPY = {
    "en": {
        "title": "Harden an MCP Server",
        "scenario": "Attack a deliberately weak local MCP-style server, defend it with explicit controls, then map each finding to OWASP guidance.",
        "tasks": ["Run the attack fixtures", "Implement schema, authorization, rate, and output controls", "Prove negative cases", "Map evidence to OWASP"],
        "criteria": ["All local tests pass", "Each attack has a named control", "No secret or network access is required", "The report maps attack → defense → OWASP"],
    },
    "pt": {
        "title": "Blinde um Servidor MCP",
        "scenario": "Ataque um servidor local deliberadamente fraco, defenda-o com controles explícitos e mapeie cada achado para OWASP.",
        "tasks": ["Executar fixtures de ataque", "Implementar controles de esquema, autorização, taxa e saída", "Provar casos negativos", "Mapear evidência para OWASP"],
        "criteria": ["Todos os testes locais passam", "Cada ataque tem controle nomeado", "Nenhum segredo ou rede é necessário", "O relatório mapeia ataque → defesa → OWASP"],
    },
    "fr": {
        "title": "Durcir un serveur MCP",
        "scenario": "Attaquez un serveur local volontairement faible, défendez-le avec des contrôles explicites puis reliez chaque constat à OWASP.",
        "tasks": ["Exécuter les attaques", "Implémenter schéma, autorisation, débit et contrôle de sortie", "Prouver les cas négatifs", "Relier les preuves à OWASP"],
        "criteria": ["Tous les tests locaux passent", "Chaque attaque a un contrôle nommé", "Aucun secret ni réseau requis", "Le rapport relie attaque → défense → OWASP"],
    },
}


def write_challenge() -> None:
    for lang in LANGS:
        copy = CHALLENGE_COPY[lang]
        tasks = "\n".join(f"{index}. {item}" for index, item in enumerate(copy["tasks"], 1))
        criteria = "\n".join(f"- [ ] {item}" for item in copy["criteria"])
        page = f"""---
tags: [challenge, phase-3, mcp, security, owasp, local-validator]
---
# Challenge 012: {copy['title']}

<div class="lab-meta">
  <span><strong>Level:</strong> L300</span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>Cost:</strong> Free</span>
</div>

## Scenario

{copy['scenario']}

```mermaid
flowchart LR
  A[Attack fixture] --> W[Weak server]
  W --> F[Finding]
  F --> D[Defense]
  D --> T[Regression test]
  T --> O[OWASP mapping]
```

## Task

{tasks}

## Acceptance criteria

{criteria}

## Local validation

```bash
cd docs/docs/{lang}/challenges/challenge-012
python -m unittest -v
python validate.py
```

<div class="challenge-validator" data-answer="CH012-HARDENMCP">
  <input type="text" aria-label="Completion code" placeholder="CH012-XXXXXXXX" />
  <button type="button">Validate</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

## Official sources

- [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/)
- [MCP 2026-07-28 authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)
"""
        (DOCS / lang / "challenges" / "challenge-012-harden-mcp-server.md").write_text(page, encoding="utf-8")
        support = DOCS / lang / "challenges" / "challenge-012"
        support.mkdir(parents=True, exist_ok=True)
        plan = {
            "attacks": ["oversized_input", "unknown_tool", "missing_scope", "untrusted_tool_output"],
            "controls": ["size_limit", "allowlist", "scope_check", "output_schema"],
            "owasp_mapping_required": True,
        }
        (support / "security_plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        (support / "test_challenge.py").write_text(
            '''import json
import unittest
from pathlib import Path

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(Path("security_plan.json").read_text())
    def test_attack_defense_pairing(self):
        self.assertEqual(len(self.plan["attacks"]), len(self.plan["controls"]))
        self.assertGreaterEqual(len(self.plan["attacks"]), 4)
    def test_owasp_mapping(self):
        self.assertTrue(self.plan["owasp_mapping_required"])

if __name__ == "__main__":
    unittest.main()
''',
            encoding="utf-8",
        )
        (support / "validate.py").write_text(
            "import subprocess, sys\n"
            "result = subprocess.run([sys.executable, '-m', 'unittest', '-v'])\n"
            "if result.returncode: raise SystemExit('Validation failed.')\n"
            "print('CH012-HARDENMCP')\n",
            encoding="utf-8",
        )


INSTRUCTOR = {
    "en": {
        "title": "Instructor Hub",
        "intro": "Public, reproducible delivery kits for facilitated learning.",
        "before": "Before the session",
        "after": "After the session",
        "feedback": "Feedback survey",
    },
    "pt": {
        "title": "Hub do Instrutor",
        "intro": "Kits públicos e reproduzíveis para aprendizagem facilitada.",
        "before": "Antes da sessão",
        "after": "Depois da sessão",
        "feedback": "Pesquisa de feedback",
    },
    "fr": {
        "title": "Hub de l'instructeur",
        "intro": "Kits publics et reproductibles pour l'apprentissage animé.",
        "before": "Avant la session",
        "after": "Après la session",
        "feedback": "Enquête de retour",
    },
}


def instructor_page(lang: str) -> str:
    copy = INSTRUCTOR[lang]
    return f"""# {copy['title']}

{copy['intro']}

```mermaid
flowchart LR
  P[Pre-work] --> B[Before checklist]
  B --> A[Timed agenda]
  A --> E[Evidence and assessment]
  E --> F[Follow-up and feedback]
```

## Delivery formats

| Format | Public kit | Agenda |
|---|---|---|
| 2 hours | Labs 014 + 104 | 15 welcome · 25 concepts · 55 lab · 15 debrief · 10 assessment |
| 4 hours | Labs 014 + 023 + 106 | 20 welcome · 40 concepts · 140 labs · 25 breaks · 35 assessment |
| 4-week cohort | AI-103 route | Weekly pre-work, 90-minute workshop, office hour, evidence review |
| Hackathon | Challenge 012 + Lab 040/042 | Brief, attack/build, mentor checks, demos, rubric |

## Pre-work

- Confirm Python 3.10+, Git, editor, and repository access.
- Run one local test directory without credentials.
- Read the cost guide and accessibility expectations.
- Do not collect private code, personal data, or secrets.

## {copy['before']}

- [ ] Select labs and publish prerequisites.
- [ ] Generate kits with `python scripts/generate_kits.py --check`.
- [ ] Test projector zoom, keyboard navigation, captions, and text alternatives.
- [ ] Prepare a local fallback for every hosted demo.
- [ ] Define timing, breaks, support channel, and escalation owner.

## Timed agenda template

| Minute | Instructor | Learners | Evidence |
|---:|---|---|---|
| 0–10 | Outcomes and safety | Confirm setup | Readiness check |
| 10–30 | Explain model and diagram | Ask questions | Concept poll |
| 30–75 | Facilitate local exercise | Pair implementation | Passing tests |
| 75–100 | Compare Real path | Record cost/cleanup | Decision record |
| 100–115 | Run scored check | Submit answers | Score |
| 115–120 | Close | Commit next step | Exit ticket |

## {copy['after']}

- [ ] Publish only public slides, notes, and links.
- [ ] Remove temporary hosted resources and test data.
- [ ] Share answers after the assessment window.
- [ ] Record accessibility, timing, and content corrections.
- [ ] Triage feedback without storing unnecessary personal data.

## {copy['feedback']}

Use a five-question anonymous survey: confidence before/after, most useful activity, blocker, pace, and one improvement. Report aggregates only.

## Instructor notes and slides

- [2-hour notes](two-hour.md)
- [4-hour notes](four-hour.md)
- [4-week cohort](four-week-cohort.md)
- [Hackathon](hackathon.md)
"""


def write_instructor_hub() -> None:
    formats = {
        "en": {
            "two-hour.md": "# 2-hour instructor notes\n\nUse Labs 014 and 104. Keep the local path mandatory and reserve the final 20 minutes for quiz, evidence, and cleanup.\n",
            "four-hour.md": "# 4-hour instructor notes\n\nUse Labs 014, 023, and 106 with two short breaks. Require a pattern decision record and passing local tests.\n",
            "four-week-cohort.md": "# Four-week cohort\n\nWeek 1: MAF foundations. Week 2: MCP 2026-07-28. Week 3: evaluation and observability. Week 4: production capstone and evidence review.\n",
            "hackathon.md": "# Hackathon guide\n\nTeams attack, defend, validate, and map Challenge 012 before presenting a production design based on Lab 040 or Lab 042.\n",
        },
        "pt": {
            "two-hour.md": "# Notas do instrutor — 2 horas\n\nUse os Labs 014 e 104. Mantenha o caminho local obrigatório e reserve os 20 minutos finais para quiz, evidências e limpeza.\n",
            "four-hour.md": "# Notas do instrutor — 4 horas\n\nUse os Labs 014, 023 e 106 com dois intervalos curtos. Exija registro da decisão de padrão e testes locais aprovados.\n",
            "four-week-cohort.md": "# Coorte de quatro semanas\n\nSemana 1: fundamentos MAF. Semana 2: MCP 2026-07-28. Semana 3: avaliação e observabilidade. Semana 4: capstone e revisão de evidências.\n",
            "hackathon.md": "# Guia do hackathon\n\nAs equipes atacam, defendem, validam e mapeiam o Desafio 012 antes de apresentar um desenho de produção baseado no Lab 040 ou 042.\n",
        },
        "fr": {
            "two-hour.md": "# Notes instructeur — 2 heures\n\nUtilisez les Labs 014 et 104. Gardez le parcours local obligatoire et réservez 20 minutes au quiz, aux preuves et au nettoyage.\n",
            "four-hour.md": "# Notes instructeur — 4 heures\n\nUtilisez les Labs 014, 023 et 106 avec deux pauses. Exigez une décision de patron et des tests locaux réussis.\n",
            "four-week-cohort.md": "# Cohorte de quatre semaines\n\nSemaine 1 : bases MAF. Semaine 2 : MCP 2026-07-28. Semaine 3 : évaluation et observabilité. Semaine 4 : capstone et revue des preuves.\n",
            "hackathon.md": "# Guide du hackathon\n\nLes équipes attaquent, défendent, valident et relient le Défi 012 à OWASP avant un design de production fondé sur le Lab 040 ou 042.\n",
        },
    }
    for lang in LANGS:
        directory = DOCS / lang / "instructor"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.md").write_text(instructor_page(lang), encoding="utf-8")
        for name, content in formats[lang].items():
            (directory / name).write_text(content, encoding="utf-8")


def append_path_section(path: Path, marker: str, content: str) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(replace_marker(text, marker, content), encoding="utf-8")


def write_paths() -> None:
    path_copy = {
        "en": {
            "additions": "Phase 3 additions",
            "focus": "Focus",
            "mcp_lines": ["MCP 2026-07-28.", "MCP Apps.", "attack, defend, map to OWASP."],
            "migration": "Microsoft Agent Framework 1.0 migration",
            "migration_text": "This path is retained as migration context. New implementations use Labs 014, 023, 034, 040, 076, and 106 with Microsoft Agent Framework 1.0.",
            "ai103": "# AI-103 preparation map\n\nUse Labs 009, 030, 035, 042, 049, 074, 099, and 102. The route covers Foundry agents, RAG, evaluation, tracing, fine-tuning decisions, cost, and cleanup.\n",
            "gh600": "# GH-600 preparation map\n\nUse Labs 085–096 plus Labs 104–105 where MCP integration is relevant. Keep repository instructions, testing, security, governance, and measurable delivery evidence explicit.\n",
            "role": "## Phase 3 route\n\nUse Labs 102–106, the modernized Agent Framework/MCP/Foundry labs, and the Instructor Hub delivery formats appropriate to this role.\n",
        },
        "pt": {
            "additions": "Adições da Fase 3",
            "focus": "Foco",
            "mcp_lines": ["MCP 2026-07-28.", "MCP Apps.", "atacar, defender e mapear para OWASP."],
            "migration": "Migração para Microsoft Agent Framework 1.0",
            "migration_text": "Esta trilha é mantida como contexto de migração. Novas implementações usam os Labs 014, 023, 034, 040, 076 e 106 com Microsoft Agent Framework 1.0.",
            "ai103": "# Mapa de preparação AI-103\n\nUse os Labs 009, 030, 035, 042, 049, 074, 099 e 102. A rota cobre agentes Foundry, RAG, avaliação, tracing, decisões de fine-tuning, custo e limpeza.\n",
            "gh600": "# Mapa de preparação GH-600\n\nUse os Labs 085–096 e os Labs 104–105 quando MCP for relevante. Torne explícitas instruções, testes, segurança, governança e evidências mensuráveis.\n",
            "role": "## Rota da Fase 3\n\nUse os Labs 102–106, os labs modernizados de Agent Framework/MCP/Foundry e os formatos do Hub do Instrutor adequados a este perfil.\n",
        },
        "fr": {
            "additions": "Ajouts de Phase 3",
            "focus": "Objectif",
            "mcp_lines": ["MCP 2026-07-28.", "MCP Apps.", "attaquer, défendre et relier à OWASP."],
            "migration": "Migration vers Microsoft Agent Framework 1.0",
            "migration_text": "Ce parcours reste un contexte de migration. Les nouvelles implémentations utilisent les Labs 014, 023, 034, 040, 076 et 106 avec Microsoft Agent Framework 1.0.",
            "ai103": "# Carte de préparation AI-103\n\nUtilisez les Labs 009, 030, 035, 042, 049, 074, 099 et 102. Le parcours couvre agents Foundry, RAG, évaluation, tracing, fine-tuning, coût et nettoyage.\n",
            "gh600": "# Carte de préparation GH-600\n\nUtilisez les Labs 085–096 et 104–105 lorsque MCP est pertinent. Rendez explicites instructions, tests, sécurité, gouvernance et preuves mesurables.\n",
            "role": "## Parcours de Phase 3\n\nUtilisez les Labs 102–106, les labs Agent Framework/MCP/Foundry modernisés et les formats du Hub instructeur adaptés à ce rôle.\n",
        },
    }
    for lang in LANGS:
        copy = path_copy[lang]
        llm = DOCS / lang / "paths" / "llm-foundations" / "index.md"
        append_path_section(
            llm,
            "phase3-path",
            f"""## {copy['additions']}

| Lab | {copy['focus']} |
|---|---|
| [102](../../labs/lab-102-finetuning-rag-prompting-lora.md) | Prompting vs RAG vs LoRA |
| [103](../../labs/lab-103-train-mini-gpt-cpu.md) | Mini-GPT on CPU |
| [042](../../labs/lab-042-enterprise-rag.md) | Enterprise RAG and evaluations |
""",
        )
        mcp = DOCS / lang / "paths" / "mcp" / "index.md"
        append_path_section(
            mcp,
            "phase3-path",
            f"""## {copy['additions']}

- [Lab 104](../../labs/lab-104-mcp-2026-stateless-discovery.md): {copy['mcp_lines'][0]}
- [Lab 105](../../labs/lab-105-mcp-apps-interactive-ui.md): {copy['mcp_lines'][1]}
- [Challenge 012](../../challenges/challenge-012-harden-mcp-server.md): {copy['mcp_lines'][2]}
""",
        )
        sk = DOCS / lang / "paths" / "semantic-kernel" / "index.md"
        append_path_section(
            sk,
            "phase3-path",
            f"""## {copy['migration']}

{copy['migration_text']}
""",
        )
        certifications = DOCS / lang / "paths" / "certifications"
        certifications.mkdir(parents=True, exist_ok=True)
        (certifications / "ai-103.md").write_text(copy["ai103"], encoding="utf-8")
        (certifications / "gh-600.md").write_text(copy["gh600"], encoding="utf-8")
        for role in ("student", "developer", "architect", "data-engineer", "admin"):
            path = DOCS / lang / "paths" / "roles" / f"{role}.md"
            append_path_section(
                path,
                "phase3-role",
                copy["role"],
            )


def write_platform_report() -> None:
    reports = {
        "en": """# Zensical Compatibility Report — Phase 3

**Decision:** retain the current production build until trilingual folder-based i18n is supported without regression.

The migration was re-evaluated against current official Zensical installation, MkDocs migration, and plugin compatibility documentation. The site requires EN/PT/FR folder routing from `mkdocs-static-i18n`, plus search, tags, glightbox, custom JavaScript, CSS, catalog JSON, quizzes, progress, and generated kits. Zensical can read MkDocs configuration and supports several Material surfaces, but its documented compatibility does not provide an equivalent supported path for this repository's folder-based `mkdocs-static-i18n` contract.

Changing the production engine would therefore violate the Phase 3 no-degradation requirement. CI continues to run the strict MkDocs build, while the configuration and content remain migration-ready.

## Re-test gate

Migrate only when a clean Zensical build proves identical EN/PT/FR page counts and routes, navigation, search, tags, glightbox, custom JS/CSS, quizzes, progress, catalogs, and strict internal links.

## Official references

- [Zensical get started](https://zensical.org/docs/get-started/)
- [Migrate from MkDocs](https://zensical.org/docs/compatibility/mkdocs/migration/)
- [Compatible plugins](https://zensical.org/docs/compatibility/mkdocs/plugins/)
""",
        "pt": """# Relatório de Compatibilidade com Zensical — Fase 3

**Decisão:** manter o build atual de produção até existir suporte sem regressão para i18n trilíngue por pastas.

A migração foi reavaliada com a documentação oficial atual de instalação, migração de MkDocs e compatibilidade de plugins do Zensical. O site exige rotas EN/PT/FR por `mkdocs-static-i18n`, além de busca, tags, glightbox, JavaScript, CSS, catálogo JSON, quizzes, progresso e kits. A compatibilidade documentada ainda não fornece caminho equivalente suportado para esse contrato por pastas.

Trocar o mecanismo degradaria o site e violaria a Fase 3. A CI mantém o build estrito do MkDocs e o conteúdo continua pronto para migração.

## Gate para novo teste

Migrar somente quando um build limpo provar contagem e rotas EN/PT/FR idênticas, navegação, busca, tags, glightbox, JS/CSS, quizzes, progresso, catálogos e links internos estritos.

## Referências oficiais

- [Zensical: primeiros passos](https://zensical.org/docs/get-started/)
- [Migração do MkDocs](https://zensical.org/docs/compatibility/mkdocs/migration/)
- [Plugins compatíveis](https://zensical.org/docs/compatibility/mkdocs/plugins/)
""",
        "fr": """# Rapport de compatibilité Zensical — Phase 3

**Décision :** conserver le build actuel jusqu'à un support sans régression de l'i18n trilingue par dossiers.

La migration a été réévaluée avec la documentation officielle actuelle d'installation, migration MkDocs et compatibilité des plugins. Le site exige le routage EN/PT/FR de `mkdocs-static-i18n`, ainsi que recherche, tags, glightbox, JavaScript, CSS, catalogue JSON, quiz, progression et kits. La compatibilité documentée ne fournit pas encore une voie équivalente prise en charge.

Changer de moteur dégraderait le site. La CI conserve le build MkDocs strict et le contenu reste prêt à migrer.

## Porte de nouveau test

Migrer uniquement lorsqu'un build propre prouve des routes et comptes EN/PT/FR identiques, navigation, recherche, tags, glightbox, JS/CSS, quiz, progression, catalogues et liens stricts.

## Références officielles

- [Démarrer avec Zensical](https://zensical.org/docs/get-started/)
- [Migrer depuis MkDocs](https://zensical.org/docs/compatibility/mkdocs/migration/)
- [Plugins compatibles](https://zensical.org/docs/compatibility/mkdocs/plugins/)
""",
    }
    for lang, content in reports.items():
        (DOCS / lang / "zensical-compatibility.md").write_text(content, encoding="utf-8")


def normalize_existing_whats_new_links() -> None:
    for lang in ("pt", "fr"):
        path = DOCS / lang / "whats-new.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"\]\(\.\./paths/([^)]*?)/\)", r"](paths/\1/index.md)", text)
        path.write_text(text, encoding="utf-8")


def write_pages() -> None:
    for lang in LANGS:
        for lab_id, lab in LABS.items():
            page = DOCS / lang / "labs" / f"lab-{lab_id}-{lab['slug']}.md"
            page.write_text(render_lab(lab_id, lab, lang), encoding="utf-8")
            support = DOCS / lang / "labs" / f"lab-{lab_id}"
            support.mkdir(parents=True, exist_ok=True)
            for name, content in support_files(lab_id, lab, lang).items():
                (support / name).write_text(content.rstrip() + "\n", encoding="utf-8")
    write_existing_updates()
    write_challenge()
    write_instructor_hub()
    write_paths()
    write_platform_report()
    normalize_existing_whats_new_links()
    for lang in ("pt", "fr"):
        shutil.copyfile(DOCS / "en" / "js" / "hub-features.js", DOCS / lang / "js" / "hub-features.js")
        shutil.copyfile(DOCS / "en" / "css" / "custom.css", DOCS / lang / "css" / "custom.css")


if __name__ == "__main__":
    write_pages()
    print(f"Generated {len(LABS)} Phase 3 labs, Challenge 012, modernization notes, and instructor content in 3 languages.")
