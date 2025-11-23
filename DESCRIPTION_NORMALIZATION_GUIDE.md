# Product Description Normalization Guide

## 🎯 Problem

The `DESCRIPCIÓN` column in `catalogo_arancel` contains many generic terms that make filtering confusing:

- **"Los demás"** (The others) - appears 500+ times
- **"Otros"** / **"Otras"** (Others) - very generic
- **"Las demás"** - feminine version
- Makes it impossible to distinguish products in Streamlit filters

### Example Problem:
```sql
SELECT DESCRIPCIÓN, COUNT(*) 
FROM catalogo_arancel 
WHERE DESCRIPCIÓN LIKE '%demás%'
GROUP BY DESCRIPCIÓN;

-- Results:
-- "Los demás" - 234 products
-- "Las demás" - 156 products
-- "Los demás flores" - 45 products
```

---

## ✅ Solution: Add `producto_normalizado` Column

Create a new column that provides **context-aware, specific names** by combining:
1. Hierarchical tariff structure (Chapter → Partida → Subpartida)
2. Original description
3. Business logic for common products

---

## 🔧 Implementation

### Step 1: Run the Normalization Script

```bash
python augment_scripts/normalize_descriptions.py
```

This will:
- Add `producto_normalizado` column to `catalogo_arancel`
- Add `producto_normalizado` column to `flowers_greens`
- Apply normalization rules
- Show before/after comparison

### Step 2: Normalization Rules

The script applies these rules in order:

#### **Rule 1: Specific Flower Types (Exact Matches)**
```sql
WHEN COD_INCISO = 60311000000 THEN 'Rosas'
WHEN COD_INCISO = 60312000000 THEN 'Claveles'
WHEN COD_INCISO = 60313000000 THEN 'Orquídeas'
-- etc.
```

#### **Rule 2: Generic Flowers (Context-Based)**
```sql
WHEN COD_PARTIDA = 603 AND DESCRIPCIÓN LIKE '%demás%' 
    THEN 'Flores Frescas - Otras Variedades'
```

#### **Rule 3: Live Plants**
```sql
WHEN COD_PARTIDA BETWEEN 601 AND 602 AND DESCRIPCIÓN LIKE '%demás%'
    THEN 'Plantas Vivas - Otras'
```

#### **Rule 4: Vegetables (Chapter 7)**
```sql
WHEN COD_CAPITULO = 7 AND DESCRIPCIÓN LIKE '%demás%'
    THEN 'Vegetales - ' || [Partida Name]
```

#### **Rule 5: Fruits (Chapter 8)**
```sql
WHEN COD_CAPITULO = 8 AND DESCRIPCIÓN LIKE '%demás%'
    THEN 'Frutas - ' || [Partida Name]
```

#### **Rule 6: Text Cleanup**
```sql
WHEN DESCRIPCIÓN LIKE 'Los demás%' 
    THEN REPLACE(DESCRIPCIÓN, 'Los demás', 'Otros')
```

---

## 📊 Before & After Examples

| COD_INCISO | Original (DESCRIPCIÓN) | Normalized (producto_normalizado) |
|------------|------------------------|-----------------------------------|
| 60311000000 | Rosas | Rosas |
| 60319990000 | Los demás | Flores Frescas - Otras Variedades |
| 60319920000 | Gladiolas | Gladiolas |
| 60110000000 | Los demás | Plantas Vivas - Otras |
| 70310000000 | Los demás | Vegetales - Cebollas y chalotes |
| 80290000000 | Los demás | Frutas - Albaricoques, cerezas |

---

## 🎨 Update Streamlit App

### Option A: Simple Replacement (Recommended)

Replace `DESCRIPCIÓN` with `producto_normalizado` in all queries:

```python
# OLD
query = """
SELECT DISTINCT DESCRIPCIÓN 
FROM flowers_greens 
ORDER BY DESCRIPCIÓN
"""

# NEW
query = """
SELECT DISTINCT producto_normalizado 
FROM flowers_greens 
ORDER BY producto_normalizado
"""
```

### Option B: Show Both Columns

Let users see both original and normalized:

```python
query = """
SELECT 
    producto_normalizado as 'Producto',
    DESCRIPCIÓN as 'Descripción Original',
    COUNT(*) as 'Registros'
FROM flowers_greens 
GROUP BY producto_normalizado, DESCRIPCIÓN
ORDER BY COUNT(*) DESC
"""
```

### Option C: Use as Filter, Show Original

```python
# Filter dropdown uses normalized names
productos = pd.read_sql("""
    SELECT DISTINCT producto_normalizado 
    FROM flowers_greens 
    ORDER BY producto_normalizado
""", conn)

selected = st.selectbox("Producto:", productos)

# Query uses normalized for filtering
df = pd.read_sql(f"""
    SELECT fecha, importador, DESCRIPCIÓN, cantidad, valor
    FROM flowers_greens
    WHERE producto_normalizado = '{selected}'
""", conn)
```

---

## 🔍 Advanced: Custom Normalization

If you need more specific rules, edit `augment_scripts/normalize_descriptions.py`:

```python
# Add custom rules
WHEN COD_INCISO = 12345678900 THEN 'My Custom Product Name'
WHEN DESCRIPCIÓN LIKE '%special keyword%' THEN 'Special Category'
```

---

## 📈 Benefits

### Before Normalization:
- ❌ "Los demás" appears 234 times
- ❌ Impossible to filter meaningfully
- ❌ Confusing for users
- ❌ Poor data analysis

### After Normalization:
- ✅ "Flores Frescas - Otras Variedades" (specific context)
- ✅ "Vegetales - Cebollas" (category + product)
- ✅ Clear, filterable names
- ✅ Better user experience
- ✅ Accurate analysis

---

## 🚀 Quick Start

1. **Run normalization:**
   ```bash
   python augment_scripts/normalize_descriptions.py
   ```

2. **Update Streamlit queries:**
   - Replace `DESCRIPCIÓN` with `producto_normalizado`
   - Test filters

3. **Verify results:**
   ```sql
   SELECT producto_normalizado, COUNT(*) 
   FROM flowers_greens 
   GROUP BY producto_normalizado 
   ORDER BY COUNT(*) DESC;
   ```

---

## 📝 SQL Examples

### Get all normalized flower names:
```sql
SELECT DISTINCT producto_normalizado
FROM flowers_greens
WHERE categoria = 'Flores'
ORDER BY producto_normalizado;
```

### Compare original vs normalized:
```sql
SELECT 
    DESCRIPCIÓN,
    producto_normalizado,
    COUNT(*) as records
FROM catalogo_arancel
WHERE DESCRIPCIÓN LIKE '%demás%'
GROUP BY DESCRIPCIÓN, producto_normalizado
ORDER BY records DESC;
```

### Find products still needing normalization:
```sql
SELECT *
FROM catalogo_arancel
WHERE producto_normalizado LIKE '%demás%'
   OR producto_normalizado LIKE '%otros%';
```

---

## ✅ Checklist

- [ ] Run `normalize_descriptions.py`
- [ ] Verify new column exists: `SELECT producto_normalizado FROM catalogo_arancel LIMIT 10`
- [ ] Update Streamlit queries to use `producto_normalizado`
- [ ] Test filters in dashboard
- [ ] Add custom rules if needed
- [ ] Document any manual overrides

---

**Result:** Clean, context-aware product names that make filtering intuitive! 🎉

