import sqlite3
import pandas as pd
from pathlib import Path

def reorder_columns():
    """
    Reorder columns in the merged_imports table and rename PAÍS_DE_PROCEDENCIA_DESTINO.
    Creates a new table with the correct column order, then replaces the old one.
    """
    db_path = Path("data/imports/merged/merged_data.db")
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    print(f"Connecting to database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Define the new column order
    new_column_order = [
        'FECHA_IMPORTACION_EXPORTACION',
        'IMPORTADOR_EXPORTADOR',
        'PAIS_DE_PROCEDENCIA_DESTINO',  # Renamed from PAÍS_DE_PROCEDENCIA_DESTINO
        'COD_INCISO',
        'COD_CAPITULO',
        'COD_PARTIDA',
        'COD_SUBPARTIDA',
        'CATEGORIA',
        'DESCRIPCIÓN',
        'PUNTO_ENTRADA_PAIS',
        'PRECIO_UNIDAD',
        'CANTIDAD',
        'UNIDAD',
        'PESO_NETO',
        'PESO_BRUTO',
        'VALOR_FOB',
        'VALOR_FLETE',
        'VALOR_SEGURO',
        'VALOR_CIF',
        'IMPUESTO_IMPORTACION',
        'ITBMS',
        'IMP_PROTECCION_PETROLEO',
        'IMPUESTOS_ISC',
        'TOTAL_A_PAGAR',
        'MODO_TRANSPORTE',
        'source_file'
    ]
    
    print("\nCreating new table with reordered columns...")
    print("This may take several minutes for 9.5 million rows...")
    
    # Create the SELECT statement with renamed column
    select_columns = []
    for col in new_column_order:
        if col == 'PAIS_DE_PROCEDENCIA_DESTINO':
            select_columns.append('PAÍS_DE_PROCEDENCIA_DESTINO AS PAIS_DE_PROCEDENCIA_DESTINO')
        else:
            select_columns.append(col)
    
    select_statement = ', '.join(select_columns)
    
    # Create new table with reordered columns
    print("\nStep 1: Creating temporary table with new structure...")
    cursor.execute(f"""
        CREATE TABLE merged_imports_new AS
        SELECT {select_statement}
        FROM merged_imports
    """)
    
    print("Step 2: Dropping old table...")
    cursor.execute("DROP TABLE merged_imports")
    
    print("Step 3: Renaming new table...")
    cursor.execute("ALTER TABLE merged_imports_new RENAME TO merged_imports")
    
    conn.commit()
    
    print("\n✓ Columns reordered successfully!")
    
    # Verify the new structure
    cursor.execute("PRAGMA table_info(merged_imports);")
    columns = cursor.fetchall()
    
    print(f"\nNew column order ({len(columns)} columns):")
    for i, col in enumerate(columns, 1):
        print(f"  {i:2d}. {col[1]} ({col[2]})")
    
    # Verify row count
    cursor.execute("SELECT COUNT(*) FROM merged_imports")
    row_count = cursor.fetchone()[0]
    print(f"\nTotal rows: {row_count:,}")
    
    # Show sample data
    print("\nSample data (first 3 rows):")
    df_sample = pd.read_sql("SELECT * FROM merged_imports LIMIT 3", conn)
    print(df_sample.T)  # Transpose to show columns vertically
    
    conn.close()
    print("\nOperation complete!")

if __name__ == "__main__":
    reorder_columns()

