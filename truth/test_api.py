"""
Simple script to test World Bank API connectivity and data fetching.
"""

import requests
import json
from datetime import datetime

# World Bank API configuration
WB_API_BASE = "https://api.worldbank.org/v2"
INDICATOR = "NY.GDP.MKTP.CD"  # GDP (current US$)
COUNTRY = "all"

def test_api_connection():
    """Test basic API connection and fetch sample data."""
    
    print("=" * 60)
    print("Testing World Bank API Connection")
    print("=" * 60)
    print()
    
    # Build URL
    url = f"{WB_API_BASE}/country/{COUNTRY}/indicator/{INDICATOR}"
    params = {
        "format": "json",
        "per_page": 10,  # Just get 10 records for testing
        "date": "2020:2020"  # Single year for simplicity
    }
    
    print(f"URL: {url}")
    print(f"Parameters: {params}")
    print()
    
    try:
        print("Making API request...")
        response = requests.get(url, params=params, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response URL: {response.url}")
        print()
        
        if response.status_code != 200:
            print(f"ERROR: Received status code {response.status_code}")
            print(f"Response text: {response.text[:500]}")
            return False
        
        print("Parsing JSON response...")
        data = response.json()
        
        print(f"Response type: {type(data).__name__}")
        print(f"Response length: {len(data) if isinstance(data, list) else 'N/A'}")
        print()
        
        # Check structure
        if not isinstance(data, list):
            print(f"ERROR: Expected list, got {type(data).__name__}")
            print(f"Response: {str(data)[:500]}")
            return False
        
        if len(data) == 0:
            print("ERROR: Empty response")
            return False
        
        # Display metadata
        if len(data) > 0:
            metadata = data[0]
            print("Metadata:")
            print(json.dumps(metadata, indent=2))
            print()
        
        # Display sample data
        if len(data) > 1:
            rows = data[1]
            print(f"Data rows count: {len(rows) if isinstance(rows, list) else 'N/A'}")
            print()
            
            if isinstance(rows, list) and len(rows) > 0:
                print("Sample data (first 5 rows):")
                print("-" * 60)
                
                for i, row in enumerate(rows[:5], 1):
                    print(f"\nRow {i}:")
                    print(f"  Country: {row.get('country', {}).get('value', 'N/A')}")
                    print(f"  Country Code: {row.get('country', {}).get('id', 'N/A')}")
                    print(f"  Date: {row.get('date', 'N/A')}")
                    print(f"  Value: {row.get('value', 'N/A')}")
                    print(f"  Indicator: {row.get('indicator', {}).get('value', 'N/A')}")
                
                print()
                print("=" * 60)
                print("SUCCESS: API connection working!")
                print("=" * 60)
                return True
            else:
                print("WARNING: No data rows found")
                return False
        else:
            print("ERROR: Response has metadata but no data array")
            return False
            
    except requests.exceptions.Timeout:
        print("ERROR: Request timed out")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"ERROR: Connection error - {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Request failed - {e}")
        return False
    except ValueError as e:
        print(f"ERROR: JSON parsing failed - {e}")
        print(f"Response text (first 500 chars): {response.text[:500]}")
        return False
    except Exception as e:
        print(f"ERROR: Unexpected error - {type(e).__name__}: {e}")
        return False


def test_multiple_indicators():
    """Test fetching multiple indicators."""
    
    print("\n" + "=" * 60)
    print("Testing Multiple Indicators")
    print("=" * 60)
    print()
    
    indicators = {
        "NY.GDP.MKTP.CD": "GDP (current US$)",
        "SP.POP.TOTL": "Population, total",
        "SP.DYN.LE00.IN": "Life expectancy at birth"
    }
    
    results = {}
    
    for indicator_id, indicator_name in indicators.items():
        print(f"Testing: {indicator_name} ({indicator_id})")
        
        url = f"{WB_API_BASE}/country/USA/indicator/{indicator_id}"
        params = {
            "format": "json",
            "per_page": 5,
            "date": "2020:2020"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 1:
                    rows = data[1] if isinstance(data[1], list) else []
                    results[indicator_id] = {
                        "status": "SUCCESS",
                        "rows": len(rows),
                        "sample_value": rows[0].get('value') if len(rows) > 0 else None
                    }
                    print(f"  [OK] Success: {len(rows)} rows")
                else:
                    results[indicator_id] = {"status": "NO_DATA"}
                    print(f"  [X] No data")
            else:
                results[indicator_id] = {"status": f"HTTP_{response.status_code}"}
                print(f"  [X] HTTP {response.status_code}")
        except Exception as e:
            results[indicator_id] = {"status": "ERROR", "error": str(e)}
            print(f"  [X] Error: {e}")
        
        print()
    
    print("Summary:")
    print(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    # Test basic connection
    success = test_api_connection()
    
    if success:
        # Test multiple indicators
        test_multiple_indicators()
    
    print(f"\nTest completed at: {datetime.now().isoformat()}")

