# Project Blum - Agricultural Imports Analysis

Comprehensive analysis system for Panama agricultural imports (2020-2025) with interactive Streamlit dashboard.

## 🌱 Overview

This project analyzes 9.5 million import records from Panama customs data, focusing on agricultural products including flowers, vegetables, fruits, seeds, and plants. It includes tariff catalogue integration, price validation, and interactive visualizations.

## 📊 Key Features

- **Database:** 9.5M import records merged from 12 Excel files (2020-2025)
- **Tariff Catalogue:** 14,433 official codes extracted from PDF (81.64% match rate)
- **Agricultural Focus:** 160K records for flowers, vegetables, fruits, seeds
- **Interactive Dashboard:** Streamlit app with 4 analysis tabs
- **Price Validation:** Rose import prices validated against current wholesale market
- **Comprehensive Reports:** Top 10 flowers, importers, market analysis

## 🚀 Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Run the Dashboard
```bash
streamlit run streamlit_app.py
```

Access at: http://localhost:8501

## 📁 Project Structure

```
ProjectBlum/
├── streamlit_app.py              # Main dashboard application
├── requirements.txt              # Python dependencies
├── data/
│   ├── docs/
│   │   └── arancel_2025.pdf     # Official tariff PDF (not in repo)
│   └── imports/
│       ├── *.xlsx               # Source Excel files (not in repo - too large)
│       └── merged/
│           ├── merged_data.db   # SQLite database (not in repo - 1GB+)
│           └── *.csv            # Exported analysis results
├── augment_scripts/             # Data processing scripts
│   ├── merge_xlsx_to_sqlite.py
│   ├── extract_arancel_improved.py
│   ├── create_flowers_greens_table.py
│   └── [other analysis scripts]
└── [documentation files]
```

## 📚 Documentation

- **PROJECT_SUMMARY.md** - Complete project overview
- **TOP_10_FLOWERS_REPORT.md** - Top 10 flowers analysis with importers
- **ROSE_PRICE_VALIDATION.md** - Price validation against market data
- **STREAMLIT_README.md** - Dashboard user guide
- **ROSES_TAB_DOCUMENTATION.md** - Roses analysis tab documentation
- **DAOFLOWERS_PRICE_ANALYSIS.md** - Current wholesale market pricing

## 🗄️ Database Schema

### Tables

1. **merged_imports** (9,509,593 rows, 26 columns)
   - All import records from 2020-2025
   - Includes: dates, importers, products, quantities, prices, tariffs

2. **catalogo_arancel** (14,433 rows)
   - Official tariff catalogue from PDF
   - Includes: codes, descriptions, tax rates

3. **flowers_greens** (160,356 rows)
   - Agricultural products only
   - Includes: official descriptions, categories, product types

## 📈 Dashboard Features

### Tab 1: Historical Trends
- Monthly import volume charts
- Weighted average price trends
- Total value analysis
- Filter by product type

### Tab 2: Importer Analysis
- Top 20 importers by volume
- Market share analysis
- Detailed importer statistics

### Tab 3: Product Comparison
- Top 15 most imported products
- Bottom 15 least imported products
- Full product comparison table

### Tab 4: Roses Deep-Dive
- Complete rose import analysis
- Monthly trends (volume & price)
- Top importers with market share
- Price distribution analysis
- Countries of origin
- Key market insights

## 📊 Key Statistics

**Overall Database:**
- Total records: 9,509,593
- Date range: 2020-01-02 to 2025-09-30
- Unique products: 9,838 tariff codes

**Agricultural Products:**
- Records: 160,356
- Categories: 6 (flowers, vegetables, fruits, coffee/tea, cereals, seeds)
- Unique products: 367
- Unique importers: 1,097
- Total value: $80.2M

**Top Flower (Roses):**
- Shipments: 4,317
- Volume: 52.6M stems
- Value: $2.46M
- Importers: 62
- Average price: $0.0684/stem (2020-2025 average)

## 🔧 Data Processing Scripts

Located in `augment_scripts/`:

- `merge_xlsx_to_sqlite.py` - Merge Excel files into SQLite
- `extract_arancel_improved.py` - Extract tariff catalogue from PDF
- `create_flowers_greens_table.py` - Create agricultural products table
- `top_10_flowers_analysis.py` - Analyze top flowers and importers
- `add_precio_unidad.py` - Calculate price per unit
- `reorder_columns.py` - Standardize column order

## 💡 Key Insights

1. **Roses dominate** flower imports (52.6M units, $2.46M value)
2. **Market concentration:** Top 5 importers control 60-70% of volume
3. **CERRO PUNTA S.A.** is the largest importer across multiple categories
4. **Price inflation:** Rose prices increased 2-3x from 2020 to 2025
5. **Current wholesale prices:** $0.16-$0.60/stem (vs $0.0684 historical avg)

## 🛠️ Tech Stack

- **Python 3.x**
- **SQLite** - Database
- **Pandas** - Data processing
- **Streamlit** - Interactive dashboard
- **Plotly** - Visualizations
- **PyPDF2** - PDF extraction

## ⚠️ Note on Data Files

Due to GitHub file size limitations (100MB), the following files are **not included** in this repository:

- `data/imports/merged/merged_data.db` (~1GB)
- `data/imports/*.xlsx` (12 Excel files, ~500MB total)
- `data/docs/arancel_2025.pdf` (optional, 3.86MB)

**To recreate the database:**
1. Place Excel files in `data/imports/`
2. Run: `python augment_scripts/merge_xlsx_to_sqlite.py`
3. Run: `python augment_scripts/add_precio_unidad.py`
4. Run: `python augment_scripts/extract_arancel_improved.py`
5. Run: `python augment_scripts/create_flowers_greens_table.py`

## 📝 License

This project is for analysis and educational purposes.

## 👤 Author

Rod Blasser (RBlasser)

## 📅 Last Updated

2025-11-18

