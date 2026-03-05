# Comment utiliser ce hub

Cette page explique comment le Hub d'Apprentissage des Agents IA est structuré afin que vous puissiez y naviguer efficacement et tirer le meilleur parti de chaque lab.

---

## 📊 Le système de niveaux

Chaque lab est étiqueté avec un niveau de **50 à 400**, inspiré de la numérotation des sessions de conférences Microsoft (un signal largement reconnu de profondeur).

| Niveau | Badge | Nom | À quoi s'attendre | Compte nécessaire |
|--------|-------|-----|-------------------|-------------------|
| 50 | <span class="level-badge level-50">L50</span> | Sensibilisation | Lecture et concepts. Pas d'outils, pas de compte. | ❌ Aucun |
| 100 | <span class="level-badge level-100">L100</span> | Fondamentaux | Premiers labs pratiques. Configuration minimale. | ✅ GitHub gratuit |
| 200 | <span class="level-badge level-200">L200</span> | Intermédiaire | Code + cloud gratuit (GitHub Models). | ✅ GitHub gratuit |
| 300 | <span class="level-badge level-300">L300</span> | Avancé | Services cloud, patterns d'intégration. | ✅ Abonnement Azure |
| 400 | <span class="level-badge level-400">L400</span> | Expert | Architecture de production, évaluations, coûts. | ✅ Azure payant |

!!! tip "Commencez au bon niveau"
    Ne sautez pas les niveaux L50/L100 même si vous êtes un développeur expérimenté — le cadrage conceptuel vous aide à prendre de meilleures décisions par la suite.

---

## 🗺️ Parcours d'apprentissage

Les labs sont regroupés en **8 parcours d'apprentissage**, chacun axé sur un outil ou une technologie :

| Parcours | Idéal pour | Point d'entrée |
|----------|-----------|----------------|
| 🤖 GitHub Copilot | Utilisateurs GitHub, développeurs | L100 |
| 🏭 Microsoft Foundry | Développeurs Azure, ingénieurs ML | L200 |
| 🔌 MCP | Toute personne créant des intégrations d'agents | L100 |
| 🧠 Semantic Kernel | Développeurs Python / C# | L100 |
| 📚 RAG | Développeurs travaillant avec des documents/données | L100 |
| 👥 Agent Builder — Teams | Développeurs M365 | L100 |
| 💻 Agent Builder — VS Code | Développeurs d'extensions | L100 |
| ⚙️ Pro Code Agents | Ingénieurs seniors, architectes | L200 |

Chaque parcours a une **page d'index** avec la liste complète des labs, un ordre recommandé et un bref aperçu de ce que vous allez construire.

---

## 💡 Itinéraires d'apprentissage suggérés

### Itinéraire A — « De zéro à l'agent » (Aucun compte requis pour commencer)
```
Lab 001 → Lab 002 → Lab 003 → Lab 012 → Lab 020 (Python or C#)
```
Passez de zéro connaissance à l'exécution de votre propre serveur MCP en local, sans aucun compte cloud nécessaire.

### Itinéraire B — « GitHub uniquement » (Compte GitHub gratuit uniquement)
```
Lab 010 → Lab 013 → Lab 014 → Lab 022 → Lab 023
```
Utilisez GitHub Copilot, GitHub Models et Semantic Kernel — tout est gratuit, sans carte bancaire.

### Itinéraire C — « Stack Azure complète »
```
Lab 013 → Lab 020 → Lab 030 → Lab 031 → Lab 032 → Lab 033
```
Nécessite un abonnement Azure. Construisez un agent Foundry complet avec MCP, pgvector, RLS et observabilité.

### Itinéraire D — « Développeur Teams »
```
Lab 001 → Lab 011 → Lab 024
```
Construisez des agents Copilot Studio et des bots Teams étape par étape.

---

## 🔖 Lire une page de lab

Chaque page de lab suit cette structure standard :

```
# Lab XXX: [Title]

[Info box: Level · Path · Time · Cost]

## What You'll Learn
## Introduction
## Prerequisites Setup
## Lab Exercise
  ### Step 1 ...
  ### Step 2 ...
## Summary
## Next Steps
```

- **Encadré d'information** en haut vous indique tout en un coup d'œil : niveau, temps estimé et exigences de coût/compte.
- **Configuration des prérequis** vous indique exactement quoi installer ou configurer — avec des liens directs vers les inscriptions aux essais gratuits.
- **Exercice du lab** est la procédure pas à pas.
- **Prochaines étapes** renvoie à la suite naturelle du lab.

---

## 💰 Gratuit vs. Payant — Notre engagement

Nous croyons que les meilleures ressources d'apprentissage sont accessibles. Nos objectifs :

- ✅ **L50 et L100** : Zéro coût, zéro carte bancaire, juste un compte GitHub gratuit
- ✅ **L200** : Utilisez [GitHub Models](https://github.com/marketplace/models) — inférence gratuite, sans carte bancaire
- ⚠️ **L300** : Niveau gratuit Azure quand c'est possible ; clairement indiqué quand un abonnement Azure est nécessaire
- ⚠️ **L400** : Ressources Azure payantes requises — coûts estimés indiqués dans chaque lab

→ Voir [Prérequis & comptes](prerequisites.md) pour le guide de configuration complet.
