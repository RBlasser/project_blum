import sqlite3
import pandas as pd
from pathlib import Path

def create_flowers_greens_table():
    """
    Create flowers_greens table with agricultural products.
    Chapters: 6 (flowers/plants), 7 (vegetables), 8 (fruits), 9 (coffee/tea/spices), 
              10 (cereals), 12 (seeds)
    """
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    
    print("CREATING FLOWERS_GREENS TABLE")
    print("=" * 100)
    
    # Drop existing table
    conn.execute("DROP TABLE IF EXISTS flowers_greens")
    
    # Create table with agricultural products
    query = """
    CREATE TABLE flowers_greens AS
    SELECT 
        i.*,
        c.DESCRIPCIÓN as descripcion_oficial,
        c.CAPITULO_NOMBRE,
        c.DAI as tarifa_oficial,
        CASE 
            WHEN c.COD_CAPITULO = 6 THEN 'Flores y Plantas'
            WHEN c.COD_CAPITULO = 7 THEN 'Vegetales'
            WHEN c.COD_CAPITULO = 8 THEN 'Frutas y Nueces'
            WHEN c.COD_CAPITULO = 9 THEN 'Café, Té, Especias'
            WHEN c.COD_CAPITULO = 10 THEN 'Cereales'
            WHEN c.COD_CAPITULO = 12 THEN 'Semillas y Plantas Agrícolas'
            ELSE 'Otros Agrícolas'
        END as categoria_agricola,
        CASE
            -- Flowers (Chapter 6)
            WHEN c.COD_INCISO = 60311000000 THEN 'Rosas'
            WHEN c.COD_INCISO = 60312000000 THEN 'Claveles'
            WHEN c.COD_INCISO = 60313000000 THEN 'Orquídeas'
            WHEN c.COD_INCISO = 60314000000 THEN 'Crisantemos'
            WHEN c.COD_INCISO = 60315000000 THEN 'Azucenas'
            WHEN c.COD_INCISO = 60319600000 THEN 'Gerberas'
            WHEN c.COD_INCISO = 60319920000 THEN 'Gladiolas'
            WHEN c.COD_INCISO = 60319930000 THEN 'Anturios'
            WHEN c.COD_INCISO = 60319940000 THEN 'Heliconias'
            WHEN c.COD_INCISO BETWEEN 60300000000 AND 60399999999 THEN 'Otras Flores'
            WHEN c.COD_INCISO BETWEEN 60100000000 AND 60299999999 THEN 'Plantas Vivas'
            WHEN c.COD_INCISO BETWEEN 60400000000 AND 60499999999 THEN 'Follaje'
            -- Vegetables (Chapter 7)
            WHEN c.COD_CAPITULO = 7 THEN COALESCE(c.DESCRIPCIÓN, i.DESCRIPCIÓN)
            -- Fruits (Chapter 8)
            WHEN c.COD_CAPITULO = 8 THEN COALESCE(c.DESCRIPCIÓN, i.DESCRIPCIÓN)
            -- Coffee/Tea/Spices (Chapter 9)
            WHEN c.COD_CAPITULO = 9 THEN COALESCE(c.DESCRIPCIÓN, i.DESCRIPCIÓN)
            -- Cereals (Chapter 10)
            WHEN c.COD_CAPITULO = 10 THEN COALESCE(c.DESCRIPCIÓN, i.DESCRIPCIÓN)
            -- Seeds (Chapter 12)
            WHEN c.COD_CAPITULO = 12 THEN COALESCE(c.DESCRIPCIÓN, i.DESCRIPCIÓN)
            ELSE COALESCE(c.DESCRIPCIÓN, i.DESCRIPCIÓN)
        END as tipo_producto
    FROM merged_imports i
    LEFT JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
    WHERE c.COD_CAPITULO IN (6, 7, 8, 9, 10, 12)
       OR i.COD_CAPITULO IN (6, 7, 8, 9, 10, 12)
    """
    
    print("Creating table...")
    conn.execute(query)
    conn.commit()
    
    # Create indexes
    print("Creating indexes...")
    conn.execute("CREATE INDEX idx_fg_fecha ON flowers_greens(FECHA_IMPORTACION_EXPORTACION)")
    conn.execute("CREATE INDEX idx_fg_importador ON flowers_greens(IMPORTADOR_EXPORTADOR)")
    conn.execute("CREATE INDEX idx_fg_tipo ON flowers_greens(tipo_producto)")
    conn.execute("CREATE INDEX idx_fg_categoria ON flowers_greens(categoria_agricola)")
    conn.commit()
    
    # Get statistics
    print("\n" + "=" * 100)
    print("STATISTICS")
    print("=" * 100)
    
    stats = pd.read_sql("""
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT COD_INCISO) as unique_products,
            COUNT(DISTINCT IMPORTADOR_EXPORTADOR) as unique_importers,
            MIN(FECHA_IMPORTACION_EXPORTACION) as first_date,
            MAX(FECHA_IMPORTACION_EXPORTACION) as last_date,
            SUM(TOTAL_A_PAGAR) as total_value
        FROM flowers_greens
    """, conn)
    
    print(stats.T.to_string())
    
    # By category
    print("\n\nBY CATEGORY:")
    by_category = pd.read_sql("""
        SELECT 
            categoria_agricola,
            COUNT(*) as records,
            COUNT(DISTINCT tipo_producto) as unique_products,
            SUM(TOTAL_A_PAGAR) as total_value
        FROM flowers_greens
        GROUP BY categoria_agricola
        ORDER BY records DESC
    """, conn)
    print(by_category.to_string(index=False))
    
    # Top products
    print("\n\nTOP 20 PRODUCTS:")
    top_products = pd.read_sql("""
        SELECT 
            tipo_producto,
            categoria_agricola,
            COUNT(*) as records,
            SUM(CANTIDAD) as total_cantidad,
            ROUND(SUM(TOTAL_A_PAGAR), 2) as total_value
        FROM flowers_greens
        GROUP BY tipo_producto, categoria_agricola
        ORDER BY records DESC
        LIMIT 20
    """, conn)
    print(top_products.to_string(index=False))
    
    # Export sample
    sample_file = Path("data/imports/merged/flowers_greens_sample.csv")
    sample = pd.read_sql("SELECT * FROM flowers_greens LIMIT 1000", conn)
    sample.to_csv(sample_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ Sample exported to: {sample_file}")
    
    conn.close()
    
    print("\n" + "=" * 100)
    print("✓ FLOWERS_GREENS TABLE CREATED")
    print("=" * 100)

if __name__ == "__main__":
    create_flowers_greens_table()

