# 🌱 Agricultural Imports Dashboard

Interactive dashboard for analyzing agricultural imports (flowers, vegetables, fruits, seeds, and plants) in Panama.

## Quick Start

```bash
streamlit run streamlit_app.py
```

The dashboard will open at: http://localhost:8501

## Features

### 📈 Historical Trends Tab
Analyze import volume and prices over time.

**Charts:**
- Monthly import volume (line chart)
- Weighted average price per month (line chart)
- Total import value per month (bar chart)

**Metrics:**
- Total volume
- Average monthly volume
- Total value (USD)
- Total shipments

**Filter:** Select specific product type from dropdown (Rosas, Orquídeas, Claveles, etc.)

---

### 🏢 Importer Analysis Tab
Identify top importers and market concentration.

**Charts:**
- Top 20 importers by volume (horizontal bar chart)

**Table:**
- Detailed importer statistics (shipments, volume, value)

**Metrics:**
- Total number of importers
- Top importer volume
- Top importer value

**Filter:** Select specific product type from dropdown

---

### 📦 Product Comparison Tab
Compare different agricultural products.

**Charts:**
- Top 15 most imported products (horizontal bar chart)
- Bottom 15 least imported products (horizontal bar chart)

**Table:**
- All products with shipments, volume, value, and average price
- Color-coded by category (Flores, Vegetales, Frutas, etc.)

**No filter** - Shows all products for comparison

---

## Data Source

**Database:** `data/imports/merged/merged_data.db`
**Table:** `flowers_greens`

**Data Coverage:**
- 160,356 import records
- Date range: 2020-01-02 to 2025-09-30
- 367 unique products
- 1,097 unique importers
- Total value: $80.2M

**Categories:**
- Flores y Plantas (Flowers & Plants)
- Vegetales (Vegetables)
- Frutas y Nueces (Fruits & Nuts)
- Café, Té, Especias (Coffee, Tea, Spices)
- Cereales (Cereals)
- Semillas y Plantas Agrícolas (Seeds & Agricultural Plants)

---

## Product Types Available

**Flowers:**
- Rosas (Roses)
- Claveles (Carnations)
- Orquídeas (Orchids)
- Crisantemos (Chrysanthemums)
- Azucenas (Lilies)
- Gerberas
- Gladiolas
- Anturios (Anthuriums)
- Heliconias
- Otras Flores (Other Flowers)
- Follaje (Foliage)

**Vegetables, Fruits, and More:**
- 350+ additional products from official tariff catalogue

---

## Technical Details

**Weighted Average Price Calculation:**
```sql
SUM(PRECIO_UNIDAD * CANTIDAD) / SUM(CANTIDAD)
```

This ensures that larger shipments have proportionally more weight in the average price calculation.

**Dependencies:**
- streamlit
- pandas
- plotly
- sqlite3 (built-in)

**Install dependencies:**
```bash
pip install -r requirements.txt
```

---

## Usage Examples

### Filter by Product
1. Open the dashboard
2. Use the sidebar dropdown to select a product (e.g., "Rosas")
3. All three tabs will update to show data for that product only

### Analyze Trends
1. Go to "Historical Trends" tab
2. Select a product from dropdown
3. View monthly volume and price trends
4. Identify seasonal patterns

### Find Top Importers
1. Go to "Importer Analysis" tab
2. Select a product (or "All Products")
3. View top 20 importers by volume
4. Scroll down for detailed table

### Compare Products
1. Go to "Product Comparison" tab
2. View most and least imported products
3. Scroll down to see full sortable table
4. Click column headers to sort

---

## Notes

- Dashboard queries data directly from SQLite - no caching of results
- Fails gracefully if no data available for selected filter
- All monetary values in USD
- Dates in YYYY-MM-DD format
- Volume units vary by product (see UNIDAD column in database)

---

## Troubleshooting

**Dashboard won't start:**
```bash
# Try with python -m
python -m streamlit run streamlit_app.py
```

**No data showing:**
- Check that `data/imports/merged/merged_data.db` exists
- Verify `flowers_greens` table exists in database
- Run `augment_scripts/create_flowers_greens_table.py` to recreate table

**Slow performance:**
- Database has indexes on key columns
- Queries are optimized for speed
- If still slow, check database file size and available RAM

---

## Future Enhancements

Potential additions (not implemented):
- Country of origin analysis
- Seasonality heatmaps
- Price prediction models
- Export to Excel functionality
- Custom date range filters
- Multi-product comparison
- Year-over-year growth metrics

---

## Support

For issues or questions, refer to:
- `PROJECT_SUMMARY.md` - Complete project documentation
- `augment_scripts/` - Data processing scripts
- Database schema in `augment_scripts/database_schema.txt`

