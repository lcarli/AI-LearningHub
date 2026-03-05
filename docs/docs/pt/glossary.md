# Glossário

Termos comuns usados ao longo do Hub de Aprendizado de Agentes de IA, organizados alfabeticamente.

---

## A

**Agent**
Um sistema de software que percebe seu ambiente, toma decisões e executa ações para alcançar um objetivo. Agentes de IA usam LLMs como motor de raciocínio combinados com ferramentas, memória e planejamento.

**AgentGroupChat**
Uma construção do Semantic Kernel que permite que múltiplos agentes colaborem em uma conversa compartilhada. Cada agente vê o histórico da conversa e pode responder, delegar ou chamar ferramentas.

**Agentic RAG**
Uma extensão do RAG básico onde um agente decide *quando* recuperar informações, *qual* consulta usar e *se* deve recuperar novamente caso o primeiro resultado seja insuficiente.

**ARM Template**
Template do Azure Resource Manager — um arquivo JSON que descreve declarativamente a infraestrutura do Azure. Pode ser implantado com o botão "Deploy to Azure".

---

## B

**Bicep**
Uma linguagem específica de domínio (DSL) para infraestrutura como código no Azure. Compila para ARM JSON. Sintaxe mais limpa que templates JSON brutos. Usada na pasta `infra/` deste repositório.

**Chunking**
O processo de dividir um documento grande em partes menores antes de gerar embeddings e indexar. O tamanho do chunk afeta a qualidade da recuperação — muito pequeno perde contexto, muito grande perde precisão.

---

## C

**Chat Participant**
Um conceito de extensão do VS Code — um `@agent` personalizado que se conecta ao GitHub Copilot Chat. Registrado via `contributes.chatParticipants` no `package.json`.

**Completion**
Uma resposta de um LLM dado um prompt de entrada. Também chamado de "geração" ou "inferência."

**Copilot Extension**
Uma integração do GitHub que adiciona um agente personalizado ao GitHub Copilot no github.com, VS Code e outras superfícies. Requer um endpoint de API (webhooks).

**Context Window**
A quantidade máxima de texto (medida em tokens) que um LLM pode processar em uma única requisição. Em 2025, varia de 8k (modelos pequenos) a 1M+ tokens (Gemini 1.5).

---

## D

**Dense Embedding**
Uma representação vetorial numérica de texto, onde textos semanticamente similares têm vetores similares. Produzido por modelos de embedding como `text-embedding-3-small`.

**Document Grounding**
Fornecer documentos recuperados ao LLM como contexto, para que a resposta seja baseada em fontes específicas em vez dos dados de treinamento do modelo. Reduz alucinações.

---

## E

**Embedding**
Um vetor numérico de comprimento fixo que captura o significado semântico do texto. Veja [Lab 007 — O que são Embeddings?](labs/lab-007-what-are-embeddings.md).

**Embedding Model**
Um modelo que converte texto em embeddings. Exemplos: `text-embedding-3-small` (OpenAI), `text-embedding-ada-002`, `nomic-embed-text` (local/Ollama).

---

## F

**Function Calling**
Um recurso de LLM onde o modelo pode solicitar a chamada de uma função específica com argumentos estruturados, em vez de retornar texto simples. Também chamado de "uso de ferramentas."

**Foundry Agent Service**
Serviço gerenciado da Microsoft para implantar agentes de IA com integração de ferramentas, rastreamento e avaliação integrados. Parte do Azure AI Foundry.

---

## G

**GitHub Models**
Um serviço gratuito (github.com/marketplace/models) que fornece acesso à API de LLMs líderes (GPT-4o, Llama 3, etc.) usando um token do GitHub. Sem necessidade de cartão de crédito.

**Grounding**
Veja *Document Grounding*.

---

## H

**Hallucination**
Quando um LLM gera uma saída que soa confiante, mas é factualmente incorreta. Grounding com RAG reduz alucinações ao fornecer documentos de origem precisos.

**Hybrid Search**
Combinação de busca por vetores densos (similaridade semântica) com busca por palavras-chave esparsas (BM25/texto completo) para melhor recuperação. Geralmente pontuado com Reciprocal Rank Fusion (RRF).

---

## I

**Intent Classification**
Determinar o que um usuário deseja a partir de sua mensagem. Agentes usam isso para rotear para o especialista, ferramenta ou fluxo de trabalho correto.

---

## K

**Kernel (Semantic Kernel)**
O objeto de orquestração central no Semantic Kernel. Contém serviços de IA, plugins, memória e planejadores. Ponto de entrada para todas as operações do SK.

---

## L

**Language Model API (VS Code)**
`vscode.lm` — uma API que permite que extensões do VS Code usem o LLM que alimenta o Copilot, sem precisar de uma chave de API separada. Disponível no VS Code 1.90+.

**LLM**
Large Language Model (Modelo de Linguagem de Grande Porte) — um modelo de deep learning treinado em grandes conjuntos de dados textuais para compreender e gerar linguagem humana. Exemplos: GPT-4o, Claude 3.5, Llama 3.

---

## M

**MCP (Model Context Protocol)**
Um padrão aberto da Anthropic para conectar modelos de IA a ferramentas e fontes de dados externas por meio de um protocolo estruturado. Veja [Lab 012 — O que é MCP?](labs/lab-012-what-is-mcp.md).

**MCP Server**
Um processo que expõe ferramentas e recursos para agentes de IA por meio do protocolo MCP. Pode ser local ou remoto. Escrito em Python, TypeScript, C#, etc.

**Memory (agent)**
A capacidade de um agente de armazenar e recuperar informações. Tipos: *in-context* (dentro do prompt), *external* (banco de dados vetorial, armazenamento chave-valor), *episodic* (histórico de conversas).

**Multi-Agent System**
Uma arquitetura onde múltiplos agentes especializados colaboram para resolver uma tarefa. Inclui um orquestrador que roteia requisições e especialistas que lidam com trabalho específico de domínio.

---

## O

**Ollama**
Uma ferramenta open-source para executar LLMs localmente no seu laptop. Suporta Llama, Mistral, Phi, Gemma e mais de 100 modelos. Completamente gratuito, sem necessidade de internet.

**Orchestrator**
Um agente cuja função principal é entender a intenção do usuário e delegar sub-tarefas a agentes especialistas ou ferramentas.

---

## P

**pgvector**
Uma extensão open-source do PostgreSQL que adiciona tipos de dados vetoriais e busca por similaridade. Permite armazenar embeddings diretamente em um banco de dados Postgres.

**Planner (Semantic Kernel)**
Um componente que decompõe um objetivo de alto nível em uma sequência de passos, cada um mapeado para uma função de plugin disponível. Exemplos: `FunctionChoiceBehavior.Auto()`.

**Plugin (Semantic Kernel)**
Uma classe com métodos decorados com `@kernel_function`. Exposta ao LLM como ferramentas chamáveis. Equivalente a "tools" ou "functions" na terminologia da OpenAI.

**Prompt Engineering**
A prática de criar prompts eficazes para guiar o comportamento do LLM. Inclui prompts de sistema, exemplos few-shot, cadeia de pensamento e formatação de saída. Veja [Lab 005](labs/lab-005-prompt-engineering.md).

**Prompt Injection**
Um ataque onde conteúdo malicioso em dados externos (documentos, entrada do usuário) sobrescreve as instruções do agente. Uma preocupação de segurança chave para sistemas RAG e agênticos.

---

## R

**RAG (Retrieval Augmented Generation)**
Um padrão que aprimora as respostas do LLM recuperando primeiro documentos relevantes de uma base de conhecimento e incluindo-os no prompt. Veja [Lab 006 — O que é RAG?](labs/lab-006-what-is-rag.md).

**Reranking**
Uma etapa de segunda passagem após a recuperação inicial que reordena os resultados por relevância usando um modelo cross-encoder. Melhora a precisão ao custo de latência adicional.

**Row Level Security (RLS)**
Um recurso do PostgreSQL que restringe quais linhas um usuário do banco de dados pode ver. Política definida em SQL: `CREATE POLICY ... USING (customer_id = current_user)`. Veja [Lab 032](labs/lab-032-row-level-security.md).

---

## S

**Semantic Kernel (SK)**
SDK open-source da Microsoft para construir agentes de IA em Python, C# e Java. Fornece kernels, plugins, memória, planejadores e padrões multi-agente.

**Semantic Search**
Encontrar resultados com base no significado/intenção em vez de correspondência exata de palavras-chave. Usa similaridade vetorial (cosseno, produto escalar) em embeddings.

**Sparse Embedding**
Um vetor de alta dimensionalidade onde a maioria dos valores é zero. Usado em busca por palavras-chave/BM25. Contrasta com *dense embedding*.

**Streaming**
Retornar a saída do LLM token por token à medida que é gerada, em vez de esperar pela resposta completa. Melhora a percepção de latência.

**System Prompt**
Instruções dadas ao LLM no início de uma conversa que definem sua persona, capacidades e restrições. Não visível para o usuário na maioria das interfaces.

---

## T

**Temperature**
Um parâmetro (0.0–2.0) que controla a aleatoriedade do LLM. 0 = determinístico (melhor para saída estruturada), 1 = equilibrado, >1 = mais criativo/aleatório.

**Token**
A unidade básica de texto processada por um LLM. Aproximadamente 3/4 de uma palavra em inglês. Custos e limites de contexto são medidos em tokens.

**Tool Calling**
Veja *Function Calling*.

**Top-K / Top-P**
Estratégias de amostragem para saída de LLM. Top-K: considerar apenas os K próximos tokens mais prováveis. Top-P (amostragem de núcleo): considerar tokens cuja probabilidade cumulativa excede P.

---

## V

**Vector Database**
Um banco de dados otimizado para armazenar e consultar embeddings por similaridade. Exemplos: pgvector, ChromaDB, Pinecone, Weaviate, Azure AI Search.

**Vector Search**
Encontrar os vetores mais próximos (embeddings mais similares) a um vetor de consulta usando métricas como similaridade de cosseno ou distância L2.

---

## W

**Webhook**
Um endpoint HTTP que recebe eventos de um serviço externo. GitHub Copilot Extensions usam webhooks para receber mensagens de chat e retornar respostas.

---

## Acrônimos Comuns

| Acrônimo | Nome Completo |
|----------|---------------|
| AI | Artificial Intelligence (Inteligência Artificial) |
| API | Application Programming Interface (Interface de Programação de Aplicações) |
| BM25 | Best Match 25 (algoritmo de pontuação por palavras-chave) |
| CE | Conformité Européenne (certificação de segurança) |
| CLI | Command Line Interface (Interface de Linha de Comando) |
| CV | Computer Vision (Visão Computacional) |
| DI | Dependency Injection (Injeção de Dependência) |
| DSL | Domain-Specific Language (Linguagem Específica de Domínio) |
| GPT | Generative Pre-trained Transformer (Transformador Pré-treinado Generativo) |
| JSON | JavaScript Object Notation (Notação de Objetos JavaScript) |
| JWT | JSON Web Token |
| LLM | Large Language Model (Modelo de Linguagem de Grande Porte) |
| MCP | Model Context Protocol (Protocolo de Contexto de Modelo) |
| ML | Machine Learning (Aprendizado de Máquina) |
| NLP | Natural Language Processing (Processamento de Linguagem Natural) |
| RAG | Retrieval Augmented Generation (Geração Aumentada por Recuperação) |
| RLS | Row Level Security (Segurança em Nível de Linha) |
| RRF | Reciprocal Rank Fusion (Fusão de Classificação Recíproca) |
| SDK | Software Development Kit (Kit de Desenvolvimento de Software) |
| SK | Semantic Kernel |
| SQL | Structured Query Language (Linguagem de Consulta Estruturada) |

---

*Faltando algum termo? [Abra uma issue](https://github.com/lcarli/AI-LearningHub/issues/new) ou envie um PR!*
