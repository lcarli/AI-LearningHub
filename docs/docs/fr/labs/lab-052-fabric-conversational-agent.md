---
tags:
  - fabric
  - data-agent
  - nl-to-sql
  - sqlite
  - python
  - entra-id
---

# Lab 052 : Fabric IQ — Agent de données conversationnel (NL → SQL)

<div class="lab-meta">
  <span class="level-badge level-200">L200</span>
  <span class="path-badge">All paths</span>
  <span class="time-badge">~75 min</span>
  <span class="cost-badge cost-free">Gratuit — Utilise SQLite localement (capacité Fabric optionnelle)</span>
</div>

## Ce que vous apprendrez

- Comment les **Microsoft Fabric Data Agents** traduisent des questions en langage naturel en requêtes SQL, DAX ou KQL
- Le flux de bout en bout de la génération **NL → SQL**, l'exécution et la présentation des résultats
- Comment l'accès **moindre privilège** et la liaison d'identité **Entra ID** sécurisent les données à chaque étape
- Pourquoi la **transparence des requêtes** et la **journalisation d'audit** sont essentielles pour la confiance dans les requêtes générées par l'IA
- Comment permettre l'**analytique en libre-service** pour les utilisateurs non techniques sans exposer l'accès brut à la base de données

## Introduction

![NL to SQL Flow](../../assets/diagrams/fabric-nl-to-sql.svg)

Un **Fabric Data Agent** permet aux utilisateurs métier de poser des questions sur les données en langage courant. En coulisses, l'agent inspecte le schéma de la base de données, génère une requête SQL (ou DAX / KQL), l'exécute sous l'identité Entra de l'appelant et renvoie une réponse formatée — le tout sans que l'utilisateur n'écrive une seule ligne de code.

Dans ce lab, vous allez construire une simulation locale de ce pipeline en utilisant **SQLite** et **Python**. Le scénario est **OutdoorGear**, un détaillant fictif d'équipements de plein air. La base de données contient deux tables :

| Table | Description |
|-------|-------------|
| `products` | Catalogue de produits — 10 articles répartis dans des catégories telles que Tentes, Sacs à dos, Sacs de couchage et Accessoires |
| `orders` | Historique des commandes — 15 commandes référençant les produits par `product_id` |

Les utilisateurs non techniques — responsables de magasin, analystes marketing, planificateurs de la chaîne d'approvisionnement — ont besoin de poser des questions comme *« Combien de tentes sont en stock ? »* ou *« Quel est le chiffre d'affaires total ? »* sans apprendre le SQL. À la fin de ce lab, vous comprendrez exactement comment un Fabric Data Agent répond à ces questions et pourquoi le modèle de sécurité est important.

## Prérequis

| Prérequis | Notes |
|-----------|-------|
| **Python 3.10+** | [python.org/downloads](https://www.python.org/downloads/){:target="_blank"} |
| **pandas** | `pip install pandas` — utilisé pour charger les fichiers CSV dans SQLite |
| **sqlite3** | Fait partie de la bibliothèque standard Python — aucune installation requise |

!!! tip "Aucune capacité Fabric nécessaire"
    Ce lab s'exécute entièrement sur votre machine locale avec SQLite. Une capacité Fabric n'est nécessaire que si vous souhaitez déployer un vrai Data Agent par la suite.

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-052/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|---------|-------------|-------------|
| `broken_query_gen.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-052/broken_query_gen.py) |
| `orders.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-052/orders.csv) |
| `products.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-052/products.csv) |

---

## Étape 1 : Comprendre les Fabric Data Agents

Un Fabric Data Agent se situe entre l'utilisateur et les données. Lorsqu'un utilisateur saisit une question, l'agent :

1. **Analyse** l'entrée en langage naturel et identifie l'intention, les entités et les filtres.
2. **Inspecte** le schéma de la source de données connectée (tables, colonnes, relations).
3. **Génère** une requête dans le langage approprié — SQL pour les entrepôts et les points de terminaison SQL, DAX pour les modèles sémantiques, KQL pour les bases de données KQL.
4. **Exécute** la requête sous l'**identité Entra ID de l'utilisateur**. L'agent n'utilise jamais un compte de service avec des privilèges élevés ; il délègue à l'identité de l'appelant afin que la sécurité au niveau des lignes (RLS) et les permissions au niveau des objets soient appliquées automatiquement.
5. **Renvoie** le résultat accompagné de la requête générée afin que l'utilisateur (ou un auditeur) puisse inspecter exactement ce qui a été exécuté.

Cette conception offre trois garanties :

| Garantie | Comment |
|----------|---------|
| **Moindre privilège** | Les requêtes s'exécutent en tant qu'utilisateur authentifié — pas de super-utilisateur partagé |
| **Transparence** | Le SQL/DAX/KQL généré est toujours montré à l'appelant |
| **Auditabilité** | Chaque requête est journalisée avec l'identité de l'utilisateur et l'horodatage |

!!! info "Pourquoi la transparence est importante"
    Si l'agent génère une requête incorrecte, l'utilisateur peut voir — et signaler — l'erreur. Cette boucle de rétroaction est essentielle pour construire la confiance dans l'analytique générée par l'IA.

---

## Étape 2 : Configurer la base de données

Dans cette étape, vous allez créer une base de données SQLite locale à partir de deux fichiers CSV fournis avec le lab.

### 2.1 Charger les fichiers CSV dans SQLite

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("lab-052/outdoor_gear.db")

pd.read_csv("lab-052/products.csv").to_sql("products", conn, if_exists="replace", index=False)
pd.read_csv("lab-052/orders.csv").to_sql("orders", conn, if_exists="replace", index=False)

print("✅ Database created: lab-052/outdoor_gear.db")
```

### 2.2 Explorer le schéma

```python
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

for table in tables:
    print(f"\n--- {table} ---")
    info = conn.execute(f"PRAGMA table_info({table})").fetchall()
    for col in info:
        print(f"  {col[1]:20s} {col[2]}")
```

Sortie attendue :

```
Tables: ['products', 'orders']

--- products ---
  product_id           TEXT
  product_name         TEXT
  category             TEXT
  price                REAL
  stock                INTEGER

--- orders ---
  order_id             TEXT
  product_id           TEXT
  customer_name        TEXT
  quantity             INTEGER
  total                REAL
  order_date           TEXT
```

### 2.3 Comptage rapide des lignes

```python
for table in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count} rows")
```

```
products: 10 rows
orders: 15 rows
```

---

## Étape 3 : Construire des modèles de requêtes NL → SQL

Un Fabric Data Agent associe des questions en langage naturel à des requêtes SQL. Voici cinq modèles représentatifs qui couvrent les types de questions les plus courants : comptage, agrégation, filtrage, jointure et moyenne.

### Modèle 1 — Comptage avec un filtre

> **L'utilisateur demande :** *« Combien de tentes sont en stock ? »*

```sql
SELECT COUNT(*)
FROM   products
WHERE  category = 'Tents'
  AND  stock > 0;
```

**Résultat attendu :** `2`

!!! warning "Le filtre `stock > 0` est important"
    Sans la clause `stock > 0`, la requête compterait les produits qui existent dans le catalogue même s'ils sont en rupture de stock. Un agent bien conçu applique toujours le filtre « en stock » lorsque l'utilisateur dit *« en stock ».*

---

### Modèle 2 — Agrégation par somme

> **L'utilisateur demande :** *« Quel est le chiffre d'affaires total ? »*

```sql
SELECT SUM(total)
FROM   orders;
```

**Résultat attendu :** `3209.74`

Le chiffre d'affaires provient de la table **orders** — et non de la multiplication de `price × stock` dans la table products. C'est une erreur courante dans les systèmes NL → SQL.

---

### Modèle 3 — Filtre simple / SELECT *

> **L'utilisateur demande :** *« Afficher tous les sacs à dos »*

```sql
SELECT *
FROM   products
WHERE  category = 'Backpacks';
```

Cela renvoie toutes les colonnes pour les produits de la catégorie Backpacks.

---

### Modèle 4 — JOIN + GROUP BY + ORDER BY

> **L'utilisateur demande :** *« Quel produit a le plus de commandes ? »*

```sql
SELECT   p.product_name,
         COUNT(*) AS order_count
FROM     orders o
JOIN     products p ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY order_count DESC
LIMIT    1;
```

**Résultat attendu :** `Alpine Explorer Tent` — 3 commandes

!!! note "COUNT(*) vs SUM(quantity)"
    *« Le plus de commandes »* signifie le plus grand **nombre de lignes de commandes**, et non la quantité totale la plus élevée. L'agrégat correct est `COUNT(*)`, et non `SUM(quantity)`.

---

### Modèle 5 — Agrégation par moyenne

> **L'utilisateur demande :** *« Valeur moyenne des commandes ? »*

```sql
SELECT AVG(total)
FROM   orders;
```

**Résultat attendu :** `213.98`

Vérification : le chiffre d'affaires total est de 3 209,74 et il y a 15 commandes → 3 209,74 ÷ 15 = **213,9827 ≈ 213,98**.

---

## Étape 4 : Exécuter les requêtes et vérifier

Exécutez chaque modèle sur la base de données SQLite locale et confirmez que les résultats correspondent aux valeurs attendues.

```python
queries = {
    "How many tents are in stock?": (
        "SELECT COUNT(*) FROM products WHERE category='Tents' AND stock > 0",
        "2",
    ),
    "What is the total revenue?": (
        "SELECT SUM(total) FROM orders",
        "3209.74",
    ),
    "Show all backpacks": (
        "SELECT * FROM products WHERE category='Backpacks'",
        None,  # tabular result — just display
    ),
    "Which product has the most orders?": (
        "SELECT p.product_name, COUNT(*) AS order_count "
        "FROM orders o JOIN products p ON o.product_id=p.product_id "
        "GROUP BY p.product_name ORDER BY order_count DESC LIMIT 1",
        "Alpine Explorer Tent|3",
    ),
    "Average order value?": (
        "SELECT AVG(total) FROM orders",
        "213.98",
    ),
}

print("=" * 60)
for question, (sql, expected) in queries.items():
    print(f"\n❓ {question}")
    print(f"   SQL ➜ {sql}")
    result = conn.execute(sql).fetchall()
    print(f"   Result: {result}")
    if expected:
        print(f"   Expected: {expected}")
print("\n" + "=" * 60)
```

!!! tip "Comparez attentivement"
    Si un résultat ne correspond pas, vérifiez à nouveau les données CSV et la requête. Les écarts proviennent généralement d'un filtre incorrect ou d'une mauvaise fonction d'agrégation.

---

## Étape 5 : Sécurité et audit

Dans un déploiement Fabric en production, les mêmes requêtes que vous avez exécutées localement seraient exécutées via le Data Agent avec une sécurité d'entreprise complète. Cette section explique les protections clés.

### Liaison d'identité Entra ID

Chaque requête est exécutée sous le **jeton Entra ID de l'utilisateur appelant**. Le Data Agent ne possède pas ses propres identifiants de base de données — il délègue l'authentification au fournisseur d'identité. Cela signifie :

- Un responsable de magasin ne voit que les données de son magasin (si la RLS est configurée).
- Un analyste marketing peut interroger le chiffre d'affaires agrégé mais ne peut pas voir les enregistrements individuels des clients.
- Un auditeur externe peut examiner les journaux de requêtes liés à des identités utilisateur spécifiques.

### Sécurité au niveau des lignes (RLS)

Fabric prend en charge la RLS sur les points de terminaison SQL et les modèles sémantiques. Lorsque le Data Agent génère une requête, le moteur de base de données applique automatiquement les filtres RLS en fonction de l'identité de l'utilisateur authentifié. L'agent lui-même ne modifie ni ne supprime jamais ces filtres.

### Journalisation des requêtes et audit

Chaque requête générée — accompagnée de l'identité de l'utilisateur, de l'horodatage et du nombre de lignes du résultat — est enregistrée dans le journal d'activité Fabric. Cela permet :

| Capacité | Avantage |
|----------|----------|
| **Rapports de conformité** | Prouver qui a accédé à quelles données et quand |
| **Détection d'anomalies** | Signaler des modèles de requêtes inhabituels (par ex., exports en masse) |
| **Amélioration de l'agent** | Identifier les requêtes fréquemment échouées et améliorer le modèle NL → SQL |

!!! info "Simulation locale"
    Dans ce lab, vous exécutez les requêtes directement sur SQLite, il n'y a donc pas de liaison Entra ni de RLS. Dans un déploiement Fabric réel, ces contrôles sont appliqués automatiquement.

---

## Exercice de correction de bugs

Le fichier `lab-052/broken_query_gen.py` contient un générateur NL → SQL simplifié avec **trois bugs**. Votre tâche est de trouver et corriger chacun d'entre eux.

### Exécuter le script défectueux

```bash
python lab-052/broken_query_gen.py
```

### Bug 1 — Filtre `stock > 0` manquant

```python
# ❌ BUG: counts all products in the category, including out-of-stock
def count_in_stock(category):
    return f"SELECT COUNT(*) FROM products WHERE category='{category}'"
```

**Correction :** Ajouter `AND stock > 0` à la clause WHERE.

```python
# ✅ FIXED
def count_in_stock(category):
    return f"SELECT COUNT(*) FROM products WHERE category='{category}' AND stock > 0"
```

### Bug 2 — Le chiffre d'affaires utilise `price × stock` au lieu des totaux de commandes

```python
# ❌ BUG: calculates potential inventory value, not actual revenue
def total_revenue():
    return "SELECT SUM(price * stock) FROM products"
```

**Correction :** Interroger la table `orders` à la place.

```python
# ✅ FIXED
def total_revenue():
    return "SELECT SUM(total) FROM orders"
```

### Bug 3 — Le produit le plus commandé utilise `quantity DESC` au lieu de `COUNT(*)`

```python
# ❌ BUG: returns the order with the highest single-order quantity,
#          not the product with the most orders
def most_ordered_product():
    return (
        "SELECT p.product_name, o.quantity "
        "FROM orders o JOIN products p ON o.product_id=p.product_id "
        "ORDER BY o.quantity DESC LIMIT 1"
    )
```

**Correction :** Regrouper par produit et compter les lignes de commandes.

```python
# ✅ FIXED
def most_ordered_product():
    return (
        "SELECT p.product_name, COUNT(*) AS order_count "
        "FROM orders o JOIN products p ON o.product_id=p.product_id "
        "GROUP BY p.product_name ORDER BY order_count DESC LIMIT 1"
    )
```

---

## Fichiers de support

Les fichiers suivants sont fournis dans le répertoire `lab-052/`.

### `lab-052/products.csv`

```csv
product_id,product_name,category,price,stock
P001,Alpine Explorer Tent,Tents,349.99,5
P002,TrailMaster 2P Tent,Tents,199.99,8
P003,Summit Backpack 65L,Backpacks,189.99,12
P004,DayHiker 30L Pack,Backpacks,79.99,20
P005,Arctic Dream Sleeping Bag,Sleeping Bags,299.99,3
P006,Summer Lite Sleeping Bag,Sleeping Bags,89.99,15
P007,Trekking Poles Carbon,Accessories,59.99,25
P008,Headlamp ProBeam 400,Accessories,34.99,30
P009,Portable Water Filter,Accessories,34.92,18
P010,Camping Cookset Titanium,Accessories,124.99,7
```

### `lab-052/orders.csv`

```csv
order_id,product_id,customer_name,quantity,total,order_date
O001,P001,Alice Martin,1,349.99,2025-01-05
O002,P003,Bob Chen,1,189.99,2025-01-08
O003,P005,Carla Diaz,1,299.99,2025-01-10
O004,P002,David Kim,2,399.98,2025-01-12
O005,P007,Eva Novak,3,179.97,2025-01-15
O006,P001,Frank Osei,1,349.99,2025-01-17
O007,P004,Grace Liu,1,79.99,2025-01-20
O008,P008,Hiro Tanaka,2,69.98,2025-01-22
O009,P006,Isabelle Roy,1,89.99,2025-01-24
O010,P001,Jake Wilson,1,349.99,2025-01-27
O011,P009,Karen Patel,1,34.92,2025-01-29
O012,P003,Liam Murphy,1,189.99,2025-02-01
O013,P010,Mia Santos,1,124.99,2025-02-04
O014,P002,Noah Berg,1,199.99,2025-02-06
O015,P005,Olivia Park,1,299.99,2025-02-09
```

### `lab-052/broken_query_gen.py`

```python
"""Broken NL → SQL generator — fix the three bugs!"""

import sqlite3

DB_PATH = "lab-052/outdoor_gear.db"

# ❌ BUG 1: Missing stock > 0 filter
def count_in_stock(category):
    return f"SELECT COUNT(*) FROM products WHERE category='{category}'"

# ❌ BUG 2: Uses price * stock instead of order totals
def total_revenue():
    return "SELECT SUM(price * stock) FROM products"

# ❌ BUG 3: Uses quantity DESC instead of COUNT(*)
def most_ordered_product():
    return (
        "SELECT p.product_name, o.quantity "
        "FROM orders o JOIN products p ON o.product_id=p.product_id "
        "ORDER BY o.quantity DESC LIMIT 1"
    )

def run(query_fn, *args):
    conn = sqlite3.connect(DB_PATH)
    sql = query_fn(*args)
    print(f"SQL: {sql}")
    result = conn.execute(sql).fetchall()
    print(f"Result: {result}\n")
    conn.close()

if __name__ == "__main__":
    print("--- Tents in stock ---")
    run(count_in_stock, "Tents")

    print("--- Total revenue ---")
    run(total_revenue)

    print("--- Most ordered product ---")
    run(most_ordered_product)
```

---

## Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quel modèle de sécurité un Fabric Data Agent utilise-t-il pour l'exécution des requêtes ?"

    - A) Un compte de service partagé avec un accès complet à la base de données
    - B) L'identité Entra ID propre à l'utilisateur avec des permissions de moindre privilège
    - C) Une clé API intégrée dans la configuration de l'agent
    - D) Un accès anonyme avec des restrictions basées sur l'adresse IP

    ??? success "✅ Révéler la réponse"
        **Correct : B) L'identité Entra ID propre à l'utilisateur avec des permissions de moindre privilège**

        Les Fabric Data Agents exécutent chaque requête sous l'identité Entra de l'utilisateur appelant. Cela garantit que la sécurité au niveau des lignes, les permissions sur les objets et les politiques d'accès conditionnel sont appliquées automatiquement — l'agent n'élève jamais les privilèges au-delà de ce que l'utilisateur possède déjà.

??? question "**Q2 (Choix multiple) :** Pourquoi est-il important que le SQL généré soit consultable par l'utilisateur ?"

    - A) Pour que les utilisateurs puissent copier le SQL et l'exécuter plus rapidement la prochaine fois
    - B) Pour permettre la transparence, l'auditabilité et la confiance dans les requêtes générées par l'IA
    - C) Parce que la coloration syntaxique SQL est plus belle dans l'interface
    - D) Pour permettre aux utilisateurs d'optimiser manuellement les performances des requêtes

    ??? success "✅ Révéler la réponse"
        **Correct : B) Pour permettre la transparence, l'auditabilité et la confiance dans les requêtes générées par l'IA**

        Lorsque les utilisateurs peuvent voir le SQL exact qui a été généré et exécuté, ils peuvent vérifier l'exactitude, signaler les erreurs, et les auditeurs peuvent examiner les modèles d'accès aux données. Cette transparence est une exigence fondamentale pour une analytique assistée par l'IA digne de confiance.

??? question "**Q3 (Exécuter la requête) :** Combien de tentes sont actuellement en stock (stock > 0) ?"

    Exécutez cette requête sur la base de données du lab :

    ```sql
    SELECT COUNT(*) FROM products WHERE category='Tents' AND stock > 0;
    ```

    ??? success "✅ Révéler la réponse"
        **Réponse : 2**

        L'Alpine Explorer Tent (P001, stock=5) et la TrailMaster 2P Tent (P002, stock=8) ont toutes deux un stock supérieur à zéro. La requête filtre correctement sur `category='Tents'` et `stock > 0`.

??? question "**Q4 (Exécuter la requête) :** Quel est le chiffre d'affaires total de toutes les commandes ?"

    Exécutez cette requête sur la base de données du lab :

    ```sql
    SELECT SUM(total) FROM orders;
    ```

    ??? success "✅ Révéler la réponse"
        **Réponse : 3 209,74 $**

        La colonne `total` dans la table orders contient le chiffre d'affaires réel de chaque commande (prix × quantité). La somme des 15 totaux de commandes donne 3 209,74. Une erreur courante est de calculer `SUM(price * stock)` à partir de la table products, ce qui donne la valeur de l'inventaire — et non le chiffre d'affaires.

??? question "**Q5 (Exécuter la requête) :** Quel produit a le plus de commandes ?"

    Exécutez cette requête sur la base de données du lab :

    ```sql
    SELECT p.product_name, COUNT(*) AS order_count
    FROM   orders o
    JOIN   products p ON o.product_id = p.product_id
    GROUP BY p.product_name
    ORDER BY order_count DESC
    LIMIT 1;
    ```

    ??? success "✅ Révéler la réponse"
        **Réponse : Alpine Explorer Tent (P001) — 3 commandes**

        Le produit P001 apparaît dans les commandes O001, O006 et O010. La requête joint les commandes aux produits, regroupe par nom de produit, compte le nombre de lignes de commandes par produit et renvoie celui avec le compte le plus élevé. Notez que `COUNT(*)` compte les lignes de commandes — et non la quantité totale expédiée.

---

## Résumé

| Sujet | Point clé |
|-------|-----------|
| **Fabric Data Agents** | Traduisent les questions en langage naturel en SQL, DAX ou KQL et les exécutent au nom de l'utilisateur |
| **Pipeline NL → SQL** | Analyser l'intention → inspecter le schéma → générer la requête → exécuter → renvoyer les résultats |
| **Identité et sécurité** | Les requêtes s'exécutent sous l'identité Entra ID de l'utilisateur — moindre privilège par défaut |
| **Sécurité au niveau des lignes** | Les filtres RLS sont appliqués par le moteur de base de données, pas par l'agent |
| **Transparence des requêtes** | La requête générée est toujours affichée pour que les utilisateurs puissent vérifier et les auditeurs examiner |
| **Journalisation d'audit** | Chaque requête est enregistrée avec l'identité de l'utilisateur, l'horodatage et les métadonnées du résultat |
| **Bugs courants NL → SQL** | Filtres manquants, mauvaise table pour l'agrégation, fonction d'agrégation incorrecte |

---

## Prochaines étapes

- [← Lab 051 : Lab précédent](lab-051-previous-lab.md) — continuez votre parcours d'apprentissage
- [→ Lab 053 : Lab suivant](lab-053-next-lab.md) — passez au sujet suivant
