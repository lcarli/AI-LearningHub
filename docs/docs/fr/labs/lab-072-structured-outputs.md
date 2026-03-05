---
tags: [structured-outputs, json-schema, pydantic, reliability, python]
---
# Lab 072 : Sorties structurées — JSON garanti pour les agents

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~45 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des données d'extraction simulées</span>
</div>

## Ce que vous apprendrez

- Ce que sont les **sorties structurées** et pourquoi les agents ont besoin de JSON garanti
- En quoi l'application d'un JSON Schema diffère des prompts en forme libre « veuillez retourner du JSON »
- Analyser les résultats de tests d'extraction comparant les sorties avec et sans schéma
- Mesurer les **taux de validité de schéma** et la **précision des champs** selon les types d'entrée
- Construire un **rapport de fiabilité** prouvant que les sorties structurées éliminent les échecs d'analyse

## Introduction

Lorsqu'un agent extrait des informations d'un texte non structuré — e-mails, factures, CV, tickets de support — il doit retourner des **données structurées** que les systèmes en aval peuvent analyser de manière fiable. Sans application de schéma, même les meilleurs modèles retournent occasionnellement du JSON mal formé, des champs manquants ou des types inattendus.

Les **sorties structurées** résolvent ce problème en contraignant la sortie du modèle à un JSON Schema au moment du décodage. Le modèle *ne peut littéralement pas* produire du JSON invalide.

| Approche | Garantie de validité | Précision des champs | Échecs d'analyse |
|----------|---------------------|---------------------|-----------------|
| Prompt en forme libre (« retournez du JSON ») | ❌ Aucune garantie | Variable | Fréquents |
| Mode JSON | ✅ JSON valide | Variable | Rares |
| **Sorties structurées (JSON Schema)** | ✅ Valide + conforme au schéma | Élevée | **Zéro** |

### Le scénario

Vous êtes un **ingénieur données** qui construit un pipeline d'extraction pour une compagnie d'assurance. Le pipeline traite 5 types de documents : e-mails, factures, CV, tickets de support et avis produits. Vous avez exécuté **15 tests d'extraction** — 10 avec application de schéma et 5 sans — et devez prouver que les sorties structurées sont prêtes pour la production.

Votre jeu de données (`structured_outputs.csv`) contient les résultats. Votre mission : analyser les taux de validité, la précision des champs et construire le dossier pour l'application de schéma.

!!! info "Données simulées"
    Ce lab utilise un fichier CSV de résultats de tests simulés. Les modèles reflètent le comportement réel : les sorties avec schéma atteignent une précision quasi parfaite, tandis que les sorties en forme libre sont incohérentes.

## Prérequis

| Exigence | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| `pandas` | Manipulation des données |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-072/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `broken_structured.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-072/broken_structured.py) |
| `structured_outputs.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-072/structured_outputs.csv) |

---

## Étape 1 : Comprendre les sorties structurées

Les sorties structurées fonctionnent en fournissant un **JSON Schema** en plus de votre prompt. Le décodeur du modèle est contraint à ne produire que des tokens qui résultent en un JSON valide correspondant au schéma.

### Exemple de schéma (Pydantic)

```python
from pydantic import BaseModel
from typing import List

class EmailExtraction(BaseModel):
    name: str
    email: str
    subject: str
    urgency: str  # "low", "medium", "high"

class InvoiceExtraction(BaseModel):
    vendor: str
    amount: float
    date: str
    line_items: List[str]
```

### Fonctionnement

1. Vous définissez un JSON Schema (ou un modèle Pydantic)
2. Vous le passez à l'API en même temps que votre prompt
3. L'échantillonnage de tokens du modèle est contraint pour correspondre au schéma
4. La sortie est **garantie** d'être un JSON valide correspondant à votre schéma — chaque champ présent, chaque type correct

!!! tip "Intégration Pydantic"
    Le SDK Python d'OpenAI peut accepter un modèle Pydantic directement via `response_format=EmailExtraction`. Le SDK gère automatiquement la conversion du schéma.

---

## Étape 2 : Charger et explorer les résultats de tests

Le jeu de données contient **15 tests d'extraction** — 10 avec application de schéma (`gpt-4o`) et 5 sans (`gpt-4o-no-schema`) :

```python
import pandas as pd

df = pd.read_csv("lab-072/structured_outputs.csv")

# Convert string booleans
for col in ["structured_output_valid", "json_parse_success"]:
    df[col] = df[col].astype(str).str.strip().str.lower() == "true"

print(f"Total tests: {len(df)}")
print(f"Models: {df['model'].unique().tolist()}")
print(f"Input types: {df['input_type'].unique().tolist()}")
print(f"\nFirst 5 rows:\n{df.head()}")
```

**Résultat attendu :**

```
Total tests: 15
Models: ['gpt-4o', 'gpt-4o-no-schema']
Input types: ['email', 'invoice', 'resume', 'support_ticket', 'product_review']
```

---

## Étape 3 : Comparer les taux de validité de schéma

La colonne `structured_output_valid` indique si la sortie correspondait au schéma attendu (tous les champs présents, types corrects) :

```python
schema_rows = df[df["model"] == "gpt-4o"]
no_schema_rows = df[df["model"] == "gpt-4o-no-schema"]

schema_valid_rate = schema_rows["structured_output_valid"].mean() * 100
no_schema_valid_rate = no_schema_rows["structured_output_valid"].mean() * 100

print(f"Schema-enforced validity rate:  {schema_valid_rate:.0f}%")
print(f"No-schema validity rate:        {no_schema_valid_rate:.0f}%")
```

**Résultat attendu :**

```
Schema-enforced validity rate:  100%
No-schema validity rate:        0%
```

!!! tip "Aperçu"
    **100 % contre 0 %** — c'est l'argument complet pour les sorties structurées. Avec l'application de schéma, chaque extraction passe la validation. Sans elle, *aucune* ne passe (certaines peuvent être analysées comme JSON, mais des champs manquent ou des types sont incorrects).

---

## Étape 4 : Analyser la précision des champs

Même lorsque le JSON est valide, les *valeurs* extraites peuvent ne pas être précises. La colonne `field_accuracy_pct` mesure combien de champs avaient la valeur correcte :

```python
schema_accuracy = schema_rows["field_accuracy_pct"].mean()
no_schema_accuracy = no_schema_rows["field_accuracy_pct"].mean()

print(f"Avg field accuracy (with schema):    {schema_accuracy:.0f}%")
print(f"Avg field accuracy (without schema): {no_schema_accuracy:.0f}%")
```

**Résultat attendu :**

```
Avg field accuracy (with schema):    98%
Avg field accuracy (without schema): 68%
```

Détaillez par type d'entrée :

```python
accuracy_by_type = df.groupby(["input_type", "model"])["field_accuracy_pct"].mean().unstack()
print(accuracy_by_type.round(1))
```

```python
# Which input types show the biggest accuracy gap?
for input_type in df["input_type"].unique():
    schema_acc = df[(df["input_type"] == input_type) & (df["model"] == "gpt-4o")]["field_accuracy_pct"].mean()
    no_schema_acc = df[(df["input_type"] == input_type) & (df["model"] == "gpt-4o-no-schema")]["field_accuracy_pct"].mean()
    gap = schema_acc - no_schema_acc if not pd.isna(no_schema_acc) else 0
    print(f"  {input_type:>20s}: schema={schema_acc:.0f}%  no-schema={no_schema_acc:.0f}%  gap={gap:.0f}pp")
```

---

## Étape 5 : Mesurer la latence et l'utilisation de tokens

L'application de schéma a un léger surcoût — le modèle doit se conformer aux contraintes pendant le décodage :

```python
for model in df["model"].unique():
    subset = df[df["model"] == model]
    avg_time = subset["time_ms"].mean()
    avg_tokens = subset["tokens"].mean()
    print(f"{model:>20s}: avg_time={avg_time:.0f}ms  avg_tokens={avg_tokens:.0f}")
```

**Résultat attendu :**

```
           gpt-4o: avg_time=915ms  avg_tokens=139
  gpt-4o-no-schema: avg_time=660ms  avg_tokens=121
```

!!! warning "Compromis de latence"
    Les sorties avec schéma sont en moyenne ~38 % plus lentes. C'est attendu — le décodage contraint nécessite un traitement supplémentaire. Pour la plupart des workflows d'agents, la garantie de fiabilité l'emporte largement sur le coût en latence.

---

## Étape 6 : Construire le rapport de fiabilité

```python
report = f"""# 📊 Structured Outputs Reliability Report

## Test Summary
| Metric | With Schema | Without Schema |
|--------|-------------|----------------|
| Tests Run | {len(schema_rows)} | {len(no_schema_rows)} |
| Schema Valid | {schema_valid_rate:.0f}% | {no_schema_valid_rate:.0f}% |
| Avg Field Accuracy | {schema_accuracy:.0f}% | {no_schema_accuracy:.0f}% |
| Avg Latency | {schema_rows['time_ms'].mean():.0f}ms | {no_schema_rows['time_ms'].mean():.0f}ms |
| Avg Tokens | {schema_rows['tokens'].mean():.0f} | {no_schema_rows['tokens'].mean():.0f} |

## Conclusion
Structured Outputs deliver **{schema_valid_rate:.0f}% schema validity** vs. {no_schema_valid_rate:.0f}%
without enforcement. Field accuracy improves from {no_schema_accuracy:.0f}% to {schema_accuracy:.0f}%.

**Recommendation:** Enable Structured Outputs for all extraction pipelines.
The ~38% latency overhead is justified by zero parsing failures in production.
"""

print(report)

with open("lab-072/reliability_report.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-072/reliability_report.md")
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-072/broken_structured.py` contient **3 bugs** qui produisent des métriques incorrectes. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-072/broken_structured.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|-----------------|--------|
| Test 1 | Métrique de taux de succès de schéma | Devrait vérifier `structured_output_valid`, pas `json_parse_success` |
| Test 2 | Précision sans schéma | Devrait filtrer par le modèle sans schéma, pas le modèle avec schéma |
| Test 3 | Tokens moyens par modèle | Devrait filtrer par modèle avant de moyenner |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `All passed!`, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Qu'est-ce qui distingue les sorties structurées du mode JSON classique ?"

    - A) Les sorties structurées sont plus rapides que le mode JSON
    - B) Les sorties structurées garantissent que la sortie correspond à un JSON Schema spécifique, pas seulement à du JSON valide
    - C) Les sorties structurées fonctionnent sans clé API
    - D) Les sorties structurées utilisent une architecture de modèle différente

    ??? success "✅ Révéler la réponse"
        **Correct : B) Les sorties structurées garantissent que la sortie correspond à un JSON Schema spécifique, pas seulement à du JSON valide**

        Le mode JSON assure une syntaxe JSON valide (crochets, guillemets, etc. appropriés), mais la *structure* — quels champs existent, leurs types, l'imbrication — n'est pas appliquée. Les sorties structurées contraignent le décodeur à correspondre à un schéma spécifique, garantissant que chaque champ est présent avec le type correct.

??? question "**Q2 (Choix multiple) :** Quelle bibliothèque Python s'intègre le plus naturellement avec les sorties structurées d'OpenAI pour la définition de schéma ?"

    - A) dataclasses
    - B) marshmallow
    - C) Pydantic
    - D) attrs

    ??? success "✅ Révéler la réponse"
        **Correct : C) Pydantic**

        Le SDK Python d'OpenAI accepte directement les sous-classes `BaseModel` de Pydantic via le paramètre `response_format`. Le SDK convertit automatiquement le modèle Pydantic en JSON Schema, rendant la définition de schéma aussi simple que l'écriture d'une classe Python.

??? question "**Q3 (Exécuter le lab) :** Quel est le taux de validité de schéma pour les tests d'extraction avec schéma ?"

    Exécutez l'analyse de l'étape 3 sur [📥 `structured_outputs.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-072/structured_outputs.csv) et vérifiez les résultats.

    ??? success "✅ Révéler la réponse"
        **100 %**

        Les 10 tests avec schéma (`model=gpt-4o`) ont `structured_output_valid=true`. Le décodeur contraint garantit que chaque sortie correspond au JSON Schema défini — zéro échec d'analyse ou de validation.

??? question "**Q4 (Exécuter le lab) :** Quel est le taux de validité de schéma pour les tests **sans** application de schéma ?"

    Exécutez l'analyse de l'étape 3 pour comparer.

    ??? success "✅ Révéler la réponse"
        **0 %**

        Les 5 tests sans schéma (`model=gpt-4o-no-schema`) ont `structured_output_valid=false`. Même si certains produisent du JSON analysable (`json_parse_success=true`), ils échouent à la validation de schéma car des champs manquent, ont des types incorrects ou utilisent des noms de clés inattendus.

??? question "**Q5 (Exécuter le lab) :** Quelle est la précision moyenne des champs pour les tests avec schéma (lignes gpt-4o) ?"

    Exécutez l'analyse de l'étape 4 pour le calculer.

    ??? success "✅ Révéler la réponse"
        **98 %**

        Les 10 tests avec schéma ont des précisions de champs de 100, 100, 100, 95, 100, 90, 100, 100, 100 et 95. La moyenne est (100+100+100+95+100+90+100+100+100+95) ÷ 10 = **98 %**.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|------------------------|
| Sorties structurées | Décodage contraint par JSON Schema qui garantit une sortie valide |
| Validité du schéma | 100 % avec application vs 0 % sans — élimine les échecs d'analyse |
| Précision des champs | 98 % avec schéma vs 68 % sans — la structure améliore la précision du contenu |
| Intégration Pydantic | Définir des schémas comme des classes Python pour une intégration API transparente |
| Compromis de latence | ~38 % de surcoût justifié par la fiabilité en production |
| Prêt pour la production | Zéro échec d'analyse rend les sorties structurées essentielles pour les pipelines |

---

## Prochaines étapes

- **[Lab 018](lab-018-function-calling.md)** — Appel de fonctions (la base des agents utilisant des outils)
- **[Lab 017](lab-017-structured-output.md)** — Approfondissement des sorties structurées (théorie complémentaire)
- **[Lab 071](lab-071-context-caching.md)** — Mise en cache du contexte (optimisation des coûts pour les workflows riches en schémas)
- **[Lab 073](lab-073-swe-bench.md)** — Benchmarking d'agents avec SWE-bench (évaluer la qualité des agents)
