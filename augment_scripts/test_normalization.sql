-- Test Normalization Results
-- Run these queries after executing normalize_descriptions.py

-- ============================================================================
-- 1. CHECK IF COLUMN EXISTS
-- ============================================================================
PRAGMA table_info(catalogo_arancel);
-- Look for 'producto_normalizado' in the output

PRAGMA table_info(flowers_greens);
-- Look for 'producto_normalizado' in the output


-- ============================================================================
-- 2. BEFORE/AFTER COMPARISON - Generic Descriptions
-- ============================================================================

-- Count of "Los demás" BEFORE normalization
SELECT 
    'BEFORE (Original)' as status,
    COUNT(*) as count_los_demas
FROM catalogo_arancel
WHERE DESCRIPCIÓN LIKE '%demás%' OR DESCRIPCIÓN LIKE '%otros%';

-- Count of "Los demás" AFTER normalization
SELECT 
    'AFTER (Normalized)' as status,
    COUNT(*) as count_los_demas
FROM catalogo_arancel
WHERE producto_normalizado LIKE '%demás%' OR producto_normalizado LIKE '%otros%';


-- ============================================================================
-- 3. SIDE-BY-SIDE COMPARISON - Flowers (Chapter 6)
-- ============================================================================
SELECT 
    COD_INCISO,
    DESCRIPCIÓN as original,
    producto_normalizado as normalized,
    CASE 
        WHEN DESCRIPCIÓN = producto_normalizado THEN '✓ Same'
        ELSE '→ Changed'
    END as status
FROM catalogo_arancel
WHERE COD_CAPITULO = 6
ORDER BY COD_INCISO
LIMIT 50;


-- ============================================================================
-- 4. MOST COMMON NORMALIZED NAMES
-- ============================================================================
SELECT 
    producto_normalizado,
    COUNT(*) as product_count,
    GROUP_CONCAT(DISTINCT DESCRIPCIÓN) as original_descriptions
FROM catalogo_arancel
WHERE COD_CAPITULO IN (6, 7, 8)
GROUP BY producto_normalizado
ORDER BY product_count DESC
LIMIT 20;


-- ============================================================================
-- 5. VERIFY SPECIFIC FLOWER TYPES
-- ============================================================================
SELECT 
    COD_INCISO,
    DESCRIPCIÓN,
    producto_normalizado,
    tipo_producto
FROM flowers_greens
WHERE tipo_producto IN ('Rosas', 'Claveles', 'Orquídeas', 'Gerberas')
GROUP BY producto_normalizado
ORDER BY tipo_producto;


-- ============================================================================
-- 6. FIND PRODUCTS STILL NEEDING NORMALIZATION
-- ============================================================================
SELECT 
    COD_CAPITULO,
    COD_INCISO,
    DESCRIPCIÓN,
    producto_normalizado
FROM catalogo_arancel
WHERE (producto_normalizado LIKE '%demás%' 
   OR producto_normalizado LIKE '%otros%'
   OR producto_normalizado LIKE '%otras%')
  AND COD_CAPITULO IN (6, 7, 8, 9, 10, 12)
ORDER BY COD_CAPITULO, COD_INCISO;


-- ============================================================================
-- 7. UNIQUE PRODUCT NAMES FOR STREAMLIT DROPDOWN
-- ============================================================================
SELECT DISTINCT producto_normalizado 
FROM flowers_greens 
WHERE producto_normalizado IS NOT NULL
ORDER BY producto_normalizado;


-- ============================================================================
-- 8. VERIFY ROSES DATA
-- ============================================================================
SELECT 
    producto_normalizado,
    COUNT(*) as shipments,
    SUM(CANTIDAD) as total_volume,
    SUM(TOTAL_A_PAGAR) as total_value,
    ROUND(AVG(PRECIO_UNIDAD), 4) as avg_price
FROM flowers_greens
WHERE producto_normalizado = 'Rosas'
GROUP BY producto_normalizado;


-- ============================================================================
-- 9. CATEGORY BREAKDOWN WITH NORMALIZED NAMES
-- ============================================================================
SELECT 
    categoria_agricola,
    producto_normalizado,
    COUNT(*) as records,
    SUM(CANTIDAD) as volume
FROM flowers_greens
GROUP BY categoria_agricola, producto_normalizado
ORDER BY categoria_agricola, volume DESC;


-- ============================================================================
-- 10. QUALITY CHECK - NULL or EMPTY normalized names
-- ============================================================================
SELECT 
    COUNT(*) as total_records,
    SUM(CASE WHEN producto_normalizado IS NULL THEN 1 ELSE 0 END) as null_count,
    SUM(CASE WHEN producto_normalizado = '' THEN 1 ELSE 0 END) as empty_count,
    SUM(CASE WHEN producto_normalizado IS NOT NULL AND producto_normalizado != '' THEN 1 ELSE 0 END) as valid_count
FROM flowers_greens;


-- ============================================================================
-- 11. EXPORT FOR STREAMLIT TESTING
-- ============================================================================
-- Copy this result to test in Streamlit
SELECT DISTINCT 
    producto_normalizado as product_name,
    COUNT(*) OVER (PARTITION BY producto_normalizado) as record_count
FROM flowers_greens
WHERE producto_normalizado IS NOT NULL
ORDER BY record_count DESC, producto_normalizado;


-- ============================================================================
-- 12. COMPARE ORIGINAL vs NORMALIZED DISTRIBUTION
-- ============================================================================
SELECT 
    'Original (tipo_producto)' as source,
    COUNT(DISTINCT tipo_producto) as unique_products
FROM flowers_greens
WHERE tipo_producto IS NOT NULL

UNION ALL

SELECT 
    'Normalized (producto_normalizado)' as source,
    COUNT(DISTINCT producto_normalizado) as unique_products
FROM flowers_greens
WHERE producto_normalizado IS NOT NULL;

