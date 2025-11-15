# Time-Series Correlation Analysis Web App

A minimal web application that fetches time-series data from a public API, aligns two series by shared keys (country + year), and computes correlation statistics with a scatter plot visualization.

## Features

- **Data Access**: Fetches time-series from World Bank API (free, no authentication required)
- **Indicator Catalogue**: 6 pre-configured indicators (GDP, Population, Life Expectancy, etc.)
- **Alignment**: Joins two series by country code and year
- **Correlation**: Computes Pearson correlation coefficient (r) and p-value
- **Visualization**: Interactive scatter plot using Chart.js
- **Provenance**: Tracks data source URLs and fetch timestamps

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to:
```
http://localhost:5000
```

## API Endpoints

### `GET /indicators`
Returns the indicator catalogue (id → label map).

**Response:**
```json
{
  "NY.GDP.MKTP.CD": "GDP (current US$)",
  "SP.POP.TOTL": "Population, total",
  ...
}
```

### `GET /series?indicator=<id>`
Returns normalized rows for a given indicator (for debugging/inspection).

**Example:**
```
GET /series?indicator=NY.GDP.MKTP.CD
```

**Response:**
```json
{
  "indicator": "NY.GDP.MKTP.CD",
  "indicator_label": "GDP (current US$)",
  "rows": [
    {
      "entity": "United States",
      "entity_code": "USA",
      "year": 2020,
      "value": 20953000000000.0
    },
    ...
  ],
  "provenance": {
    "source": "World Bank API",
    "url": "https://api.worldbank.org/v2/...",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### `GET /correlate?x=<id1>&y=<id2>&year_from=<year>&year_to=<year>`
Returns correlation statistics and aligned points.

**Parameters:**
- `x`: Indicator ID for X-axis
- `y`: Indicator ID for Y-axis
- `year_from`: Start year (optional, defaults to min available)
- `year_to`: End year (optional, defaults to max available)

**Example:**
```
GET /correlate?x=NY.GDP.MKTP.CD&y=SP.POP.TOTL&year_from=2000&year_to=2020
```

**Response:**
```json
{
  "x": "NY.GDP.MKTP.CD",
  "y": "SP.POP.TOTL",
  "x_label": "GDP (current US$)",
  "y_label": "Population, total",
  "year_from": 2000,
  "year_to": 2020,
  "stats": {
    "n": 150,
    "r": 0.8234,
    "p": 0.0001
  },
  "points": [
    {
      "entity": "United States",
      "entity_code": "USA",
      "year": 2000,
      "x": 10252300000000.0,
      "y": 282162411.0
    },
    ...
  ],
  "provenance": {
    "x": {
      "source": "World Bank API",
      "url": "https://api.worldbank.org/v2/...",
      "timestamp": "2024-01-01T12:00:00Z"
    },
    "y": {
      "source": "World Bank API",
      "url": "https://api.worldbank.org/v2/...",
      "timestamp": "2024-01-01T12:00:00Z"
    }
  }
}
```

## Available Indicators

- `NY.GDP.MKTP.CD` - GDP (current US$)
- `SP.POP.TOTL` - Population, total
- `SP.DYN.LE00.IN` - Life expectancy at birth, total (years)
- `NY.GDP.PCAP.CD` - GDP per capita (current US$)
- `EN.ATM.CO2E.PC` - CO2 emissions (metric tons per capita)
- `SH.DYN.MORT` - Mortality rate, under-5 (per 1,000 live births)

## Architecture

- **Backend**: Flask (Python) with in-memory data processing
- **Frontend**: Single-page HTML with Chart.js for visualization
- **Data Source**: World Bank API (https://api.worldbank.org)
- **Statistics**: SciPy for Pearson correlation computation

## Error Handling

- Missing or invalid indicator IDs return 404
- Same indicator for X and Y returns 400
- API fetch errors are logged in provenance and returned to user
- Correlation requires at least 3 points (n < 3 returns r = null, p = null)

## Extensibility

The code structure is designed to allow:
1. Adding more indicators from the same World Bank source
2. Adding new data sources with minimal changes to the data access layer
3. Adding caching or database storage in future versions

