import sqlite3
import pandas as pd
from pathlib import Path

def final_catalogue_summary():
    """
    Create final summary of catalogue and JOIN capabilities.
    """
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    
    print("=" * 100)
    print("TARIFF CATALOGUE - FINAL SUMMARY & JOIN VALIDATION")
    print("=" * 100)
    
    # 1. Catalogue Statistics
    print("\n1. CATALOGUE STATISTICS")
    print("-" * 100)
    
    df_cat_stats = pd.read_sql("""
        SELECT 
            COUNT(*) as total_codes,
            COUNT(DISTINCT COD_CAPITULO) as unique_chapters,
            COUNT(DISTINCT COD_PARTIDA) as unique_partidas,
            COUNT(DISTINCT COD_SUBPARTIDA) as unique_subpartidas,
            MIN(COD_INCISO) as min_code,
            MAX(COD_INCISO) as max_code
        FROM catalogo_arancel
    """, conn)
    print(df_cat_stats.T.to_string())
    
    # 2. JOIN Coverage
    print("\n2. JOIN COVERAGE ANALYSIS")
    print("-" * 100)
    
    coverage_query = """
        SELECT 
            COUNT(DISTINCT i.COD_INCISO) as codes_in_imports,
            COUNT(DISTINCT CASE WHEN c.COD_INCISO IS NOT NULL THEN i.COD_INCISO END) as matched_codes,
            COUNT(DISTINCT CASE WHEN c.COD_INCISO IS NULL THEN i.COD_INCISO END) as unmatched_codes,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN c.COD_INCISO IS NOT NULL THEN i.COD_INCISO END) / 
                  COUNT(DISTINCT i.COD_INCISO), 2) as match_percentage,
            COUNT(*) as total_import_records,
            SUM(CASE WHEN c.COD_INCISO IS NOT NULL THEN 1 ELSE 0 END) as matched_records,
            ROUND(100.0 * SUM(CASE WHEN c.COD_INCISO IS NOT NULL THEN 1 ELSE 0 END) / 
                  COUNT(*), 2) as record_match_percentage
        FROM merged_imports i
        LEFT JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
    """
    
    df_coverage = pd.read_sql(coverage_query, conn)
    print(df_coverage.T.to_string())
    
    # 3. Chapter 6 (Flowers) Analysis
    print("\n3. CHAPTER 6 (FLOWERS & PLANTS) - DETAILED ANALYSIS")
    print("-" * 100)
    
    flower_query = """
        SELECT 
            c.COD_INCISO,
            c.DESCRIPCIÓN as descripcion_oficial,
            c.DAI as tarifa_oficial,
            COUNT(i.COD_INCISO) as import_records,
            SUM(i.CANTIDAD) as total_cantidad,
            SUM(i.TOTAL_A_PAGAR) as total_value_usd
        FROM catalogo_arancel c
        LEFT JOIN merged_imports i ON c.COD_INCISO = i.COD_INCISO
        WHERE c.COD_CAPITULO = 6
        GROUP BY c.COD_INCISO, c.DESCRIPCIÓN, c.DAI
        ORDER BY import_records DESC
    """
    
    df_flowers = pd.read_sql(flower_query, conn)
    print(f"\nTotal Chapter 6 codes in catalogue: {len(df_flowers)}")
    print(f"Codes with actual imports: {(df_flowers['import_records'] > 0).sum()}")
    print(f"\nTop 10 flower codes by import volume:")
    print(df_flowers.head(10).to_string(index=False))
    
    # 4. Sample JOIN Query
    print("\n4. SAMPLE JOIN QUERY (First 5 flower imports with official data)")
    print("-" * 100)
    
    sample_query = """
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
        INNER JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
        WHERE c.COD_CAPITULO = 6
        LIMIT 5
    """
    
    df_sample = pd.read_sql(sample_query, conn)
    if len(df_sample) > 0:
        print(df_sample.T.to_string())
    else:
        print("No matched records found")
    
    # 5. Export summary
    print("\n5. EXPORTING RESULTS")
    print("-" * 100)
    
    # Export flower catalogue
    flower_cat_file = Path("data/imports/merged/chapter_06_flowers_catalogue.csv")
    df_flowers.to_csv(flower_cat_file, index=False, encoding='utf-8-sig')
    print(f"✓ Chapter 6 catalogue exported to: {flower_cat_file}")
    
    # Export all chapters summary
    chapters_query = """
        SELECT 
            c.COD_CAPITULO,
            c.CAPITULO_NOMBRE,
            COUNT(DISTINCT c.COD_INCISO) as codes_in_catalogue,
            COUNT(DISTINCT i.COD_INCISO) as codes_with_imports,
            COUNT(i.COD_INCISO) as total_import_records,
            SUM(i.TOTAL_A_PAGAR) as total_value_usd
        FROM catalogo_arancel c
        LEFT JOIN merged_imports i ON c.COD_INCISO = i.COD_INCISO
        GROUP BY c.COD_CAPITULO, c.CAPITULO_NOMBRE
        ORDER BY c.COD_CAPITULO
    """
    
    df_chapters = pd.read_sql(chapters_query, conn)
    chapters_file = Path("data/imports/merged/chapters_summary.csv")
    df_chapters.to_csv(chapters_file, index=False, encoding='utf-8-sig')
    print(f"✓ All chapters summary exported to: {chapters_file}")
    
    conn.close()
    
    print("\n" + "=" * 100)
    print("✓ CATALOGUE READY FOR USE")
    print("=" * 100)
    print("\nJOIN SYNTAX:")
    print("  SELECT * FROM merged_imports i")
    print("  LEFT JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO")
    print("\nFILTER BY CHAPTER:")
    print("  WHERE c.COD_CAPITULO = 6  -- For flowers")
    print("=" * 100)

if __name__ == "__main__":
    final_catalogue_summary()

