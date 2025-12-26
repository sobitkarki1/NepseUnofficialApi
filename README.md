[![Status](https://github.com/basic-bgnr/NepseUnofficialApi/actions/workflows/actions.yml/badge.svg)](https://github.com/basic-bgnr/NepseUnofficialApi/actions/workflows/actions.yml)

# NepseUnofficialApi

Unofficial Python library to interface with [nepalstock.com](https://www.nepalstock.com). This library deciphers the authentication mechanism and provides a clean API to access NEPSE (Nepal Stock Exchange) data programmatically.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
  - [Initialization](#initialization)
  - [Market Status & Summary](#market-status--summary)
  - [Company & Security Information](#company--security-information)
  - [Market Indices](#market-indices)
  - [Top Performers](#top-performers)
  - [Company-Specific Data](#company-specific-data)
  - [Floorsheet Data](#floorsheet-data)
  - [Market Depth](#market-depth)
  - [Historical Data](#historical-data)
  - [Index Graphs](#index-graphs)
  - [Sub-Index Graphs](#sub-index-graphs)
- [CLI Tool](#cli-tool)
- [Example Server](#example-server)
- [API Endpoints Reference](#api-endpoints-reference)
- [Async Support](#async-support)
- [Error Handling](#error-handling)
- [Uninstallation](#uninstallation)
- [Contributing](#contributing)
- [Development History](#development-history)

---

## Features

- ✅ **Synchronous and Asynchronous API** - Use `Nepse` for blocking calls or `AsyncNepse` for async/await
- ✅ **Market Data** - Real-time market status, summary, and live market data
- ✅ **Company Information** - Complete company and security listings
- ✅ **Index Data** - NEPSE main index and all sub-indices
- ✅ **Top Performers** - Top gainers, losers, and most traded scrips
- ✅ **Floorsheet** - Complete floorsheet data with pagination support
- ✅ **Market Depth** - Order book depth for individual securities
- ✅ **Historical Data** - Price and volume history for any company
- ✅ **Graph Data** - Daily graph data for indices and securities
- ✅ **CLI Tool** - Command-line interface for common operations
- ✅ **Flask Server** - Example REST API server included

---

## Requirements

- **Python** >= 3.11
- **Dependencies**:
  - `httpx[http2]==0.27.2`
  - `pywasm==1.2.2`
  - `flask==3.0.3`
  - `tqdm==4.66.5`

---

## Installation

### Method A: Using Git + pip

```bash
git clone https://github.com/basic-bgnr/NepseUnofficialApi.git
cd NepseUnofficialApi
pip install .
```

### Method B: Direct from GitHub

```bash
pip install git+https://github.com/basic-bgnr/NepseUnofficialApi
```

---

## Quick Start

### Synchronous Usage

```python
from nepse import Nepse

# Initialize the API
nepse = Nepse()
nepse.setTLSVerification(False)  # Temporary fix for NEPSE SSL certificate issue

# Get market summary
summary = nepse.getSummary()
print(summary)

# Get company list
companies = nepse.getCompanyList()
print(f"Total companies: {len(companies)}")

# Get top gainers
gainers = nepse.getTopGainers()
for stock in gainers:
    print(f"{stock['symbol']}: +{stock['percentageChange']}%")
```

### Asynchronous Usage

```python
import asyncio
from nepse import AsyncNepse

async def main():
    # Initialize the async API
    nepse = AsyncNepse()
    nepse.setTLSVerification(False)
    
    # Get market data
    summary = await nepse.getSummary()
    companies = await nepse.getCompanyList()
    
    # Get floorsheet (much faster with async)
    floorsheet = await nepse.getFloorSheet(show_progress=True)
    print(f"Total transactions today: {len(floorsheet)}")

# Run async code
asyncio.run(main())
```

---

## API Reference

### Initialization

#### `Nepse()`
Creates a synchronous NEPSE API client.

```python
from nepse import Nepse
nepse = Nepse()
```

#### `AsyncNepse()`
Creates an asynchronous NEPSE API client.

```python
from nepse import AsyncNepse
nepse = AsyncNepse()
```

#### `setTLSVerification(flag: bool)`
Enable or disable TLS certificate verification.

```python
nepse.setTLSVerification(False)  # Disable SSL verification
```

**Note**: Currently required due to SSL certificate issues on nepalstock.com

---

### Market Status & Summary

#### `getMarketStatus()`
**Endpoint**: `/api/nots/nepse-data/market-open`

Get current market status (open/closed).

```python
status = nepse.getMarketStatus()
# Returns: {"isOpen": "OPEN"} or {"isOpen": "CLOSE"}
```

#### `isNepseOpen()`
**Endpoint**: `/api/nots/nepse-data/market-open`

Alias for `getMarketStatus()`.

```python
status = nepse.isNepseOpen()
```

#### `getSummary()`
**Endpoint**: `/api/nots/market-summary/`

Get market summary with key metrics.

```python
summary = nepse.getSummary()
# Returns list of dicts: [
#   {"detail": "Total Turnover", "value": "1234567890.50"},
#   {"detail": "Total Traded Shares", "value": "5000000"},
#   {"detail": "Total Transactions", "value": "25000"},
#   ...
# ]
```

#### `getLiveMarket()`
**Endpoint**: `/api/nots/lives-market`

Get live market data with real-time updates.

```python
live_data = nepse.getLiveMarket()
```

#### `getSupplyDemand()`
**Endpoint**: `/api/nots/nepse-data/supplydemand`

Get supply and demand statistics.

```python
supply_demand = nepse.getSupplyDemand()
```

#### `getPriceVolume()`
**Endpoint**: `/api/nots/securityDailyTradeStat/58`

Get price and volume statistics for all securities.

```python
price_volume = nepse.getPriceVolume()
# Returns array of securities with price/volume data
```

---

### Company & Security Information

#### `getCompanyList()`
**Endpoint**: `/api/nots/company/list`

Get list of all companies listed on NEPSE (including delisted, excludes promoter shares).

```python
companies = nepse.getCompanyList()
# Returns: [
#   {
#     "id": 123,
#     "symbol": "NABIL",
#     "companyName": "Nabil Bank Limited",
#     "sectorName": "Commercial Banks",
#     ...
#   },
#   ...
# ]
```

#### `getSecurityList()`
**Endpoint**: `/api/nots/security?nonDelisted=true`

Get list of all active securities (excludes delisted, includes promoter shares).

```python
securities = nepse.getSecurityList()
# Returns array of security objects
```

#### `getSectorScrips()`
Get securities grouped by sector.

```python
sectors = nepse.getSectorScrips()
# Returns: {
#   "Commercial Banks": ["NABIL", "SCB", ...],
#   "Hydro Power": ["NHPC", "UPPER", ...],
#   "Promoter Share": ["NABILP", ...],
#   ...
# }
```

#### `getCompanyIDKeyMap(force_update=False)`
Get mapping of company symbols to their IDs.

```python
id_map = nepse.getCompanyIDKeyMap()
# Returns: {"NABIL": 123, "SCB": 456, ...}
```

#### `getSecurityIDKeyMap(force_update=False)`
Get mapping of security symbols to their IDs.

```python
id_map = nepse.getSecurityIDKeyMap()
# Returns: {"NABIL": 123, "NABILP": 789, ...}
```

---

### Market Indices

#### `getNepseIndex()`
**Endpoint**: `/api/nots/nepse-index`

Get NEPSE main index values.

```python
index = nepse.getNepseIndex()
# Returns: [
#   {
#     "index": "NEPSE Index",
#     "currentValue": 2650.50,
#     "percentageChange": 1.25,
#     "pointChange": 32.75,
#     ...
#   },
#   ...
# ]
```

#### `getNepseSubIndices()`
**Endpoint**: `/api/nots`

Get all sub-indices (sector-wise indices).

```python
subindices = nepse.getNepseSubIndices()
# Returns array of all sector indices:
# - Banking SubIndex
# - Development Bank Index
# - Finance Index
# - Hotel And Tourism Index
# - HydroPower Index
# - Investment Index
# - Life Insurance
# - Manufacturing And Processing
# - Microfinance Index
# - Mutual Fund
# - Non Life Insurance
# - Others Index
# - Trading Index
```

---

### Top Performers

#### `getTopGainers()`
**Endpoint**: `/api/nots/top-ten/top-gainer`

Get top gaining stocks.

```python
gainers = nepse.getTopGainers()
# Returns: [
#   {
#     "symbol": "XYZ",
#     "ltp": 450.00,
#     "pointChange": 45.00,
#     "percentageChange": 11.11,
#     ...
#   },
#   ...
# ]
```

#### `getTopLosers()`
**Endpoint**: `/api/nots/top-ten/top-loser`

Get top losing stocks.

```python
losers = nepse.getTopLosers()
# Returns array similar to getTopGainers()
```

#### `getTopTenTradeScrips()`
**Endpoint**: `/api/nots/top-ten/trade`

Get top 10 most traded stocks by volume.

```python
top_trade = nepse.getTopTenTradeScrips()
# Returns: [
#   {
#     "symbol": "ABC",
#     "shareTraded": 500000,
#     ...
#   },
#   ...
# ]
```

#### `getTopTenTransactionScrips()`
**Endpoint**: `/api/nots/top-ten/transaction`

Get top 10 stocks by number of transactions.

```python
top_txn = nepse.getTopTenTransactionScrips()
# Returns: [
#   {
#     "symbol": "ABC",
#     "totalTrades": 2500,
#     ...
#   },
#   ...
# ]
```

#### `getTopTenTurnoverScrips()`
**Endpoint**: `/api/nots/top-ten/turnover`

Get top 10 stocks by turnover value.

```python
top_turnover = nepse.getTopTenTurnoverScrips()
# Returns: [
#   {
#     "symbol": "ABC",
#     "turnover": 50000000.00,
#     ...
#   },
#   ...
# ]
```

---

### Company-Specific Data

#### `getCompanyDetails(symbol: str)`
**Endpoint**: `/api/nots/security/{id}`

Get detailed information about a specific company.

```python
details = nepse.getCompanyDetails("NABIL")
# Returns comprehensive company data including:
# - Basic info (name, symbol, sector)
# - Price data (LTP, high, low, open, close)
# - Volume data
# - Market cap
# - And more...
```

#### `getDailyScripPriceGraph(symbol: str)`
**Endpoint**: `/api/nots/market/graphdata/daily/{id}`

Get intraday price graph data for a symbol.

```python
graph_data = nepse.getDailyScripPriceGraph("NABIL")
# Returns array of price points for the day
```

#### `getCompanyPriceVolumeHistory(symbol: str, start_date=None, end_date=None)`
**Endpoint**: `/api/nots/market/history/security/{id}`

Get historical price and volume data.

```python
from datetime import date, timedelta

# Last 30 days
end = date.today()
start = end - timedelta(days=30)
history = nepse.getCompanyPriceVolumeHistory("NABIL", start_date=start, end_date=end)

# Last 365 days (default if dates not provided)
history = nepse.getCompanyPriceVolumeHistory("NABIL")

# Returns: {
#   "content": [
#     {
#       "businessDate": "2024-12-23",
#       "openPrice": 1000.0,
#       "highPrice": 1050.0,
#       "lowPrice": 990.0,
#       "closePrice": 1030.0,
#       "totalTradedQuantity": 5000,
#       ...
#     },
#     ...
#   ]
# }
```

---

### Floorsheet Data

#### `getFloorSheet(show_progress=False)`
**Endpoint**: `/api/nots/nepse-data/floorsheet`

Get complete floorsheet (all transactions) for the current trading day.

```python
# Synchronous
floorsheet = nepse.getFloorSheet(show_progress=True)

# Asynchronous (much faster!)
floorsheet = await async_nepse.getFloorSheet(show_progress=True)

# Returns: [
#   {
#     "contractId": 12345,
#     "stockSymbol": "NABIL",
#     "buyerMemberId": 10,
#     "sellerMemberId": 25,
#     "contractQuantity": 100,
#     "contractRate": 1000.0,
#     "contractAmount": 100000.0,
#     "businessDate": "2024-12-24",
#     "tradeTime": "11:30:00",
#     ...
#   },
#   ...
# ]
```

**Performance Note**: Async version is significantly faster (5-10 seconds vs several minutes for large datasets).

#### `getFloorSheetOf(symbol: str, business_date=None)`
**Endpoint**: `/api/nots/security/floorsheet/{id}`

Get floorsheet for a specific symbol.

```python
# Today's floorsheet for NABIL
floorsheet = nepse.getFloorSheetOf("NABIL")

# Specific date (YYYY-MM-DD string or date object)
from datetime import date
floorsheet = nepse.getFloorSheetOf("NABIL", business_date="2024-12-20")
floorsheet = nepse.getFloorSheetOf("NABIL", business_date=date(2024, 12, 20))

# Returns array of transactions for that symbol
```

---

### Market Depth

#### `getSymbolMarketDepth(symbol: str)`
**Endpoint**: `/api/nots/nepse-data/marketdepth/{id}/`

Get order book depth (buy/sell orders) for a security.

```python
depth = nepse.getSymbolMarketDepth("NABIL")
# Returns: {
#   "buyDepth": [
#     {"price": 999.0, "quantity": 500},
#     {"price": 998.0, "quantity": 1000},
#     ...
#   ],
#   "sellDepth": [
#     {"price": 1001.0, "quantity": 300},
#     {"price": 1002.0, "quantity": 800},
#     ...
#   ],
#   ...
# }
```

---

### Historical Data

#### `getPriceVolumeHistory(business_date=None)`
**Endpoint**: `/api/nots/nepse-data/today-price`

Get price and volume history for all securities on a specific date.

```python
# Today's data
data = nepse.getPriceVolumeHistory()

# Specific date
data = nepse.getPriceVolumeHistory(business_date="2024-12-20")
```

---

### Index Graphs

#### `getDailyNepseIndexGraph()`
**Endpoint**: `/api/nots/graph/index/58`

Get daily graph data for NEPSE main index.

```python
graph = nepse.getDailyNepseIndexGraph()
```

#### `getDailySensitiveIndexGraph()`
**Endpoint**: `/api/nots/graph/index/57`

Get sensitive index graph data.

```python
graph = nepse.getDailySensitiveIndexGraph()
```

#### `getDailyFloatIndexGraph()`
**Endpoint**: `/api/nots/graph/index/62`

Get float index graph data.

```python
graph = nepse.getDailyFloatIndexGraph()
```

#### `getDailySensitiveFloatIndexGraph()`
**Endpoint**: `/api/nots/graph/index/63`

Get sensitive float index graph data.

```python
graph = nepse.getDailySensitiveFloatIndexGraph()
```

---

### Sub-Index Graphs

All methods return daily graph data for respective sub-indices:

```python
# Banking Sub-Index
nepse.getDailyBankSubindexGraph()  # Endpoint: /api/nots/graph/index/51

# Development Bank Sub-Index
nepse.getDailyDevelopmentBankSubindexGraph()  # /api/nots/graph/index/55

# Finance Sub-Index
nepse.getDailyFinanceSubindexGraph()  # /api/nots/graph/index/60

# Hotel & Tourism Sub-Index
nepse.getDailyHotelTourismSubindexGraph()  # /api/nots/graph/index/52

# Hydro Sub-Index
nepse.getDailyHydroSubindexGraph()  # /api/nots/graph/index/54

# Investment Sub-Index
nepse.getDailyInvestmentSubindexGraph()  # /api/nots/graph/index/67

# Life Insurance Sub-Index
nepse.getDailyLifeInsuranceSubindexGraph()  # /api/nots/graph/index/65

# Manufacturing Sub-Index
nepse.getDailyManufacturingSubindexGraph()  # /api/nots/graph/index/56

# Microfinance Sub-Index
nepse.getDailyMicrofinanceSubindexGraph()  # /api/nots/graph/index/64

# Mutual Fund Sub-Index
nepse.getDailyMutualfundSubindexGraph()  # /api/nots/graph/index/66

# Non-Life Insurance Sub-Index
nepse.getDailyNonLifeInsuranceSubindexGraph()  # /api/nots/graph/index/59

# Others Sub-Index
nepse.getDailyOthersSubindexGraph()  # /api/nots/graph/index/53

# Trading Sub-Index
nepse.getDailyTradingSubindexGraph()  # /api/nots/graph/index/61
```

---

## CLI Tool

After installation, the `nepse-cli` command-line tool becomes available.

### Usage

```bash
nepse-cli --help
```

### Available Commands

#### Show Version

```bash
nepse-cli --version
```

#### Start Flask Server

```bash
nepse-cli --start-server
```

Starts a local REST API server at `http://0.0.0.0:8000` with web interface and JSON endpoints.

#### Show Market Status

```bash
nepse-cli --show-status
```

Outputs market status to stdout in JSON format.

#### Download Floorsheet

```bash
# Download to JSON file
nepse-cli --get-floorsheet --output-file floor.json

# Download to CSV file
nepse-cli --get-floorsheet --to-csv --output-file floor.csv

# Show to stdout without file
nepse-cli --get-floorsheet

# Hide progress bar
nepse-cli --get-floorsheet --hide-progressbar --output-file floor.json
```

### CLI Options

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help message |
| `-v`, `--version` | Display version info |
| `--start-server` | Start local server at `0.0.0.0:8000` |
| `--show-status` | Dump NEPSE status to stdout |
| `--get-floorsheet` | Dump floorsheet to stdout |
| `--output-file FILE` | Set output file for dumping content |
| `--to-csv` | Convert output from JSON to CSV |
| `--hide-progressbar` | Hide progress bar |

---

## Example Server

The package includes a complete Flask server example demonstrating all features.

### Running the Server

```bash
cd example
python NepseServer.py
```

Or using the CLI:

```bash
nepse-cli --start-server
```

### Server Endpoints

The server runs at `http://localhost:8000` with the following endpoints:

| Endpoint | Description |
|----------|-------------|
| `/` | Home page with links to all endpoints |
| `/Summary` | Market summary |
| `/NepseIndex` | NEPSE main index |
| `/NepseSubIndices` | All sub-indices |
| `/PriceVolume` | Price and volume for all securities |
| `/SupplyDemand` | Supply and demand data |
| `/TopGainers` | Top gaining stocks |
| `/TopLosers` | Top losing stocks |
| `/TopTenTradeScrips` | Top 10 by trade volume |
| `/TopTenTransactionScrips` | Top 10 by transactions |
| `/TopTenTurnoverScrips` | Top 10 by turnover |
| `/IsNepseOpen` | Market status |
| `/DailyNepseIndexGraph` | NEPSE index graph data |
| `/DailyScripPriceGraph` | List of all symbols |
| `/DailyScripPriceGraph/<symbol>` | Daily price graph for symbol |
| `/CompanyList` | All companies |
| `/SecurityList` | All securities |
| `/LiveMarket` | Live market data |
| `/MarketDepth` | List of all symbols |
| `/MarketDepth/<symbol>` | Market depth for symbol |
| `/TradeTurnoverTransactionSubindices` | Aggregated sector data |

### Example API Call

```bash
# Get market summary
curl http://localhost:8000/Summary

# Get top gainers
curl http://localhost:8000/TopGainers

# Get specific stock data
curl http://localhost:8000/DailyScripPriceGraph/NABIL

# Get market depth
curl http://localhost:8000/MarketDepth/NABIL
```

---

## API Endpoints Reference

Complete list of NEPSE API endpoints used by this library:

| Endpoint | Description |
|----------|-------------|
| `/api/nots/nepse-data/market-open` | Market status |
| `/api/nots/market-summary/` | Market summary |
| `/api/nots/securityDailyTradeStat/58` | Price/volume stats |
| `/api/nots/nepse-data/supplydemand` | Supply/demand |
| `/api/nots/top-ten/top-gainer` | Top gainers |
| `/api/nots/top-ten/top-loser` | Top losers |
| `/api/nots/top-ten/trade` | Top by trade volume |
| `/api/nots/top-ten/transaction` | Top by transactions |
| `/api/nots/top-ten/turnover` | Top by turnover |
| `/api/nots/nepse-index` | NEPSE index |
| `/api/nots` | Sub-indices |
| `/api/nots/company/list` | Company list |
| `/api/nots/security?nonDelisted=true` | Security list |
| `/api/nots/lives-market` | Live market |
| `/api/nots/nepse-data/today-price` | Today's prices |
| `/api/nots/nepse-data/floorsheet` | Floorsheet |
| `/api/nots/security/{id}` | Company details |
| `/api/nots/security/floorsheet/{id}` | Symbol floorsheet |
| `/api/nots/market/graphdata/daily/{id}` | Daily price graph |
| `/api/nots/market/history/security/{id}` | Price history |
| `/api/nots/nepse-data/marketdepth/{id}/` | Market depth |
| `/api/nots/graph/index/{indexId}` | Index graphs (51-67) |

---

## Async Support

The library provides full async support through the `AsyncNepse` class, which is significantly faster for operations involving multiple API calls.

### When to Use Async

- **Floorsheet downloads**: 5-10 seconds vs several minutes
- **Multiple concurrent requests**: Fetch multiple company data simultaneously
- **Large data operations**: Any operation that makes many API calls

### Async Example

```python
import asyncio
from nepse import AsyncNepse
from datetime import date, timedelta

async def get_multiple_companies():
    nepse = AsyncNepse()
    nepse.setTLSVerification(False)
    
    symbols = ["NABIL", "SCB", "NICA", "EBL", "NIB"]
    
    # Fetch all company details concurrently
    tasks = [nepse.getCompanyDetails(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks)
    
    for symbol, data in zip(symbols, results):
        print(f"{symbol}: LTP = {data.get('lastTradedPrice', 'N/A')}")

asyncio.run(get_multiple_companies())
```

---

## Error Handling

The library includes custom exceptions for better error handling:

```python
from nepse import Nepse
from nepse.Errors import (
    NepseTokenExpired,
    NepseInvalidClientRequest,
    NepseInvalidServerResponse,
    NepseNetworkError
)

nepse = Nepse()
nepse.setTLSVerification(False)

try:
    data = nepse.getCompanyDetails("INVALID_SYMBOL")
except NepseInvalidClientRequest:
    print("Invalid request - check symbol name")
except NepseInvalidServerResponse:
    print("Server error - try again later")
except NepseNetworkError:
    print("Network error - check connection")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Exception Types

- `NepseTokenExpired`: Authentication token expired (auto-retry handled internally)
- `NepseInvalidClientRequest`: Invalid request (HTTP 400)
- `NepseInvalidServerResponse`: Server error (HTTP 502)
- `NepseNetworkError`: Network/connection error

---

## Uninstallation

```bash
pip uninstall nepse
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Clone the repository
2. Install in development mode: `pip install -e .`
3. Make your changes
4. Test thoroughly
5. Submit a PR

---

## Development History

### Recent Updates

1. **[Dec 13, 2024]**
   * PR [#39](https://github.com/basic-bgnr/NepseUnofficialApi/pull/39) ([@surajrimal07](https://github.com/surajrimal07)) merged to master
   * Patch fix for async bug

2. **[Dec 11, 2024]**
   * PR [#24](https://github.com/basic-bgnr/NepseUnofficialApi/pull/24) ([@iamaakashbasnet](https://github.com/iamaakashbasnet)) merged to master
   * Added market depth functionality - `getSymbolMarketDepth()`
   * Minimum Python version upgraded from 3.10 to 3.11 to support `pywasm` version upgrade
   * Added hyperlinked routes for scrips in `nepse-cli --start-server` feature

3. **[Sep 23, 2024]**
   * Floorsheet downloads now asynchronous in `nepse-cli`
   * Massive performance improvement: entire floorsheet downloads in ~5-10 seconds
   * Minimum Python version upgraded from 3.8 to 3.10

4. **[Jun 24, 2024]**
   * Added live-market API endpoint to `nepse-cli --start-server`

5. **[Jun 23, 2024]**
   * Merged Async Feature to master branch
   * PR [#11](https://github.com/basic-bgnr/NepseUnofficialApi/pull/12) ([@iamaakashbasnet](https://github.com/iamaakashbasnet)) merged
   * Enabled access to live-market API endpoint

6. **[Apr 19, 2024]**
   * Added Async support through `AsyncNepse` class

7. **[Apr 14, 2024]**
   * Added `--version` flag to CLI

8. **[Apr 11, 2024]**
   * Added `--to-csv` flag for CSV export
   * Fixed bug with empty arguments to nepse-cli

9. **[Apr 10, 2024]**
   * Initial CLI tool implementation
   * Added floorsheet download functionality

10. **[Mar 23, 2024]**
    * Added setup.py to ease installation process

11. **[Oct 20, 2023]**
    * Moved api_endpoints, headers, and dummy_data to loadable JSON files

12. **[Oct 10, 2023]**
    * Module restructuring (files and folders)

13. **[Sep 24, 2023]**
    * Fixed SSL CERTIFICATE_VERIFY_FAILED error
    * Branch `15_feb_2023` merged with master

14. **[Feb 15, 2023]**
    * Initial adjustments for NEPSE API changes

---

## License

This project is unofficial and not affiliated with Nepal Stock Exchange Ltd. Use at your own risk.

---

## Acknowledgments

- [@surajrimal07](https://github.com/surajrimal07) - Async bug fix
- [@iamaakashbasnet](https://github.com/iamaakashbasnet) - Market depth and live market features
- [@Prabesh01](https://github.com/Prabesh01) - SSL error fix contribution
- All contributors to the project

---

## Support

For issues, questions, or contributions:
- **GitHub Issues**: [https://github.com/basic-bgnr/NepseUnofficialApi/issues](https://github.com/basic-bgnr/NepseUnofficialApi/issues)
- **GitHub Repository**: [https://github.com/basic-bgnr/NepseUnofficialApi](https://github.com/basic-bgnr/NepseUnofficialApi)

---

## Notes

### SSL Certificate Issue

The `setTLSVerification(False)` call is currently required due to SSL certificate issues on nepalstock.com. This is a temporary workaround until NEPSE resolves their SSL configuration.

**Alternative Solution**: If you want to properly fix the SSL issue on Linux, follow these steps:

1. Find out the SSL [certificate details of NEPSE](https://www.ssllabs.com/ssltest/analyze.html?d=nepalstock.com.np)
2. Copy the .pem file from SSLLabs and save it to `/usr/local/share/ca-certificates/`
3. Run `sudo update-ca-certificates` to include the CA details

The issue is due to incomplete certificate chain on NEPSE's side.

### Performance Tips

1. **Use AsyncNepse for large operations**: Floorsheet downloads and bulk data fetching are significantly faster
2. **Cache company/security lists**: These don't change frequently, cache them instead of fetching repeatedly
3. **Use pagination wisely**: The floorsheet download automatically handles pagination
4. **Rate limiting**: Be respectful of the NEPSE servers - avoid making excessive requests

### Common Use Cases

#### Example 1: Daily Stock Scanner

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

# Get all gainers above 5%
gainers = nepse.getTopGainers()
significant_gainers = [s for s in gainers if s['percentageChange'] > 5]

print("Significant Gainers Today:")
for stock in significant_gainers:
    print(f"{stock['symbol']}: {stock['ltp']} (+{stock['percentageChange']}%)")
```

#### Example 2: Sector Analysis

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

# Get all sectors and their scrips
sectors = nepse.getSectorScrips()

# Get market data
price_volume = {s['symbol']: s for s in nepse.getPriceVolume()}

# Analyze each sector
for sector, symbols in sectors.items():
    total_turnover = sum(
        price_volume.get(s, {}).get('totalTurnover', 0) 
        for s in symbols
    )
    print(f"{sector}: Rs. {total_turnover:,.2f}")
```

#### Example 3: Download Historical Data

```python
from nepse import Nepse
from datetime import date, timedelta
import json

nepse = Nepse()
nepse.setTLSVerification(False)

# Get 1 year of data
symbol = "NABIL"
end = date.today()
start = end - timedelta(days=365)

history = nepse.getCompanyPriceVolumeHistory(symbol, start, end)

# Save to file
with open(f"{symbol}_history.json", "w") as f:
    json.dump(history, f, indent=2)

print(f"Downloaded {len(history['content'])} days of data for {symbol}")
```

#### Example 4: Real-time Monitoring

```python
import asyncio
from nepse import AsyncNepse

async def monitor_market():
    nepse = AsyncNepse()
    nepse.setTLSVerification(False)
    
    while True:
        # Get live market data
        live = await nepse.getLiveMarket()
        status = await nepse.getMarketStatus()
        
        print(f"Market Status: {status['isOpen']}")
        print(f"Live Data: {len(live)} securities")
        
        # Wait 30 seconds before next check
        await asyncio.sleep(30)
        
        # Break if market closed
        if status['isOpen'] == 'CLOSE':
            break

# Run monitoring
asyncio.run(monitor_market())
```

---

**Made with ❤️ for the Nepali Stock Market Community**
