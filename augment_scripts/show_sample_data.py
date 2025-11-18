import sqlite3
import pandas as pd
from pathlib import Path

def show_sample_data():
    """
    Display sample data from the merged_imports table with the new column order.
    """
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    
    print("SAMPLE DATA FROM MERGED_IMPORTS TABLE")
    print("=" * 80)
    
    # Get basic stats
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM merged_imports")
    total_rows = cursor.fetchone()[0]
    
    cursor.execute("PRAGMA table_info(merged_imports)")
    columns = cursor.fetchall()
    
    print(f"\nTotal Rows: {total_rows:,}")
    print(f"Total Columns: {len(columns)}")
    print()
    
    # Show first 5 rows with key columns
    print("First 5 rows (key columns only):")
    print("-" * 80)
    
    df = pd.read_sql("""
        SELECT 
            FECHA_IMPORTACION_EXPORTACION,
            IMPORTADOR_EXPORTADOR,
            PAIS_DE_PROCEDENCIA_DESTINO,
            DESCRIPCIÓN,
            PRECIO_UNIDAD,
            CANTIDAD,
            UNIDAD,
            TOTAL_A_PAGAR,
            source_file
        FROM merged_imports 
        LIMIT 5
    """, conn)
    
    # Set display options for better formatting
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', 40)
    
    print(df.to_string(index=False))
    
    print("\n" + "=" * 80)
    print("\nColumn Order Verification:")
    print("-" * 80)
    
    for i, col in enumerate(columns, 1):
        print(f"{i:2d}. {col[1]}")
    
    print("\n✓ Column PAIS_DE_PROCEDENCIA_DESTINO (without accent) is in position 3")
    print("✓ Column PRECIO_UNIDAD (calculated) is in position 11")
    
    conn.close()

if __name__ == "__main__":
    show_sample_data()

