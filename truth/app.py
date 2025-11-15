"""
Minimal correlation analysis web app.
Fetches time-series from a public API, aligns them, and computes correlations.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import requests
from datetime import datetime
from scipy.stats import pearsonr
from typing import Dict, List, Optional, Tuple
import json
import math

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuration
WB_API_BASE = "https://api.worldbank.org/v2"
WB_COUNTRY = "all"  # Use 'all' to get data for all countries
YEAR_MIN = 1960
YEAR_MAX = 2023
MAX_POINTS = 1000  # Cap returned points for performance

# Indicator Catalogue (hardcoded minimal set)
INDICATORS = {
    "NY.GDP.MKTP.CD": "GDP (current US$)",
    "SP.POP.TOTL": "Population, total",
    "SP.DYN.LE00.IN": "Life expectancy at birth, total (years)",
    "NY.GDP.PCAP.CD": "GDP per capita (current US$)",
    "EN.ATM.CO2E.PC": "CO2 emissions (metric tons per capita)",
    "SH.DYN.MORT": "Mortality rate, under-5 (per 1,000 live births)"
}


def fetch_series(indicator_id: str) -> Tuple[List[Dict], Dict]:
    """
    Fetch a time-series for a given indicator from World Bank API.
    
    Args:
        indicator_id: World Bank indicator code
        
    Returns:
        Tuple of (normalized_rows, provenance_info)
        normalized_rows: list of {entity, entity_code, year, value}
        provenance_info: {source, url, timestamp}
    """
    url = f"{WB_API_BASE}/country/{WB_COUNTRY}/indicator/{indicator_id}"
    params = {
        "format": "json",
        "per_page": 10000,
        "date": f"{YEAR_MIN}:{YEAR_MAX}"
    }
    
    timestamp = datetime.utcnow().isoformat() + "Z"
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        # Try to parse JSON, handle parse errors
        try:
            data = response.json()
        except ValueError as json_error:
            return [], {
                "source": "World Bank API",
                "url": response.url,
                "timestamp": timestamp,
                "error": f"Failed to parse JSON response: {str(json_error)}",
                "response_preview": response.text[:500] if response.text else "empty response"
            }
        
        # World Bank API returns [metadata, data_rows]
        # Handle cases where data might be empty or in unexpected format
        if not isinstance(data, list):
            return [], {
                "source": "World Bank API",
                "url": response.url,
                "timestamp": timestamp,
                "error": f"Unexpected API response format: expected list, got {type(data).__name__}",
                "response_preview": str(data)[:200] if data else "empty response"
            }
        
        if len(data) == 0:
            return [], {
                "source": "World Bank API",
                "url": response.url,
                "timestamp": timestamp,
                "error": "API returned empty response",
                "response_preview": "empty list"
            }
        
        # If only one element, it might be metadata only (no data)
        if len(data) == 1:
            return [], {
                "source": "World Bank API",
                "url": response.url,
                "timestamp": timestamp,
                "error": "API returned only metadata, no data rows",
                "response_preview": str(data[0])[:200] if data[0] else "empty metadata"
            }
        
        # Check if data[1] is None or not a list
        if data[1] is None:
            return [], {
                "source": "World Bank API",
                "url": response.url,
                "timestamp": timestamp,
                "error": "API returned null data array",
                "metadata": data[0] if len(data) > 0 else None
            }
        
        if not isinstance(data[1], list):
            return [], {
                "source": "World Bank API",
                "url": response.url,
                "timestamp": timestamp,
                "error": f"Expected data array, got {type(data[1]).__name__}",
                "response_preview": str(data[1])[:200] if data[1] else "null"
            }
        
        rows = data[1]
        
        # Check metadata for error messages
        if len(data) > 0 and isinstance(data[0], dict):
            metadata = data[0]
            # Check if API returned an error message
            if "message" in metadata:
                return [], {
                    "source": "World Bank API",
                    "url": response.url,
                    "timestamp": timestamp,
                    "error": f"API error: {metadata.get('message')}",
                    "metadata": metadata
                }
        
        # Check if rows is empty (no data found, but not an error)
        if len(rows) == 0:
            return [], {
                "source": "World Bank API",
                "url": response.url,
                "timestamp": timestamp,
                "warning": "No data rows found for this indicator",
                "metadata": data[0] if len(data) > 0 else None
            }
        
        # Normalize rows
        normalized = []
        for row in rows:
            if not isinstance(row, dict):
                continue
                
            entity = row.get("country", {}).get("value", "Unknown")
            entity_code = row.get("country", {}).get("id", "")
            year_str = row.get("date", "")
            value = row.get("value")
            
            # Skip if missing critical fields
            if not entity_code or not year_str:
                continue
            
            # Coerce year to integer
            try:
                year = int(year_str)
            except (ValueError, TypeError):
                continue
            
            # Skip if outside sane year range
            if year < YEAR_MIN or year > YEAR_MAX:
                continue
            
            # Handle null/missing values - omit them
            if value is None:
                continue
            
            # Coerce value to float
            try:
                value_float = float(value)
            except (ValueError, TypeError):
                continue
            
            # Only include finite numbers (check using math.isfinite for proper NaN/inf handling)
            if not math.isfinite(value_float):
                continue
            
            normalized.append({
                "entity": entity,
                "entity_code": entity_code,
                "year": year,
                "value": value_float
            })
        
        return normalized, {
            "source": "World Bank API",
            "url": response.url,
            "timestamp": timestamp
        }
        
    except requests.exceptions.RequestException as e:
        return [], {
            "source": "World Bank API",
            "url": url,
            "timestamp": timestamp,
            "error": str(e)
        }
    except Exception as e:
        return [], {
            "source": "World Bank API",
            "url": url,
            "timestamp": timestamp,
            "error": f"Unexpected error: {str(e)}"
        }


def align_series(
    series_x: List[Dict],
    series_y: List[Dict],
    year_from: Optional[int] = None,
    year_to: Optional[int] = None
) -> List[Dict]:
    """
    Align two series by (entity_code, year) and filter by year window.
    
    Args:
        series_x: normalized series for X indicator
        series_y: normalized series for Y indicator
        year_from: start year (inclusive), defaults to min available
        year_to: end year (inclusive), defaults to max available
        
    Returns:
        List of aligned points: {entity, entity_code, year, x, y}
    """
    # Build lookup maps: (entity_code, year) -> value
    map_x = {(r["entity_code"], r["year"]): r["value"] for r in series_x}
    map_y = {(r["entity_code"], r["year"]): r["value"] for r in series_y}
    
    # Find all matching (entity_code, year) pairs
    common_keys = set(map_x.keys()) & set(map_y.keys())
    
    # Determine year range if not provided
    if year_from is None or year_to is None:
        if common_keys:
            years = [year for _, year in common_keys]
            if year_from is None:
                year_from = min(years)
            if year_to is None:
                year_to = max(years)
        else:
            year_from = YEAR_MIN
            year_to = YEAR_MAX
    
    # Filter by year range and create aligned points
    points = []
    for entity_code, year in common_keys:
        if year < year_from or year > year_to:
            continue
        
        x_val = map_x[(entity_code, year)]
        y_val = map_y[(entity_code, year)]
        
        # Only include if both are finite numbers
        if math.isfinite(x_val) and math.isfinite(y_val):
            
            # Get entity name from either series
            entity_name = next(
                (r["entity"] for r in series_x if r["entity_code"] == entity_code and r["year"] == year),
                next(
                    (r["entity"] for r in series_y if r["entity_code"] == entity_code and r["year"] == year),
                    entity_code
                )
            )
            
            points.append({
                "entity": entity_name,
                "entity_code": entity_code,
                "year": year,
                "x": x_val,
                "y": y_val
            })
    
    # Sort by year, then entity_code for consistency
    points.sort(key=lambda p: (p["year"], p["entity_code"]))
    
    # Cap returned points
    if len(points) > MAX_POINTS:
        points = points[:MAX_POINTS]
    
    return points


def compute_correlation(points: List[Dict]) -> Dict:
    """
    Compute Pearson correlation statistics from aligned points.
    
    Args:
        points: list of {x, y, ...} aligned points
        
    Returns:
        {n, r, p} where n is count, r is correlation, p is p-value
    """
    n = len(points)
    
    if n < 3:
        return {
            "n": n,
            "r": None,
            "p": None
        }
    
    x_vals = [p["x"] for p in points]
    y_vals = [p["y"] for p in points]
    
    try:
        r, p = pearsonr(x_vals, y_vals)
        return {
            "n": n,
            "r": float(r) if r != float('inf') and r != float('-inf') else None,
            "p": float(p) if p != float('inf') and p != float('-inf') else None
        }
    except Exception:
        return {
            "n": n,
            "r": None,
            "p": None
        }


@app.route('/')
def index():
    """Serve the main UI page."""
    return send_from_directory('static', 'index.html')


@app.route('/test')
def test_page():
    """Serve the API test page."""
    return send_from_directory('static', 'test_api.html')


@app.route('/indicators', methods=['GET'])
def get_indicators():
    """
    GET /indicators
    Returns the indicator catalogue (id -> label map).
    """
    return jsonify(INDICATORS)


@app.route('/series', methods=['GET'])
def get_series():
    """
    GET /series?indicator=<id>
    Returns normalized rows for a given indicator (for debugging/inspection).
    """
    indicator = request.args.get('indicator')
    
    if not indicator:
        return jsonify({"error": "Missing 'indicator' parameter"}), 400
    
    if indicator not in INDICATORS:
        return jsonify({"error": f"Unknown indicator: {indicator}"}), 404
    
    rows, provenance = fetch_series(indicator)
    
    return jsonify({
        "indicator": indicator,
        "indicator_label": INDICATORS[indicator],
        "rows": rows,
        "rows_count": len(rows),
        "provenance": provenance
    })


@app.route('/debug/fetch', methods=['GET'])
def debug_fetch():
    """
    Debug endpoint to test API fetch directly.
    GET /debug/fetch?indicator=<id>
    """
    indicator = request.args.get('indicator', 'NY.GDP.MKTP.CD')
    
    url = f"{WB_API_BASE}/country/{WB_COUNTRY}/indicator/{indicator}"
    params = {
        "format": "json",
        "per_page": 10,  # Small sample for debugging
        "date": f"{YEAR_MIN}:{YEAR_MAX}"
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        data = response.json()
        
        return jsonify({
            "status_code": response.status_code,
            "url": response.url,
            "response_type": type(data).__name__,
            "response_length": len(data) if isinstance(data, list) else "N/A",
            "metadata": data[0] if isinstance(data, list) and len(data) > 0 else None,
            "data_sample": data[1][:3] if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list) else None,
            "data_count": len(data[1]) if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list) else 0,
            "raw_response_preview": str(data)[:1000] if data else "empty"
        })
    except Exception as e:
        return jsonify({
            "error": str(e),
            "error_type": type(e).__name__
        }), 500


@app.route('/correlate', methods=['GET'])
def correlate():
    """
    GET /correlate?x=<id1>&y=<id2>&year_from=<year>&year_to=<year>
    Returns correlation stats and aligned points.
    """
    x_id = request.args.get('x')
    y_id = request.args.get('y')
    year_from = request.args.get('year_from', type=int)
    year_to = request.args.get('year_to', type=int)
    
    # Validate inputs
    if not x_id or not y_id:
        return jsonify({"error": "Missing 'x' or 'y' parameter"}), 400
    
    if x_id not in INDICATORS or y_id not in INDICATORS:
        return jsonify({"error": "Unknown indicator ID"}), 404
    
    if x_id == y_id:
        return jsonify({"error": "X and Y indicators must be different"}), 400
    
    # Fetch both series
    series_x, prov_x = fetch_series(x_id)
    series_y, prov_y = fetch_series(y_id)
    
    # Check for errors or warnings in fetching
    if "error" in prov_x:
        error_msg = prov_x.get('error', 'Unknown error')
        error_details = prov_x.get('response_preview', '')
        return jsonify({
            "error": f"Failed to fetch X series: {error_msg}",
            "error_details": error_details,
            "provenance": {"x": prov_x, "y": prov_y}
        }), 500
    
    if "error" in prov_y:
        error_msg = prov_y.get('error', 'Unknown error')
        error_details = prov_y.get('response_preview', '')
        return jsonify({
            "error": f"Failed to fetch Y series: {error_msg}",
            "error_details": error_details,
            "provenance": {"x": prov_x, "y": prov_y}
        }), 500
    
    # Check for warnings (empty data)
    if "warning" in prov_x:
        return jsonify({
            "error": f"X series returned no data: {prov_x.get('warning')}",
            "provenance": {"x": prov_x, "y": prov_y}
        }), 404
    
    if "warning" in prov_y:
        return jsonify({
            "error": f"Y series returned no data: {prov_y.get('warning')}",
            "provenance": {"x": prov_x, "y": prov_y}
        }), 404
    
    # Align series
    points = align_series(series_x, series_y, year_from, year_to)
    
    # Compute correlation
    stats = compute_correlation(points)
    
    # Determine actual year range used
    if points:
        actual_year_from = min(p["year"] for p in points)
        actual_year_to = max(p["year"] for p in points)
    else:
        actual_year_from = year_from
        actual_year_to = year_to
    
    return jsonify({
        "x": x_id,
        "y": y_id,
        "x_label": INDICATORS[x_id],
        "y_label": INDICATORS[y_id],
        "year_from": actual_year_from,
        "year_to": actual_year_to,
        "stats": stats,
        "points": points,
        "provenance": {
            "x": prov_x,
            "y": prov_y
        }
    })


# ============================================================================
# Geospatial Visualization Routes
# ============================================================================

# Available statistics layers for US states
GEO_STATISTICS_LAYERS = {
    "population": {
        "name": "Population (2020)",
        "description": "Total population by state",
        "source": "US Census Bureau",
        "endpoint": "population"
    },
    "median_income": {
        "name": "Median Household Income",
        "description": "Median household income by state",
        "source": "US Census Bureau ACS",
        "endpoint": "income"
    },
    "education": {
        "name": "Bachelor's Degree or Higher",
        "description": "Percentage of adults with bachelor's degree or higher",
        "source": "US Census Bureau ACS",
        "endpoint": "education"
    },
    "unemployment": {
        "name": "Unemployment Rate",
        "description": "Unemployment rate by state",
        "source": "US Bureau of Labor Statistics",
        "endpoint": "unemployment"
    },
    "poverty": {
        "name": "Poverty Rate",
        "description": "Percentage of population below poverty line",
        "source": "US Census Bureau",
        "endpoint": "poverty"
    },
    "life_expectancy": {
        "name": "Life Expectancy",
        "description": "Average life expectancy at birth (years)",
        "source": "CDC National Center for Health Statistics",
        "endpoint": "life_expectancy"
    },
    "home_ownership": {
        "name": "Home Ownership Rate",
        "description": "Percentage of housing units occupied by owners",
        "source": "US Census Bureau",
        "endpoint": "home_ownership"
    }
}


def fetch_state_population() -> Dict[str, float]:
    """Fetch population data for US states (sample data for proof of concept)."""
    population_data = {
        "AL": 5024279, "AK": 733391, "AZ": 7151502, "AR": 3011524, "CA": 39538223,
        "CO": 5773714, "CT": 3605944, "DE": 989948, "FL": 21538187, "GA": 10711908,
        "HI": 1455271, "ID": 1839106, "IL": 12812508, "IN": 6785528, "IA": 3190369,
        "KS": 2937880, "KY": 4505836, "LA": 4657757, "ME": 1362359, "MD": 6177224,
        "MA": 7029917, "MI": 10037319, "MN": 5706494, "MS": 2961279, "MO": 6154913,
        "MT": 1084225, "NE": 1961504, "NV": 3104614, "NH": 1377529, "NJ": 9288994,
        "NM": 2117522, "NY": 20201249, "NC": 10439388, "ND": 779094, "OH": 11799448,
        "OK": 3959353, "OR": 4237256, "PA": 13002700, "RI": 1097379, "SC": 5118425,
        "SD": 886667, "TN": 6910840, "TX": 29145505, "UT": 3271616, "VT": 643077,
        "VA": 8631393, "WA": 7705281, "WV": 1793716, "WI": 5893718, "WY": 576851
    }
    return population_data


def fetch_state_income() -> Dict[str, float]:
    """Fetch median household income by state (sample data)."""
    income_data = {
        "AL": 52205, "AK": 75760, "AZ": 62955, "AR": 49831, "CA": 80440,
        "CO": 77464, "CT": 79406, "DE": 70726, "FL": 59920, "GA": 61980,
        "HI": 83899, "ID": 60108, "IL": 69230, "IN": 58235, "IA": 61417,
        "KS": 62120, "KY": 52375, "LA": 51571, "ME": 58722, "MD": 87244,
        "MA": 85750, "MI": 59584, "MN": 74270, "MS": 45792, "MO": 57209,
        "MT": 57769, "NE": 63229, "NV": 63190, "NH": 77601, "NJ": 85751,
        "NM": 51389, "NY": 72850, "NC": 57055, "ND": 64177, "OH": 58600,
        "OK": 54334, "OR": 67861, "PA": 63827, "RI": 71341, "SC": 56647,
        "SD": 59453, "TN": 56183, "TX": 64334, "UT": 74795, "VT": 63414,
        "VA": 76398, "WA": 79726, "WV": 48537, "WI": 63488, "WY": 65604
    }
    return income_data


def fetch_state_education() -> Dict[str, float]:
    """Fetch percentage of adults with bachelor's degree or higher by state."""
    education_data = {
        "AL": 26.1, "AK": 29.7, "AZ": 30.2, "AR": 23.9, "CA": 34.7,
        "CO": 41.2, "CT": 40.0, "DE": 32.8, "FL": 31.5, "GA": 32.3,
        "HI": 33.9, "ID": 29.0, "IL": 35.4, "IN": 27.5, "IA": 29.6,
        "KS": 33.4, "KY": 25.6, "LA": 25.6, "ME": 32.8, "MD": 40.9,
        "MA": 44.5, "MI": 30.7, "MN": 36.7, "MS": 23.2, "MO": 30.6,
        "MT": 32.8, "NE": 32.4, "NV": 25.6, "NH": 37.0, "NJ": 40.1,
        "NM": 27.9, "NY": 37.0, "NC": 32.4, "ND": 30.7, "OH": 29.5,
        "OK": 26.4, "OR": 33.9, "PA": 33.2, "RI": 35.7, "SC": 29.4,
        "SD": 29.9, "TN": 28.6, "TX": 30.9, "UT": 34.7, "VT": 38.8,
        "VA": 39.5, "WA": 36.7, "WV": 21.3, "WI": 31.2, "WY": 27.8
    }
    return education_data


def fetch_state_unemployment() -> Dict[str, float]:
    """Fetch unemployment rate by state."""
    unemployment_data = {
        "AL": 3.1, "AK": 4.4, "AZ": 4.2, "AR": 3.4, "CA": 4.8,
        "CO": 3.0, "CT": 3.6, "DE": 4.0, "FL": 2.9, "GA": 3.2,
        "HI": 3.2, "ID": 2.8, "IL": 4.5, "IN": 3.3, "IA": 2.8,
        "KS": 2.9, "KY": 3.9, "LA": 3.5, "ME": 2.8, "MD": 2.8,
        "MA": 3.1, "MI": 3.9, "MN": 2.6, "MS": 3.1, "MO": 3.0,
        "MT": 2.6, "NE": 2.2, "NV": 5.4, "NH": 2.6, "NJ": 3.8,
        "NM": 3.9, "NY": 4.1, "NC": 3.4, "ND": 2.0, "OH": 3.8,
        "OK": 3.0, "OR": 3.6, "PA": 3.4, "RI": 3.0, "SC": 3.1,
        "SD": 2.0, "TN": 3.2, "TX": 3.7, "UT": 2.6, "VT": 2.1,
        "VA": 2.8, "WA": 4.0, "WV": 4.0, "WI": 3.0, "WY": 2.8
    }
    return unemployment_data


def fetch_state_poverty() -> Dict[str, float]:
    """Fetch poverty rate by state (percentage below poverty line)."""
    # Sample poverty rate data (percentage) - inversely correlated with income
    poverty_data = {
        "AL": 15.5, "AK": 10.1, "AZ": 13.5, "AR": 16.2, "CA": 12.3,
        "CO": 9.3, "CT": 9.9, "DE": 11.3, "FL": 12.7, "GA": 13.3,
        "HI": 9.3, "ID": 11.2, "IL": 11.5, "IN": 12.1, "IA": 11.2,
        "KS": 11.4, "KY": 16.3, "LA": 19.0, "ME": 10.9, "MD": 9.0,
        "MA": 9.4, "MI": 13.0, "MN": 9.0, "MS": 19.6, "MO": 12.6,
        "MT": 12.6, "NE": 10.2, "NV": 12.5, "NH": 7.3, "NJ": 9.2,
        "NM": 18.2, "NY": 13.0, "NC": 13.6, "ND": 10.6, "OH": 13.1,
        "OK": 15.2, "OR": 11.4, "PA": 11.8, "RI": 10.8, "SC": 13.8,
        "SD": 11.9, "TN": 13.6, "TX": 13.6, "UT": 8.9, "VT": 10.2,
        "VA": 9.9, "WA": 9.8, "WV": 16.8, "WI": 10.4, "WY": 10.7
    }
    
    return poverty_data


def fetch_state_life_expectancy() -> Dict[str, float]:
    """Fetch life expectancy at birth by state (in years)."""
    # Sample life expectancy data - positively correlated with income and education
    life_expectancy_data = {
        "AL": 75.4, "AK": 78.8, "AZ": 79.6, "AR": 75.9, "CA": 81.0,
        "CO": 80.1, "CT": 80.9, "DE": 78.5, "FL": 80.0, "GA": 77.2,
        "HI": 81.0, "ID": 79.4, "IL": 79.0, "IN": 77.0, "IA": 79.4,
        "KS": 78.5, "KY": 75.5, "LA": 75.6, "ME": 78.7, "MD": 78.8,
        "MA": 80.4, "MI": 78.0, "MN": 80.9, "MS": 74.4, "MO": 77.3,
        "MT": 78.7, "NE": 79.1, "NV": 78.2, "NH": 79.8, "NJ": 80.1,
        "NM": 77.4, "NY": 80.5, "NC": 77.8, "ND": 79.8, "OH": 77.0,
        "OK": 75.8, "OR": 79.8, "PA": 78.5, "RI": 79.8, "SC": 76.5,
        "SD": 79.1, "TN": 75.6, "TX": 78.5, "UT": 80.1, "VT": 79.8,
        "VA": 79.0, "WA": 80.2, "WV": 74.5, "WI": 79.3, "WY": 78.2
    }
    
    return life_expectancy_data


def fetch_state_home_ownership() -> Dict[str, float]:
    """Fetch home ownership rate by state (percentage)."""
    # Sample home ownership rate data - correlated with income
    home_ownership_data = {
        "AL": 70.1, "AK": 64.2, "AZ": 64.9, "AR": 66.0, "CA": 55.3,
        "CO": 65.1, "CT": 66.0, "DE": 71.4, "FL": 66.1, "GA": 64.1,
        "HI": 59.0, "ID": 70.8, "IL": 66.5, "IN": 69.6, "IA": 71.6,
        "KS": 66.7, "KY": 69.0, "LA": 67.8, "ME": 72.4, "MD": 67.3,
        "MA": 62.0, "MI": 71.5, "MN": 72.1, "MS": 70.0, "MO": 68.2,
        "MT": 69.1, "NE": 67.0, "NV": 58.7, "NH": 71.3, "NJ": 64.0,
        "NM": 68.0, "NY": 54.3, "NC": 65.8, "ND": 68.1, "OH": 67.4,
        "OK": 68.1, "OR": 62.2, "PA": 70.0, "RI": 61.8, "SC": 70.6,
        "SD": 68.2, "TN": 67.4, "TX": 62.0, "UT": 71.2, "VT": 72.5,
        "VA": 67.0, "WA": 63.3, "WV": 73.4, "WI": 67.8, "WY": 70.1
    }
    
    return home_ownership_data


def fetch_geo_statistics_data(layer_id: str) -> Dict[str, float]:
    """Fetch statistics data for a given layer."""
    if layer_id == "population":
        return fetch_state_population()
    elif layer_id == "median_income":
        return fetch_state_income()
    elif layer_id == "education":
        return fetch_state_education()
    elif layer_id == "unemployment":
        return fetch_state_unemployment()
    elif layer_id == "poverty":
        return fetch_state_poverty()
    elif layer_id == "life_expectancy":
        return fetch_state_life_expectancy()
    elif layer_id == "home_ownership":
        return fetch_state_home_ownership()
    else:
        return {}


@app.route('/geo')
def geo_index():
    """Serve the geospatial visualization page."""
    return send_from_directory('static', 'geo.html')


@app.route('/api/geo/layers', methods=['GET'])
def get_geo_layers():
    """GET /api/geo/layers - Returns available statistics layers."""
    return jsonify(GEO_STATISTICS_LAYERS)


@app.route('/api/geo/data/<layer_id>', methods=['GET'])
def get_geo_layer_data(layer_id: str):
    """GET /api/geo/data/<layer_id> - Returns statistics data for a given layer."""
    if layer_id not in GEO_STATISTICS_LAYERS:
        return jsonify({"error": f"Unknown layer: {layer_id}"}), 404
    
    data = fetch_geo_statistics_data(layer_id)
    
    # Calculate min/max for normalization
    values = list(data.values())
    min_val = min(values) if values else 0
    max_val = max(values) if values else 0
    
    return jsonify({
        "layer_id": layer_id,
        "layer_name": GEO_STATISTICS_LAYERS[layer_id]["name"],
        "data": data,
        "min": min_val,
        "max": max_val,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)

