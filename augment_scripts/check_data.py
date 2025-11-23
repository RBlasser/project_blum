import sqlite3
import pandas as pd

conn = sqlite3.connect('data/imports/merged/merged_data.db')

print('=== Check tipo_producto vs producto_normalizado ===')
df = pd.read_sql("""
    SELECT 
        tipo_producto,
        producto_normalizado,
        COUNT(*) as count
    FROM flowers_greens
    WHERE tipo_producto LIKE '%demás%' OR tipo_producto LIKE '%otros%'
    GROUP BY tipo_producto, producto_normalizado
    ORDER BY count DESC
    LIMIT 20
""", conn)
print(df.to_string(index=False))

print('\n=== Check if normalization is working ===')
df2 = pd.read_sql("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN tipo_producto = producto_normalizado THEN 1 ELSE 0 END) as unchanged,
        SUM(CASE WHEN tipo_producto != producto_normalizado THEN 1 ELSE 0 END) as changed
    FROM flowers_greens
    WHERE tipo_producto IS NOT NULL
""", conn)
print(df2.to_string(index=False))

print('\n=== Sample of unchanged rows ===')
df3 = pd.read_sql("""
    SELECT tipo_producto, producto_normalizado, COD_INCISO
    FROM flowers_greens
    WHERE tipo_producto = producto_normalizado
      AND (tipo_producto LIKE '%demás%' OR tipo_producto LIKE '%otros%')
    LIMIT 10
""", conn)
print(df3.to_string(index=False))

conn.close()

