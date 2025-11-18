import sqlite3
import pandas as pd
from pathlib import Path

db_path = Path("data/imports/merged/merged_data.db")
conn = sqlite3.connect(db_path)

flowers = ['Rosas', 'Otras Flores', 'Crisantemos', 'Claveles', 'Plantas Vivas', 
           'Follaje', 'Azucenas', 'Gerberas', 'Gladiolas', 'Orquídeas']

print("=" * 120)
print("TOP IMPORTERS FOR EACH TOP 10 FLOWER")
print("=" * 120)

for flower in flowers:
    print(f"\n{flower.upper()}")
    print("-" * 120)
    
    query = """
    SELECT 
        IMPORTADOR_EXPORTADOR as importer,
        COUNT(*) as shipments,
        ROUND(SUM(CANTIDAD), 0) as volume,
        ROUND(SUM(TOTAL_A_PAGAR), 2) as value_usd
    FROM flowers_greens
    WHERE tipo_producto = ?
      AND IMPORTADOR_EXPORTADOR IS NOT NULL
    GROUP BY IMPORTADOR_EXPORTADOR
    ORDER BY volume DESC
    LIMIT 5
    """
    
    df = pd.read_sql(query, conn, params=[flower])
    print(df.to_string(index=False))

conn.close()

