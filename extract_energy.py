import os
import re
import pandas as pd
from docling.document_converter import DocumentConverter
from pathlib import Path
from datetime import datetime

def extract_hourly_data(md_content):
    # Standardize content: collapse whitespace
    content = re.sub(r'\s+', ' ', md_content)
    
    extracted = []
    
    # Extract date if present (e.g., "January 7, 2026")
    date_match = re.search(r'(January|February|March)\s+\d{1,2},?\s+2026', content, re.I)
    current_date = date_match.group(0).replace(',', '') if date_match else None
    
    # This regex looks for:
    # 1. An hour (HH:00)
    # 2. Key appliance values within a reasonable proximity
    # We use a non-greedy approach to capture segments starting with an hour
    hour_segments = re.finditer(r'(\d{1,2}:00)', content)
    
    last_pos = 0
    matches = list(hour_segments)
    
    for i, match in enumerate(matches):
        hour = match.group(1)
        start = match.start()
        # End of segment is either the start of the next hour or the end of the content
        end = matches[i+1].start() if i + 1 < len(matches) else len(content)
        seg = content[start:end]
        
        def get_val(pattern):
            # Look for "Appliance: X.X kWh" or "Appliance: X kWh"
            m = re.search(pattern, seg, re.I)
            if m:
                try:
                    return float(m.group(1))
                except:
                    return 0.0
            return 0.0

        reading = {
            "Date": current_date,
            "Hour_24": hour,
            "Aircon": get_val(r'Aircon:\s*([\d\.]+)'),
            "Refrigerator": get_val(r'Refrigerator:\s*([\d\.]+)'),
            "Electric Fan": get_val(r'Electric\s*Fan:\s*([\d\.]+)')
        }
        
        # Convert hour to 12h format for output
        try:
            dt = datetime.strptime(hour, "%H:%M")
            reading["Hours"] = dt.strftime("%-I:%M %p")
        except:
            reading["Hours"] = hour
            
        # Only add if there's some energy recorded or if it's explicitly 0.0
        # (The user example shows many rows with 0 values)
        extracted.append(reading)
    
    return extracted

def main():
    smartlife_dir = "/Users/geovannyportodo/Sarimax-Thesis/SmartLife"
    pdf_files = [f for f in os.listdir(smartlife_dir) if f.endswith(".pdf")]
    pdf_files.sort() # Sort to process roughly in order
    
    converter = DocumentConverter()
    
    all_readings = []
    
    for pdf in pdf_files:
        pdf_path = os.path.join(smartlife_dir, pdf)
        print(f"Processing {pdf}...")
        try:
            result = converter.convert(pdf_path)
            md = result.document.export_to_markdown()
            
            readings = extract_hourly_data(md)
            
            # Fallback date from filename if not found in content
            filename_date = Path(pdf).stem.replace(',', '').split(' to ')[0] # Basic fallback
            
            for r in readings:
                if not r["Date"]:
                    r["Date"] = filename_date
                all_readings.append(r)
        except Exception as e:
            print(f"Error processing {pdf}: {e}")

    if not all_readings:
        print("No data extracted.")
        return

    df = pd.DataFrame(all_readings)
    
    # Drop duplicates (same date, same hour)
    df = df.drop_duplicates(subset=["Date", "Hours"])
    
    # Calculate Total Energy
    df["Total Energy"] = df["Aircon"] + df["Refrigerator"] + df["Electric Fan"]
    
    # Sort by Date and Hour
    # Need to normalize date for sorting
    def parse_dt(row):
        try:
            return datetime.strptime(f"{row['Date']} {row['Hour_24']}", "%B %d %Y %H:%M")
        except:
            return datetime.min

    df["dt_sort"] = df.apply(parse_dt, axis=1)
    df = df.sort_values("dt_sort")
    
    # Group by Date and produce the requested format
    output_lines = ["Date,Hours,Total Energy,Aircon,Refrigerator,Electric Fan"]
    
    for date, group in df.groupby("Date", sort=False):
        first_row = True
        for _, row in group.iterrows():
            date_col = date if first_row else ""
            line = f"{date_col},{row['Hours']},{row['Total Energy']:.2f},{row['Aircon']:.2f},{row['Refrigerator']:.2f},{row['Electric Fan']:.2f}"
            output_lines.append(line)
            first_row = False
        
        # Add TOTAL row for this day
        total_e = group["Total Energy"].sum()
        total_a = group["Aircon"].sum()
        total_r = group["Refrigerator"].sum()
        total_f = group["Electric Fan"].sum()
        output_lines.append(f"TOTAL,,{total_e:.2f},{total_a:.2f},{total_r:.2f},{total_f:.2f}")

    with open("energy_extracted.csv", "w") as f:
        f.write("\n".join(output_lines))
    
    print("Extraction complete. Results saved to energy_extracted.csv")

if __name__ == "__main__":
    main()
