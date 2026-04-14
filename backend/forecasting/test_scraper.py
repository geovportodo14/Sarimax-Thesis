#!/usr/bin/env python3
"""
Quick verification script for the MeralcoRateScraper.

Usage:
    python backend/forecasting/test_scraper.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from forecasting.meralco_scraper import MeralcoRateScraper, scrape_latest_tariff


def main():
    print("=" * 60)
    print("Meralco Rate Scraper — Test Run")
    print("=" * 60)

    # --- Test 1: fetch latest RSS item ---
    print("\n[1] Fetching latest RSS item...")
    scraper = MeralcoRateScraper()
    item = scraper.fetch_latest_rss_item()

    if item is None:
        print("FAIL: No 'Summary of Schedule of Rates' entry found in RSS feed.")
        sys.exit(1)

    print(f"  Title     : {item['title']}")
    print(f"  PDF URL   : {item['pdf_url']}")
    print(f"  Month Key : {item['month_key_str']}")
    print(f"  Source URL : {item['rss_item_url']}")

    # --- Test 2: full scrape_latest_tariff (download + parse + cache) ---
    print("\n[2] Running full scrape_latest_tariff()...")
    result = scrape_latest_tariff()

    print(f"  Month Key      : {result['month_key']}")
    print(f"  Effective Tariff: PHP {result['tariff_php']:.4f}/kWh")
    print(f"  From Cache     : {result['cached']}")
    print(f"  Brackets Found : {len(result['rates'])}")

    # --- Test 3: print extracted brackets ---
    print("\n[3] Extracted residential rate brackets:")
    for i, rate in enumerate(result["rates"]):
        bracket = rate["consumption_bracket"]
        gen = rate["generation_charge"]
        dist = rate["distribution_charge"]
        trans = rate["transmission_charge"]
        sys_loss = rate["system_loss_charge"]
        total_main = gen + trans + sys_loss + dist
        print(f"  [{i+1}] {bracket:20s} | Gen={gen:.4f} Trans={trans:.4f} SysLoss={sys_loss:.4f} Dist={dist:.4f} | Subtotal={total_main:.4f}")

    # --- Test 4: dump full JSON ---
    print("\n[4] Full JSON output:")
    print(json.dumps(result["rates"], indent=2))

    print("\n" + "=" * 60)
    print("All tests passed.")
    print("=" * 60)


if __name__ == "__main__":
    main()
