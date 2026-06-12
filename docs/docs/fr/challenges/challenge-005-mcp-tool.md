---
tags: [challenge, mcp, tools, schema, privacy, python, local]
---
# Défi 005 : Construire un outil sûr de style MCP

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Type :</strong> Défi</span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit (local)</span></span>
</div>

## Scénario

OutdoorGear veut exposer un outil de consultation de statut de commande aux agents via un contrat de style MCP. L'outil actuel divulgue les emails clients, accepte des arguments supplémentaires et possède un schéma incomplet.

Votre tâche consiste à concevoir un contrat local d'outil et un chemin d'exécution sûrs avant d'exposer l'outil à un runtime d'agent.

---

## Objectif

Corrigez `starter_mcp_tool.py` afin que le manifeste de l'outil soit valide, que la validation des arguments soit stricte, que les appels invalides soient bloqués, que les recherches de commandes masquent les PII et que le validateur génère un code de réussite.

Votre outil final doit :

- Définir un manifeste clair de `get_order_status` avec un schéma d'entrée
- Accepter uniquement `order_id`
- Rejeter les outils inconnus et les arguments supplémentaires
- Retourner des données sûres de statut de commande sans `customer_email`
- Rapporter correctement les métriques de contrat

---

## Fichiers de départ

Enregistrez ces fichiers dans un dossier nommé `challenge-005/` :

| Fichier | Objectif | Télécharger |
|---------|----------|-------------|
| `orders.json` | Commandes mock OutdoorGear | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/orders.json) |
| `tool_requests.json` | Appels d'outil valides et invalides | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/tool_requests.json) |
| `starter_mcp_tool.py` | Implémentation cassée d'outil style MCP | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/starter_mcp_tool.py) |
| `test_mcp_tool.py` | Tests d'acceptation | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/test_mcp_tool.py) |
| `validate_mcp_tool.py` | Génère le code final de réussite | [Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/challenges/challenge-005/validate_mcp_tool.py) |

---

## Brief du défi

Vous recevez des commandes mock, des appels d'outil valides et invalides, et une implémentation cassée. Il n'y a pas de walkthrough : décidez comment décrire l'outil, valider les arguments, dispatcher l'exécution et masquer les champs sensibles.

---

## Contraintes

- Utilisez uniquement la bibliothèque standard Python dans `starter_mcp_tool.py`.
- N'exposez pas `customer_email` dans les résultats de l'outil.
- N'acceptez pas d'arguments supplémentaires.
- N'exécutez pas d'outils inconnus.
- Préservez les noms publics des fonctions utilisés par les tests.

---

## Critères d'acceptation

Votre solution est complète lorsque :

- `python -m pytest test_mcp_tool.py` passe
- Le manifeste inclut un `inputSchema` valide
- Seul `order_id` est accepté en entrée
- Les outils inconnus et les arguments supplémentaires avec PII sont bloqués
- Les appels réussis retournent `delivered` et `processing`
- Les résultats de l'outil sont masqués

---

## Validation

Lorsque votre implémentation est prête, exécutez :

```bash
python -m pytest test_mcp_tool.py
python validate_mcp_tool.py
```

Saisissez le code de réussite imprimé par `validate_mcp_tool.py` :

<div class="challenge-validator" data-answer="CH005-CD4DDCBC">
  <input type="text" aria-label="Code de réussite" placeholder="CH005-XXXXXXXX" />
  <button type="button">Valider</button>
  <p class="challenge-validator-result" aria-live="polite"></p>
</div>

---

## Indices

??? tip "Indice 1 — Le schéma est une frontière de sécurité"
    Un schéma trop souple invite les agents à envoyer des champs que l'outil ne devrait jamais recevoir.

??? tip "Indice 2 — Le masquage doit être proche de l'outil"
    Ne comptez pas sur l'agent pour cacher les champs sensibles après leur retour par l'outil.

??? tip "Indice 3 — Échouez fermé"
    Les outils inconnus, champs requis manquants et arguments supplémentaires doivent générer une erreur.

---

## Rubrique

| Domaine | Points | Ce qui est attendu |
|---------|:------:|--------------------|
| Contrat du manifeste | 25 | Nom, description, schéma et champs requis clairs |
| Validation des arguments | 25 | Les champs manquants et supplémentaires sont rejetés |
| Exécution sûre | 25 | Statut correct de commande avec PII masquées |
| Gestion d'erreurs | 15 | Les appels inconnus ou invalides échouent fermés |
| Simplicité | 10 | Code d'outil petit et déterministe |

---

## Labs associés

- [Lab 012 — Qu'est-ce que MCP ?](../labs/lab-012-what-is-mcp.md)
- [Lab 020 — Serveur MCP en Python](../labs/lab-020-mcp-server-python.md)
- [Lab 064 — Sécuriser MCP avec APIM](../labs/lab-064-securing-mcp-apim.md)
