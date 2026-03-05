# Prérequis & comptes

Cette page vous indique exactement quels comptes et outils sont nécessaires pour chaque niveau de lab — et comment les obtenir gratuitement.

---

## Référence rapide

| Ce que vous avez | Ce que vous pouvez exécuter |
|------------------|----------------------------|
| Rien (juste un navigateur) | Labs L50 |
| Compte GitHub gratuit | Labs L50, L100, L200 |
| Compte GitHub gratuit + locataire développeur M365 | L50–L200 + labs Teams |
| Essai gratuit Azure (crédit de 200 $) | La plupart des labs L300 |
| Abonnement Azure (paiement à l'utilisation) | Tous les labs, y compris L400 |

---

## 1. Compte GitHub (gratuit)

**Requis pour :** L100 et au-dessus.

Inscrivez-vous sur [github.com](https://github.com/signup) — c'est gratuit, sans carte bancaire.

Avec un compte GitHub gratuit, vous avez accès à :

- ✅ **GitHub Copilot niveau gratuit** — 2 000 complétions de code/mois + 50 messages de chat/mois
- ✅ **GitHub Models** — API d'inférence gratuite pour GPT-4o, Llama, Phi, et plus (avec limites de débit)
- ✅ **GitHub Codespaces** — 60 heures/mois d'environnement de développement cloud gratuit
- ✅ **GitHub Actions** — 2 000 minutes/mois de CI/CD gratuit

!!! tip "GitHub Copilot pour les étudiants"
    Si vous êtes étudiant, obtenez **GitHub Copilot Pro gratuitement** via le [GitHub Student Developer Pack](https://education.github.com/pack).

---

## 2. GitHub Models (inférence LLM gratuite)

**Requis pour :** Les labs L200 qui utilisent des LLM sans Azure.

GitHub Models fournit un accès API gratuit aux LLM de pointe depuis votre compte GitHub. Aucune carte bancaire requise.

**Configuration :**

1. Allez sur [github.com/marketplace/models](https://github.com/marketplace/models)
2. Choisissez un modèle (par ex., `gpt-4o`, `Phi-4`, `Llama-3.3-70B`)
3. Cliquez sur **« Use this model »** → **« Get API key »** pour obtenir votre jeton d'accès personnel
4. Stockez-le comme `GITHUB_TOKEN` dans votre environnement

**Les modèles disponibles incluent :**
- OpenAI : `gpt-4o`, `gpt-4o-mini`, `o1-mini`
- Meta : `Llama-3.3-70B-Instruct`, `Llama-3.2-90B-Vision`
- Microsoft : `Phi-4`, `Phi-3.5-MoE`
- Mistral : `Mistral-Large`

!!! warning "Limites de débit"
    GitHub Models est limité en débit pour les comptes gratuits. Pour les besoins des labs, c'est largement suffisant. Si vous atteignez les limites, attendez quelques minutes et réessayez.

---

## 3. Compte Azure gratuit

**Requis pour :** Les labs L300.

Azure offre un compte gratuit avec :

- ✅ **200 $ de crédit** pendant 30 jours
- ✅ **12 mois** de services gratuits populaires
- ✅ **Services toujours gratuits** (comprend du calcul, du stockage, de l'IA)

Inscrivez-vous sur [azure.microsoft.com/free](https://azure.microsoft.com/free) — nécessite une carte bancaire pour la vérification d'identité, mais vous ne serez pas facturé pendant la période gratuite.

!!! note "Azure pour les étudiants"
    Les étudiants obtiennent **100 $ de crédit** **sans carte bancaire** via [Azure for Students](https://azure.microsoft.com/free/students).

### Services Azure utilisés dans les labs L300

| Service | Niveau gratuit ? | Notes |
|---------|-----------------|-------|
| Azure AI Foundry | ✅ Oui (limité) | Certains modèles nécessitent le paiement à l'utilisation |
| Azure Database for PostgreSQL Flexible Server | ✅ Oui (Burstable B1ms) | Extension pgvector disponible |
| Azure Container Apps | ✅ Oui (limité) | Pour héberger les serveurs MCP |
| Application Insights | ✅ Oui (5 Go/mois) | Pour les labs d'observabilité |

---

## 4. Abonnement Azure (paiement à l'utilisation)

**Requis pour :** Les labs L400 et une utilisation plus intensive des L300.

Après l'expiration de vos crédits gratuits, vous aurez besoin d'un abonnement **paiement à l'utilisation**.

!!! danger "Surveillez vos coûts"
    Les labs L400 utilisent des services plus coûteux. Chaque lab inclut un coût mensuel estimé en haut de page. **Définissez toujours des alertes de budget** dans le portail Azure.

    → [Comment définir une alerte de budget dans Azure](https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-acm-create-budgets)

---

## 5. Locataire développeur Microsoft 365 (optionnel)

**Requis pour :** Les labs du parcours **Agent Builder — Teams**.

Obtenez un abonnement développeur M365 gratuit :

1. Rejoignez le [Microsoft 365 Developer Program](https://developer.microsoft.com/microsoft-365/dev-program) (gratuit)
2. Configurez un bac à sable instantané avec 25 licences utilisateur
3. Utilisez-le pour les labs Teams AI Library et Copilot Studio

---

## 6. Outils de développement local

Tous les labs de programmation supposent que vous avez installé localement ces outils (tous gratuits) :

| Outil | Lien d'installation | Labs |
|-------|---------------------|------|
| **VS Code** | [code.visualstudio.com](https://code.visualstudio.com) | Tous les labs de programmation |
| **Python 3.11+** | [python.org](https://python.org) | Labs Python |
| **.NET 8 SDK** | [dotnet.microsoft.com](https://dotnet.microsoft.com/download) | Labs C# |
| **Docker Desktop** | [docker.com](https://www.docker.com/products/docker-desktop/) | Labs avec PostgreSQL local |
| **Node.js 20+** | [nodejs.org](https://nodejs.org) | Certains labs MCP |
| **Git** | [git-scm.com](https://git-scm.com) | Tous les labs |

!!! tip "Utilisez GitHub Codespaces pour éviter la configuration locale"
    De nombreux labs incluent un bouton **Ouvrir dans Codespaces**. Cela vous donne un environnement de développement cloud entièrement configuré dans votre navigateur — inclus dans le niveau gratuit de GitHub (60 h/mois).

---

## Tableau récapitulatif

| Niveau | Comptes nécessaires | Coût estimé |
|--------|--------------------|--------------------|
| <span class="level-badge level-50">L50</span> | Aucun | Gratuit |
| <span class="level-badge level-100">L100</span> | GitHub (gratuit) | Gratuit |
| <span class="level-badge level-200">L200</span> | GitHub (gratuit) | Gratuit |
| <span class="level-badge level-300">L300</span> | GitHub + essai gratuit Azure | ~0–10 $/lab |
| <span class="level-badge level-400">L400</span> | GitHub + Azure payant | ~10–50 $/lab |
