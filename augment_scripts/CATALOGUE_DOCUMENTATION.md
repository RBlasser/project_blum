# TARIFF CATALOGUE DOCUMENTATION

## Overview

A complete tariff catalogue has been extracted from `arancel_2025.pdf` and integrated into the database for easy JOINs with import data.

## Database Structure

### Table: `catalogo_arancel`

Located in: `data/imports/merged/merged_data.db`

**Columns:**
- `COD_INCISO` (INTEGER) - Full 11-digit tariff code (PRIMARY KEY)
- `COD_CAPITULO` (INTEGER) - Chapter code (first 2 digits)
- `COD_PARTIDA` (INTEGER) - Heading code (first 4 digits)
- `COD_SUBPARTIDA` (INTEGER) - Subheading code (first 6 digits)
- `DESCRIPCIÓN` (TEXT) - Official tariff description
- `DAI` (TEXT) - Import duty rate
- `ITBMS` (REAL) - Tax percentage
- `ISC` (REAL) - Selective consumption tax
- `ICCDP` (REAL) - Other tax
- `CAPITULO_NOMBRE` (TEXT) - Chapter name/description

**Indexes:**
- `idx_cat_inciso` on COD_INCISO
- `idx_cat_capitulo` on COD_CAPITULO
- `idx_cat_partida` on COD_PARTIDA
- `idx_cat_subpartida` on COD_SUBPARTIDA

## Statistics

- **Total tariff codes:** 9,040
- **Unique chapters:** 97
- **Unique partidas:** 1,156
- **Unique subpartidas:** 5,262
- **Match rate with imports:** ~78%

## JOIN Syntax

### Basic JOIN

```sql
SELECT 
    i.*,
    c.DESCRIPCIÓN as descripcion_oficial,
    c.CAPITULO_NOMBRE,
    c.DAI as tarifa_oficial
FROM merged_imports i
LEFT JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
```

### Filter by Chapter (e.g., Flowers - Chapter 6)

```sql
SELECT 
    i.FECHA_IMPORTACION_EXPORTACION,
    i.IMPORTADOR_EXPORTADOR,
    i.COD_INCISO,
    c.DESCRIPCIÓN as descripcion_oficial,
    i.CANTIDAD,
    i.PRECIO_UNIDAD,
    i.TOTAL_A_PAGAR,
    c.DAI as tarifa_oficial
FROM merged_imports i
INNER JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
WHERE c.COD_CAPITULO = 6
```

### Aggregate by Chapter

```sql
SELECT 
    c.COD_CAPITULO,
    c.CAPITULO_NOMBRE,
    COUNT(*) as import_records,
    SUM(i.TOTAL_A_PAGAR) as total_value
FROM merged_imports i
INNER JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
GROUP BY c.COD_CAPITULO, c.CAPITULO_NOMBRE
ORDER BY total_value DESC
```

## Chapter 6: Flowers & Plants

### Official Tariff Codes for Flowers

**Fresh Cut Flowers (Partida 0603):**
- `60311000000` - Rosas (Roses) - 15% DAI
- `60312000000` - Claveles (Carnations) - 15% DAI
- `60313000000` - Orquídeas (Orchids) - 15% DAI
- `60314000000` - Crisantemos (Chrysanthemums) - 15% DAI
- `60315000000` - Azucenas/Lilium (Lilies) - 15% DAI
- `60319100000` - Ginger - 15% DAI
- `60319200000` - Ave del paraíso (Bird of Paradise) - 15% DAI
- `60319300000` - Calas (Calla lilies) - 15% DAI
- `60319500000` - Gypsophila - 15% DAI
- `60319600000` - Gerberas - 15% DAI
- `60319700000` - Estaticias (Statice) - 15% DAI
- `60319800000` - Astromelias (Alstroemeria) - 15% DAI
- `60319910000` - Agapantos (Agapanthus) - 15% DAI
- `60319920000` - Gladiolas (Gladiolus) - 15% DAI
- `60319930000` - Anturios (Anthuriums) - 15% DAI
- `60319940000` - Heliconias - 15% DAI
- `60319990000` - Los demás (Others) - 15% DAI

**Live Plants (Partida 0601-0602):**
- `60110000000` - Bulbs, tubers (dormant)
- `60120000000` - Bulbs, tubers (growing/flowering)
- `60210000000` - Cuttings and grafts
- `60240000000` - Rose plants

**Foliage (Partida 0604):**
- `60420100000` - Christmas trees
- `60420900010` - Arrangements
- `60420900090` - Other fresh foliage
- `60490100000` - Mosses and lichens
- `60490200000` - Arrangements (dried)
- `60490900000` - Other (dried, preserved)

## Exported Files

1. **catalogo_arancel.csv** - Complete catalogue (9,040 codes)
2. **chapter_06_flowers_catalogue.csv** - Chapter 6 only with import statistics
3. **chapters_summary.csv** - Summary by chapter with import volumes

## Code Format Notes

- **PDF Format:** `0603.11.00.00.00` (with dots)
- **Database Format:** `60311000000` (integer, no leading zeros for chapters < 10)
- **Import Data:** May have 9, 10, or 11 digits depending on specificity

## Usage Examples

### Find all agricultural products (Chapters 6-14)

```sql
SELECT DISTINCT c.COD_CAPITULO, c.CAPITULO_NOMBRE
FROM catalogo_arancel c
WHERE c.COD_CAPITULO BETWEEN 6 AND 14
ORDER BY c.COD_CAPITULO
```

### Analyze flower imports by type

```sql
SELECT 
    c.DESCRIPCIÓN,
    COUNT(*) as records,
    SUM(i.CANTIDAD) as total_quantity,
    SUM(i.TOTAL_A_PAGAR) as total_value
FROM merged_imports i
INNER JOIN catalogo_arancel c ON i.COD_INCISO = c.COD_INCISO
WHERE c.COD_PARTIDA = 603  -- Fresh cut flowers
GROUP BY c.DESCRIPCIÓN
ORDER BY total_value DESC
```

## Scripts

- `extract_arancel_catalogue.py` - Extracts catalogue from PDF
- `test_catalogue_joins.py` - Tests JOIN operations
- `final_catalogue_summary.py` - Generates summary reports
- `check_chapter_6.py` - Analyzes Chapter 6 specifically

## Notes

- The catalogue is automatically indexed for fast JOINs
- Match rate is ~78% because some import codes may be outdated or use different formats
- All fresh flowers have 15% import duty (DAI)
- Chapter names may include extra text from PDF extraction - use COD_CAPITULO for filtering

