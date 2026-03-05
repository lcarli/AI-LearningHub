---
tags: [enterprise, microsoft-365, agent-governance, pro-code, mcp, observability]
---
# Lab 046 : Microsoft Agent 365 — Gouvernance des agents en entreprise

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Durée :</strong> ~75 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-azure">Payant — Licence Microsoft 365 Copilot + abonnement Azure + programme Frontier</span></span>
</div>

## Ce que vous apprendrez

- Ce qu'est Microsoft Agent 365 et en quoi il diffère des *frameworks* d'agents
- Comment Agent 365 attribue à chaque agent IA sa propre **Entra Agent Identity**
- Comment installer et configurer le **CLI Agent 365**
- Comment créer un **Agent Blueprint** (le modèle de gouvernance d'entreprise)
- Comment ajouter l'**observabilité (OpenTelemetry)** à un agent Python existant avec le SDK Agent 365
- Comment **publier un agent** dans le Centre d'administration Microsoft 365
- Comment créer une **instance d'agent** qui apparaît dans l'organigramme dans Teams

---

## Introduction

La plupart des frameworks d'agents IA se concentrent sur la *construction* d'agents — comment ils raisonnent, appellent des outils et mémorisent le contexte. **Microsoft Agent 365** résout un problème différent : **comment les entreprises gouvernent, sécurisent et gèrent les agents à grande échelle ?**

Considérez Agent 365 comme le *plan de contrôle* des agents IA dans votre tenant Microsoft 365 :

![Plan de contrôle Agent 365](../../assets/diagrams/agent-365-control-plane.svg)

Un agent amélioré avec Agent 365 obtient :

| Capacité | Ce que cela signifie |
|-----------|--------------|
| **Entra Agent ID** | Sa propre identité dans Azure AD — comme un compte utilisateur, mais pour un agent |
| **Blueprint** | Modèle approuvé par l'IT définissant les capacités, les permissions MCP et les politiques de gouvernance |
| **Notifications** | Peut recevoir et répondre aux @mentions dans Teams, aux e-mails, aux commentaires Word |
| **Outils MCP gouvernés** | Accès à Mail, Calendrier, Teams, SharePoint sous contrôle administrateur |
| **Observabilité** | Traces OpenTelemetry complètes de chaque appel d'outil et inférence LLM |

!!! warning "Programme Preview requis"
    Microsoft Agent 365 est en **preview Frontier**. Vous devez rejoindre le [Microsoft Copilot Frontier Program](https://adoption.microsoft.com/copilot/frontier-program/) et disposer d'au moins une licence **Microsoft 365 Copilot** dans votre tenant.

---

## Architecture : couches d'Agent 365

![Architecture en couches d'Agent 365](../../assets/diagrams/agent-365-layers.svg)

Le SDK Agent 365 se situe *au-dessus* de votre framework d'agent. Il ne le **remplace pas** — il l'enveloppe et l'améliore.

---

## Prérequis

- [ ] **Licence Microsoft 365 Copilot** (au moins 1 dans votre tenant)
- [ ] **Accès au programme Frontier** — [inscrivez-vous ici](https://adoption.microsoft.com/copilot/frontier-program/)
- [ ] **Abonnement Azure** — droits de création de ressources
- [ ] **Permissions Entra ID** — Rôle Administrateur global, Administrateur Agent ID ou Développeur Agent ID
- [ ] **.NET 8.0 ou ultérieur** — pour le CLI Agent 365
- [ ] **Python 3.11+** et pip
- [ ] **Jeton GitHub Models** (gratuit) — pour l'agent OutdoorGear que nous améliorerons

!!! tip "Pas d'accès Frontier ? Suivez quand même"
    Si vous n'avez pas encore accès à Frontier, vous pouvez toujours suivre les étapes 1–4 localement avec des outils simulés. Le fichier de démarrage inclut un mode simulé. Les étapes 5–7 nécessitent un vrai tenant.

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Ouvrir dans GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont préinstallées dans le devcontainer.


## 📦 Fichiers d'accompagnement

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-046/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|------|-------------|----------|
| `a365.config.sample.json` | Fichier de configuration / données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-046/a365.config.sample.json) |
| `broken_observability.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-046/broken_observability.py) |
| `outdoorgear_a365_starter.py` | Script de démarrage avec TODOs | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-046/outdoorgear_a365_starter.py) |

---

## Étape 1 : Installer le CLI Agent 365

Le CLI Agent 365 (`a365`) est l'épine dorsale en ligne de commande pour l'ensemble du cycle de vie de développement des agents.

```bash
# Install (requires .NET 8.0+)
dotnet tool install --global Microsoft.Agents.A365.DevTools.Cli --prerelease

# Verify installation
a365 -h
```

Sortie attendue :
```
Microsoft Agent 365 CLI
Version: x.x.x-preview

Usage: a365 [command] [options]

Commands:
  config      Manage Agent 365 configuration
  setup       Set up agent blueprint and Azure resources
  deploy      Deploy agent code to Azure
  publish     Publish agent to Microsoft 365 admin center
  ...
```

!!! note "Utilisez toujours --prerelease"
    Tant qu'Agent 365 n'est pas en GA, incluez toujours `--prerelease` dans les commandes d'installation/mise à jour. Sans cela, le package ne sera pas trouvé dans les flux NuGet.

---

## Étape 2 : Enregistrer une application cliente personnalisée dans Entra ID

Le CLI a besoin de son propre enregistrement d'application Entra pour s'authentifier auprès de votre tenant.

**Dans le portail Azure → Entra ID → Inscriptions d'applications :**

1. Cliquez sur **Nouvelle inscription**
2. Nom : `Agent365-CLI-App`
3. Types de comptes pris en charge : **Comptes dans cet annuaire organisationnel uniquement**
4. Cliquez sur **Inscrire**
5. Copiez l'**ID d'application (client)** — vous en aurez besoin à l'étape 3
6. Allez dans **Permissions d'API → Ajouter une permission → Microsoft Graph**
7. Ajoutez ces **Permissions d'application** :
   - `AgentLifecycle.ReadWrite.All`
   - `Application.ReadWrite.All`
8. Cliquez sur **Accorder le consentement administrateur**

```bash
# Verify you can authenticate
az login --tenant YOUR_TENANT_ID
```

---

## Étape 3 : Initialiser la configuration Agent 365

```bash
# Create a new Agent 365 config
a365 config init
```

Le CLI vous demandera :
- L'ID du tenant
- L'ID de l'abonnement Azure
- Le nom du groupe de ressources
- L'ID de l'application cliente de l'étape 2
- L'URL du point de terminaison de messagerie de votre agent

Cela crée un fichier `a365.config.json` dans le répertoire de votre projet :

```json
{
  "tenantId": "YOUR_TENANT_ID",
  "subscriptionId": "YOUR_SUBSCRIPTION_ID",
  "resourceGroup": "rg-outdoorgear-agent",
  "clientAppId": "YOUR_CLIENT_APP_ID",
  "agentMessagingEndpoint": "https://your-agent.azurewebsites.net/api/messages",
  "agentBlueprintName": "OutdoorGearAgent",
  "mcpPermissions": [
    "mail.read",
    "calendar.readwrite",
    "teams.message.send"
  ]
}
```

!!! tip "Utilisez l'exemple de configuration"
    Le lab inclut `lab-046/a365.config.sample.json` comme référence. Copiez-le, remplissez vos valeurs, renommez-le en `a365.config.json`.

---

## Étape 4 : Ajouter le SDK Agent 365 à votre agent Python

Installez les packages du SDK Agent 365 :

```bash
pip install openai \
  microsoft-agents-a365-observability-core \
  microsoft-agents-a365-observability-extensions-openai \
  microsoft-agents-a365-notifications \
  microsoft-agents-a365-tooling \
  microsoft-agents-a365-tooling-extensions-openai
```

### 4a. Ajouter l'observabilité (OpenTelemetry)

Le SDK instrumente automatiquement votre agent pour le SDK OpenAI Agents :

```python
from openai import AsyncOpenAI
from agents import Agent, Runner
from microsoft.agents.a365.observability.core import A365ObservabilityProvider
from microsoft.agents.a365.observability.extensions.openai import OpenAIAgentInstrumentation

# Initialize observability
observability = A365ObservabilityProvider(
    service_name="OutdoorGearAgent",
    service_version="1.0.0",
    exporter_endpoint="https://your-otel-collector.endpoint"
)

# Auto-instrument the OpenAI Agents SDK
instrumentation = OpenAIAgentInstrumentation(provider=observability)
instrumentation.instrument()

# Every agent run is now traced automatically!
```

### 4b. Ajouter les outils MCP gouvernés

Connectez-vous aux serveurs MCP Microsoft 365 (Mail, Calendrier, Teams) sous contrôle administrateur :

```python
from microsoft.agents.a365.tooling import A365ToolingClient
from microsoft.agents.a365.tooling.extensions.openai import OpenAIMcpRegistrationService

async def setup_m365_tools(agent: Agent) -> Agent:
    """Register governed M365 MCP tools to an existing agent."""
    
    tooling_client = A365ToolingClient(
        agent_id="YOUR_ENTRA_AGENT_ID",
        tenant_id="YOUR_TENANT_ID"
    )
    
    # Get available governed MCP servers for this agent
    mcp_servers = await tooling_client.get_mcp_servers()
    
    # Register with OpenAI Agents SDK
    registration_service = OpenAIMcpRegistrationService(agent)
    for server in mcp_servers:
        await registration_service.register(server)
    
    return agent
```

### 4c. Ajouter les notifications (Teams / Outlook)

Faites en sorte que votre agent réponde aux @mentions et aux e-mails :

```python
from microsoft.agents.a365.notifications import A365NotificationHandler

class OutdoorGearNotificationHandler(A365NotificationHandler):
    
    async def on_teams_mention(self, context):
        """Called when @OutdoorGearAgent is mentioned in Teams."""
        user_message = context.activity.text
        # Pass to your agent's run loop
        response = await Runner.run(
            self.agent,
            input=user_message,
            context=context
        )
        await context.send_activity(response.final_output)
    
    async def on_email_received(self, context):
        """Called when agent mailbox receives an email."""
        subject = context.activity.subject
        body = context.activity.body
        # Handle email queries
        response = await Runner.run(
            self.agent,
            input=f"Email subject: {subject}\n\n{body}"
        )
        await context.reply_to_email(response.final_output)
```

---

## Étape 5 : Créer l'Agent Blueprint

Le blueprint est le modèle d'entreprise approuvé par l'IT pour votre agent. Créez-le avec une seule commande CLI :

```bash
a365 setup
```

Cette commande :
1. Crée un **Azure Entra Agent ID** (principal de service pour votre agent)
2. Enregistre les **permissions d'outils MCP** de l'agent telles que définies dans `a365.config.json`
3. Crée l'**Agent Blueprint** dans Azure
4. Génère un `blueprintId` dont vous aurez besoin pour la publication

```
✅ Agent identity created: OutdoorGearAgent (ID: agt-12345-...)
✅ MCP permissions registered: mail.read, calendar.readwrite, teams.message.send
✅ Blueprint created: OutdoorGearAgent-Blueprint-v1
   Blueprint ID: bpnt-67890-...
```

---

## Étape 6 : Déployer le code de l'agent sur Azure

Si vous n'avez pas de déploiement Azure existant :

```bash
# Deploy to Azure App Service
a365 deploy --target azure-app-service --resource-group rg-outdoorgear-agent

# Or deploy to Azure Container Apps
a365 deploy --target azure-container-apps --resource-group rg-outdoorgear-agent
```

Votre agent doit être accessible à l'URL du point de terminaison de messagerie que vous avez définie dans `a365.config.json`.

---

## Étape 7 : Publier dans le Centre d'administration Microsoft 365

```bash
a365 publish --blueprint-id bpnt-67890-...
```

Après la publication :

1. Allez dans le [Centre d'administration Microsoft 365](https://admin.microsoft.com) → **Agents**
2. Trouvez **OutdoorGearAgent** dans le registre
3. Cliquez sur **Créer une instance** pour instancier l'agent pour votre organisation
4. L'agent obtient :
   - Sa propre entrée dans votre organigramme
   - Une adresse e-mail (`outdoorgear-agent@yourorg.com`)
   - La possibilité d'être @mentionné dans Teams
   - Une visibilité dans la **carte des agents** (qui l'utilise, quelles données il accède)

!!! info "L'agent apparaît dans Teams en quelques minutes"
    Après la création d'une instance, votre agent apparaît dans la recherche Teams. Les utilisateurs peuvent le @mentionner dans les conversations et les canaux. Il apparaît également dans les contacts Outlook.

---

## 🐛 Exercice de correction de bugs : Corriger la configuration d'observabilité cassée

Le lab inclut une configuration d'observabilité cassée. Trouvez et corrigez 3 bugs !

```
lab-046/
└── broken_observability.py    ← 3 bugs intentionnels à trouver et corriger
```

**Installation :**
```bash
pip install microsoft-agents-a365-observability-core \
            microsoft-agents-a365-observability-extensions-openai

python lab-046/broken_observability.py
```

**Les 3 bugs :**

| # | Composant | Symptôme | Type |
|---|-----------|---------|------|
| 1 | `A365ObservabilityProvider` | `TypeError: missing required argument 'service_name'` | Paramètre requis manquant |
| 2 | `OpenAIAgentInstrumentation` | Les traces affichent `service_name: unknown` au lieu de `OutdoorGearAgent` | Provider non passé à l'instrumentation |
| 3 | Point de terminaison de l'exporteur | `ConnectionRefusedError: localhost:4317` | Mauvais point de terminaison — devrait utiliser un collecteur HTTPS |

**Vérifiez vos corrections :** Après avoir corrigé les 3 bugs, exécutez :
```bash
python lab-046/broken_observability.py
# Expected:
# ✅ ObservabilityProvider initialized: OutdoorGearAgent v1.0.0
# ✅ Instrumentation active — traces will include service_name: OutdoorGearAgent
# ✅ Exporter endpoint validated: https://...
# 🎉 Observability configured correctly!
```

---


## 🧠 Quiz de connaissances

??? question "**Q1 (Choix multiple) :** Un agent construit avec LangChain souhaite utiliser Microsoft Agent 365. Qu'est-ce qu'Agent 365 fournit que LangChain ne fournit PAS ?"

    - A) La capacité d'appeler des API et des outils externes
    - B) Le raisonnement et la planification en plusieurs étapes
    - C) Une identité Entra, des outils MCP gouvernés, l'observabilité et la gouvernance/conformité d'entreprise
    - D) Un meilleur modèle LLM pour le raisonnement

    ??? success "✅ Révéler la réponse"
        **Correct : C**

        Agent 365 n'est PAS un framework d'agent — il n'aide pas à construire la logique de raisonnement. LangChain gère déjà l'appel d'outils, le raisonnement en plusieurs étapes et la planification. Ce qu'Agent 365 ajoute, c'est la **couche entreprise** : une identité Entra unique pour l'agent, un accès MCP gouverné approuvé par l'IT aux charges de travail M365, l'observabilité OpenTelemetry, la gouvernance basée sur les blueprints, et la capacité pour les administrateurs IT de voir, surveiller et contrôler l'agent depuis le Centre d'administration M365.

??? question "**Q2 (Choix multiple) :** Qu'est-ce qu'un Agent Blueprint dans Microsoft Agent 365 ?"

    - A) Un modèle Bicep/ARM pour déployer des ressources Azure
    - B) Un modèle préconfiguré approuvé par l'IT définissant les capacités d'un agent, les permissions MCP, les politiques de gouvernance et les contraintes de conformité
    - C) Une classe Python dont tous les agents Agent 365 doivent hériter
    - D) Un diagramme du flux d'appels d'outils de l'agent

    ??? success "✅ Révéler la réponse"
        **Correct : B**

        Un blueprint provient de Microsoft Entra et constitue le *modèle d'entreprise* à partir duquel des instances d'agents conformes sont créées. Il définit ce que l'agent peut faire (capacités), quelles données M365 il peut accéder (permissions MCP), comment il est gouverné (politiques DLP, restrictions d'accès externe, règles de journalisation) et les métadonnées de cycle de vie. Chaque instance d'agent créée à partir du blueprint hérite de toutes ces règles — garantissant qu'aucun « agent fantôme » n'a un accès non contrôlé.

??? question "**Q3 (Exécutez le lab) :** Ouvrez `lab-046/outdoorgear_a365_starter.py`. Combien de commentaires TODO y a-t-il dans le fichier ?"

    Ouvrez le fichier de démarrage et comptez les marqueurs `# TODO`.

    ??? success "✅ Révéler la réponse"
        **5 TODOs**

        Le fichier de démarrage comporte 5 points d'intégration à compléter :
        1. TODO 1 : Initialiser `A365ObservabilityProvider` avec le nom et la version du service
        2. TODO 2 : Appliquer `OpenAIAgentInstrumentation` pour auto-instrumenter les traces
        3. TODO 3 : Implémenter le gestionnaire `on_teams_mention`
        4. TODO 4 : Se connecter aux serveurs d'outils MCP gouvernés
        5. TODO 5 : Enregistrer l'Entra Agent ID de l'agent

??? question "**Q4 (Choix multiple) :** Un utilisateur @mentionne votre agent OutdoorGear dans un canal Teams. Quel composant du SDK Agent 365 reçoit et achemine cette notification vers votre code d'agent ?"

    - A) `A365ObservabilityProvider`
    - B) `A365ToolingClient`
    - C) `A365NotificationHandler`
    - D) `OpenAIMcpRegistrationService`

    ??? success "✅ Révéler la réponse"
        **Correct : C — `A365NotificationHandler`**

        Le `A365NotificationHandler` reçoit les événements des applications Microsoft 365 — @mentions Teams, e-mails entrants dans la boîte aux lettres de l'agent, notifications de commentaires Word, et plus encore. Vous le sous-classez et redéfinissez des méthodes comme `on_teams_mention()` et `on_email_received()`. Le `A365ObservabilityProvider` gère la télémétrie, `A365ToolingClient` gère l'accès aux outils MCP, et `OpenAIMcpRegistrationService` enregistre les serveurs MCP avec le SDK OpenAI Agents.

---

## Résumé

| Concept | Point clé |
|---------|-------------|
| **Agent 365 ≠ framework d'agent** | Il ajoute des *capacités d'entreprise* par-dessus votre agent existant — ne remplace pas SK, LangChain, etc. |
| **Entra Agent ID** | Chaque agent obtient sa propre identité — comme un compte utilisateur mais pour un agent |
| **Blueprint** | Modèle approuvé par l'IT ; toutes les instances héritent de ses règles de gouvernance |
| **Observabilité** | Auto-instrumentation OpenTelemetry — chaque appel d'outil et inférence LLM est tracé |
| **MCP gouverné** | Outils M365 (Mail, Calendrier, Teams, SharePoint) accessibles sous contrôle IT |
| **Notifications** | Les agents peuvent être @mentionnés dans Teams, recevoir des e-mails, répondre aux commentaires Word |
| **Frontier requis** | Encore en preview — nécessite une licence M365 Copilot + inscription au programme Frontier |

---

## Prochaines étapes

- **Construisez d'abord l'agent sous-jacent :** → [Lab 016 — OpenAI Agents SDK](lab-016-openai-agents-sdk.md)
- **Ajoutez des outils MCP à votre agent :** → [Lab 020 — Serveur MCP en Python](lab-020-mcp-server-python.md)
- **Approfondissement de l'observabilité :** → [Lab 033 — Observabilité des agents avec App Insights](lab-033-agent-observability.md)
- **Pipeline RAG d'entreprise :** → [Lab 042 — RAG d'entreprise avec évaluations](lab-042-enterprise-rag.md)
