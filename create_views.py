import sqlite3, os
db = "data/northwind.sqlite"
if not os.path.exists(db):
    raise SystemExit("DB not found: " + db)
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.executescript("""
CREATE VIEW IF NOT EXISTS orders AS SELECT * FROM Orders;
CREATE VIEW IF NOT EXISTS order_items AS SELECT * FROM "Order Details";
CREATE VIEW IF NOT EXISTS products AS SELECT * FROM Products;
CREATE VIEW IF NOT EXISTS customers AS SELECT * FROM Customers;
""")
conn.commit()
conn.close()
print("Views created successfully in", db)
