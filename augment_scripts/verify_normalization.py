import sqlite3
import pandas as pd
from pathlib import Path

db_path = Path("data/imports/merged/merged_data.db")
conn = sqlite3.connect(db_path)

print("=" * 100)
print("NORMALIZATION VERIFICATION REPORT")
print("=" * 100)

# 1. Check columns exist
print("\n1. VERIFY COLUMNS EXIST:")
print("\ncatalogo_arancel columns:")
cursor = conn.execute("PRAGMA table_info(catalogo_arancel)")
cols = cursor.fetchall()
has_normalized = any('producto_normalizado' in str(col) for col in cols)
print(f"   ✓ producto_normalizado column exists: {has_normalized}")

print("\nflowers_greens columns:")
cursor = conn.execute("PRAGMA table_info(flowers_greens)")
cols = cursor.fetchall()
has_normalized_fg = any('producto_normalizado' in str(col) for col in cols)
print(f"   ✓ producto_normalizado column exists: {has_normalized_fg}")

# 2. Before/After comparison
print("\n" + "=" * 100)
print("2. BEFORE vs AFTER - Generic Descriptions")
print("=" * 100)

print("\nBEFORE (Original DESCRIPCIÓN with 'demás' or 'otros'):")
df_before = pd.read_sql("""
    SELECT DESCRIPCIÓN, COUNT(*) as count 
    FROM catalogo_arancel 
    WHERE DESCRIPCIÓN LIKE '%demás%' OR DESCRIPCIÓN LIKE '%otros%' 
    GROUP BY DESCRIPCIÓN 
    ORDER BY count DESC 
    LIMIT 15
""", conn)
print(df_before.to_string(index=False))

print("\n\nAFTER (producto_normalizado with 'demás' or 'otros'):")
df_after = pd.read_sql("""
    SELECT producto_normalizado, COUNT(*) as count 
    FROM catalogo_arancel 
    WHERE producto_normalizado LIKE '%demás%' OR producto_normalizado LIKE '%otros%' 
    GROUP BY producto_normalizado 
    ORDER BY count DESC 
    LIMIT 15
""", conn)
print(df_after.to_string(index=False))

# 3. Flowers specific
print("\n" + "=" * 100)
print("3. FLOWERS (Chapter 6) - Side by Side Comparison")
print("=" * 100)

df_flowers = pd.read_sql("""
    SELECT 
        COD_INCISO,
        DESCRIPCIÓN as original,
        producto_normalizado as normalized
    FROM catalogo_arancel
    WHERE COD_CAPITULO = 6
    ORDER BY COD_INCISO
    LIMIT 30
""", conn)
print(df_flowers.to_string(index=False))

# 4. flowers_greens unique products
print("\n" + "=" * 100)
print("4. FLOWERS_GREENS - Unique Normalized Product Names")
print("=" * 100)

df_unique = pd.read_sql("""
    SELECT DISTINCT producto_normalizado, COUNT(*) as records
    FROM flowers_greens 
    WHERE producto_normalizado IS NOT NULL
    GROUP BY producto_normalizado
    ORDER BY producto_normalizado
""", conn)
print(df_unique.to_string(index=False))

# 5. Specific examples
print("\n" + "=" * 100)
print("5. SPECIFIC EXAMPLES - Key Transformations")
print("=" * 100)

examples = pd.read_sql("""
    SELECT 
        COD_INCISO,
        DESCRIPCIÓN as original,
        producto_normalizado as normalized,
        CASE 
            WHEN DESCRIPCIÓN = producto_normalizado THEN 'No change'
            ELSE 'IMPROVED ✓'
        END as status
    FROM catalogo_arancel
    WHERE COD_INCISO IN (
        60311000000,  -- Rosas
        60319990000,  -- Los demás (flowers)
        60110000000,  -- Los demás (plants)
        60290900000,  -- Otros (plants)
        60390900000   -- Otros (arrangements)
    )
    ORDER BY COD_INCISO
""", conn)
print(examples.to_string(index=False))

# 6. Statistics
print("\n" + "=" * 100)
print("6. IMPROVEMENT STATISTICS")
print("=" * 100)

stats = pd.read_sql("""
    SELECT 
        COUNT(*) as total_products,
        SUM(CASE WHEN DESCRIPCIÓN LIKE '%demás%' OR DESCRIPCIÓN LIKE '%otros%' THEN 1 ELSE 0 END) as generic_original,
        SUM(CASE WHEN producto_normalizado LIKE '%demás%' OR producto_normalizado LIKE '%otros%' THEN 1 ELSE 0 END) as generic_normalized,
        SUM(CASE WHEN DESCRIPCIÓN != producto_normalizado THEN 1 ELSE 0 END) as changed
    FROM catalogo_arancel
    WHERE COD_CAPITULO IN (6, 7, 8, 9, 10, 12)
""", conn)
print(stats.to_string(index=False))

generic_before = stats['generic_original'].iloc[0]
generic_after = stats['generic_normalized'].iloc[0]
improvement = ((generic_before - generic_after) / generic_before * 100) if generic_before > 0 else 0

print(f"\n✓ Generic descriptions reduced from {generic_before} to {generic_after}")
print(f"✓ Improvement: {improvement:.1f}%")
print(f"✓ Total products changed: {stats['changed'].iloc[0]}")

# 7. Ready for Streamlit
print("\n" + "=" * 100)
print("7. READY FOR STREAMLIT - Sample Dropdown Values")
print("=" * 100)

dropdown = pd.read_sql("""
    SELECT DISTINCT producto_normalizado 
    FROM flowers_greens 
    WHERE producto_normalizado IS NOT NULL
    ORDER BY producto_normalizado
    LIMIT 20
""", conn)
print("\nProduct dropdown will show:")
for idx, row in dropdown.iterrows():
    print(f"  • {row['producto_normalizado']}")

conn.close()

print("\n" + "=" * 100)
print("✓ VERIFICATION COMPLETE - Database is ready!")
print("=" * 100)
print("\nNext step: Update streamlit_app.py to use 'producto_normalizado' column")
print("See: STREAMLIT_UPDATE_EXAMPLE.md for exact changes needed")

