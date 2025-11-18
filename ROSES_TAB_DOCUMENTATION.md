# 🌹 Roses Analysis Tab - Documentation

## Overview

A dedicated analysis tab in the Streamlit dashboard providing comprehensive insights into rose imports in Panama (2020-2025).

**Access:** http://localhost:8501 → "🌹 Roses Analysis" tab

---

## Features

### 📊 Overview Metrics (Top Section)

**Key Performance Indicators:**
- Total Shipments
- Total Volume (units)
- Total Value (USD)
- Number of Importers
- Number of Countries
- Average Price per Unit
- Min/Max Price per Unit

**Example Data:**
- 4,317 shipments
- 52.6M roses
- $2.46M total value
- 62 importers
- Multiple countries of origin

---

### 📈 Monthly Trends

**Three Interactive Charts:**

1. **Monthly Import Volume (Line Chart)**
   - X-axis: Month (YYYY-MM)
   - Y-axis: Volume in units
   - Color: Red (#C62828)
   - Shows seasonal patterns and trends

2. **Monthly Weighted Average Price (Line Chart)**
   - X-axis: Month (YYYY-MM)
   - Y-axis: Price in USD
   - Color: Blue (#1565C0)
   - Weighted by quantity: `SUM(price * quantity) / SUM(quantity)`

3. **Volume vs Price Combined (Dual-Axis Chart)**
   - Left Y-axis: Volume (bar chart, red)
   - Right Y-axis: Price (line chart, blue)
   - Shows correlation between volume and pricing

**Insights Available:**
- Identify peak import months
- Detect seasonal price fluctuations
- Understand volume-price relationships
- Track market trends over time

---

### 🏢 Top Importers

**Interactive Bar Chart:**
- Top 10 importers by volume
- Horizontal bars
- Color-coded by total value (red gradient)
- Sorted by volume (descending)

**Detailed Table (Top 20):**

| Column | Description |
|--------|-------------|
| importer | Company name |
| shipments | Number of import shipments |
| volume | Total units imported |
| total_value | Total USD value |
| avg_price | Average price per unit |
| first_import | Date of first import |
| last_import | Date of most recent import |

**Key Players:**
1. CERRO PUNTA S.A. - ~7.2M units
2. DISTRIBUIDORA EL VALLE F, S.A - ~7.2M units
3. INMOBILIARIA DON ANTONIO S,A. - ~6.8M units
4. C.I. GRUPO LA MARQUETA, S.A. - ~6.1M units
5. EXPOFLORES, SA - ~5.6M units

---

### 💰 Price Analysis

**Two Visualizations:**

1. **Price Distribution (Histogram)**
   - Shows frequency of different price points
   - 50 bins for detailed distribution
   - Filters out outliers (prices > $1)
   - Identifies most common price ranges

2. **Price Range (Box Plot)**
   - Shows quartiles and outliers
   - Median price clearly visible
   - Identifies price spread
   - Highlights unusual pricing

**Data Filtering:**
- Only includes valid prices (> 0, < $1)
- Limited to 5,000 most recent records for performance
- Excludes null or zero prices

**Typical Price Range:**
- Minimum: ~$0.01
- Average: ~$0.07
- Maximum: ~$0.20 (excluding outliers)

---

### 🌍 Countries of Origin

**Two Visualizations:**

1. **Pie Chart (Top 10 Countries)**
   - Shows volume distribution by country
   - Interactive - hover for details
   - Color-coded segments

2. **Horizontal Bar Chart (Top 10 Countries)**
   - Sorted by volume
   - Easy comparison between countries
   - Shows exact volumes

**Detailed Table (Top 15):**

| Column | Description |
|--------|-------------|
| country | Country name |
| shipments | Number of shipments |
| volume | Total units |
| total_value | Total USD value |
| avg_price | Average price per unit |

**Insights:**
- Identify primary supply sources
- Compare pricing by country
- Understand supply chain diversity
- Track country-specific trends

---

### 💡 Key Insights Section

**Automatically Calculated Metrics:**

1. **Market Size**
   - Total volume and value summary
   - Quick overview of market scale

2. **Average Price**
   - Overall weighted average
   - Benchmark for pricing analysis

3. **Top Importer**
   - Name and market share percentage
   - Market concentration indicator

4. **Top Origin Country**
   - Primary source country
   - Supply concentration metric

5. **Market Concentration**
   - Top 5 importers' combined market share
   - Indicates market competitiveness

6. **Active Period**
   - Date range of available data
   - Data coverage information

**Example Output:**
```
- Market Size: 52,628,350 roses imported worth $2,455,920.00
- Average Price: $0.0700 per unit
- Top Importer: DISTRIBUIDORA EL VALLE F, S.A (13.6% market share)
- Top Origin: COLOMBIA (85.2% of volume)
- Market Concentration: Top 5 importers control 62.3% of market
- Active Period: 2020-01-15 to 2025-09-28
```

---

## Technical Details

### Data Source
- **Database:** `data/imports/merged/merged_data.db`
- **Table:** `flowers_greens`
- **Filter:** `tipo_producto = 'Rosas'`

### SQL Queries

**Overview Query:**
```sql
SELECT 
    COUNT(*) as total_shipments,
    SUM(CANTIDAD) as total_volume,
    SUM(TOTAL_A_PAGAR) as total_value,
    COUNT(DISTINCT IMPORTADOR_EXPORTADOR) as num_importers,
    COUNT(DISTINCT PAIS_DE_PROCEDENCIA_DESTINO) as num_countries,
    MIN/MAX/AVG(PRECIO_UNIDAD) as price_stats
FROM flowers_greens
WHERE tipo_producto = 'Rosas'
```

**Monthly Trends:**
```sql
SELECT 
    strftime('%Y-%m', FECHA_IMPORTACION_EXPORTACION) as month,
    SUM(CANTIDAD) as volume,
    SUM(PRECIO_UNIDAD * CANTIDAD) / SUM(CANTIDAD) as weighted_avg_price
FROM flowers_greens
WHERE tipo_producto = 'Rosas'
GROUP BY month
```

### Performance Optimizations
- Indexed on `tipo_producto` column
- Limited price analysis to 5,000 records
- Efficient aggregation queries
- Cached database connection

---

## Use Cases

### For Importers
1. **Competitive Analysis** - Compare your volumes with top players
2. **Pricing Strategy** - Understand market price ranges
3. **Sourcing Decisions** - Identify primary supply countries
4. **Market Entry** - Assess market size and concentration

### For Market Analysts
1. **Trend Analysis** - Track seasonal patterns
2. **Price Forecasting** - Analyze historical price movements
3. **Market Structure** - Understand concentration and competition
4. **Supply Chain** - Map country-importer relationships

### For Business Development
1. **Partnership Opportunities** - Identify major importers
2. **Market Sizing** - Quantify total addressable market
3. **Competitive Landscape** - Map key players
4. **Entry Barriers** - Assess market concentration

---

## Insights & Observations

### Market Characteristics
- **High Volume Product:** 52.6M units over 5 years
- **Moderate Concentration:** Top 5 control ~60-65% of market
- **Competitive Pricing:** Average $0.07/unit
- **Stable Market:** 62 active importers indicate healthy competition

### Seasonal Patterns
- Check monthly charts for peak seasons
- Valentine's Day (February) likely shows spikes
- Mother's Day (May) another potential peak
- Year-end holidays may show increased volume

### Price Dynamics
- Relatively stable pricing around $0.07
- Some variation based on quality/variety
- Country of origin may affect pricing
- Volume discounts likely for large importers

---

## Future Enhancements

Potential additions (not yet implemented):
- Year-over-year growth comparison
- Seasonal decomposition analysis
- Price elasticity calculations
- Importer market share trends over time
- Country-specific price comparisons
- Quality/variety breakdown (if data available)

---

## Related Resources

- **Main Dashboard:** Other tabs for cross-product analysis
- **Top 10 Flowers Report:** `TOP_10_FLOWERS_REPORT.md`
- **Project Documentation:** `PROJECT_SUMMARY.md`
- **Database Schema:** `augment_scripts/database_schema.txt`

---

**Last Updated:** 2025-11-18  
**Data Coverage:** 2020-2025  
**Total Rose Records:** 4,317 shipments

