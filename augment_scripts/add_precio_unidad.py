import sqlite3
import pandas as pd
from pathlib import Path

def add_precio_unidad_column():
    """
    Add PRECIO_UNIDAD column to the merged_imports table.
    PRECIO_UNIDAD = TOTAL_A_PAGAR / CANTIDAD
    """
    db_path = Path("data/imports/merged/merged_data.db")
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(merged_imports);")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'PRECIO_UNIDAD' in columns:
        print("Column PRECIO_UNIDAD already exists. Updating values...")
        # Update existing column
        cursor.execute("""
            UPDATE merged_imports
            SET PRECIO_UNIDAD = CASE 
                WHEN CANTIDAD IS NOT NULL AND CANTIDAD != 0 
                THEN TOTAL_A_PAGAR / CANTIDAD 
                ELSE NULL 
            END
        """)
    else:
        print("Adding PRECIO_UNIDAD column...")
        # Add new column
        cursor.execute("ALTER TABLE merged_imports ADD COLUMN PRECIO_UNIDAD REAL;")
        
        # Calculate and populate the column
        cursor.execute("""
            UPDATE merged_imports
            SET PRECIO_UNIDAD = CASE 
                WHEN CANTIDAD IS NOT NULL AND CANTIDAD != 0 
                THEN TOTAL_A_PAGAR / CANTIDAD 
                ELSE NULL 
            END
        """)
    
    conn.commit()
    
    # Get statistics
    cursor.execute("""
        SELECT 
            COUNT(*) as total_rows,
            COUNT(PRECIO_UNIDAD) as rows_with_precio,
            COUNT(*) - COUNT(PRECIO_UNIDAD) as rows_without_precio
        FROM merged_imports
    """)
    stats = cursor.fetchone()
    
    print(f"\nColumn added successfully!")
    print(f"Total rows: {stats[0]:,}")
    print(f"Rows with PRECIO_UNIDAD: {stats[1]:,}")
    print(f"Rows without PRECIO_UNIDAD (NULL): {stats[2]:,}")
    
    # Show sample data
    print("\nSample data with PRECIO_UNIDAD:")
    df_sample = pd.read_sql("""
        SELECT 
            CANTIDAD, 
            TOTAL_A_PAGAR, 
            PRECIO_UNIDAD,
            DESCRIPCIÓN,
            source_file
        FROM merged_imports 
        WHERE PRECIO_UNIDAD IS NOT NULL
        LIMIT 10
    """, conn)
    print(df_sample)
    
    # Show statistics
    print("\nPRECIO_UNIDAD statistics:")
    df_stats = pd.read_sql("""
        SELECT 
            MIN(PRECIO_UNIDAD) as min_precio,
            MAX(PRECIO_UNIDAD) as max_precio,
            AVG(PRECIO_UNIDAD) as avg_precio,
            COUNT(PRECIO_UNIDAD) as count
        FROM merged_imports
        WHERE PRECIO_UNIDAD IS NOT NULL
    """, conn)
    print(df_stats)
    
    conn.close()
    print("\nOperation complete!")

if __name__ == "__main__":
    add_precio_unidad_column()

