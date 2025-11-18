import PyPDF2
import sqlite3
import re
import pandas as pd
from pathlib import Path

def normalize_code(code_str):
    """Convert code from PDF format to database format."""
    if not code_str:
        return None
    clean_code = code_str.replace('.', '').replace(' ', '')
    if not clean_code.isdigit():
        return None
    try:
        return int(clean_code)
    except:
        return None

def extract_improved_catalogue():
    """
    Improved extraction with multiple patterns to increase match rate.
    """
    pdf_path = Path("data/docs/arancel_2025.pdf")
    db_path = Path("data/imports/merged/merged_data.db")
    
    print("IMPROVED CATALOGUE EXTRACTION")
    print("=" * 100)
    
    # Get ground truth codes from imports
    conn = sqlite3.connect(db_path)
    df_ground_truth = pd.read_sql("SELECT DISTINCT COD_INCISO FROM merged_imports ORDER BY COD_INCISO", conn)
    ground_truth_codes = set(df_ground_truth['COD_INCISO'].values)
    print(f"Ground truth: {len(ground_truth_codes):,} unique codes in import data")
    
    # Read PDF
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        print(f"PDF pages: {num_pages}")
        
        all_text = []
        for page_num in range(num_pages):
            if (page_num + 1) % 50 == 0:
                print(f"  Reading page {page_num + 1}/{num_pages}...")
            all_text.append(pdf_reader.pages[page_num].extract_text())
    
    full_text = '\n'.join(all_text)
    print("✓ Text extraction complete")
    
    # Multiple extraction patterns
    print("\nExtracting with multiple patterns...")
    
    catalogue_data = []
    seen_codes = set()
    
    # Pattern 1: Full format with all taxes
    pattern1 = r'(\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+(\d+|II/\d+)\s+(\d+)\s+(\d+)\s+(\d+)'
    matches1 = re.findall(pattern1, full_text)
    print(f"Pattern 1 (full): {len(matches1)} matches")
    
    for match in matches1:
        code_str, desc, dai, itbms, isc, iccdp = match
        cod_inciso = normalize_code(code_str)
        if cod_inciso and cod_inciso not in seen_codes:
            parts = code_str.split('.')
            catalogue_data.append({
                'COD_INCISO': cod_inciso,
                'COD_CAPITULO': int(parts[0][:2]),
                'COD_PARTIDA': int(parts[0]),
                'COD_SUBPARTIDA': int(parts[0] + parts[1]),
                'DESCRIPCIÓN': desc.strip(),
                'DAI': dai,
                'ITBMS': float(itbms),
                'ISC': float(isc),
                'ICCDP': float(iccdp)
            })
            seen_codes.add(cod_inciso)
    
    # Pattern 2: Code with description only (no taxes on same line)
    pattern2 = r'(\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})\s+([A-Za-zÀ-ÿ\s\-\,\.\(\)]+?)(?=\n|\d{4}\.)'
    matches2 = re.findall(pattern2, full_text)
    print(f"Pattern 2 (no taxes): {len(matches2)} matches")
    
    for match in matches2:
        code_str, desc = match
        cod_inciso = normalize_code(code_str)
        if cod_inciso and cod_inciso not in seen_codes:
            parts = code_str.split('.')
            catalogue_data.append({
                'COD_INCISO': cod_inciso,
                'COD_CAPITULO': int(parts[0][:2]),
                'COD_PARTIDA': int(parts[0]),
                'COD_SUBPARTIDA': int(parts[0] + parts[1]),
                'DESCRIPCIÓN': desc.strip(),
                'DAI': None,
                'ITBMS': 0.0,
                'ISC': 0.0,
                'ICCDP': 0.0
            })
            seen_codes.add(cod_inciso)
    
    # Pattern 3: Alternative format (2 digits at start)
    pattern3 = r'(\d{2}\.\d{2}\.\d{2}\.\d{2}\.\d{2})\s+(.+?)\s+(\d+|II/\d+)\s+(\d+)\s+(\d+)\s+(\d+)'
    matches3 = re.findall(pattern3, full_text)
    print(f"Pattern 3 (alt format): {len(matches3)} matches")
    
    for match in matches3:
        code_str, desc, dai, itbms, isc, iccdp = match
        # Pad to 4 digits at start
        code_str_padded = code_str.split('.')[0].zfill(4) + '.' + '.'.join(code_str.split('.')[1:])
        cod_inciso = normalize_code(code_str_padded)
        if cod_inciso and cod_inciso not in seen_codes:
            parts = code_str_padded.split('.')
            catalogue_data.append({
                'COD_INCISO': cod_inciso,
                'COD_CAPITULO': int(parts[0][:2]),
                'COD_PARTIDA': int(parts[0]),
                'COD_SUBPARTIDA': int(parts[0] + parts[1]),
                'DESCRIPCIÓN': desc.strip(),
                'DAI': dai,
                'ITBMS': float(itbms),
                'ISC': float(isc),
                'ICCDP': float(iccdp)
            })
            seen_codes.add(cod_inciso)
    
    print(f"\nTotal unique codes extracted: {len(catalogue_data):,}")
    
    # Extract chapter names
    chapter_pattern = r'Capítulo\s+(\d+)\s*\n\s*(.+?)(?=\n|$)'
    chapter_matches = re.findall(chapter_pattern, full_text)
    chapter_names = {int(ch): name.strip() for ch, name in chapter_matches}
    
    # Create DataFrame
    df = pd.DataFrame(catalogue_data)
    df['CAPITULO_NOMBRE'] = df['COD_CAPITULO'].map(chapter_names)
    
    # Save to database
    print("\nSaving to database...")
    conn.execute("DROP TABLE IF EXISTS catalogo_arancel")
    df.to_sql('catalogo_arancel', conn, index=False, if_exists='replace')
    
    # Create indexes
    conn.execute("CREATE INDEX idx_cat_inciso ON catalogo_arancel(COD_INCISO)")
    conn.execute("CREATE INDEX idx_cat_capitulo ON catalogo_arancel(COD_CAPITULO)")
    conn.execute("CREATE INDEX idx_cat_partida ON catalogo_arancel(COD_PARTIDA)")
    conn.execute("CREATE INDEX idx_cat_subpartida ON catalogo_arancel(COD_SUBPARTIDA)")
    conn.commit()
    
    # Calculate match rate
    matched = ground_truth_codes.intersection(seen_codes)
    match_rate = len(matched) / len(ground_truth_codes) * 100
    
    print(f"\n{'=' * 100}")
    print(f"RESULTS:")
    print(f"  Codes in catalogue: {len(seen_codes):,}")
    print(f"  Codes in imports: {len(ground_truth_codes):,}")
    print(f"  Matched codes: {len(matched):,}")
    print(f"  Match rate: {match_rate:.2f}%")
    print(f"{'=' * 100}")
    
    conn.close()
    return df

if __name__ == "__main__":
    extract_improved_catalogue()

