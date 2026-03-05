---
tags: [security, apim, mcp, oauth, enterprise, governance]
---
# Lab 064 : Sécuriser MCP à grande échelle avec Azure API Management

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Durée :</strong> ~90 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Données de serveur simulées (aucun abonnement Azure requis)</span>
</div>

## Ce que vous apprendrez

- Utiliser **Azure API Management (APIM)** comme passerelle centralisée pour les serveurs MCP
- Appliquer l'authentification **OAuth 2.0** sur tous les points de terminaison MCP
- Appliquer la **limitation de débit**, les **politiques DLP** et la **journalisation** au trafic MCP
- Auditer la conformité des serveurs MCP entre les équipes et identifier les failles de sécurité
- Analyser les **taux d'erreur**, la **latence** et les **volumes d'appels** à travers une flotte MCP

!!! abstract "Prérequis"
    Complétez d'abord **[Lab 012 : Qu'est-ce que MCP ?](lab-012-what-is-mcp.md)** et **[Lab 020 : Serveur MCP (Python)](lab-020-mcp-server-python.md)**. Ce lab suppose une familiarité avec l'architecture MCP et les modèles de service d'outils.

## Introduction

À mesure que les organisations déploient leurs agents IA à grande échelle, le nombre de **serveurs MCP** croît rapidement — chaque équipe construit le sien, avec des schémas d'authentification, des limites de débit et des contrôles de prévention de perte de données (DLP) différents. Sans gouvernance centralisée, vous vous retrouvez avec un ensemble hétérogène de politiques de sécurité incohérentes.

**Azure API Management** résout ce problème en se plaçant devant tous les serveurs MCP en tant que passerelle unifiée :

| Préoccupation | Sans APIM | Avec APIM |
|---------------|-----------|-----------|
| **Authentification** | Chaque serveur gère la sienne (clé API, basic, OAuth…) | OAuth 2.0 centralisé avec Azure AD |
| **Limitation de débit** | Aucune limite ou limites incohérentes par serveur | Politique uniforme sur tous les points de terminaison |
| **DLP** | Aucune analyse des entrées/sorties d'outils | Inspection du contenu et masquage des PII |
| **Surveillance** | Logs dispersés, pas de vue unifiée | Métriques, alertes et tableaux de bord centralisés |

### Le scénario

Vous êtes un **ingénieur en sécurité de plateforme** dans une entreprise exécutant **10 serveurs MCP** à travers **6 équipes**. La direction souhaite un rapport de conformité : quels serveurs respectent le niveau de sécurité de base (OAuth + DLP + journalisation), lesquels ne le font pas, et à quoi ressemble l'exposition aux risques.

Vous disposez d'un jeu de données d'inventaire de flotte avec les types d'authentification, les limites de débit, le statut DLP, le statut de journalisation, les volumes d'appels, la latence et les taux d'erreur.

---

## Prérequis

| Exigence | Pourquoi |
|----------|----------|
| Python 3.10+ | Exécuter les scripts d'analyse |
| `pandas` | Analyser les données de la flotte de serveurs |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-064/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|---------|-------------|-------------|
| `broken_apim.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-064/broken_apim.py) |
| `mcp_servers.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-064/mcp_servers.csv) |

---

## Étape 1 : Comprendre le modèle de sécurité APIM

Lorsqu'APIM se place devant les serveurs MCP, chaque appel d'outil passe par un pipeline de politiques :

```
Agent → APIM Gateway → [Auth Policy] → [Rate Limit] → [DLP Scan] → MCP Server
                                                                        ↓
Agent ← APIM Gateway ← [Response DLP] ← [Logging] ←────────────── Response
```

Politiques clés pour MCP :

| Politique | Objectif | Exemple |
|-----------|----------|---------|
| **validate-jwt** | Vérifier les jetons OAuth 2.0 | Rejeter les appels sans jeton Azure AD valide |
| **rate-limit-by-key** | Limiter le débit par client/équipe | 100 RPM par agent |
| **set-body** | Inspection de contenu DLP | Masquer les numéros de sécurité sociale et de carte bancaire dans les sorties d'outils |
| **log-to-eventhub** | Journalisation d'audit centralisée | Chaque appel d'outil → Event Hub → Log Analytics |

!!! tip "Pourquoi OAuth plutôt que les clés API ?"
    Les clés API n'ont pas d'identité utilisateur, pas d'expiration de jeton et pas de contrôle de portée. Si une clé fuit, n'importe qui peut appeler le serveur MCP jusqu'à ce que vous la renouveliez manuellement. Les jetons OAuth 2.0 expirent automatiquement, portent l'identité utilisateur/application et peuvent être limités à des outils spécifiques.

---

## Étape 2 : Charger et explorer la flotte de serveurs MCP

Le jeu de données contient **10 serveurs MCP** à travers **6 équipes** :

```python
import pandas as pd

servers = pd.read_csv("lab-064/mcp_servers.csv")
print(f"Total MCP servers: {len(servers)}")
print(f"Teams: {sorted(servers['team'].unique())}")
print(f"\nServers per team:")
print(servers.groupby("team")["server_name"].count().sort_values(ascending=False))
```

**Sortie attendue :**

```
Total MCP servers: 10
Teams: ['Analytics', 'Commerce', 'Finance', 'HR', 'Logistics', 'Marketing', 'Operations', 'Support']

Commerce      2
Operations    2
Analytics     1
Finance       1
HR            1
Logistics     1
Marketing     1
Support       1
```

---

## Étape 3 : Audit de conformité

Un serveur est **conforme** s'il possède les trois éléments suivants : authentification OAuth 2.0, DLP activé et journalisation activée. Vérifiez la flotte :

```python
compliant = servers[servers["compliant"] == True]
non_compliant = servers[servers["compliant"] == False]

print(f"Compliant servers:     {len(compliant)}")
print(f"Non-compliant servers: {len(non_compliant)}")
print(f"\nNon-compliant details:")
print(non_compliant[["server_name", "team", "auth_type", "has_dlp", "has_logging"]].to_string(index=False))
```

**Sortie attendue :**

```
Compliant servers:     6
Non-compliant servers: 4

Non-compliant details:
     server_name       team auth_type has_dlp has_logging
 customer-support   Support   api_key   false       true
 analytics-export Analytics   api_key   false      false
       legacy-erp Operations    basic   false      false
   maps-geocoding  Logistics   api_key   false       true
```

!!! warning "Alerte de risque"
    4 serveurs sur 10 ne sont pas conformes — c'est **40 % de la flotte**. Le serveur `legacy-erp` est le pire contrevenant : authentification basic, pas de DLP, pas de journalisation et le taux d'erreur le plus élevé.

---

## Étape 4 : Analyse des lacunes d'authentification

Identifiez les serveurs qui **n'utilisent pas** OAuth 2.0 :

```python
non_oauth = servers[servers["auth_type"] != "oauth2"]
print(f"Servers without OAuth 2.0: {len(non_oauth)}")
print(non_oauth[["server_name", "auth_type", "monthly_calls"]].to_string(index=False))

total_non_oauth_calls = non_oauth["monthly_calls"].sum()
total_calls = servers["monthly_calls"].sum()
pct = total_non_oauth_calls / total_calls * 100
print(f"\nNon-OAuth call volume: {total_non_oauth_calls:,} / {total_calls:,} ({pct:.1f}%)")
```

**Sortie attendue :**

```
Servers without OAuth 2.0: 4

     server_name auth_type  monthly_calls
 customer-support   api_key         28000
 analytics-export   api_key         12000
       legacy-erp     basic          8000
   maps-geocoding   api_key         22000

Non-OAuth call volume: 70,000 / 194,500 (36.0%)
```

!!! danger "36 % de tous les appels MCP utilisent une authentification faible"
    Plus d'un tiers des appels API mensuels passent par des serveurs avec des clés API ou une authentification basic. Une seule clé divulguée pourrait exposer les données du support client, les exports analytiques, les enregistrements ERP ou les services de géocodage.

---

## Étape 5 : Analyse de la couverture DLP

Vérifiez quels serveurs ne disposent pas d'analyse de prévention de perte de données :

```python
no_dlp = servers[servers["has_dlp"].astype(str).str.lower() == "false"]
print(f"Servers without DLP: {len(no_dlp)}")
print(no_dlp[["server_name", "team", "monthly_calls"]].to_string(index=False))
```

**Sortie attendue :**

```
Servers without DLP: 4

     server_name       team  monthly_calls
 customer-support   Support         28000
 analytics-export Analytics         12000
       legacy-erp Operations          8000
   maps-geocoding  Logistics         22000
```

Les 4 serveurs sans DLP traitent **70 000 appels mensuels** — n'importe lequel d'entre eux pourrait laisser fuiter des PII ou des données sensibles via les sorties d'outils sans détection.

---

## Étape 6 : Analyse du taux d'erreur et de la latence

Identifiez les serveurs avec les taux d'erreur et la latence les plus élevés :

```python
print("Error rates (sorted):")
error_sorted = servers.sort_values("error_rate_pct", ascending=False)
print(error_sorted[["server_name", "error_rate_pct", "avg_latency_ms"]].to_string(index=False))

highest_error = error_sorted.iloc[0]
print(f"\nHighest error rate: {highest_error['server_name']} at {highest_error['error_rate_pct']}%")
print(f"Its average latency: {highest_error['avg_latency_ms']}ms")
```

**Sortie attendue :**

```
Highest error rate: legacy-erp at 5.8%
Its average latency: 450ms
```

!!! tip "Observation"
    Le serveur `legacy-erp` se distingue comme le serveur le plus à risque : authentification basic, pas de DLP, pas de journalisation, taux d'erreur le plus élevé (5,8 %) et latence la plus élevée (450 ms). Il devrait être la priorité numéro un pour l'intégration à APIM.

---

## Étape 7 : Volume total d'appels

Calculez le total des appels mensuels sur tous les serveurs MCP :

```python
total = servers["monthly_calls"].sum()
print(f"Total monthly calls across fleet: {total:,}")
```

**Sortie attendue :**

```
Total monthly calls across fleet: 194,500
```

---

## Étape 8 : Priorité de migration APIM

Créez un plan de migration priorisé basé sur le risque :

```python
servers["risk_score"] = (
    (servers["auth_type"] != "oauth2").astype(int) * 3 +
    (servers["has_dlp"].astype(str).str.lower() == "false").astype(int) * 2 +
    (servers["has_logging"].astype(str).str.lower() == "false").astype(int) * 1 +
    servers["error_rate_pct"] / servers["error_rate_pct"].max()
)

priority = servers.sort_values("risk_score", ascending=False)
print("Migration Priority:")
print(priority[["server_name", "auth_type", "has_dlp", "has_logging", "risk_score"]]
      .head(5).to_string(index=False))
```

Cela produit une liste classée par risque pour guider la séquence d'intégration à APIM.

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-064/broken_apim.py` contient **3 bugs** dans la manière dont il analyse la flotte de serveurs MCP :

```bash
python lab-064/broken_apim.py
```

| Test | Ce qu'il vérifie | Indice |
|------|-------------------|--------|
| Test 1 | Nombre de serveurs non conformes | Devrait compter `compliant == False`, pas `True` |
| Test 2 | Total des appels mensuels | Devrait être la **somme**, pas la **moyenne** |
| Test 3 | Serveurs sans OAuth | Devrait filtrer `auth_type != "oauth2"`, pas `== "oauth2"` |

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Pourquoi APIM est-il l'approche recommandée pour sécuriser les serveurs MCP à grande échelle ?"

    - A) Il remplace MCP par un protocole différent
    - B) Il fournit une authentification, une limitation de débit et une surveillance centralisées sur tous les points de terminaison MCP
    - C) Il élimine le besoin d'OAuth 2.0
    - D) Il ne fonctionne qu'avec les serveurs MCP hébergés sur Azure

    ??? success "✅ Révéler la réponse"
        **Correct : B) Il fournit une authentification, une limitation de débit et une surveillance centralisées sur tous les points de terminaison MCP**

        APIM agit comme une passerelle unifiée devant tous les serveurs MCP, appliquant de manière cohérente la validation OAuth 2.0, la limitation de débit, l'inspection de contenu DLP et la journalisation d'audit — indépendamment de la manière dont chaque serveur MCP individuel a été construit à l'origine. Sans APIM, chaque équipe implémente (ou ignore) ces contrôles de manière indépendante.

??? question "**Q2 (Choix multiple) :** Pourquoi l'authentification par clé API est-elle insuffisante pour les serveurs MCP en production ?"

    - A) Les clés API sont trop longues pour être stockées de manière sécurisée
    - B) Les clés API ne fournissent pas d'identité utilisateur, pas d'expiration de jeton et pas de contrôle de portée
    - C) Les clés API ne fonctionnent qu'avec les API REST, pas MCP
    - D) Les clés API nécessitent Azure AD pour fonctionner

    ??? success "✅ Révéler la réponse"
        **Correct : B) Les clés API ne fournissent pas d'identité utilisateur, pas d'expiration de jeton et pas de contrôle de portée**

        Les clés API sont des secrets statiques : si l'une d'elles fuit, n'importe qui peut l'utiliser indéfiniment jusqu'à un renouvellement manuel. Elles ne portent aucune information sur *qui* appelle ou *ce qu'il* est autorisé à faire. Les jetons OAuth 2.0 expirent automatiquement, embarquent les claims d'identité utilisateur/application et peuvent être limités à des permissions spécifiques (ex. : accès en lecture seule à un outil spécifique).

??? question "**Q3 (Exécuter le lab) :** Combien de serveurs MCP dans la flotte sont non conformes ?"

    Filtrez le DataFrame des serveurs pour `compliant == False` et comptez les lignes.

    ??? success "✅ Révéler la réponse"
        **4 serveurs non conformes**

        Les serveurs non conformes sont : `customer-support` (api_key, pas de DLP), `analytics-export` (api_key, pas de DLP, pas de journalisation), `legacy-erp` (authentification basic, pas de DLP, pas de journalisation) et `maps-geocoding` (api_key, pas de DLP). Les 4 n'ont ni OAuth ni DLP ; 2 n'ont pas non plus de journalisation.

??? question "**Q4 (Exécuter le lab) :** Quel est le volume total d'appels mensuels sur les 10 serveurs MCP ?"

    Additionnez la colonne `monthly_calls` sur tous les serveurs.

    ??? success "✅ Révéler la réponse"
        **194 500 appels mensuels au total**

        45 000 + 32 000 + 28 000 + 18 000 + 15 000 + 12 000 + 5 000 + 8 000 + 22 000 + 9 500 = **194 500**. Parmi ceux-ci, 70 000 (36 %) passent par des serveurs sans OAuth 2.0 — une exposition de sécurité significative.

??? question "**Q5 (Exécuter le lab) :** Quel serveur MCP a le taux d'erreur le plus élevé, et quel est-il ?"

    Triez les serveurs par `error_rate_pct` décroissant et inspectez la première ligne.

    ??? success "✅ Révéler la réponse"
        **legacy-erp à 5,8 %**

        Le serveur `legacy-erp` (équipe Operations) a le taux d'erreur le plus élevé à 5,8 %, soit près de 3 fois le suivant (payment-gateway à 2,1 %). Combiné avec une authentification basic, pas de DLP, pas de journalisation et une latence moyenne de 450 ms, c'est le serveur le plus à risque de la flotte et il devrait être la priorité numéro un pour l'intégration à APIM.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-------------------------|
| APIM comme passerelle | Sécurité centralisée, limitation de débit et surveillance pour MCP |
| OAuth 2.0 | Authentification basée sur les jetons avec identité, expiration et contrôle de portée |
| Politiques DLP | Inspection de contenu pour empêcher la fuite de PII/données sensibles |
| Audit de conformité | Évaluation systématique de la posture de sécurité de la flotte |
| Priorisation des risques | Planification de migration basée sur les données selon l'authentification, DLP et les taux d'erreur |

---

## Prochaines étapes

- **[Lab 012](lab-012-what-is-mcp.md)** — Qu'est-ce que MCP ? (concepts fondamentaux de MCP)
- **[Lab 028](lab-028-deploy-mcp-azure.md)** — Déployer MCP sur Azure (déployer les serveurs que APIM protège)
- **[Lab 036](lab-036-prompt-injection-security.md)** — Sécurité contre l'injection de prompt (couche de sécurité complémentaire)
