import sqlite3
from pathlib import Path

def test_flower_search():
    """
    Quick test to find flower-related items.
    """
    db_path = Path("data/imports/merged/merged_data.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Testing flower search...")
    
    # Simple search for 'flor' in DESCRIPCIÓN
    query = """
        SELECT COUNT(*) 
        FROM merged_imports 
        WHERE LOWER(DESCRIPCIÓN) LIKE '%flor%' 
           OR LOWER(CATEGORIA) LIKE '%flor%'
    """
    
    cursor.execute(query)
    count = cursor.fetchone()[0]
    print(f"Records containing 'flor': {count:,}")
    
    # Get sample records
    query2 = """
        SELECT COD_INCISO, CATEGORIA, DESCRIPCIÓN
        FROM merged_imports 
        WHERE LOWER(DESCRIPCIÓN) LIKE '%flor%' 
           OR LOWER(CATEGORIA) LIKE '%flor%'
        LIMIT 20
    """
    
    cursor.execute(query2)
    results = cursor.fetchall()
    
    print(f"\nSample records (first 20):")
    print("-" * 100)
    for row in results:
        print(f"COD_INCISO: {row[0]}")
        print(f"  CATEGORIA: {row[1]}")
        print(f"  DESCRIPCIÓN: {row[2]}")
        print()
    
    conn.close()

if __name__ == "__main__":
    test_flower_search()

