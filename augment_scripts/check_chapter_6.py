import sqlite3
import pandas as pd
from pathlib import Path

def check_chapter_6():
    """
    Check Chapter 6 codes in both catalogue and imports.
    """
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    
    print("CHAPTER 6 ANALYSIS")
    print("=" * 100)
    
    # Check catalogue
    print("\n1. Chapter 6 codes in CATALOGUE:")
    df_cat = pd.read_sql("""
        SELECT * FROM catalogo_arancel
        WHERE COD_CAPITULO = 6
        ORDER BY COD_INCISO
    """, conn)
    print(f"Found {len(df_cat)} codes")
    print(df_cat[['COD_INCISO', 'COD_CAPITULO', 'COD_PARTIDA', 'DESCRIPCIÓN', 'DAI']].to_string(index=False))
    
    # Check imports
    print("\n2. Chapter 6 codes in IMPORTS:")
    df_imp = pd.read_sql("""
        SELECT DISTINCT
            COD_INCISO,
            COD_CAPITULO,
            COD_PARTIDA,
            CATEGORIA,
            DESCRIPCIÓN
        FROM merged_imports
        WHERE COD_CAPITULO = 6
        ORDER BY COD_INCISO
    """, conn)
    print(f"Found {len(df_imp)} unique codes")
    print(df_imp.to_string(index=False))
    
    # Try to match
    print("\n3. MATCHING TEST:")
    for inciso in df_imp['COD_INCISO'].unique():
        match = df_cat[df_cat['COD_INCISO'] == inciso]
        if len(match) > 0:
            print(f"✓ {inciso} MATCHED: {match.iloc[0]['DESCRIPCIÓN']}")
        else:
            print(f"✗ {inciso} NOT MATCHED")
    
    conn.close()

if __name__ == "__main__":
    check_chapter_6()

