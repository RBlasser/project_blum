import sqlite3
import pandas as pd
from pathlib import Path

def check_precio_unidad():
    """
    Quick check of the PRECIO_UNIDAD column.
    """
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    
    # Get column list
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(merged_imports);")
    columns = cursor.fetchall()
    
    print("Columns in merged_imports table:")
    for col in columns:
        print(f"  {col[0] + 1}. {col[1]} ({col[2]})")
    
    print(f"\nTotal columns: {len(columns)}")
    
    # Check if PRECIO_UNIDAD exists
    column_names = [col[1] for col in columns]
    if 'PRECIO_UNIDAD' in column_names:
        print("\n✓ PRECIO_UNIDAD column exists!")
        
        # Show sample calculations
        print("\nSample data showing calculation:")
        df = pd.read_sql("""
            SELECT 
                CANTIDAD,
                TOTAL_A_PAGAR,
                PRECIO_UNIDAD,
                ROUND(TOTAL_A_PAGAR / CANTIDAD, 2) as calculated,
                DESCRIPCIÓN
            FROM merged_imports 
            WHERE CANTIDAD > 0 AND TOTAL_A_PAGAR IS NOT NULL
            LIMIT 5
        """, conn)
        print(df.to_string())
    else:
        print("\n✗ PRECIO_UNIDAD column NOT found!")
    
    conn.close()

if __name__ == "__main__":
    check_precio_unidad()

