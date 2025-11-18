AUGMENT SCRIPTS FOLDER
======================

This folder contains utility scripts for the ProjectBlum project.

SCRIPTS:
--------

1. merge_xlsx_to_sqlite.py
   - Merges all XLSX files from data/imports into a single SQLite database
   - Handles files with different column structures
   - Uses chunked processing to avoid memory issues
   - Output: data/imports/merged/merged_data.db

2. verify_database.py
   - Verifies the merged SQLite database
   - Shows database statistics, column info, and sample data
   - Displays row counts by source file

3. add_precio_unidad.py
   - Adds PRECIO_UNIDAD column to the database
   - Calculates PRECIO_UNIDAD = TOTAL_A_PAGAR / CANTIDAD
   - Handles division by zero (sets to NULL)

4. check_precio_unidad.py
   - Quick verification of PRECIO_UNIDAD column
   - Shows sample calculations to verify accuracy

5. reorder_columns.py
   - Reorders all columns in the database table
   - Renames PAÍS_DE_PROCEDENCIA_DESTINO to PAIS_DE_PROCEDENCIA_DESTINO
   - Creates optimized column order for analysis

6. verify_column_order.py
   - Verifies that columns are in the correct order
   - Confirms column renaming was successful

USAGE:
------

To merge XLSX files:
  python augment_scripts/merge_xlsx_to_sqlite.py

To add PRECIO_UNIDAD column:
  python augment_scripts/add_precio_unidad.py

To verify the database:
  python augment_scripts/verify_database.py

To check PRECIO_UNIDAD column:
  python augment_scripts/check_precio_unidad.py

To reorder columns:
  python augment_scripts/reorder_columns.py

To verify column order:
  python augment_scripts/verify_column_order.py

MERGED DATABASE INFO:
--------------------

Location: data/imports/merged/merged_data.db
Table: merged_imports
Total Rows: 9,509,593
Database Size: ~2.88 GB
Columns: 26 (including calculated PRECIO_UNIDAD column)

Files merged:
- IMP_2020_1.xlsx (615,258 rows)
- IMP_2020_2.xlsx (747,675 rows)
- IMP_2021_1.xlsx (813,348 rows)
- IMP_2021_2.xlsx (891,606 rows)
- IMP_2022_1.xlsx (785,472 rows)
- IMP_2022_2.xlsx (854,690 rows)
- IMP_2023_1.xlsx (827,925 rows)
- IMP_2023_2.xlsx (866,187 rows)
- IMP_2024_1.xlsx (821,179 rows)
- IMP_2024_2.xlsx (930,109 rows)
- IMP_2025_1.xlsx (881,443 rows)
- IMP_2025_2.xlsx (474,701 rows)

