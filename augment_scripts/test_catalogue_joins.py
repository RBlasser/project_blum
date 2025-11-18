import sqlite3
import pandas as pd
from pathlib import Path

def test_catalogue_joins():
    """
    Test JOIN operations between merged_imports and catalogo_arancel.
    Validate matching logic and coverage.
    """
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    
    print("TESTING CATALOGUE JOIN LOGIC")
    print("=" * 100)
    
    # Test 1: Check table existence
    print("\n1. Verifying tables exist...")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"   Tables found: {tables}")
    
    if 'catalogo_arancel' not in tables:
        print("   ✗ ERROR: catalogo_arancel table not found!")
        return
    
    print("   ✓ Both tables exist")
    
    # Test 2: Sample catalogue data
    print("\n2. Sample catalogue data (first 10 flower codes)...")
    df_cat_sample = pd.read_sql("""
        SELECT * FROM catalogo_arancel 
        WHERE COD_CAPITULO = 6
        LIMIT 10
    """, conn)
    print(df_cat_sample.to_string(index=False))
    
    # Test 3: Check matching coverage
    print("\n3. Checking JOIN coverage...")
    
    coverage_query = """
        SELECT 
            COUNT(DISTINCT i.COD_INCISO) as total_codes_in_imports,
            COUNT(DISTINCT c.COD_INCISO) as matched_codes,
            COUNT(DISTINCT i.COD_INCISO) - COUNT(DISTINCT c.COD_INCISO) as unmatched_codes,
            ROUND(100.0 * COUNT(DISTINCT c.COD_INCISO) / COUNT(DISTINCT i.COD_INCISO), 2) as match_percentage
        FROM merged_imports i
        LEFT JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
    """
    
    df_coverage = pd.read_sql(coverage_query, conn)
    print(df_coverage.to_string(index=False))
    
    # Test 4: Test JOIN with flower data
    print("\n4. Testing JOIN with flower data (Chapter 6)...")
    
    flower_join_query = """
        SELECT 
            i.COD_INCISO,
            c.DESCRIPCIÓN as descripcion_oficial,
            c.CAPITULO_NOMBRE,
            c.DAI,
            COUNT(*) as import_records,
            SUM(i.TOTAL_A_PAGAR) as total_value
        FROM merged_imports i
        INNER JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
        WHERE c.COD_CAPITULO = 6
        GROUP BY i.COD_INCISO, c.DESCRIPCIÓN, c.CAPITULO_NOMBRE, c.DAI
        ORDER BY import_records DESC
        LIMIT 20
    """
    
    df_flowers = pd.read_sql(flower_join_query, conn)
    
    if len(df_flowers) > 0:
        print(f"   ✓ Found {len(df_flowers)} flower codes with imports")
        print("\n   Top flower imports:")
        print(df_flowers.to_string(index=False))
    else:
        print("   ✗ No flower imports found with Chapter 6 codes")
    
    # Test 5: Find unmatched codes
    print("\n5. Sample of unmatched COD_INCISO codes...")
    
    unmatched_query = """
        SELECT 
            i.COD_INCISO,
            i.CATEGORIA,
            i.DESCRIPCIÓN,
            COUNT(*) as record_count
        FROM merged_imports i
        LEFT JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
        WHERE c.COD_INCISO IS NULL
        GROUP BY i.COD_INCISO, i.CATEGORIA, i.DESCRIPCIÓN
        ORDER BY record_count DESC
        LIMIT 10
    """
    
    df_unmatched = pd.read_sql(unmatched_query, conn)
    
    if len(df_unmatched) > 0:
        print(f"   Found {len(df_unmatched)} unmatched codes (showing top 10):")
        print(df_unmatched.to_string(index=False))
    else:
        print("   ✓ All codes matched!")
    
    # Test 6: Create a sample enriched view
    print("\n6. Creating sample enriched data view...")
    
    enriched_query = """
        SELECT 
            i.FECHA_IMPORTACION_EXPORTACION,
            i.IMPORTADOR_EXPORTADOR,
            i.COD_INCISO,
            c.DESCRIPCIÓN as descripcion_oficial,
            c.CAPITULO_NOMBRE,
            i.CANTIDAD,
            i.PRECIO_UNIDAD,
            i.TOTAL_A_PAGAR,
            c.DAI as tarifa_oficial
        FROM merged_imports i
        LEFT JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
        WHERE c.COD_CAPITULO = 6
        LIMIT 5
    """
    
    df_enriched = pd.read_sql(enriched_query, conn)
    
    if len(df_enriched) > 0:
        print("   Sample enriched records:")
        print(df_enriched.T.to_string())  # Transpose for better readability
    
    # Test 7: Summary by chapter
    print("\n7. Import summary by chapter (top 10)...")
    
    chapter_summary_query = """
        SELECT 
            c.COD_CAPITULO,
            c.CAPITULO_NOMBRE,
            COUNT(DISTINCT i.COD_INCISO) as unique_codes,
            COUNT(*) as total_records,
            SUM(i.TOTAL_A_PAGAR) as total_value
        FROM merged_imports i
        INNER JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
        GROUP BY c.COD_CAPITULO, c.CAPITULO_NOMBRE
        ORDER BY total_records DESC
        LIMIT 10
    """
    
    df_chapter_summary = pd.read_sql(chapter_summary_query, conn)
    print(df_chapter_summary.to_string(index=False))
    
    conn.close()
    
    print("\n" + "=" * 100)
    print("✓ JOIN TESTING COMPLETE")
    print("=" * 100)

if __name__ == "__main__":
    test_catalogue_joins()

