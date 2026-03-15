"""Extract add_ele scaling information from thesis PDFs using docling."""
from docling.document_converter import DocumentConverter
import re

def extract_and_search(pdf_path, label):
    print(f"\n{'='*80}")
    print(f"EXTRACTING: {label} ({pdf_path})")
    print(f"{'='*80}")
    
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    md_text = result.document.export_to_markdown()
    
    # Save full extraction for reference
    safe_label = label.replace(" ", "_")
    with open(f"extracted_{safe_label}.md", "w") as f:
        f.write(md_text)
    print(f"Full extraction saved to extracted_{safe_label}.md")
    
    # Search for add_ele related content
    keywords = [
        "add_ele", "kwh_raw", "kwh_total", "total_kwh",
        "scale factor", "scaling", "multiple", "interval",
        "divide", "division", "/100", "/1000", 
        "÷ 100", "÷ 1000", "× 100", "× 1000",
        "Increase power", "cumulative energy",
        "Table 3.5", "Table 3.6", "Table 3.7",
        "Equation 3.1", "Equation 3.2",
        "engineering unit", "raw reading",
        "Tuya specification", "Tuya Cloud",
        "data point", "DP code"
    ]
    
    lines = md_text.split('\n')
    
    print(f"\n--- Relevant sections found ---")
    found_any = False
    
    for keyword in keywords:
        matching_lines = []
        for i, line in enumerate(lines):
            if keyword.lower() in line.lower():
                # Get context: 3 lines before and after
                start = max(0, i - 3)
                end = min(len(lines), i + 4)
                context = '\n'.join(lines[start:end])
                matching_lines.append((i, context))
        
        if matching_lines:
            found_any = True
            print(f"\n>>> Keyword: '{keyword}' - {len(matching_lines)} match(es)")
            for line_num, context in matching_lines[:3]:  # Limit to 3 matches per keyword
                print(f"  [Line {line_num}]:")
                print(f"  {context}")
                print(f"  {'---'*20}")
    
    if not found_any:
        print("No relevant sections found.")
    
    return md_text

if __name__ == "__main__":
    # Extract from both thesis PDFs
    extract_and_search("TH1 SARIMAX.pdf", "TH1 SARIMAX V1")
    extract_and_search("TH1 SARIMAX V2.pdf", "TH1 SARIMAX V2")
