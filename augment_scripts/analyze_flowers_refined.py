import sqlite3
import pandas as pd
from pathlib import Path

def analyze_flowers_refined():
    """
    Search for actual flower items (excluding cauliflower, artificial flowers, etc.)
    """
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    
    print("REFINED FLOWER ANALYSIS")
    print("=" * 100)
    
    # Search for actual flowers, excluding false positives
    query = """
        SELECT 
            COD_INCISO,
            COD_CAPITULO,
            COD_PARTIDA,
            COD_SUBPARTIDA,
            CATEGORIA,
            DESCRIPCIÓN,
            COUNT(*) as record_count,
            SUM(CANTIDAD) as total_cantidad,
            SUM(TOTAL_A_PAGAR) as total_value
        FROM merged_imports
        WHERE (
            -- Include flower-related terms
            LOWER(DESCRIPCIÓN) LIKE '%flores frescas%'
            OR LOWER(DESCRIPCIÓN) LIKE '%flores naturales%'
            OR LOWER(DESCRIPCIÓN) LIKE '%rosas%'
            OR LOWER(DESCRIPCIÓN) LIKE '%orquideas%'
            OR LOWER(DESCRIPCIÓN) LIKE '%orquídeas%'
            OR LOWER(DESCRIPCIÓN) LIKE '%claveles%'
            OR LOWER(DESCRIPCIÓN) LIKE '%lirios%'
            OR LOWER(DESCRIPCIÓN) LIKE '%tulipanes%'
            OR LOWER(DESCRIPCIÓN) LIKE '%girasoles%'
            OR LOWER(DESCRIPCIÓN) LIKE '%gerberas%'
            OR LOWER(DESCRIPCIÓN) LIKE '%crisantemos%'
            OR LOWER(DESCRIPCIÓN) LIKE '%gladiolos%'
            OR LOWER(DESCRIPCIÓN) LIKE '%hortensias%'
            OR LOWER(DESCRIPCIÓN) LIKE '%margaritas%'
            OR LOWER(DESCRIPCIÓN) LIKE '%azucenas%'
            OR LOWER(DESCRIPCIÓN) LIKE '%gardenias%'
            OR LOWER(DESCRIPCIÓN) LIKE '%dalias%'
            OR LOWER(DESCRIPCIÓN) LIKE '%petunias%'
            OR LOWER(CATEGORIA) LIKE '%rosas%'
            OR LOWER(CATEGORIA) LIKE '%orquideas%'
            OR LOWER(CATEGORIA) LIKE '%orquídeas%'
            OR LOWER(CATEGORIA) LIKE '%claveles%'
            OR LOWER(CATEGORIA) LIKE '%flores frescas%'
            OR (LOWER(DESCRIPCIÓN) LIKE '%flor%' AND LOWER(DESCRIPCIÓN) LIKE '%fresc%')
            OR (LOWER(CATEGORIA) LIKE '%flor%' AND LOWER(CATEGORIA) LIKE '%fresc%')
        )
        AND (
            -- Exclude false positives
            LOWER(DESCRIPCIÓN) NOT LIKE '%coliflor%'
            AND LOWER(DESCRIPCIÓN) NOT LIKE '%cauliflower%'
            AND LOWER(DESCRIPCIÓN) NOT LIKE '%artificial%'
            AND LOWER(DESCRIPCIÓN) NOT LIKE '%florero%'
            AND LOWER(DESCRIPCIÓN) NOT LIKE '%florida%'
            AND LOWER(DESCRIPCIÓN) NOT LIKE '%floral%'
            AND LOWER(CATEGORIA) NOT LIKE '%coliflor%'
            AND LOWER(CATEGORIA) NOT LIKE '%artificial%'
        )
        GROUP BY COD_INCISO, COD_CAPITULO, COD_PARTIDA, COD_SUBPARTIDA, CATEGORIA, DESCRIPCIÓN
        ORDER BY record_count DESC
    """
    
    print("Searching for actual fresh flowers...")
    print("(Excluding: cauliflower, artificial flowers, vases, etc.)\n")
    
    df = pd.read_sql(query, conn)
    
    print(f"✓ Found {len(df):,} unique flower product entries")
    print(f"✓ Total import records: {df['record_count'].sum():,}")
    print(f"✓ Total value: ${df['total_value'].sum():,.2f}\n")
    
    # Get unique COD_INCISO
    unique_inciso = df['COD_INCISO'].unique()
    print(f"Unique COD_INCISO codes: {len(unique_inciso)}")
    print(f"Codes: {sorted(unique_inciso)}\n")
    
    # Summary by COD_INCISO
    print("=" * 100)
    print("SUMMARY BY COD_INCISO")
    print("=" * 100)
    
    inciso_summary = df.groupby('COD_INCISO').agg({
        'record_count': 'sum',
        'total_cantidad': 'sum',
        'total_value': 'sum'
    }).reset_index()
    inciso_summary.columns = ['COD_INCISO', 'total_records', 'total_cantidad', 'total_value_usd']
    inciso_summary = inciso_summary.sort_values('total_records', ascending=False)
    
    pd.set_option('display.float_format', '{:,.2f}'.format)
    print(inciso_summary.to_string(index=False))
    
    # Show detailed samples for each COD_INCISO
    print("\n" + "=" * 100)
    print("DETAILED SAMPLES BY COD_INCISO")
    print("=" * 100)
    
    for inciso in sorted(unique_inciso):
        inciso_data = df[df['COD_INCISO'] == inciso]
        total_recs = inciso_data['record_count'].sum()
        
        print(f"\n{'='*100}")
        print(f"COD_INCISO: {inciso} ({total_recs:,} records)")
        print(f"{'='*100}")
        
        # Show top descriptions
        top_items = inciso_data.nlargest(10, 'record_count')[['CATEGORIA', 'DESCRIPCIÓN', 'record_count']]
        for idx, row in top_items.iterrows():
            print(f"\n  Records: {row['record_count']:,}")
            print(f"  CATEGORIA: {row['CATEGORIA']}")
            print(f"  DESCRIPCIÓN: {row['DESCRIPCIÓN']}")
    
    # Export results
    output_file = Path("data/imports/merged/flowers_detailed.csv")
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n\n✓ Detailed results exported to: {output_file}")
    
    summary_file = Path("data/imports/merged/flowers_inciso_summary.csv")
    inciso_summary.to_csv(summary_file, index=False, encoding='utf-8-sig')
    print(f"✓ Summary exported to: {summary_file}")
    
    conn.close()

if __name__ == "__main__":
    analyze_flowers_refined()

