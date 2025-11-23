import sqlite3
import pandas as pd
from pathlib import Path

def normalize_product_descriptions():
    """
    Normalize product descriptions by creating a more specific product name
    that combines hierarchical context with the description.
    
    Strategy:
    1. For "Los demás" / "Otros" -> Use parent category (partida/subpartida) name
    2. Clean up redundant text
    3. Create a normalized product name column
    """
    
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    
    print("=" * 100)
    print("NORMALIZING PRODUCT DESCRIPTIONS")
    print("=" * 100)
    
    # First, let's see the problem
    print("\n1. CURRENT PROBLEM - Generic descriptions:")
    query = """
    SELECT DESCRIPCIÓN, COUNT(*) as count
    FROM catalogo_arancel
    WHERE DESCRIPCIÓN LIKE '%demás%' OR DESCRIPCIÓN LIKE '%otros%' OR DESCRIPCIÓN LIKE '%otras%'
    GROUP BY DESCRIPCIÓN
    ORDER BY count DESC
    LIMIT 20
    """
    df_problem = pd.read_sql(query, conn)
    print(df_problem.to_string(index=False))
    
    # Strategy: Create normalized names based on hierarchy
    print("\n\n2. CREATING NORMALIZED PRODUCT NAMES...")
    
    # Add normalized column if it doesn't exist
    try:
        conn.execute("ALTER TABLE catalogo_arancel ADD COLUMN producto_normalizado TEXT")
        conn.commit()
        print("✓ Added producto_normalizado column")
    except:
        print("✓ Column already exists")
    
    # Update with normalized names
    # Rule 1: For "Los demás" - use chapter context
    update_query = """
    UPDATE catalogo_arancel
    SET producto_normalizado = CASE
        -- Specific flower types (Chapter 6)
        WHEN COD_INCISO = 60311000000 THEN 'Rosas'
        WHEN COD_INCISO = 60312000000 THEN 'Claveles'
        WHEN COD_INCISO = 60313000000 THEN 'Orquídeas'
        WHEN COD_INCISO = 60314000000 THEN 'Crisantemos'
        WHEN COD_INCISO = 60315000000 THEN 'Azucenas (Lilium)'
        WHEN COD_INCISO = 60319600000 THEN 'Gerberas'
        WHEN COD_INCISO = 60319920000 THEN 'Gladiolas'
        WHEN COD_INCISO = 60319930000 THEN 'Anturios'
        WHEN COD_INCISO = 60319940000 THEN 'Heliconias'
        
        -- Generic "Los demás" in flowers (0603.19.99)
        WHEN COD_PARTIDA = 603 AND (DESCRIPCIÓN LIKE '%demás%' OR DESCRIPCIÓN LIKE '%otros%') 
            THEN 'Flores Frescas - Otras Variedades'
        
        -- Generic in live plants (0601-0602)
        WHEN COD_PARTIDA BETWEEN 601 AND 602 AND (DESCRIPCIÓN LIKE '%demás%' OR DESCRIPCIÓN LIKE '%otros%')
            THEN 'Plantas Vivas - Otras'
        
        -- Generic in foliage (0604)
        WHEN COD_PARTIDA = 604 AND (DESCRIPCIÓN LIKE '%demás%' OR DESCRIPCIÓN LIKE '%otros%')
            THEN 'Follaje y Ramas - Otros'
        
        -- For vegetables (Chapter 7)
        WHEN COD_CAPITULO = 7 AND (DESCRIPCIÓN LIKE '%demás%' OR DESCRIPCIÓN LIKE '%otros%')
            THEN 'Vegetales - ' || SUBSTR(CAPITULO_NOMBRE, 1, 30)
        
        -- For fruits (Chapter 8)
        WHEN COD_CAPITULO = 8 AND (DESCRIPCIÓN LIKE '%demás%' OR DESCRIPCIÓN LIKE '%otros%')
            THEN 'Frutas - ' || SUBSTR(CAPITULO_NOMBRE, 1, 30)
        
        -- Clean up common patterns
        WHEN DESCRIPCIÓN LIKE 'Los demás%' THEN REPLACE(DESCRIPCIÓN, 'Los demás', 'Otros')
        WHEN DESCRIPCIÓN LIKE 'Las demás%' THEN REPLACE(DESCRIPCIÓN, 'Las demás', 'Otras')
        
        -- Keep original if already specific
        ELSE TRIM(DESCRIPCIÓN)
    END
    """
    
    conn.execute(update_query)
    conn.commit()
    print("✓ Updated producto_normalizado column")
    
    # Now update flowers_greens table
    print("\n3. UPDATING flowers_greens TABLE...")
    
    try:
        conn.execute("ALTER TABLE flowers_greens ADD COLUMN producto_normalizado TEXT")
        conn.commit()
        print("✓ Added producto_normalizado column to flowers_greens")
    except:
        print("✓ Column already exists in flowers_greens")
    
    # Update flowers_greens with normalized names
    update_fg = """
    UPDATE flowers_greens
    SET producto_normalizado = CASE
        -- Use catalogue normalized name if available
        WHEN EXISTS (
            SELECT 1 FROM catalogo_arancel c 
            WHERE c.COD_INCISO = flowers_greens.COD_INCISO
        ) THEN (
            SELECT producto_normalizado 
            FROM catalogo_arancel c 
            WHERE c.COD_INCISO = flowers_greens.COD_INCISO
        )
        -- Fallback to tipo_producto
        ELSE tipo_producto
    END
    """
    
    conn.execute(update_fg)
    conn.commit()
    print("✓ Updated flowers_greens with normalized names")
    
    # Show results
    print("\n4. RESULTS - Normalized names:")
    query_results = """
    SELECT 
        COD_INCISO,
        DESCRIPCIÓN as original,
        producto_normalizado as normalized,
        COUNT(*) OVER (PARTITION BY producto_normalizado) as products_with_same_name
    FROM catalogo_arancel
    WHERE COD_CAPITULO = 6
    ORDER BY COD_INCISO
    LIMIT 30
    """
    df_results = pd.read_sql(query_results, conn)
    print(df_results.to_string(index=False))
    
    # Summary
    print("\n5. SUMMARY:")
    summary = pd.read_sql("""
        SELECT 
            'Before' as status,
            COUNT(DISTINCT DESCRIPCIÓN) as unique_descriptions
        FROM catalogo_arancel
        WHERE COD_CAPITULO IN (6,7,8,9,10,12)
        UNION ALL
        SELECT 
            'After' as status,
            COUNT(DISTINCT producto_normalizado) as unique_descriptions
        FROM catalogo_arancel
        WHERE COD_CAPITULO IN (6,7,8,9,10,12)
    """, conn)
    print(summary.to_string(index=False))
    
    conn.close()
    
    print("\n" + "=" * 100)
    print("✓ NORMALIZATION COMPLETE")
    print("=" * 100)
    print("\nNew column 'producto_normalizado' added to:")
    print("  - catalogo_arancel")
    print("  - flowers_greens")
    print("\nUse this column in Streamlit for cleaner filtering!")

if __name__ == "__main__":
    normalize_product_descriptions()

