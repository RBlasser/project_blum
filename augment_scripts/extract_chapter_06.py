import PyPDF2
from pathlib import Path

def extract_chapter_06():
    """
    Extract Chapter 06 (flowers and plants) from the arancel PDF.
    """
    pdf_path = Path("data/docs/arancel_2025.pdf")
    output_file = Path("data/docs/chapter_06_flowers.txt")
    
    print(f"Reading: {pdf_path}")
    
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
        
        print(f"Total pages: {num_pages}")
        print("Searching for Chapter 06 (Plantas vivas y productos de la floricultura)...")
        
        chapter_06_content = []
        in_chapter_06 = False
        
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()

            # Check if we're entering Chapter 06
            if not in_chapter_06 and ('Capítulo   6' in text or 'Capítulo 6' in text or 'Capítulo  6' in text):
                in_chapter_06 = True
                print(f"Found Chapter 06 starting at page {page_num + 1}")
                chapter_06_content.append(f"\n--- PAGE {page_num + 1} ---\n")
                chapter_06_content.append(text)
                continue

            # If we're in Chapter 06, add content
            if in_chapter_06:
                # Check if we're leaving Chapter 06 (entering Chapter 07)
                if 'Capítulo   7' in text or 'Capítulo 7' in text or 'Capítulo  7' in text:
                    print(f"Chapter 06 ends at page {page_num}")
                    break

                chapter_06_content.append(f"\n--- PAGE {page_num + 1} ---\n")
                chapter_06_content.append(text)
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("CHAPTER 06 - PLANTAS VIVAS Y PRODUCTOS DE LA FLORICULTURA\n")
            f.write("=" * 100 + "\n")
            f.write(''.join(chapter_06_content))
        
        print(f"\n✓ Chapter 06 content saved to: {output_file}")
        print(f"✓ Total pages extracted: {len(chapter_06_content) // 2}")
        
        # Also print to console
        print("\n" + "=" * 100)
        print("CHAPTER 06 CONTENT:")
        print("=" * 100)
        print(''.join(chapter_06_content))

if __name__ == "__main__":
    extract_chapter_06()

