---
tags: [connectors, mcp, m365, copilot, federation, enterprise]
---
# Lab 056 : Connecteurs fédérés M365 Copilot avec MCP

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~90 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des données de comparaison simulées (aucun tenant M365 requis)</span>
</div>

## Ce que vous apprendrez

- La différence entre les **connecteurs synchronisés (indexés)** et les **connecteurs fédérés (temps réel)** dans Microsoft 365 Copilot
- Comment **MCP peut agir comme connecteur fédéré** — fournissant un accès aux données en temps réel sans indexation
- Comment les **citations** fonctionnent dans les connecteurs fédérés vs synchronisés
- Les **considérations OAuth et de conformité** pour les données réglementées (santé, juridique, finance)
- Quand choisir chaque type de connecteur en fonction de la latence, de la fraîcheur des données et des exigences de conformité

## Introduction

Microsoft 365 Copilot utilise des **connecteurs** pour intégrer des données externes dans l'expérience Copilot. Il existe deux architectures fondamentales :

| Type de connecteur | Fonctionnement | Emplacement des données |
|--------------------|----------------|------------------------|
| **Synchronisé (Indexé)** | Explore et copie les données dans l'index Microsoft Search | Données stockées sur les serveurs Microsoft |
| **Fédéré (Temps réel)** | Interroge le système source au moment de l'exécution — aucune donnée n'est copiée | Les données restent dans le système source |

Chaque approche a ses compromis :

| Dimension | Fédéré | Synchronisé |
|-----------|--------|-------------|
| **Latence** | Plus élevée (requête en temps réel) | Plus basse (pré-indexé) |
| **Fraîcheur des données** | Toujours à jour (0 sec) | Dépend du calendrier d'exploration |
| **Conformité** | Les données ne quittent jamais la source | Données copiées sur les serveurs Microsoft |
| **Accès hors ligne** | Nécessite la disponibilité de la source | Fonctionne même si la source est indisponible |

### Le scénario

OutdoorGear Inc. doit connecter **plusieurs sources de données** à Microsoft 365 Copilot :

- **Catalogue de produits** et **historique des commandes** — peuvent être indexés (synchronisés) pour une recherche rapide
- **Dossiers médicaux des patients**, **données salariales des employés** et **contrats juridiques** — données réglementées qui ne doivent **jamais** quitter le système source (fédéré uniquement)
- **Cours boursiers en temps réel** et **suivi des expéditions** — nécessitent les données les plus fraîches possible

Votre travail consiste à analyser un jeu de données comparatif de 20 requêtes (10 fédérées, 10 synchronisées) et à déterminer quand chaque type de connecteur est le bon choix.

!!! info "MCP comme connecteur fédéré"
    Un serveur MCP peut servir de connecteur fédéré pour M365 Copilot. Le serveur MCP interroge le système source en temps réel et renvoie les résultats avec des citations — aucune donnée n'est jamais indexée ni stockée sur les serveurs Microsoft. Cela rend MCP idéal pour les données réglementées devant se conformer aux exigences HIPAA, GDPR ou SOX.

## Prérequis

| Exigence | Pourquoi |
|----------|----------|
| Python 3.10+ | Analyser les données de comparaison des connecteurs |
| Bibliothèque `pandas` | Opérations DataFrame |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-056/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|---------|-------------|-------------|
| `broken_connector.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-056/broken_connector.py) |
| `connector_comparison.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-056/connector_comparison.csv) |

---

## Étape 1 : Comprendre les types de connecteurs

### Connecteurs synchronisés (indexés)

Les connecteurs synchronisés **explorent** une source de données selon un calendrier et **copient** le contenu dans l'index Microsoft Search :

```
┌─────────────┐    Crawl     ┌──────────────┐    Index    ┌─────────────┐
│  Source      │ ──────────► │  Microsoft   │ ─────────► │  Copilot    │
│  System      │  (schedule) │  Graph       │  (fast)    │  Search     │
│             │             │  Connector    │            │             │
└─────────────┘             └──────────────┘            └─────────────┘
```

- ✅ **Requêtes rapides** — les données sont pré-indexées
- ✅ **Fonctionne hors ligne** — le système source peut être indisponible
- ❌ **Données obsolètes** — dépend de la fréquence d'exploration
- ❌ **Risque de conformité** — les données sont copiées sur les serveurs Microsoft

### Connecteurs fédérés (temps réel)

Les connecteurs fédérés interrogent le système source **au moment de l'exécution** — aucune donnée n'est jamais copiée :

```
┌─────────────┐   Real-time   ┌──────────────┐   Results   ┌─────────────┐
│  Source      │ ◄──────────► │  Federated   │ ──────────► │  Copilot    │
│  System      │    query      │  Connector   │  + citation │  Search     │
│             │              │  (MCP Server) │             │             │
└─────────────┘              └──────────────┘             └─────────────┘
```

- ✅ **Toujours à jour** — interroge les données en direct
- ✅ **Conforme** — les données ne quittent jamais la source
- ✅ **Citations** — les réponses incluent des liens vers les sources
- ❌ **Latence plus élevée** — surcoût de la requête en temps réel
- ❌ **Dépendance à la source** — nécessite la disponibilité du système source

---

## Étape 2 : Charger le jeu de données comparatif

Le jeu de données contient **20 requêtes** — chaque requête a été exécutée via un connecteur fédéré et un connecteur synchronisé :

```python
import pandas as pd

df = pd.read_csv("lab-056/connector_comparison.csv")
print(f"Total queries: {len(df)}")
print(f"Connector types: {df['connector_type'].unique().tolist()}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst 6 rows:")
print(df.head(6).to_string(index=False))
```

**Sortie attendue :**

```
Total queries: 20
Connector types: ['federated', 'synced']
Columns: ['query_id', 'query_text', 'connector_type', 'latency_ms', 'results_count',
           'data_freshness_sec', 'data_size_kb', 'compliant']

First 6 rows:
query_id                      query_text connector_type  latency_ms  results_count  data_freshness_sec  data_size_kb compliant
     Q01             Show all hiking boots      federated         450              5                   0            12      true
     Q02             Show all hiking boots         synced         120              5                3600            12      true
     Q03           Find tents under $300      federated         520              3                   0             8      true
     Q04           Find tents under $300         synced          95              3                7200             8      true
     Q05  Customer order history C001      federated         680              4                   0            15      true
     Q06  Customer order history C001         synced         150              4                1800            15      true
```

---

## Étape 3 : Comparer latence vs fraîcheur

Analysez les compromis de performance entre les types de connecteurs :

### 3a — Latence moyenne par type

```python
fed = df[df["connector_type"] == "federated"]
syn = df[df["connector_type"] == "synced"]

avg_fed_latency = fed["latency_ms"].mean()
avg_syn_latency = syn["latency_ms"].mean()
ratio = avg_fed_latency / avg_syn_latency

print(f"Average federated latency: {avg_fed_latency:.0f} ms")
print(f"Average synced latency:    {avg_syn_latency:.1f} ms")
print(f"Federated/Synced ratio:    {ratio:.1f}×")
```

**Sortie attendue :**

```
Average federated latency: 473 ms
Average synced latency:    109.8 ms
Federated/Synced ratio:    4.3×
```

### 3b — Comparaison de la fraîcheur

```python
print("Data freshness (seconds since last update):")
print(f"  Federated average: {fed['data_freshness_sec'].mean():.0f} sec (always 0 — real-time)")
print(f"  Synced average:    {syn['data_freshness_sec'].mean():.0f} sec")
print(f"  Synced max:        {syn['data_freshness_sec'].max():.0f} sec ({syn['data_freshness_sec'].max()/3600:.1f} hours)")
```

**Sortie attendue :**

```
Data freshness (seconds since last update):
  Federated average: 0 sec (always 0 — real-time)
  Synced average:    3660 sec
  Synced max:        14400 sec (4.0 hours)
```

### 3c — Distribution de la latence

```python
print("Latency ranges:")
for ctype, group in df.groupby("connector_type"):
    print(f"  {ctype}: {group['latency_ms'].min()}–{group['latency_ms'].max()} ms "
          f"(median: {group['latency_ms'].median():.0f} ms)")
```

**Sortie attendue :**

```
Latency ranges:
  federated: 290–680 ms (median: 465 ms)
  synced: 88–150 ms (median: 105 ms)
```

---

## Étape 4 : Analyse de conformité

Déterminez quelles requêtes impliquent des données réglementées qui ne peuvent pas être indexées :

### 4a — Requêtes non conformes

```python
non_compliant = df[df["compliant"] == False]
print(f"Non-compliant queries: {len(non_compliant)}")
print(f"\nDetails:")
print(non_compliant[["query_id", "query_text", "connector_type"]].to_string(index=False))
```

**Sortie attendue :**

```
Non-compliant queries: 3

Details:
query_id               query_text connector_type
     Q10  Patient medical records         synced
     Q12      Employee salary data         synced
     Q18    Legal contract clauses         synced
```

### 4b — Pourquoi le synchronisé est non conforme pour les données réglementées

```python
# Compare federated vs synced for the same regulated queries
regulated_queries = ["Patient medical records", "Employee salary data", "Legal contract clauses"]
for query_text in regulated_queries:
    rows = df[df["query_text"] == query_text]
    fed_row = rows[rows["connector_type"] == "federated"].iloc[0]
    syn_row = rows[rows["connector_type"] == "synced"].iloc[0]
    print(f"\n{query_text}:")
    print(f"  Federated: compliant={fed_row['compliant']}, latency={fed_row['latency_ms']}ms, freshness={fed_row['data_freshness_sec']}s")
    print(f"  Synced:    compliant={syn_row['compliant']}, latency={syn_row['latency_ms']}ms, freshness={syn_row['data_freshness_sec']}s")
```

**Sortie attendue :**

```
Patient medical records:
  Federated: compliant=True, latency=550ms, freshness=0s
  Synced:    compliant=False, latency=130ms, freshness=3600s

Employee salary data:
  Federated: compliant=True, latency=420ms, freshness=0s
  Synced:    compliant=False, latency=105ms, freshness=1800s

Legal contract clauses:
  Federated: compliant=True, latency=480ms, freshness=0s
  Synced:    compliant=False, latency=115ms, freshness=7200s
```

!!! warning "La conformité n'est pas négociable"
    Pour les données réglementées (HIPAA, GDPR, SOX), le connecteur synchronisé **copie les données sur les serveurs Microsoft** lors de l'indexation. Cela viole les exigences de résidence et de souveraineté des données. Le connecteur fédéré (ex. serveur MCP) conserve les données dans le système source — seuls les résultats des requêtes sont renvoyés au moment de l'exécution, jamais stockés.

---

## Étape 5 : Quand utiliser chaque type de connecteur

Sur la base de l'analyse, voici les critères de décision :

### Matrice de décision

| Critère | Utiliser fédéré | Utiliser synchronisé |
|---------|-----------------|----------------------|
| **Données réglementées** (HIPAA, GDPR, SOX) | ✅ Requis | ❌ Non conforme |
| **Fraîcheur temps réel nécessaire** | ✅ Toujours à jour | ❌ Obsolète (délai d'exploration) |
| **Faible latence critique** | ❌ ~473ms moy. | ✅ ~110ms moy. |
| **La source peut être hors ligne** | ❌ Nécessite la source | ✅ Fonctionne depuis l'index |
| **Grands ensembles de résultats** | ❌ Coût d'exécution | ✅ Pré-indexé |
| **Données rarement modifiées** | ⚠️ Excessif | ✅ L'exploration capte les mises à jour |

### Recommandations pour OutdoorGear

```python
recommendations = {
    "Product catalog": "Synced — low latency, not regulated, changes infrequently",
    "Order history": "Synced — historical data, benefits from indexing",
    "Patient medical records": "Federated — HIPAA regulated, must not leave source",
    "Employee salary data": "Federated — PII/compensation data, compliance required",
    "Real-time stock prices": "Federated — must be current, stale data is worse than slow",
    "Legal contracts": "Federated — SOX regulated, data sovereignty required",
    "Product reviews": "Synced — public data, benefits from fast search",
    "Shipping tracking": "Federated — real-time status updates needed",
}

print("OutdoorGear Connector Recommendations:")
for source, rec in recommendations.items():
    connector = "🔄 Federated" if "Federated" in rec else "📦 Synced"
    print(f"  {connector}  {source}: {rec.split(' — ')[1]}")
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-056/broken_connector.py` contient **3 bugs** dans les fonctions d'analyse des connecteurs. Pouvez-vous tous les trouver et les corriger ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-056/broken_connector.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|-------------------|--------|
| Test 1 | Fraîcheur moyenne par type | Devrait retourner `data_freshness_sec`, pas `latency_ms` |
| Test 2 | Nombre de non-conformes | Devrait compter `compliant == False`, pas `compliant == True` |
| Test 3 | Ratio de latence | Devrait calculer `federated / synced`, pas `synced / federated` |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `🎉 All 3 tests passed`, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quel est le principal avantage d'un connecteur fédéré par rapport à un connecteur synchronisé ?"

    - A) Latence plus faible pour tous les types de requêtes
    - B) Fraîcheur des données en temps réel sans indexation — les données ne quittent jamais la source
    - C) Meilleur support de l'accès hors ligne
    - D) Configuration d'authentification plus simple

    ??? success "✅ Révéler la réponse"
        **Correct : B) Fraîcheur des données en temps réel sans indexation — les données ne quittent jamais la source**

        Les connecteurs fédérés interrogent le système source au moment de l'exécution, garantissant que les résultats sont toujours à jour (fraîcheur de 0 seconde). Comme aucune donnée n'est copiée ni indexée, elle reste dans le système source — ce qui la rend conforme aux exigences de résidence des données (HIPAA, GDPR, SOX).

??? question "**Q2 (Choix multiple) :** Pourquoi les connecteurs synchronisés sont-ils non conformes pour les données réglementées comme les dossiers médicaux des patients ?"

    - A) Les connecteurs synchronisés ne supportent pas le chiffrement
    - B) Les données sont copiées sur les serveurs Microsoft lors de l'indexation, violant les exigences de résidence des données
    - C) Les connecteurs synchronisés ne peuvent pas gérer de grands ensembles de données
    - D) Les connecteurs synchronisés ne supportent pas l'authentification OAuth

    ??? success "✅ Révéler la réponse"
        **Correct : B) Les données sont copiées sur les serveurs Microsoft lors de l'indexation, violant les exigences de résidence des données**

        Lorsqu'un connecteur synchronisé explore une source de données, il **copie le contenu dans l'index de recherche de Microsoft**. Pour les données réglementées (dossiers patients HIPAA, données personnelles GDPR, données financières SOX), cela viole les exigences de souveraineté et de résidence des données. Les données doivent rester dans le système source — seuls les connecteurs fédérés garantissent cela.

??? question "**Q3 (Exécuter le lab) :** Quelle est la latence moyenne pour les requêtes du connecteur fédéré ?"

    Filtrez [📥 `connector_comparison.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-056/connector_comparison.csv) par `connector_type == "federated"` et calculez `latency_ms.mean()`.

    ??? success "✅ Révéler la réponse"
        **473 ms**

        Les 10 requêtes fédérées ont des latences de : 450, 520, 680, 380, 550, 420, 610, 290, 480, 350. Somme = 4730, moyenne = 4730 ÷ 10 = **473 ms**.

??? question "**Q4 (Exécuter le lab) :** Combien de requêtes synchronisées sont non conformes ?"

    Filtrez par `connector_type == "synced"` et `compliant == False`.

    ??? success "✅ Révéler la réponse"
        **3**

        Trois requêtes synchronisées sont non conformes : Q10 (dossiers médicaux des patients), Q12 (données salariales des employés) et Q18 (clauses de contrats juridiques). Celles-ci impliquent des données réglementées qui ne doivent pas être copiées sur des serveurs externes.

??? question "**Q5 (Exécuter le lab) :** Quel est le ratio approximatif de latence fédéré/synchronisé ?"

    Divisez la latence moyenne fédérée par la latence moyenne synchronisée.

    ??? success "✅ Révéler la réponse"
        **≈ 4,3×**

        Latence moyenne fédérée = 473 ms. Latence moyenne synchronisée ≈ 110 ms. Ratio = 473 ÷ 110 ≈ **4,3×**. Les requêtes fédérées sont environ 4,3 fois plus lentes que les requêtes synchronisées — le compromis pour la fraîcheur en temps réel et la conformité.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|------------------------|
| Types de connecteurs | Synchronisé (indexé, rapide, obsolète) vs Fédéré (temps réel, conforme, plus lent) |
| MCP comme connecteur | Les serveurs MCP peuvent servir de connecteurs fédérés pour M365 Copilot |
| Conformité | Les données réglementées nécessitent des connecteurs fédérés — le synchronisé copie les données chez Microsoft |
| Compromis de latence | Fédéré ≈ 4,3× plus lent mais toujours à jour ; synchronisé est rapide mais obsolète |
| Critères de décision | Choisissez en fonction de la réglementation, des besoins de fraîcheur, de la tolérance à la latence et de l'accès hors ligne |

---

## Prochaines étapes

- **[Lab 054](lab-054-a2a-protocol.md)** — Protocole A2A — Construire des systèmes multi-agents interopérables
- **[Lab 055](lab-055-a2a-mcp-capstone.md)** — A2A + MCP Full Stack — Capstone d'interopérabilité des agents