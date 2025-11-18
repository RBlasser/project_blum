import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from pathlib import Path
from datetime import datetime

# Page config
st.set_page_config(page_title="Agricultural Imports Dashboard", page_icon="🌱", layout="wide")

# Database connection
@st.cache_resource
def get_connection():
    db_path = Path("data/imports/merged/merged_data.db")
    return sqlite3.connect(db_path, check_same_thread=False)

conn = get_connection()

# Load product types for dropdown
@st.cache_data
def get_product_types():
    query = """
    SELECT DISTINCT tipo_producto 
    FROM flowers_greens 
    WHERE tipo_producto IS NOT NULL
    ORDER BY tipo_producto
    """
    df = pd.read_sql(query, conn)
    return ['All Products'] + df['tipo_producto'].tolist()

# Sidebar
st.sidebar.title("🌱 Filters")
product_types = get_product_types()
selected_product = st.sidebar.selectbox("Product Type", product_types)

# Title
st.title("🌱 Agricultural Imports Dashboard")
st.markdown("Analysis of flowers, vegetables, fruits, leafy greens, seeds, and plants")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Historical Trends", "🏢 Importer Analysis", "📦 Product Comparison", "🌹 Roses Analysis"])

# TAB 1: Historical Trends
with tab1:
    st.header("📈 Historical Import Volume and Prices")
    
    # Query monthly data
    if selected_product == 'All Products':
        query = """
        SELECT 
            strftime('%Y-%m', FECHA_IMPORTACION_EXPORTACION) as month,
            SUM(CANTIDAD) as volume,
            SUM(PRECIO_UNIDAD * CANTIDAD) / NULLIF(SUM(CANTIDAD), 0) as weighted_avg_price,
            SUM(TOTAL_A_PAGAR) as total_value,
            COUNT(*) as num_shipments
        FROM flowers_greens
        WHERE FECHA_IMPORTACION_EXPORTACION IS NOT NULL
        GROUP BY month
        ORDER BY month
        """
        df_monthly = pd.read_sql(query, conn)
    else:
        query = """
        SELECT 
            strftime('%Y-%m', FECHA_IMPORTACION_EXPORTACION) as month,
            SUM(CANTIDAD) as volume,
            SUM(PRECIO_UNIDAD * CANTIDAD) / NULLIF(SUM(CANTIDAD), 0) as weighted_avg_price,
            SUM(TOTAL_A_PAGAR) as total_value,
            COUNT(*) as num_shipments
        FROM flowers_greens
        WHERE tipo_producto = ? AND FECHA_IMPORTACION_EXPORTACION IS NOT NULL
        GROUP BY month
        ORDER BY month
        """
        df_monthly = pd.read_sql(query, conn, params=[selected_product])
    
    if not df_monthly.empty:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Volume", f"{df_monthly['volume'].sum():,.0f}")
        col2.metric("Avg Monthly Volume", f"{df_monthly['volume'].mean():,.0f}")
        col3.metric("Total Value", f"${df_monthly['total_value'].sum():,.2f}")
        col4.metric("Total Shipments", f"{df_monthly['num_shipments'].sum():,}")
        
        # Volume chart
        st.subheader("Monthly Import Volume")
        fig1 = px.line(df_monthly, x='month', y='volume', 
                       title='Import Volume Over Time',
                       labels={'month': 'Month', 'volume': 'Volume'})
        fig1.update_traces(line_color='#2E7D32')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Price chart
        st.subheader("Weighted Average Price per Month")
        fig2 = px.line(df_monthly, x='month', y='weighted_avg_price',
                       title='Weighted Average Price Over Time',
                       labels={'month': 'Month', 'weighted_avg_price': 'Price (USD)'})
        fig2.update_traces(line_color='#1976D2')
        st.plotly_chart(fig2, use_container_width=True)
        
        # Value chart
        st.subheader("Total Import Value per Month")
        fig3 = px.bar(df_monthly, x='month', y='total_value',
                      title='Total Import Value Over Time',
                      labels={'month': 'Month', 'total_value': 'Value (USD)'})
        fig3.update_traces(marker_color='#F57C00')
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("No data available for selected product")

# TAB 2: Importer Analysis
with tab2:
    st.header("🏢 Importer Analysis")
    
    # Query importer data
    if selected_product == 'All Products':
        query = """
        SELECT 
            IMPORTADOR_EXPORTADOR as importer,
            COUNT(*) as shipments,
            SUM(CANTIDAD) as volume,
            SUM(TOTAL_A_PAGAR) as total_value
        FROM flowers_greens
        WHERE IMPORTADOR_EXPORTADOR IS NOT NULL
        GROUP BY IMPORTADOR_EXPORTADOR
        ORDER BY volume DESC
        LIMIT 30
        """
        df_importers = pd.read_sql(query, conn)
    else:
        query = """
        SELECT 
            IMPORTADOR_EXPORTADOR as importer,
            COUNT(*) as shipments,
            SUM(CANTIDAD) as volume,
            SUM(TOTAL_A_PAGAR) as total_value
        FROM flowers_greens
        WHERE tipo_producto = ? AND IMPORTADOR_EXPORTADOR IS NOT NULL
        GROUP BY IMPORTADOR_EXPORTADOR
        ORDER BY volume DESC
        LIMIT 30
        """
        df_importers = pd.read_sql(query, conn, params=[selected_product])
    
    if not df_importers.empty:
        # Metrics
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Importers", f"{len(df_importers):,}")
        col2.metric("Top Importer Volume", f"{df_importers['volume'].iloc[0]:,.0f}")
        col3.metric("Top Importer Value", f"${df_importers['total_value'].iloc[0]:,.2f}")
        
        # Top importers chart
        st.subheader("Top 20 Importers by Volume")
        fig = px.bar(df_importers.head(20), x='volume', y='importer', orientation='h',
                     title='Top 20 Importers',
                     labels={'volume': 'Volume', 'importer': 'Importer'})
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed table
        st.subheader("Importer Details")
        st.dataframe(df_importers, use_container_width=True)
    else:
        st.warning("No data available for selected product")

# TAB 3: Product Comparison  
with tab3:
    st.header("📦 Product Comparison")
    
    # Query product data
    query = """
    SELECT 
        tipo_producto,
        categoria_agricola,
        COUNT(*) as shipments,
        SUM(CANTIDAD) as volume,
        SUM(TOTAL_A_PAGAR) as total_value,
        AVG(PRECIO_UNIDAD) as avg_price
    FROM flowers_greens
    WHERE tipo_producto IS NOT NULL
    GROUP BY tipo_producto, categoria_agricola
    ORDER BY volume DESC
    """
    df_products = pd.read_sql(query, conn)
    
    if not df_products.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top 15 Most Imported Products")
            top_15 = df_products.head(15)
            fig = px.bar(top_15, x='volume', y='tipo_producto', orientation='h',
                        color='categoria_agricola',
                        labels={'volume': 'Volume', 'tipo_producto': 'Product'})
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Bottom 15 Least Imported Products")
            bottom_15 = df_products.tail(15)
            fig = px.bar(bottom_15, x='volume', y='tipo_producto', orientation='h',
                        color='categoria_agricola',
                        labels={'volume': 'Volume', 'tipo_producto': 'Product'})
            fig.update_layout(yaxis={'categoryorder':'total descending'}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Full table
        st.subheader("All Products")
        st.dataframe(df_products, use_container_width=True)
    else:
        st.warning("No data available")

# TAB 4: Roses Analysis
with tab4:
    st.header("🌹 Roses - Complete Analysis")

    # Overview metrics
    query_overview = """
    SELECT
        COUNT(*) as total_shipments,
        SUM(CANTIDAD) as total_volume,
        SUM(TOTAL_A_PAGAR) as total_value,
        COUNT(DISTINCT IMPORTADOR_EXPORTADOR) as num_importers,
        COUNT(DISTINCT PAIS_DE_PROCEDENCIA_DESTINO) as num_countries,
        MIN(FECHA_IMPORTACION_EXPORTACION) as first_import,
        MAX(FECHA_IMPORTACION_EXPORTACION) as last_import,
        MIN(PRECIO_UNIDAD) as min_price,
        MAX(PRECIO_UNIDAD) as max_price,
        AVG(PRECIO_UNIDAD) as avg_price
    FROM flowers_greens
    WHERE tipo_producto = 'Rosas'
    """
    df_overview = pd.read_sql(query_overview, conn)

    if not df_overview.empty and df_overview['total_shipments'].iloc[0] > 0:
        # Key metrics
        st.subheader("📊 Overview")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total Shipments", f"{df_overview['total_shipments'].iloc[0]:,}")
        col2.metric("Total Volume", f"{df_overview['total_volume'].iloc[0]:,.0f}")
        col3.metric("Total Value", f"${df_overview['total_value'].iloc[0]:,.2f}")
        col4.metric("Importers", f"{df_overview['num_importers'].iloc[0]}")
        col5.metric("Countries", f"{df_overview['num_countries'].iloc[0]}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Avg Price/Unit", f"${df_overview['avg_price'].iloc[0]:.4f}")
        col2.metric("Min Price/Unit", f"${df_overview['min_price'].iloc[0]:.4f}")
        col3.metric("Max Price/Unit", f"${df_overview['max_price'].iloc[0]:.4f}")

        # Monthly volume and price trends
        st.subheader("📈 Monthly Trends")
        query_monthly = """
        SELECT
            strftime('%Y-%m', FECHA_IMPORTACION_EXPORTACION) as month,
            SUM(CANTIDAD) as volume,
            SUM(PRECIO_UNIDAD * CANTIDAD) / NULLIF(SUM(CANTIDAD), 0) as weighted_avg_price,
            SUM(TOTAL_A_PAGAR) as total_value,
            COUNT(*) as shipments
        FROM flowers_greens
        WHERE tipo_producto = 'Rosas' AND FECHA_IMPORTACION_EXPORTACION IS NOT NULL
        GROUP BY month
        ORDER BY month
        """
        df_monthly = pd.read_sql(query_monthly, conn)

        if not df_monthly.empty:
            col1, col2 = st.columns(2)

            with col1:
                fig1 = px.line(df_monthly, x='month', y='volume',
                              title='Monthly Import Volume',
                              labels={'month': 'Month', 'volume': 'Volume (units)'})
                fig1.update_traces(line_color='#C62828')
                st.plotly_chart(fig1, use_container_width=True)

            with col2:
                fig2 = px.line(df_monthly, x='month', y='weighted_avg_price',
                              title='Monthly Weighted Average Price',
                              labels={'month': 'Month', 'weighted_avg_price': 'Price (USD)'})
                fig2.update_traces(line_color='#1565C0')
                st.plotly_chart(fig2, use_container_width=True)

            # Combined chart
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(x=df_monthly['month'], y=df_monthly['volume'],
                                  name='Volume', yaxis='y', marker_color='#C62828'))
            fig3.add_trace(go.Scatter(x=df_monthly['month'], y=df_monthly['weighted_avg_price'],
                                     name='Avg Price', yaxis='y2', mode='lines+markers',
                                     line=dict(color='#1565C0', width=3)))
            fig3.update_layout(
                title='Volume vs Price Over Time',
                yaxis=dict(title='Volume (units)', side='left'),
                yaxis2=dict(title='Price (USD)', overlaying='y', side='right'),
                hovermode='x unified'
            )
            st.plotly_chart(fig3, use_container_width=True)

        # Top importers
        st.subheader("🏢 Top Importers")
        query_importers = """
        SELECT
            IMPORTADOR_EXPORTADOR as importer,
            COUNT(*) as shipments,
            SUM(CANTIDAD) as volume,
            SUM(TOTAL_A_PAGAR) as total_value,
            ROUND(AVG(PRECIO_UNIDAD), 4) as avg_price,
            MIN(FECHA_IMPORTACION_EXPORTACION) as first_import,
            MAX(FECHA_IMPORTACION_EXPORTACION) as last_import
        FROM flowers_greens
        WHERE tipo_producto = 'Rosas' AND IMPORTADOR_EXPORTADOR IS NOT NULL
        GROUP BY IMPORTADOR_EXPORTADOR
        ORDER BY volume DESC
        LIMIT 20
        """
        df_importers = pd.read_sql(query_importers, conn)

        if not df_importers.empty:
            # Top 10 chart
            fig = px.bar(df_importers.head(10), x='volume', y='importer', orientation='h',
                        title='Top 10 Importers by Volume',
                        labels={'volume': 'Volume (units)', 'importer': 'Importer'},
                        color='total_value', color_continuous_scale='Reds')
            fig.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig, use_container_width=True)

            # Detailed table
            st.dataframe(df_importers, use_container_width=True)

        # Price distribution
        st.subheader("💰 Price Analysis")
        query_prices = """
        SELECT
            PRECIO_UNIDAD as price,
            CANTIDAD as quantity,
            TOTAL_A_PAGAR as value,
            FECHA_IMPORTACION_EXPORTACION as date,
            IMPORTADOR_EXPORTADOR as importer
        FROM flowers_greens
        WHERE tipo_producto = 'Rosas'
          AND PRECIO_UNIDAD IS NOT NULL
          AND PRECIO_UNIDAD > 0
          AND PRECIO_UNIDAD < 1
        LIMIT 5000
        """
        df_prices = pd.read_sql(query_prices, conn)

        if not df_prices.empty:
            col1, col2 = st.columns(2)

            with col1:
                fig = px.histogram(df_prices, x='price', nbins=50,
                                  title='Price Distribution',
                                  labels={'price': 'Price per Unit (USD)', 'count': 'Frequency'})
                fig.update_traces(marker_color='#C62828')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.box(df_prices, y='price',
                            title='Price Range (Box Plot)',
                            labels={'price': 'Price per Unit (USD)'})
                fig.update_traces(marker_color='#C62828')
                st.plotly_chart(fig, use_container_width=True)

        # Country of origin
        st.subheader("🌍 Countries of Origin")
        query_countries = """
        SELECT
            PAIS_DE_PROCEDENCIA_DESTINO as country,
            COUNT(*) as shipments,
            SUM(CANTIDAD) as volume,
            SUM(TOTAL_A_PAGAR) as total_value,
            ROUND(AVG(PRECIO_UNIDAD), 4) as avg_price
        FROM flowers_greens
        WHERE tipo_producto = 'Rosas' AND PAIS_DE_PROCEDENCIA_DESTINO IS NOT NULL
        GROUP BY PAIS_DE_PROCEDENCIA_DESTINO
        ORDER BY volume DESC
        LIMIT 15
        """
        df_countries = pd.read_sql(query_countries, conn)

        if not df_countries.empty:
            col1, col2 = st.columns(2)

            with col1:
                fig = px.pie(df_countries.head(10), values='volume', names='country',
                            title='Volume by Country (Top 10)')
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                fig = px.bar(df_countries.head(10), x='volume', y='country', orientation='h',
                            title='Top Countries by Volume',
                            labels={'volume': 'Volume (units)', 'country': 'Country'})
                fig.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df_countries, use_container_width=True)

        # Insights
        st.subheader("💡 Key Insights")

        # Calculate insights
        total_vol = df_overview['total_volume'].iloc[0]
        total_val = df_overview['total_value'].iloc[0]
        avg_price = df_overview['avg_price'].iloc[0]

        if not df_importers.empty:
            top_importer = df_importers.iloc[0]['importer']
            top_importer_share = (df_importers.iloc[0]['volume'] / total_vol * 100)

        if not df_countries.empty:
            top_country = df_countries.iloc[0]['country']
            top_country_share = (df_countries.iloc[0]['volume'] / total_vol * 100)

        insights = f"""
        - **Market Size**: {total_vol:,.0f} roses imported worth ${total_val:,.2f}
        - **Average Price**: ${avg_price:.4f} per unit
        - **Top Importer**: {top_importer if not df_importers.empty else 'N/A'} ({top_importer_share:.1f}% market share)
        - **Top Origin**: {top_country if not df_countries.empty else 'N/A'} ({top_country_share:.1f}% of volume)
        - **Market Concentration**: Top 5 importers control {df_importers.head(5)['volume'].sum() / total_vol * 100:.1f}% of market
        - **Active Period**: {df_overview['first_import'].iloc[0]} to {df_overview['last_import'].iloc[0]}
        """
        st.markdown(insights)

    else:
        st.warning("No rose import data available")

