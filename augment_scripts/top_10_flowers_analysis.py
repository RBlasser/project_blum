import sqlite3
import pandas as pd
from pathlib import Path

def analyze_top_flowers():
    """
    Analyze Top 10 flowers by volume and value with their importers.
    """
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    
    print("=" * 120)
    print("TOP 10 FLOWERS ANALYSIS")
    print("=" * 120)
    
    # Top 10 by Volume
    print("\n1. TOP 10 FLOWERS BY TOTAL VOLUME")
    print("-" * 120)
    
    query_volume = """
    SELECT 
        tipo_producto,
        COUNT(*) as shipments,
        SUM(CANTIDAD) as total_volume,
        ROUND(SUM(TOTAL_A_PAGAR), 2) as total_value_usd,
        ROUND(AVG(PRECIO_UNIDAD), 2) as avg_price_per_unit,
        COUNT(DISTINCT IMPORTADOR_EXPORTADOR) as num_importers
    FROM flowers_greens
    WHERE categoria_agricola = 'Flores y Plantas'
      AND CANTIDAD > 0
    GROUP BY tipo_producto
    ORDER BY total_volume DESC
    LIMIT 10
    """
    
    df_volume = pd.read_sql(query_volume, conn)
    print(df_volume.to_string(index=False))
    
    # Top 10 by Value
    print("\n\n2. TOP 10 FLOWERS BY TOTAL VALUE (USD)")
    print("-" * 120)
    
    query_value = """
    SELECT 
        tipo_producto,
        COUNT(*) as shipments,
        SUM(CANTIDAD) as total_volume,
        ROUND(SUM(TOTAL_A_PAGAR), 2) as total_value_usd,
        ROUND(AVG(PRECIO_UNIDAD), 2) as avg_price_per_unit,
        COUNT(DISTINCT IMPORTADOR_EXPORTADOR) as num_importers
    FROM flowers_greens
    WHERE categoria_agricola = 'Flores y Plantas'
      AND TOTAL_A_PAGAR > 0
    GROUP BY tipo_producto
    ORDER BY total_value_usd DESC
    LIMIT 10
    """
    
    df_value = pd.read_sql(query_value, conn)
    print(df_value.to_string(index=False))
    
    # Top importers for each top flower
    print("\n\n3. TOP IMPORTERS FOR EACH TOP FLOWER (BY VOLUME)")
    print("=" * 120)
    
    for flower in df_volume['tipo_producto'].head(10):
        print(f"\n{flower}")
        print("-" * 120)
        
        query_importers = """
        SELECT 
            IMPORTADOR_EXPORTADOR as importer,
            COUNT(*) as shipments,
            ROUND(SUM(CANTIDAD), 2) as volume,
            ROUND(SUM(TOTAL_A_PAGAR), 2) as value_usd,
            ROUND(AVG(PRECIO_UNIDAD), 2) as avg_price
        FROM flowers_greens
        WHERE tipo_producto = ?
          AND categoria_agricola = 'Flores y Plantas'
          AND IMPORTADOR_EXPORTADOR IS NOT NULL
        GROUP BY IMPORTADOR_EXPORTADOR
        ORDER BY volume DESC
        LIMIT 5
        """
        
        df_imp = pd.read_sql(query_importers, conn, params=[flower])
        if not df_imp.empty:
            print(df_imp.to_string(index=False))
        else:
            print("No importer data available")
    
    # Summary by flower type
    print("\n\n4. SUMMARY: ALL FLOWER TYPES")
    print("=" * 120)
    
    query_summary = """
    SELECT 
        tipo_producto,
        COUNT(*) as shipments,
        ROUND(SUM(CANTIDAD), 2) as total_volume,
        ROUND(SUM(TOTAL_A_PAGAR), 2) as total_value_usd,
        COUNT(DISTINCT IMPORTADOR_EXPORTADOR) as num_importers,
        COUNT(DISTINCT PAIS_DE_PROCEDENCIA_DESTINO) as num_countries,
        MIN(FECHA_IMPORTACION_EXPORTACION) as first_import,
        MAX(FECHA_IMPORTACION_EXPORTACION) as last_import
    FROM flowers_greens
    WHERE categoria_agricola = 'Flores y Plantas'
    GROUP BY tipo_producto
    ORDER BY total_volume DESC
    """
    
    df_summary = pd.read_sql(query_summary, conn)
    print(df_summary.to_string(index=False))
    
    # Export results
    output_dir = Path("data/imports/merged")
    
    df_volume.to_csv(output_dir / "top_10_flowers_by_volume.csv", index=False, encoding='utf-8-sig')
    df_value.to_csv(output_dir / "top_10_flowers_by_value.csv", index=False, encoding='utf-8-sig')
    df_summary.to_csv(output_dir / "all_flowers_summary.csv", index=False, encoding='utf-8-sig')
    
    print("\n\n" + "=" * 120)
    print("✓ ANALYSIS COMPLETE")
    print("=" * 120)
    print(f"\nExported files:")
    print(f"  - {output_dir / 'top_10_flowers_by_volume.csv'}")
    print(f"  - {output_dir / 'top_10_flowers_by_value.csv'}")
    print(f"  - {output_dir / 'all_flowers_summary.csv'}")
    
    conn.close()

if __name__ == "__main__":
    analyze_top_flowers()

