import sqlite3
import pandas as pd
from pathlib import Path

def debug_catalogue():
    """
    Debug the catalogue to see what was extracted.
    """
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    
    print("DEBUGGING CATALOGUE")
    print("=" * 100)
    
    # Check what chapters we have
    print("\n1. Chapters in catalogue:")
    df_chapters = pd.read_sql("""
        SELECT 
            COD_CAPITULO,
            CAPITULO_NOMBRE,
            COUNT(*) as code_count
        FROM catalogo_arancel
        GROUP BY COD_CAPITULO, CAPITULO_NOMBRE
        ORDER BY COD_CAPITULO
        LIMIT 20
    """, conn)
    print(df_chapters.to_string(index=False))
    
    # Check codes starting with 06
    print("\n2. Codes starting with 06:")
    df_06 = pd.read_sql("""
        SELECT * FROM catalogo_arancel
        WHERE COD_INCISO >= 600000000000 AND COD_INCISO < 700000000000
        LIMIT 20
    """, conn)
    print(f"Found {len(df_06)} codes")
    if len(df_06) > 0:
        print(df_06.to_string(index=False))
    
    # Check sample of all codes
    print("\n3. Sample of all codes in catalogue:")
    df_sample = pd.read_sql("""
        SELECT * FROM catalogo_arancel
        LIMIT 10
    """, conn)
    print(df_sample.to_string(index=False))
    
    # Check what's in imports for chapter 6
    print("\n4. Chapter 6 codes in imports:")
    df_imports_06 = pd.read_sql("""
        SELECT 
            COD_INCISO,
            CATEGORIA,
            DESCRIPCIÓN,
            COUNT(*) as count
        FROM merged_imports
        WHERE COD_CAPITULO = 6
        GROUP BY COD_INCISO, CATEGORIA, DESCRIPCIÓN
        LIMIT 10
    """, conn)
    print(f"Found {len(df_imports_06)} unique codes")
    if len(df_imports_06) > 0:
        print(df_imports_06.to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    debug_catalogue()

