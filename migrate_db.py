#!/usr/bin/env python3
"""Migrate the pharmacy database to add purchase_date, quantity to purchases and stock_quantity to available"""

import sqlite3
import random
from datetime import datetime, timedelta

DB_PATH = 'pharmacy_database.db'

def migrate():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Check if columns already exist
    c.execute("PRAGMA table_info(purchase)")
    cols = [row[1] for row in c.fetchall()]

    if 'purchase_date' not in cols:
        print("Adding purchase_date and quantity to purchase table...")
        c.execute("ALTER TABLE purchase ADD COLUMN purchase_date TEXT")
        c.execute("ALTER TABLE purchase ADD COLUMN quantity INTEGER DEFAULT 1")
        c.execute("ALTER TABLE purchase ADD COLUMN total_cost REAL")

        # Backfill existing records with realistic dates and quantities
        c.execute("SELECT med_id, cust_id FROM purchase")
        purchases = c.fetchall()
        base_date = datetime(2026, 1, 15)
        for i, (med_id, cust_id) in enumerate(purchases):
            days_offset = random.randint(0, 85)
            qty = random.choice([1, 1, 1, 2, 2, 3])
            pdate = (base_date + timedelta(days=days_offset)).strftime('%Y-%m-%d')
            c.execute("SELECT cost FROM medicine WHERE med_id = ?", (med_id,))
            cost = c.fetchone()[0]
            total = cost * qty
            c.execute("UPDATE purchase SET purchase_date=?, quantity=?, total_cost=? WHERE med_id=? AND cust_id=?",
                      (pdate, qty, total, med_id, cust_id))
        print(f"  Updated {len(purchases)} existing purchase records")
    else:
        print("purchase_date column already exists, skipping...")

    c.execute("PRAGMA table_info(available)")
    cols = [row[1] for row in c.fetchall()]
    if 'stock_quantity' not in cols:
        print("Adding stock_quantity to available table...")
        c.execute("ALTER TABLE available ADD COLUMN stock_quantity INTEGER DEFAULT 50")
        # Set varied stock levels
        c.execute("SELECT med_id, pharmacy_id FROM available")
        avail = c.fetchall()
        for med_id, ph_id in avail:
            qty = random.randint(10, 200)
            c.execute("UPDATE available SET stock_quantity=? WHERE med_id=? AND pharmacy_id=?",
                      (qty, med_id, ph_id))
        print(f"  Updated {len(avail)} availability records with stock quantities")
    else:
        print("stock_quantity column already exists, skipping...")

    # Add more purchase records for richer analytics
    print("Adding additional purchase records for richer analytics...")
    extra_purchases = [
        ("MED001", "CUST002", "2026-02-10", 2, None),
        ("MED003", "CUST001", "2026-02-15", 1, None),
        ("MED004", "CUST003", "2026-02-20", 3, None),
        ("MED002", "CUST003", "2026-03-01", 1, None),
        ("MED005", "CUST001", "2026-03-05", 2, None),
        ("MED001", "CUST003", "2026-03-10", 1, None),
        ("MED003", "CUST003", "2026-03-15", 2, None),
        ("MED004", "CUST001", "2026-03-20", 1, None),
        ("MED002", "CUST002", "2026-03-25", 2, None),
        ("MED005", "CUST002", "2026-04-01", 1, None),
        ("MED001", "CUST001", "2026-04-05", 3, None),
        ("MED003", "CUST002", "2026-04-10", 1, None),
    ]

    # Need to drop the composite PK constraint — recreate purchase table
    # First check if we already have extra data
    c.execute("SELECT COUNT(*) FROM purchase")
    count = c.fetchone()[0]
    if count <= 5:
        print(f"  Current purchase count: {count}, adding more records...")
        # Drop old table, recreate with new schema allowing duplicate med_id+cust_id pairs
        c.execute("SELECT med_id, cust_id, purchase_date, quantity, total_cost FROM purchase")
        existing = c.fetchall()

        c.execute("DROP TABLE purchase")
        c.execute('''CREATE TABLE purchase (
            purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
            med_id TEXT NOT NULL,
            cust_id TEXT NOT NULL,
            purchase_date TEXT,
            quantity INTEGER DEFAULT 1,
            total_cost REAL,
            FOREIGN KEY (med_id) REFERENCES medicine(med_id),
            FOREIGN KEY (cust_id) REFERENCES customer(cust_id)
        )''')

        # Re-insert existing
        for row in existing:
            c.execute("INSERT INTO purchase (med_id, cust_id, purchase_date, quantity, total_cost) VALUES (?,?,?,?,?)", row)

        # Insert new
        for med_id, cust_id, pdate, qty, _ in extra_purchases:
            c.execute("SELECT cost FROM medicine WHERE med_id = ?", (med_id,))
            cost = c.fetchone()[0]
            total = cost * qty
            c.execute("INSERT INTO purchase (med_id, cust_id, purchase_date, quantity, total_cost) VALUES (?,?,?,?,?)",
                      (med_id, cust_id, pdate, qty, total))
        print(f"  Added {len(extra_purchases)} new purchase records")
    else:
        print(f"  Already have {count} purchase records, skipping...")

    conn.commit()
    conn.close()
    print("\nMigration complete!")

    # Verify
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM purchase")
    print(f"Total purchases: {c.fetchone()[0]}")
    c.execute("SELECT * FROM purchase LIMIT 3")
    for row in c.fetchall():
        print(f"  {row}")
    conn.close()

if __name__ == '__main__':
    migrate()
