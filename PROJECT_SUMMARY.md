# Agricultural Imports Analysis - Project Summary

## ✅ Completed Tasks

### 1. Improved Tariff Catalogue Extraction
**Match Rate: 81.64%** (improved from 78%)

- **Extracted:** 14,433 tariff codes from arancel_2025.pdf
- **Matched:** 8,032 out of 9,838 import codes
- **Method:** Multiple regex patterns to capture different PDF formats
- **Script:** `augment_scripts/extract_arancel_improved.py`

**Database Table:** `catalogo_arancel`
- COD_INCISO, COD_CAPITULO, COD_PARTIDA, COD_SUBPARTIDA
- DESCRIPCIÓN (official description)
- DAI, ITBMS, ISC, ICCDP (tax rates)
- CAPITULO_NOMBRE (chapter name)
- Fully indexed for fast JOINs

---

### 2. Created flowers_greens Table
**160,356 agricultural import records** (2020-2025)

**Chapters Included:**
- Chapter 6: Flores y Plantas (40,927 records)
- Chapter 7: Vegetales (41,156 records)
- Chapter 8: Frutas y Nueces (38,389 records)
- Chapter 9: Café, Té, Especias (22,939 records)
- Chapter 10: Cereales (6,893 records)
- Chapter 12: Semillas y Plantas Agrícolas (9,145 records)

**Table Structure:**
- All columns from merged_imports
- `descripcion_oficial` - Official tariff description
- `CAPITULO_NOMBRE` - Chapter name
- `tarifa_oficial` - Official tariff rate
- `categoria_agricola` - Agricultural category
- `tipo_producto` - Specific product type (for filtering)

**Top Products:**
1. Otras Flores (24,091 records)
2. Follaje (4,522 records)
3. Rosas (4,317 records)
4. Claveles (2,942 records)
5. Crisantemos (2,282 records)

**Script:** `augment_scripts/create_flowers_greens_table.py`

---

### 3. Streamlit Dashboard
**URL:** http://localhost:8501

**Features:**

#### 📈 Tab 1: Historical Trends
- Monthly import volume line chart
- Weighted average price per month line chart
- Total import value bar chart
- Key metrics: Total volume, avg monthly volume, total value, shipments
- **Filter:** Dropdown to select product type (Rosas, Orquídeas, etc.)

**Weighted Average Calculation:**
```sql
SUM(PRECIO_UNIDAD * CANTIDAD) / SUM(CANTIDAD)
```

#### 🏢 Tab 2: Importer Analysis
- Top 20 importers by volume (horizontal bar chart)
- Detailed importer table with shipments, volume, and value
- Key metrics: Total importers, top importer stats
- **Filter:** Dropdown to select product type

#### 📦 Tab 3: Product Comparison
- Top 15 most imported products (horizontal bar chart)
- Bottom 15 least imported products (horizontal bar chart)
- Full product comparison table
- Color-coded by agricultural category
- **No filter** - shows all products for comparison

**File:** `streamlit_app.py`

---

## 📁 Project Structure

```
ProjectBlum/
├── streamlit_app.py                    # Main dashboard
├── requirements.txt                    # Python dependencies
├── data/
│   ├── docs/
│   │   └── arancel_2025.pdf           # Official tariff PDF
│   └── imports/
│       ├── IMP_2020_1.xlsx ... IMP_2025_2.xlsx  # 12 source files
│       └── merged/
│           ├── merged_data.db          # Main database
│           ├── catalogo_arancel.csv    # Catalogue export
│           └── flowers_greens_sample.csv
└── augment_scripts/
    ├── extract_arancel_improved.py     # Improved catalogue extraction
    ├── create_flowers_greens_table.py  # Create agricultural table
    ├── merge_xlsx_to_sqlite.py         # Original merge script
    ├── add_precio_unidad.py            # Add price per unit
    ├── reorder_columns.py              # Reorder columns
    └── [other utility scripts]
```

---

## 🗄️ Database Schema

### Table: merged_imports (9,509,593 rows, 26 columns)
Main import data with all products

### Table: catalogo_arancel (14,433 rows)
Official tariff catalogue from PDF

### Table: flowers_greens (160,356 rows)
**Agricultural products only** - flowers, vegetables, fruits, seeds, plants

**Key Columns:**
- All original import columns
- `descripcion_oficial` - Official product description
- `categoria_agricola` - Category (Flores, Vegetales, Frutas, etc.)
- `tipo_producto` - Specific product (Rosas, Orquídeas, Claveles, etc.)
- `tarifa_oficial` - Official import tariff rate

---

## 🚀 How to Use

### Run the Dashboard:
```bash
streamlit run streamlit_app.py
```

### Query the Database:
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/imports/merged/merged_data.db')

# Get all rose imports
df = pd.read_sql("""
    SELECT * FROM flowers_greens
    WHERE tipo_producto = 'Rosas'
""", conn)

# Monthly analysis
df_monthly = pd.read_sql("""
    SELECT 
        strftime('%Y-%m', FECHA_IMPORTACION_EXPORTACION) as month,
        SUM(CANTIDAD) as volume,
        SUM(PRECIO_UNIDAD * CANTIDAD) / SUM(CANTIDAD) as avg_price
    FROM flowers_greens
    WHERE tipo_producto = 'Rosas'
    GROUP BY month
""", conn)
```

---

## 📊 Key Statistics

**Overall Database:**
- Total import records: 9,509,593
- Date range: 2020-2025
- Total value: $80.2M (agricultural products only)

**Agricultural Products:**
- Records: 160,356 (1.7% of total)
- Unique products: 367
- Unique importers: 1,097
- Categories: 6 main chapters

**Catalogue Match Rate:**
- 81.64% of import codes matched with official tariff
- 14,433 official tariff codes extracted
- 97 chapters covered

---

## 🎯 Next Steps

1. **Improve match rate further** - Extract remaining 18% of codes
2. **Add more product mappings** - Specific names for vegetables/fruits
3. **Add country analysis** - Top countries by product
4. **Add seasonality analysis** - Monthly patterns by product
5. **Export functionality** - Download filtered data from dashboard

---

## 📝 Notes

- Dashboard uses simple, direct queries - no fallback functions
- Fails gracefully if data is missing
- All prices are in USD
- Weighted averages account for quantity in price calculations
- Product dropdown populated from actual data in database

