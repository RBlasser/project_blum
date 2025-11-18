import PyPDF2
from pathlib import Path

def read_arancel_pdf():
    """
    Read the arancel_2025.pdf file to understand the tariff code structure.
    """
    pdf_path = Path("data/docs/arancel_2025.pdf")
    
    if not pdf_path.exists():
        print(f"PDF file not found at {pdf_path}")
        return
    
    print(f"Reading: {pdf_path}")
    print(f"File size: {pdf_path.stat().st_size / (1024**2):.2f} MB")
    print("=" * 100)
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            print(f"\nTotal pages: {num_pages}")
            print("\nExtracting first 10 pages to understand structure...\n")
            print("=" * 100)
            
            # Read first 10 pages to understand structure
            for page_num in range(min(10, num_pages)):
                print(f"\n--- PAGE {page_num + 1} ---")
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                print(text[:2000])  # Print first 2000 characters
                print("...")
                
            # Search for flower-related content
            print("\n" + "=" * 100)
            print("SEARCHING FOR FLOWER-RELATED CONTENT...")
            print("=" * 100)
            
            flower_keywords = ['flor', 'rosa', 'orquidea', 'clavel', 'capitulo 6', 'capitulo 06']
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text().lower()
                
                for keyword in flower_keywords:
                    if keyword in text:
                        print(f"\nFound '{keyword}' on page {page_num + 1}")
                        # Extract context around the keyword
                        page_text = pdf_reader.pages[page_num].extract_text()
                        print(page_text[:3000])
                        print("\n" + "-" * 100)
                        break
                        
    except Exception as e:
        print(f"Error reading PDF: {e}")
        print("\nTrying alternative method...")
        
        # Try with pdfplumber if PyPDF2 fails
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                print(f"Total pages: {len(pdf.pages)}")
                for i in range(min(5, len(pdf.pages))):
                    print(f"\n--- PAGE {i + 1} ---")
                    text = pdf.pages[i].extract_text()
                    print(text[:2000])
        except ImportError:
            print("pdfplumber not installed. Install with: pip install pdfplumber")

if __name__ == "__main__":
    read_arancel_pdf()

