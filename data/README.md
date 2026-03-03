# Sample Data

This directory contains sample datasets used across the lab exercises. All data is fictional and created for educational purposes.

## Files

| File | Description | Used in Labs |
|------|-------------|-------------|
| `products.csv` | 25 outdoor gear products with SKU, price, category, description | Lab 022, 026, 027 |
| `knowledge-base.json` | Company policies, FAQs, and product guides formatted for RAG ingestion | Lab 022, 026 |
| `orders.csv` | 20 sample customer orders with status and tracking | Lab 027, 032 |

## Raw GitHub URLs (for use in labs)

```
https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv
https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json
https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/orders.csv
```

## Loading products.csv in Python

```python
import csv, urllib.request

url = "https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv"
urllib.request.urlretrieve(url, "products.csv")

with open("products.csv") as f:
    products = list(csv.DictReader(f))

print(f"Loaded {len(products)} products")
```
