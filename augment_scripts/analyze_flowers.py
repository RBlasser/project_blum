import sqlite3
import pandas as pd
from pathlib import Path

def analyze_flowers():
    """
    Search for all flower-related items in the database and identify their COD_INCISO codes.
    """
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    
    print("FLOWER ANALYSIS - SEARCHING DATABASE")
    print("=" * 80)
    
    # Define flower-related keywords in Spanish
    flower_keywords = [
        'flor', 'flores',
        'rosa', 'rosas',
        'orquidea', 'orquídea', 'orquideas', 'orquídeas',
        'clavel', 'claveles',
        'lirio', 'lirios',
        'tulipan', 'tulipán', 'tulipanes',
        'girasol', 'girasoles',
        'margarita', 'margaritas',
        'gardenia', 'gardenias',
        'azucena', 'azucenas',
        'hortensia', 'hortensias',
        'petunia', 'petunias',
        'dalia', 'dalias',
        'gladiolo', 'gladiolos',
        'crisantemo', 'crisantemos',
        'gerbera', 'gerberas',
        'florales',
        'floristeria', 'floristería',
        'ramo', 'ramos',
        'bouquet',
        'floral'
    ]
    
    # Build SQL query with LIKE conditions
    conditions = []
    for keyword in flower_keywords:
        conditions.append(f"LOWER(CATEGORIA) LIKE '%{keyword.lower()}%'")
        conditions.append(f"LOWER(DESCRIPCIÓN) LIKE '%{keyword.lower()}%'")
    
    where_clause = " OR ".join(conditions)
    
    print(f"\nSearching for {len(flower_keywords)} flower-related keywords...")
    print("Keywords:", ", ".join(flower_keywords[:10]), "...\n")
    
    # Query to find all flower-related records
    query = f"""
        SELECT 
            COD_INCISO,
            COD_CAPITULO,
            COD_PARTIDA,
            COD_SUBPARTIDA,
            CATEGORIA,
            DESCRIPCIÓN,
            COUNT(*) as record_count,
            SUM(CANTIDAD) as total_cantidad,
            SUM(TOTAL_A_PAGAR) as total_value,
            MIN(FECHA_IMPORTACION_EXPORTACION) as first_import,
            MAX(FECHA_IMPORTACION_EXPORTACION) as last_import
        FROM merged_imports
        WHERE {where_clause}
        GROUP BY COD_INCISO, COD_CAPITULO, COD_PARTIDA, COD_SUBPARTIDA, CATEGORIA, DESCRIPCIÓN
        ORDER BY record_count DESC
    """
    
    print("Executing query... (this may take a few minutes)")
    df_flowers = pd.read_sql(query, conn)
    
    print(f"\n✓ Query complete!")
    print(f"\nTotal unique flower product entries found: {len(df_flowers):,}")
    print(f"Total import records: {df_flowers['record_count'].sum():,}")
    
    # Get unique COD_INCISO codes
    unique_inciso = df_flowers['COD_INCISO'].unique()
    print(f"\nUnique COD_INCISO codes for flowers: {len(unique_inciso)}")
    
    # Summary by COD_INCISO
    print("\n" + "=" * 80)
    print("SUMMARY BY COD_INCISO")
    print("=" * 80)
    
    inciso_summary = df_flowers.groupby('COD_INCISO').agg({
        'record_count': 'sum',
        'total_cantidad': 'sum',
        'total_value': 'sum',
        'DESCRIPCIÓN': 'count'
    }).reset_index()
    inciso_summary.columns = ['COD_INCISO', 'total_records', 'total_cantidad', 'total_value', 'unique_descriptions']
    inciso_summary = inciso_summary.sort_values('total_records', ascending=False)
    
    print(inciso_summary.to_string(index=False))
    
    # Show sample descriptions for each COD_INCISO
    print("\n" + "=" * 80)
    print("SAMPLE DESCRIPTIONS BY COD_INCISO")
    print("=" * 80)
    
    for inciso in inciso_summary['COD_INCISO'].head(20):  # Top 20
        print(f"\nCOD_INCISO: {inciso}")
        samples = df_flowers[df_flowers['COD_INCISO'] == inciso][['CATEGORIA', 'DESCRIPCIÓN', 'record_count']].head(5)
        for idx, row in samples.iterrows():
            print(f"  - {row['DESCRIPCIÓN'][:70]:70s} (Records: {row['record_count']:,})")
            print(f"    Categoria: {row['CATEGORIA'][:70]}")
    
    # Export to CSV
    output_file = Path("data/imports/merged/flower_analysis.csv")
    df_flowers.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ Detailed results exported to: {output_file}")
    
    # Export summary
    summary_file = Path("data/imports/merged/flower_inciso_summary.csv")
    inciso_summary.to_csv(summary_file, index=False, encoding='utf-8-sig')
    print(f"✓ COD_INCISO summary exported to: {summary_file}")
    
    conn.close()
    print("\nAnalysis complete!")

if __name__ == "__main__":
    analyze_flowers()

