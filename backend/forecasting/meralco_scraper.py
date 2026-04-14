"""
forecasting/meralco_scraper.py
===============================
Scrapes the latest Meralco residential electricity rates from their
RSS feed / website archive.  Downloads the "Summary Schedule of Rates"
PDF and extracts per-bracket tariff components using pdfplumber.

Dependencies:  pdfplumber, certifi
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import ssl
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import certifi
import pdfplumber

ssl_context = ssl.create_default_context(cafile=certifi.where())

# Cache directory for scraped rate JSONs
_CACHE_DIR = Path(__file__).resolve().parent / "outputs" / "meralco_rates"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_negative(val_str: str) -> float:
    """Parse string to float, handling accounting negatives like '(0.123)' as '-0.123'."""
    if not val_str:
        return 0.0
    val_str = val_str.replace("P", "").replace(",", "").strip()
    if val_str.startswith("(") and val_str.endswith(")"):
        num_str = val_str.strip("()")
        return -float(num_str) if num_str else 0.0
    try:
        return float(val_str)
    except ValueError:
        return 0.0


# ---------------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------------

class MeralcoRateScraper:
    def __init__(self, rss_url: str = "https://company.meralco.com.ph/taxonomy/term/86/feed"):
        self.rss_url = rss_url

    # ------------------------------------------------------------------
    # Caching helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _cache_path(month_key: str) -> Path:
        return _CACHE_DIR / f"rates_{month_key}.json"

    @staticmethod
    def load_cached_rates(month_key: str) -> Optional[List[Dict[str, Any]]]:
        """Return cached rates for *month_key* (YYYY-MM), or None if not cached."""
        path = MeralcoRateScraper._cache_path(month_key)
        if path.exists():
            with open(path, "r") as f:
                return json.load(f)
        return None

    @staticmethod
    def save_rates_to_cache(month_key: str, rates: List[Dict[str, Any]]) -> Path:
        """Persist extracted rates as JSON.  Returns the cache file path."""
        _CACHE_DIR.mkdir(parents=True, exist_ok=True)
        path = MeralcoRateScraper._cache_path(month_key)
        with open(path, "w") as f:
            json.dump(rates, f, indent=2)
        return path

    # ------------------------------------------------------------------
    # RSS / archive fetching
    # ------------------------------------------------------------------

    def fetch_latest_rss_item(self) -> Optional[Dict[str, Any]]:
        """Fetch the RSS feed and find the most recent 'Summary of Schedule of Rates' PDF entry."""
        try:
            req = urllib.request.Request(self.rss_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, context=ssl_context) as response:
                xml_data = response.read()
        except urllib.error.URLError as e:
            raise Exception(f"Failed to fetch RSS feed: {e}")

        root = ET.fromstring(xml_data)

        for item in root.findall(".//item"):
            title_elem = item.find("title")
            title = title_elem.text if (title_elem is not None and title_elem.text) else ""

            if "SUMMARY OF SCHEDULE OF RATES" not in title.upper() and "SUMMARY SCHEDULE OF RATES" not in title.upper():
                continue

            link_elem = item.find("link")
            rss_item_url = link_elem.text if (link_elem is not None and link_elem.text) else ""

            pub_elem = item.find("pubDate")
            pubDate = pub_elem.text if (pub_elem is not None and pub_elem.text) else ""

            try:
                req_html = urllib.request.Request(rss_item_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req_html, context=ssl_context) as response:
                    html_data = response.read().decode("utf-8")

                pdf_urls = re.findall(r'href=[\'"]?([^\'" >]+\.pdf)[\'"]?', html_data, re.IGNORECASE)

                target_pdf_url = None
                for purl in pdf_urls:
                    if "rate" in purl.lower() and ("schedule" in purl.lower() or "summary" in purl.lower()):
                        target_pdf_url = purl
                        break
                if not target_pdf_url:
                    target_pdf_url = pdf_urls[-1] if pdf_urls else None

                if not target_pdf_url:
                    print("Warning: No PDF URL found in the RSS item HTML.")
                    continue

                pdf_url = target_pdf_url
                if not pdf_url.startswith("http"):
                    pdf_url = "https://company.meralco.com.ph" + pdf_url
            except Exception as e:
                print(f"Failed to fetch item HTML: {e}")
                continue

            month_key_str = None
            if pubDate:
                try:
                    month_match = re.search(
                        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (\d{4})",
                        pubDate,
                        re.IGNORECASE,
                    )
                    if month_match:
                        m_str, y_str = month_match.groups()
                        dt = datetime.strptime(f"{m_str[:3]} {y_str}", "%b %Y")
                        month_key_str = dt.strftime("%Y-%m")
                except Exception as e:
                    print(f"Failed to parse pubDate: {pubDate}, e: {e}")

            if not month_key_str:
                month_match = re.search(
                    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
                    title,
                    re.IGNORECASE,
                )
                if month_match:
                    month_name, year = month_match.groups()
                    dt = datetime.strptime(f"{month_name} {year}", "%B %Y")
                    month_key_str = dt.strftime("%Y-%m")

            return {
                "pdf_url": pdf_url,
                "rss_item_url": rss_item_url,
                "month_key_str": month_key_str,
                "title": title,
            }

        return None

    def _fetch_with_retry(self, url: str, max_retries: int = 3) -> str:
        """Fetch URL with exponential backoff for 429 and 5xx errors."""
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, context=ssl_context) as response:
                    return response.read().decode("utf-8")
            except urllib.error.HTTPError as e:
                if e.code == 429 or 500 <= e.code < 600:
                    wait_time = 2 ** attempt
                    print(f"Warning: HTTP {e.code} for {url}. Retrying in {wait_time}s (Attempt {attempt + 1}/{max_retries})...")
                    time.sleep(wait_time)
                else:
                    raise
            except urllib.error.URLError as e:
                wait_time = 2 ** attempt
                print(f"Warning: URL Error for {url}: {e}. Retrying in {wait_time}s (Attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait_time)
        raise Exception(f"Failed to fetch {url} after {max_retries} attempts.")

    def fetch_historical_archive_items(self, start_month: str, end_month: str) -> List[Dict[str, Any]]:
        """Fetch historical 'Summary of Schedule of Rates' PDF entries by crawling the paginated HTML archive."""
        items_in_range: List[Dict[str, Any]] = []
        seen_pdf_urls: set[str] = set()
        seen_node_urls: set[str] = set()

        page_num = 0
        pages_crawled = 0
        stop_crawling = False

        while not stop_crawling:
            archive_url = f"https://company.meralco.com.ph/taxonomy/term/86?page={page_num}"
            print(f"Crawling archive page {page_num}: {archive_url}")

            try:
                html_data = self._fetch_with_retry(archive_url)
                pages_crawled += 1
            except Exception as e:
                print(f"Failed to fetch archive page {page_num}: {e}")
                break

            node_links = re.findall(r'<a[^>]+href=[\'"](/node/\d+)[\'"][^>]*>(.*?)</a>', html_data)

            if not node_links:
                print(f"No more nodes found on page {page_num}. Ending pagination.")
                break

            for href, link_text in node_links:
                node_url = "https://company.meralco.com.ph" + href

                if node_url in seen_node_urls:
                    continue
                seen_node_urls.add(node_url)

                time.sleep(1)  # Polite delay
                try:
                    node_html = self._fetch_with_retry(node_url)

                    pdf_urls = re.findall(r'href=[\'"]?([^\'" >]+\.pdf)[\'"]?', node_html, re.IGNORECASE)

                    target_pdf_url = None
                    for purl in pdf_urls:
                        if "rate" in purl.lower() and ("schedule" in purl.lower() or "summary" in purl.lower()):
                            target_pdf_url = purl
                            break
                    if not target_pdf_url:
                        target_pdf_url = pdf_urls[-1] if pdf_urls else None

                    if not target_pdf_url:
                        continue

                    pdf_url = target_pdf_url
                    if not pdf_url.startswith("http"):
                        pdf_url = "https://company.meralco.com.ph" + pdf_url

                    if pdf_url in seen_pdf_urls:
                        continue

                    # Extract billing month from the PDF URL — uses broad year pattern
                    month_match = re.search(r"/(20\d{2})-(\d{2})/", pdf_url)
                    if month_match:
                        y_str, m_str = month_match.groups()
                        month_key_str = f"{y_str}-{m_str}"
                    else:
                        month_match = re.search(r"/(\d{2})-(20\d{2})_", pdf_url)
                        if month_match:
                            m_str, y_str = month_match.groups()
                            month_key_str = f"{y_str}-{m_str}"
                        else:
                            title_match = re.search(r"<title>(.*?)</title>", node_html, re.IGNORECASE)
                            title = title_match.group(1) if title_match else ""
                            m_match = re.search(
                                r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})",
                                title,
                                re.IGNORECASE,
                            )
                            if m_match:
                                m_name, y_name = m_match.groups()
                                dt = datetime.strptime(f"{m_name} {y_name}", "%B %Y")
                                month_key_str = dt.strftime("%Y-%m")
                            else:
                                continue

                    # Date filtering
                    if month_key_str > end_month:
                        seen_pdf_urls.add(pdf_url)
                        continue

                    if month_key_str < start_month:
                        print(f"Found {month_key_str} which is older than start_month {start_month}. Halting pagination.")
                        stop_crawling = True
                        break

                    seen_pdf_urls.add(pdf_url)
                    title_match = re.search(r"<title>(.*?)</title>", node_html, re.IGNORECASE)

                    items_in_range.append({
                        "pdf_url": pdf_url,
                        "rss_item_url": node_url,
                        "month_key_str": month_key_str,
                        "title": title_match.group(1).replace(" | Meralco", "").strip() if title_match else "Historical Meralco Rates",
                    })

                except Exception as e:
                    print(f"Warning: Failed to fetch historical node {node_url}: {e}")
                    continue

            page_num += 1
            time.sleep(1)  # Polite delay between taxonomy pages

        print(f"Crawler finished. Crawled {pages_crawled} pages. Found {len(items_in_range)} valid entries matching range.")
        return items_in_range

    def download_pdf(self, pdf_url: str, output_path: str) -> str:
        """Download the PDF and return its SHA-256 hash."""
        req = urllib.request.Request(pdf_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, context=ssl_context) as response, open(output_path, "wb") as out_file:
            data = response.read()
            out_file.write(data)
            pdf_sha256 = hashlib.sha256(data).hexdigest()
        return pdf_sha256

    # ------------------------------------------------------------------
    # PDF table parsing
    # ------------------------------------------------------------------

    def _build_column_index_map(self, table: list) -> dict:
        """Dynamically infer column offsets from the first 4 rows."""
        if not table or not table[0]:
            return {}

        num_cols = len(table[0])
        header_strings = [""] * num_cols
        for row in table[:4]:
            if not row:
                continue
            for i, cell in enumerate(row):
                if i < num_cols and cell:
                    header_strings[i] += " " + str(cell)

        normalized = []
        for h in header_strings:
            s = h.lower().replace("\n", " ")
            s = re.sub(r"[^a-z0-9\s]", "", s)
            s = re.sub(r"\s+", " ", s).strip()
            normalized.append(s)

        mapping: Dict[str, Any] = {}
        for i, text in enumerate(normalized):
            if not text:
                continue
            if "generation" in text:
                mapping["generation_charge"] = i
            elif "transmission" in text:
                mapping["transmission_charge"] = i
            elif "system loss" in text:
                mapping["system_loss_charge"] = i
            elif "distribution" in text:
                mapping["distribution_charge"] = i
            elif "supply" in text:
                mapping["supply_charge"] = i
            elif "metering" in text:
                mapping["metering_charge"] = i
            elif "awat" in text:
                mapping["awat_charge"] = i
            elif "reset" in text:
                if "onetime" in text or "one time" in text:
                    mapping["one_time_reset_fee_adjustment"] = i
                elif "regulatory" in text:
                    mapping["regulatory_reset_fees_adjustment"] = i
            elif "lifeline" in text and "subsidy" in text:
                mapping["lifeline_rate_subsidy"] = i
            elif "lifeline" in text and "discount" in text:
                mapping["applicable_discount_percent"] = i
            elif "senior citizen" in text:
                mapping["senior_citizen_subsidy"] = i
            elif "current rpt" in text:
                mapping["current_rpt_charge"] = i
            elif ("ucme" in text or "uc me" in text) and "npc" in text:
                mapping["uc_me_npc_spug"] = i
            elif ("ucme" in text or "uc me" in text) and "red" in text:
                mapping["uc_me_red_ci"] = i
            elif "uc ec" in text or "ucec" in text:
                mapping["uc_ec"] = i
            elif "uc sd" in text or "ucsd" in text:
                mapping["uc_sd"] = i
            elif "fitall" in text or "fit all" in text:
                mapping["fit_all"] = i
            elif "gea" in text:
                mapping["gea_all"] = i
            else:
                skip_patterns = [
                    "summary schedule", "per kw", "per custmo", "penalty", "disc", "power factor",
                ]
                if not any(pat in text for pat in skip_patterns):
                    mapping.setdefault("unmapped_headers", []).append(f"[{i}]: '{text}'")

        return mapping

    def extract_residential_rates(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract residential rate brackets from the PDF's table structure."""
        rates: List[Dict[str, Any]] = []

        with pdfplumber.open(pdf_path) as pdf:
            stop_extracting = False
            for page in pdf.pages:
                if stop_extracting:
                    break

                tables = page.extract_tables()
                if not tables:
                    continue

                for table in tables:
                    if stop_extracting:
                        break

                    col_map = self._build_column_index_map(table)

                    for row in table:
                        if not row or not any(row):
                            continue

                        clean_row = [cell.replace("\n", " ").strip() if cell else "" for cell in row]

                        if clean_row[0].upper().startswith("GENERAL SERVICE"):
                            stop_extracting = True
                            break

                        if not re.match(r"(?:^\d+\s*TO\s*\d+\s*KWH)|(?:^OVER\s*\d+\s*KWH)", clean_row[0], re.IGNORECASE):
                            continue

                        try:
                            required_core = [
                                "generation_charge", "transmission_charge", "system_loss_charge",
                                "distribution_charge", "supply_charge", "metering_charge",
                                "lifeline_rate_subsidy", "applicable_discount_percent",
                            ]
                            missing = [k for k in required_core if k not in col_map]
                            if missing:
                                print(f"Error: Residential table is missing required header mappings: {missing}. Mapped: {col_map}")
                                continue

                            expected_optional = [
                                "awat_charge", "regulatory_reset_fees_adjustment",
                                "one_time_reset_fee_adjustment", "senior_citizen_subsidy",
                                "current_rpt_charge", "uc_me_npc_spug", "uc_me_red_ci",
                                "uc_ec", "uc_sd", "fit_all", "gea_all",
                            ]
                            missing_optional = [k for k in expected_optional if k not in col_map]
                            if missing_optional:
                                print(f"Notice: Expected optional headers not found in PDF layout: {missing_optional}")

                            if "unmapped_headers" in col_map:
                                print(f"Notice: Unrecognized/Unknown columns detected in PDF layout: {col_map['unmapped_headers']}")

                            def _val(key: str, is_percent: bool = False) -> float:
                                idx_val = col_map.get(key, -1)
                                if isinstance(idx_val, list):
                                    total = 0.0
                                    for ix in idx_val:
                                        if ix != -1 and ix < len(clean_row):
                                            v = clean_row[ix]
                                            if is_percent:
                                                v = v.replace("%", "")
                                            total += parse_negative(v)
                                    return total
                                if idx_val == -1 or idx_val >= len(clean_row):
                                    return 0.0
                                val = clean_row[idx_val]
                                if is_percent:
                                    val = val.replace("%", "")
                                return parse_negative(val)

                            gen = _val("generation_charge")
                            dist = _val("distribution_charge")
                            sys_loss = _val("system_loss_charge")

                            if gen == 0.0 or dist == 0.0 or sys_loss == 0.0:
                                print(f"Error: Extracted 0.0 for core field in {clean_row[0]}. Gen: {gen}, Dist: {dist}, SysLoss: {sys_loss}.")
                                continue

                            # Parse min/max kWh from bracket string
                            bracket_upper = clean_row[0].upper()
                            min_kwh = 0
                            max_kwh = None

                            nums = [int(n) for n in re.findall(r"\d+", bracket_upper)]
                            if "OVER" in bracket_upper and nums:
                                min_kwh = nums[0] + 1
                                max_kwh = None
                            elif len(nums) >= 2:
                                min_kwh = nums[0]
                                max_kwh = nums[1]

                            rate: Dict[str, Any] = {
                                "consumption_bracket": clean_row[0],
                                "min_kwh": min_kwh,
                                "max_kwh": max_kwh,
                                "generation_charge": gen,
                                "transmission_charge": _val("transmission_charge"),
                                "system_loss_charge": sys_loss,
                                "distribution_charge": dist,
                                "supply_charge": _val("supply_charge"),
                                "metering_charge": _val("metering_charge"),
                                "awat_charge": _val("awat_charge"),
                                "regulatory_reset_fees_adjustment": _val("regulatory_reset_fees_adjustment"),
                                "one_time_reset_fee_adjustment": _val("one_time_reset_fee_adjustment"),
                                "lifeline": {
                                    "rate_subsidy_per_kwh": _val("lifeline_rate_subsidy"),
                                    "applicable_discount_percent": _val("applicable_discount_percent", is_percent=True),
                                },
                                "senior_citizen_subsidy": _val("senior_citizen_subsidy"),
                                "current_rpt_charge": _val("current_rpt_charge"),
                                "uc_me_npc_spug": _val("uc_me_npc_spug"),
                                "uc_me_red_ci": _val("uc_me_red_ci"),
                                "uc_ec": _val("uc_ec"),
                                "uc_sd": _val("uc_sd"),
                                "fit_all": _val("fit_all"),
                                "gea_all": _val("gea_all"),
                            }
                            rates.append(rate)
                        except Exception as e:
                            print(f"Error parsing row: {clean_row}, Exception: {e}")

        if not rates:
            raise ValueError(
                "PDF table extraction failed: no residential rate brackets found. "
                "The PDF layout may have changed — check the downloaded file manually."
            )

        return rates


# ---------------------------------------------------------------------------
# High-level convenience function for the pipeline
# ---------------------------------------------------------------------------

def scrape_latest_tariff(cache_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Convenience wrapper used by ``run_pipeline.py``.

    Returns
    -------
    dict with keys:
        month_key   : str   – e.g. "2026-04"
        rates       : list  – full bracket list
        tariff_php  : float – effective per-kWh rate for the lowest bracket (0-200 kWh)
        cached      : bool  – True if result came from local cache
    """
    import tempfile

    scraper = MeralcoRateScraper()
    item = scraper.fetch_latest_rss_item()

    if item is None:
        raise RuntimeError("Could not find a 'Summary of Schedule of Rates' entry in the Meralco RSS feed.")

    month_key = item["month_key_str"] or "unknown"

    # Check cache first
    cached = MeralcoRateScraper.load_cached_rates(month_key)
    if cached:
        print(f"[meralco_scraper] Using cached rates for {month_key}")
        effective = _effective_tariff(cached)
        return {"month_key": month_key, "rates": cached, "tariff_php": effective, "cached": True}

    # Download and parse
    tmp_pdf = os.path.join(tempfile.gettempdir(), f"meralco_rates_{month_key}.pdf")
    scraper.download_pdf(item["pdf_url"], tmp_pdf)
    rates = scraper.extract_residential_rates(tmp_pdf)

    # Cache for next run
    MeralcoRateScraper.save_rates_to_cache(month_key, rates)

    effective = _effective_tariff(rates)
    return {"month_key": month_key, "rates": rates, "tariff_php": effective, "cached": False}


def _effective_tariff(rates: List[Dict[str, Any]]) -> float:
    """
    Compute a single effective PHP/kWh from the lowest bracket (0–200 kWh).

    This sums the main per-kWh components: generation + transmission +
    system loss + distribution + supply + metering + universal charges.
    """
    # Find the 0-200 bracket (or the first bracket as fallback)
    target = None
    for r in rates:
        if r.get("min_kwh", 0) == 0:
            target = r
            break
    if target is None and rates:
        target = rates[0]
    if target is None:
        return 11.5  # Hardcoded fallback

    per_kwh = (
        target.get("generation_charge", 0)
        + target.get("transmission_charge", 0)
        + target.get("system_loss_charge", 0)
        + target.get("distribution_charge", 0)
        + target.get("supply_charge", 0)
        + target.get("metering_charge", 0)
        + target.get("uc_me_npc_spug", 0)
        + target.get("uc_me_red_ci", 0)
        + target.get("uc_ec", 0)
        + target.get("fit_all", 0)
        + target.get("gea_all", 0)
    )
    return round(per_kwh, 4)
