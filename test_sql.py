#!/usr/bin/env python
"""Quick test of SQLiteTool with the fixed SQL."""
from agent.tools.sqlite_tool import SQLiteTool

tool = SQLiteTool(r'C:\Users\lenovo\retail-analytics-copilot\data\Northwind.sqlite')

# Test Q2: Top category by quantity in summer 2013
sql = """SELECT c.CategoryName as category, SUM(od.Quantity) as quantity FROM [Order Details] od JOIN Orders o ON o.OrderID = od.OrderID JOIN Products p ON p.ProductID = od.ProductID JOIN Categories c ON c.CategoryID = p.CategoryID WHERE o.OrderDate BETWEEN '2013-06-01' AND '2013-06-30' GROUP BY c.CategoryID ORDER BY quantity DESC LIMIT 1;"""

print("Testing SQL:", sql)
result = tool.execute(sql)
print("Result:", result)
print()

# Test Q3: AOV in winter 2017
sql2 = """SELECT ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)) * 1.0 / NULLIF(COUNT(DISTINCT o.OrderID), 0), 2) as aov FROM [Order Details] od JOIN Orders o ON o.OrderID = od.OrderID WHERE o.OrderDate BETWEEN '2017-12-01' AND '2017-12-31';"""

print("Testing SQL:", sql2)
result2 = tool.execute(sql2)
print("Result:", result2)
print()

# Test Q5: Beverages revenue in summer 2013
sql3 = """SELECT ROUND(SUM(od.UnitPrice * od.Quantity * (1 - od.Discount)), 2) as revenue FROM [Order Details] od JOIN Orders o ON o.OrderID = od.OrderID JOIN Products p ON p.ProductID = od.ProductID JOIN Categories c ON c.CategoryID = p.CategoryID WHERE c.CategoryName = 'Beverages' AND o.OrderDate BETWEEN '2013-06-01' AND '2013-06-30';"""

print("Testing SQL:", sql3)
result3 = tool.execute(sql3)
print("Result:", result3)
