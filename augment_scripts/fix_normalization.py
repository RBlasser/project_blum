import sqlite3
import pandas as pd

conn = sqlite3.connect('data/imports/merged/merged_data.db')

print("=" * 100)
print("FIXING NORMALIZATION IN flowers_greens")
print("=" * 100)

# More aggressive normalization - handle all "Los demás", "Las demás", "Otros" cases
update_query = """
UPDATE flowers_greens
SET producto_normalizado = CASE
    -- Specific flower types (keep these first for priority)
    WHEN tipo_producto LIKE '%Rosas%' OR tipo_producto LIKE '%ROSAS%' THEN 'Rosas'
    WHEN tipo_producto LIKE '%Claveles%' OR tipo_producto LIKE '%CLAVELES%' THEN 'Claveles'
    WHEN tipo_producto LIKE '%Orquídeas%' OR tipo_producto LIKE '%ORQUIDEAS%' THEN 'Orquídeas'
    WHEN tipo_producto LIKE '%Crisantemos%' OR tipo_producto LIKE '%CRISANTEMOS%' THEN 'Crisantemos'
    WHEN tipo_producto LIKE '%Gerberas%' OR tipo_producto LIKE '%GERBERAS%' OR tipo_producto LIKE '%Serberas%' THEN 'Gerberas'
    WHEN tipo_producto LIKE '%Gladiolas%' OR tipo_producto LIKE '%GLADIOLAS%' THEN 'Gladiolas'
    WHEN tipo_producto LIKE '%Heliconias%' OR tipo_producto LIKE '%HELICONIAS%' THEN 'Heliconias'
    WHEN tipo_producto LIKE '%Anturios%' OR tipo_producto LIKE '%ANTURIOS%' THEN 'Anturios'
    WHEN tipo_producto LIKE '%Astromerias%' OR tipo_producto LIKE '%ASTROMERIAS%' THEN 'Astromerias'
    WHEN tipo_producto LIKE '%Ginger%' THEN 'Ginger'
    WHEN tipo_producto LIKE '%Ave del paraíso%' THEN 'Ave del Paraíso'
    WHEN tipo_producto LIKE '%Calas%' THEN 'Calas'
    WHEN tipo_producto LIKE '%Sysofilia%' THEN 'Gypsophila'
    WHEN tipo_producto LIKE '%Estaticias%' THEN 'Estatice'
    WHEN tipo_producto LIKE '%Agapantos%' THEN 'Agapantos'
    WHEN tipo_producto LIKE '%Azucenas%' OR tipo_producto LIKE '%Lilium%' THEN 'Azucenas (Lilium)'
    
    -- Generic terms based on COD_CAPITULO (tariff chapter)
    -- Chapter 6 = Flowers and plants
    WHEN (tipo_producto LIKE '%demás%' OR tipo_producto LIKE '%otros%' OR tipo_producto LIKE '%otras%' OR tipo_producto LIKE '%Otros%')
         AND CAST(SUBSTR(COD_INCISO, 1, 2) AS INTEGER) = 6
         AND (CAST(SUBSTR(COD_INCISO, 3, 2) AS INTEGER) = 3 OR tipo_producto LIKE '%flores%' OR tipo_producto LIKE '%Flores%')
         THEN 'Flores Frescas - Otras Variedades'
    
    WHEN (tipo_producto LIKE '%demás%' OR tipo_producto LIKE '%otros%' OR tipo_producto LIKE '%otras%' OR tipo_producto LIKE '%Otros%')
         AND CAST(SUBSTR(COD_INCISO, 1, 2) AS INTEGER) = 6
         AND CAST(SUBSTR(COD_INCISO, 3, 2) AS INTEGER) = 4
         THEN 'Follaje y Ramas - Otros'
    
    WHEN (tipo_producto LIKE '%demás%' OR tipo_producto LIKE '%otros%' OR tipo_producto LIKE '%otras%' OR tipo_producto LIKE '%Otros%')
         AND CAST(SUBSTR(COD_INCISO, 1, 2) AS INTEGER) = 6
         THEN 'Plantas Vivas - Otras'
    
    -- Chapter 7 = Vegetables
    WHEN (tipo_producto LIKE '%demás%' OR tipo_producto LIKE '%otros%' OR tipo_producto LIKE '%otras%' OR tipo_producto LIKE '%Otros%')
         AND CAST(SUBSTR(COD_INCISO, 1, 2) AS INTEGER) = 7
         THEN 'Vegetales - Hortalizas, plantas, raíces  y'
    
    -- Chapter 8 = Fruits
    WHEN (tipo_producto LIKE '%demás%' OR tipo_producto LIKE '%otros%' OR tipo_producto LIKE '%otras%' OR tipo_producto LIKE '%Otros%')
         AND CAST(SUBSTR(COD_INCISO, 1, 2) AS INTEGER) = 8
         THEN 'Frutas - Las frutas y otros frutos refr'
    
    -- Chapter 9 = Coffee, tea, spices
    WHEN (tipo_producto LIKE '%demás%' OR tipo_producto LIKE '%otros%' OR tipo_producto LIKE '%otras%' OR tipo_producto LIKE '%Otros%')
         AND CAST(SUBSTR(COD_INCISO, 1, 2) AS INTEGER) = 9
         THEN 'Café, Té, Especias - Otros'
    
    -- Chapter 10 = Cereals
    WHEN (tipo_producto LIKE '%demás%' OR tipo_producto LIKE '%otros%' OR tipo_producto LIKE '%otras%' OR tipo_producto LIKE '%Otros%')
         AND CAST(SUBSTR(COD_INCISO, 1, 2) AS INTEGER) = 10
         THEN 'Cereales - Otros'
    
    -- Chapter 12 = Seeds, plants
    WHEN (tipo_producto LIKE '%demás%' OR tipo_producto LIKE '%otros%' OR tipo_producto LIKE '%otras%' OR tipo_producto LIKE '%Otros%')
         AND CAST(SUBSTR(COD_INCISO, 1, 2) AS INTEGER) = 12
         THEN 'Semillas y Plantas - Otros'
    
    -- Fallback for any remaining generic terms
    WHEN tipo_producto LIKE '%demás%' OR tipo_producto LIKE '%otros%' OR tipo_producto LIKE '%otras%' 
         THEN 'Productos Agrícolas - Otros'
    
    -- Clean up leading dashes for everything else
    WHEN tipo_producto LIKE '- - - - %' THEN TRIM(SUBSTR(tipo_producto, 9))
    WHEN tipo_producto LIKE '- - - %' THEN TRIM(SUBSTR(tipo_producto, 7))
    WHEN tipo_producto LIKE '- - %' THEN TRIM(SUBSTR(tipo_producto, 5))
    WHEN tipo_producto LIKE '- %' THEN TRIM(SUBSTR(tipo_producto, 3))
    
    -- Keep original if already specific
    ELSE TRIM(tipo_producto)
END
"""

print("\nApplying improved normalization...")
conn.execute(update_query)
conn.commit()
print("✓ Updated!")

# Check results
print("\n" + "=" * 100)
print("RESULTS")
print("=" * 100)

print("\n1. Generic terms remaining:")
df1 = pd.read_sql("""
    SELECT producto_normalizado, COUNT(*) as count
    FROM flowers_greens
    WHERE producto_normalizado LIKE '%demás%' 
       OR producto_normalizado LIKE '%otros%'
       OR producto_normalizado LIKE '%otras%'
    GROUP BY producto_normalizado
    ORDER BY count DESC
    LIMIT 10
""", conn)
print(df1.to_string(index=False))

print("\n2. Top normalized products:")
df2 = pd.read_sql("""
    SELECT producto_normalizado, COUNT(*) as count
    FROM flowers_greens
    GROUP BY producto_normalizado
    ORDER BY count DESC
    LIMIT 20
""", conn)
print(df2.to_string(index=False))

print("\n3. Unique product count:")
df3 = pd.read_sql("""
    SELECT COUNT(DISTINCT producto_normalizado) as unique_products
    FROM flowers_greens
""", conn)
print(f"Unique products: {df3['unique_products'].iloc[0]}")

conn.close()

print("\n" + "=" * 100)
print("✓ NORMALIZATION FIXED!")
print("=" * 100)
print("\nRestart Streamlit to see the changes:")
print("  streamlit run streamlit_app.py")

