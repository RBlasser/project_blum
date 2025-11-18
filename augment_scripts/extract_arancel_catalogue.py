import PyPDF2
import sqlite3
import re
import pandas as pd
from pathlib import Path

def normalize_code(code_str):
    """
    Convert code from PDF format (0603.11.00.00.00) to database format (603110000).
    The database stores codes as integers WITHOUT leading zeros.
    """
    if not code_str:
        return None

    # Remove dots and spaces
    clean_code = code_str.replace('.', '').replace(' ', '')

    # Ensure it's numeric
    if not clean_code.isdigit():
        return None

    # Convert to integer (this removes leading zeros naturally)
    try:
        return int(clean_code)
    except:
        return None

def extract_arancel_catalogue():
    """
    Extract complete tariff catalogue from arancel_2025.pdf
    """
    pdf_path = Path("data/docs/arancel_2025.pdf")
    db_path = Path("data/imports/merged/merged_data.db")
    
    print("EXTRACTING TARIFF CATALOGUE FROM PDF")
    print("=" * 100)
    print(f"Source: {pdf_path}")
    print(f"Target: {db_path}")
    
    # Read PDF
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        print(f"\nTotal pages to process: {num_pages}")
        
        all_text = []
        print("\nExtracting text from all pages...")
        
        for page_num in range(num_pages):
            if (page_num + 1) % 50 == 0:
                print(f"  Processing page {page_num + 1}/{num_pages}...")
            
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            all_text.append(text)
        
        print("✓ Text extraction complete")
    
    # Combine all text
    full_text = '\n'.join(all_text)
    
    # Parse tariff codes
    print("\nParsing tariff codes...")
    
    # Pattern to match tariff lines
    # Example: 0603.11.00.00.00 - - Rosas 15 0 0 0
    pattern = r'(\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+(\d+|II/\d+)\s+(\d+)\s+(\d+)\s+(\d+)'
    
    matches = re.findall(pattern, full_text)
    
    print(f"✓ Found {len(matches)} tariff code entries")
    
    # Process matches
    catalogue_data = []
    current_chapter = None
    current_chapter_name = None
    
    for match in matches:
        code_str, description, dai, itbms, isc, iccdp = match

        # Normalize code
        cod_inciso = normalize_code(code_str)

        if cod_inciso is None:
            continue

        # Extract hierarchical codes from the ORIGINAL string
        # Format: 0603.11.00.00.00 -> parts = ['0603', '11', '00', '00', '00']
        # We need: Chapter=06, Partida=0603, Subpartida=060311
        parts = code_str.split('.')
        if len(parts) >= 3:
            # parts[0] is like '0603' (4 digits)
            # Chapter is first 2 digits: '06' -> 6
            # Partida is first 4 digits: '0603' -> 603
            # Subpartida is first 6 digits: '0603' + '11' -> 60311
            cod_capitulo = int(parts[0][:2])  # '06' -> 6
            cod_partida = int(parts[0])  # '0603' -> 603
            cod_subpartida = int(parts[0] + parts[1])  # '0603' + '11' -> 60311
        else:
            # Fallback to string slicing
            code_str_clean = code_str.replace('.', '')
            cod_capitulo = int(code_str_clean[:2])
            cod_partida = int(code_str_clean[:4])
            cod_subpartida = int(code_str_clean[:6])

        # Clean description
        description = description.strip()

        catalogue_data.append({
            'COD_INCISO': cod_inciso,
            'COD_CAPITULO': cod_capitulo,
            'COD_PARTIDA': cod_partida,
            'COD_SUBPARTIDA': cod_subpartida,
            'DESCRIPCIÓN': description,
            'DAI': dai,
            'ITBMS': float(itbms),
            'ISC': float(isc),
            'ICCDP': float(iccdp)
        })
    
    print(f"✓ Processed {len(catalogue_data)} valid entries")
    
    # Create DataFrame
    df = pd.DataFrame(catalogue_data)
    
    # Add chapter names by extracting from text
    print("\nExtracting chapter names...")
    chapter_pattern = r'Capítulo\s+(\d+)\s*\n\s*(.+?)(?=\n|$)'
    chapter_matches = re.findall(chapter_pattern, full_text)
    
    chapter_names = {}
    for ch_num, ch_name in chapter_matches:
        chapter_names[int(ch_num)] = ch_name.strip()
    
    df['CAPITULO_NOMBRE'] = df['COD_CAPITULO'].map(chapter_names)
    
    print(f"✓ Found {len(chapter_names)} chapter names")
    
    # Save to SQLite
    print("\nCreating catalogue table in database...")
    conn = sqlite3.connect(db_path)
    
    # Drop existing table if exists
    conn.execute("DROP TABLE IF EXISTS catalogo_arancel")
    
    # Create table
    df.to_sql('catalogo_arancel', conn, index=False, if_exists='replace')
    
    # Create indexes for fast JOINs
    print("Creating indexes...")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cat_inciso ON catalogo_arancel(COD_INCISO)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cat_capitulo ON catalogo_arancel(COD_CAPITULO)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cat_partida ON catalogo_arancel(COD_PARTIDA)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_cat_subpartida ON catalogo_arancel(COD_SUBPARTIDA)")
    
    conn.commit()
    
    print("✓ Catalogue table created with indexes")
    
    # Export to CSV
    csv_path = Path("data/imports/merged/catalogo_arancel.csv")
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"✓ Exported to CSV: {csv_path}")
    
    # Generate statistics
    print("\n" + "=" * 100)
    print("CATALOGUE STATISTICS")
    print("=" * 100)
    print(f"Total tariff codes: {len(df):,}")
    print(f"Unique chapters: {df['COD_CAPITULO'].nunique()}")
    print(f"Unique partidas: {df['COD_PARTIDA'].nunique()}")
    print(f"Unique subpartidas: {df['COD_SUBPARTIDA'].nunique()}")
    
    conn.close()
    
    return df

if __name__ == "__main__":
    df = extract_arancel_catalogue()
    print("\n✓ Extraction complete!")

