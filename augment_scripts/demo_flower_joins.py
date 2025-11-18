import sqlite3
import pandas as pd
from pathlib import Path

def demo_flower_joins():
    """
    Demonstrate working JOINs with the catalogue for flower analysis.
    """
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    
    print("=" * 100)
    print("DEMONSTRATION: FLOWER ANALYSIS USING CATALOGUE JOINS")
    print("=" * 100)
    
    # Demo 1: All flower codes from catalogue
    print("\n1. ALL FLOWER CODES IN OFFICIAL CATALOGUE (Chapter 6)")
    print("-" * 100)
    
    query1 = """
        SELECT 
            COD_INCISO,
            DESCRIPCIÓN,
            DAI
        FROM catalogo_arancel
        WHERE COD_CAPITULO = 6
        ORDER BY COD_INCISO
    """
    
    df1 = pd.read_sql(query1, conn)
    print(f"Total official flower/plant codes: {len(df1)}\n")
    print(df1.to_string(index=False))
    
    # Demo 2: Flower imports with official descriptions
    print("\n\n2. ACTUAL FLOWER IMPORTS WITH OFFICIAL CATALOGUE DATA")
    print("-" * 100)
    
    query2 = """
        SELECT 
            c.COD_INCISO,
            c.DESCRIPCIÓN as descripcion_oficial,
            c.DAI as tarifa_oficial,
            COUNT(*) as import_records,
            SUM(i.CANTIDAD) as total_cantidad,
            ROUND(SUM(i.TOTAL_A_PAGAR), 2) as total_value_usd
        FROM merged_imports i
        INNER JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
        WHERE c.COD_CAPITULO = 6
        GROUP BY c.COD_INCISO, c.DESCRIPCIÓN, c.DAI
        HAVING import_records > 0
        ORDER BY total_value_usd DESC
    """
    
    df2 = pd.read_sql(query2, conn)
    print(f"Flower codes with actual imports: {len(df2)}\n")
    
    if len(df2) > 0:
        print(df2.to_string(index=False))
        
        print(f"\n\nSUMMARY:")
        print(f"  Total import records: {df2['import_records'].sum():,}")
        print(f"  Total value: ${df2['total_value_usd'].sum():,.2f}")
    else:
        print("No flower imports found with matching catalogue codes")
    
    # Demo 3: Sample detailed records
    print("\n\n3. SAMPLE DETAILED FLOWER IMPORT RECORDS")
    print("-" * 100)
    
    query3 = """
        SELECT 
            i.FECHA_IMPORTACION_EXPORTACION as fecha,
            i.IMPORTADOR_EXPORTADOR as importador,
            i.PAIS_DE_PROCEDENCIA_DESTINO as pais,
            c.COD_INCISO,
            c.DESCRIPCIÓN as producto_oficial,
            i.CANTIDAD,
            i.UNIDAD,
            ROUND(i.PRECIO_UNIDAD, 2) as precio_unidad,
            ROUND(i.TOTAL_A_PAGAR, 2) as total_pagar,
            c.DAI as tarifa
        FROM merged_imports i
        INNER JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
        WHERE c.COD_CAPITULO = 6
        ORDER BY i.TOTAL_A_PAGAR DESC
        LIMIT 10
    """
    
    df3 = pd.read_sql(query3, conn)
    
    if len(df3) > 0:
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', 30)
        print(df3.to_string(index=False))
    else:
        print("No detailed records found")
    
    # Demo 4: Comparison - with and without catalogue
    print("\n\n4. COMPARISON: IMPORT DATA WITH vs WITHOUT CATALOGUE")
    print("-" * 100)
    
    print("\nWITHOUT CATALOGUE (original import data):")
    query4a = """
        SELECT 
            COD_INCISO,
            CATEGORIA,
            DESCRIPCIÓN,
            COUNT(*) as records
        FROM merged_imports
        WHERE COD_CAPITULO = 6
        GROUP BY COD_INCISO, CATEGORIA, DESCRIPCIÓN
        LIMIT 5
    """
    df4a = pd.read_sql(query4a, conn)
    print(df4a.to_string(index=False))
    
    print("\n\nWITH CATALOGUE (enriched with official data):")
    query4b = """
        SELECT 
            i.COD_INCISO,
            c.DESCRIPCIÓN as descripcion_oficial,
            c.DAI as tarifa_oficial,
            i.CATEGORIA as categoria_importador,
            COUNT(*) as records
        FROM merged_imports i
        INNER JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
        WHERE c.COD_CAPITULO = 6
        GROUP BY i.COD_INCISO, c.DESCRIPCIÓN, c.DAI, i.CATEGORIA
        LIMIT 5
    """
    df4b = pd.read_sql(query4b, conn)
    print(df4b.to_string(index=False))
    
    conn.close()
    
    print("\n" + "=" * 100)
    print("✓ DEMONSTRATION COMPLETE")
    print("=" * 100)
    print("\nThe catalogue is ready to use for:")
    print("  - Identifying official product descriptions")
    print("  - Filtering by product categories (chapters)")
    print("  - Analyzing tariff rates")
    print("  - Enriching import data with official classifications")
    print("=" * 100)

if __name__ == "__main__":
    demo_flower_joins()

