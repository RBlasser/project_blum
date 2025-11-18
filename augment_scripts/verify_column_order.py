import sqlite3
from pathlib import Path

def verify_column_order():
    """
    Verify the column order in the merged_imports table.
    """
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Expected column order
    expected_order = [
        'FECHA_IMPORTACION_EXPORTACION',
        'IMPORTADOR_EXPORTADOR',
        'PAIS_DE_PROCEDENCIA_DESTINO',
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
    
    # Get actual column order
    cursor.execute("PRAGMA table_info(merged_imports);")
    columns = cursor.fetchall()
    actual_order = [col[1] for col in columns]
    
    print("COLUMN ORDER VERIFICATION")
    print("=" * 60)
    print(f"\nExpected: {len(expected_order)} columns")
    print(f"Actual:   {len(actual_order)} columns")
    print()
    
    # Compare
    all_match = True
    for i, (expected, actual) in enumerate(zip(expected_order, actual_order), 1):
        match = "✓" if expected == actual else "✗"
        if expected != actual:
            all_match = False
            print(f"{match} {i:2d}. Expected: {expected:35s} | Actual: {actual}")
        else:
            print(f"{match} {i:2d}. {actual}")
    
    print()
    if all_match:
        print("✓ ALL COLUMNS MATCH THE EXPECTED ORDER!")
    else:
        print("✗ COLUMN ORDER MISMATCH DETECTED!")
    
    # Verify row count
    cursor.execute("SELECT COUNT(*) FROM merged_imports")
    row_count = cursor.fetchone()[0]
    print(f"\nTotal rows: {row_count:,}")
    
    # Check for renamed column
    if 'PAIS_DE_PROCEDENCIA_DESTINO' in actual_order:
        print("✓ Column renamed: PAÍS_DE_PROCEDENCIA_DESTINO → PAIS_DE_PROCEDENCIA_DESTINO")
    
    if 'PAÍS_DE_PROCEDENCIA_DESTINO' in actual_order:
        print("✗ Old column name still exists: PAÍS_DE_PROCEDENCIA_DESTINO")
    
    conn.close()

if __name__ == "__main__":
    verify_column_order()

