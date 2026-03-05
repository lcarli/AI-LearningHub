#!/usr/bin/env python3
"""
🐛 Broken Query Generator — Lab 052 Bug-Fix Exercise

Functions that query a product database but have 3 bugs.
Fix them and run the self-tests to verify.

Usage:
    python lab-052/broken_query_gen.py
"""

import sqlite3
import pandas as pd


def count_in_stock(conn: sqlite3.Connection, category: str) -> int:
    """Count products in a category that are currently in stock."""
    # 🐛 Bug #1: Missing 'AND stock > 0' — counts ALL products
    #            including out-of-stock items
    cur = conn.execute(
        "SELECT COUNT(*) FROM products WHERE category = ?", (category,)
    )
    return cur.fetchone()[0]


def total_revenue(conn: sqlite3.Connection) -> float:
    """Calculate total revenue from all orders."""
    # 🐛 Bug #2: Calculates price × stock (inventory value) instead
    #            of summing order totals (actual revenue)
    cur = conn.execute("SELECT SUM(price * stock) FROM products")
    return cur.fetchone()[0]


def most_ordered_product(conn: sqlite3.Connection) -> str:
    """Return the product_id with the most orders (most order rows)."""
    # 🐛 Bug #3: Orders by quantity DESC (most items in one order)
    #            instead of COUNT(*) DESC (most separate orders)
    cur = conn.execute(
        "SELECT product_id FROM orders ORDER BY quantity DESC LIMIT 1"
    )
    return cur.fetchone()[0]


def run_tests() -> bool:
    conn = sqlite3.connect(":memory:")
    conn.execute("""CREATE TABLE products (
        product_id TEXT, name TEXT, category TEXT, price REAL, stock INTEGER)""")
    conn.execute("""CREATE TABLE orders (
        order_id TEXT, customer_id TEXT, product_id TEXT, quantity INTEGER, total REAL)""")

    conn.executemany("INSERT INTO products VALUES (?,?,?,?,?)", [
        ("P1", "Tent A", "Tents", 100.0, 10),
        ("P2", "Tent B", "Tents", 80.0, 5),
        ("P3", "Tent C", "Tents", 60.0, 0),
        ("P4", "Boot A", "Footwear", 50.0, 20),
    ])
    conn.executemany("INSERT INTO orders VALUES (?,?,?,?,?)", [
        ("O1", "C1", "P1", 1, 100.0),
        ("O2", "C2", "P1", 1, 100.0),
        ("O3", "C3", "P1", 1, 100.0),
        ("O4", "C1", "P2", 10, 800.0),
        ("O5", "C2", "P4", 2, 100.0),
    ])
    conn.commit()

    passed = 0
    failed = 0

    # ── Test 1: Count in-stock tents ─────────────────────────────────────
    #   P1(stock=10), P2(stock=5) in stock. P3(stock=0) out of stock → 2
    count = count_in_stock(conn, "Tents")
    if count == 2:
        print(f"✅ Test 1 PASSED: in-stock tents = {count}")
        passed += 1
    else:
        print(f"❌ Test 1 FAILED: in-stock tents = {count}  (expected 2)")
        failed += 1

    # ── Test 2: Total revenue from orders ────────────────────────────────
    #   100+100+100+800+100 = $1,200
    rev = total_revenue(conn)
    if abs(rev - 1200.0) < 0.01:
        print(f"✅ Test 2 PASSED: revenue = ${rev:,.2f}")
        passed += 1
    else:
        print(f"❌ Test 2 FAILED: revenue = ${rev:,.2f}  (expected $1,200.00)")
        failed += 1

    # ── Test 3: Most ordered product (by number of orders) ───────────────
    #   P1 has 3 orders, P2 has 1 (qty=10), P4 has 1 → P1 wins
    pid = most_ordered_product(conn)
    if pid == "P1":
        print(f"✅ Test 3 PASSED: most ordered = {pid}")
        passed += 1
    else:
        print(f"❌ Test 3 FAILED: most ordered = {pid}  (expected P1)")
        failed += 1

    conn.close()
    print()
    if failed == 0:
        print("🎉 All 3 tests passed — great debugging!")
    else:
        print(f"🔧 {failed} test(s) failed — keep debugging!")
    return failed == 0


if __name__ == "__main__":
    print("🧪 Running self-tests for broken_query_gen.py …\n")
    run_tests()
