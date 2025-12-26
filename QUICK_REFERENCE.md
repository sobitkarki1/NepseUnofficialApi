# NEPSE API Quick Reference

Quick reference guide for NepseUnofficialApi library.

## Installation

```bash
pip install git+https://github.com/basic-bgnr/NepseUnofficialApi
```

## Basic Setup

```python
from nepse import Nepse
nepse = Nepse()
nepse.setTLSVerification(False)  # Required due to SSL issues
```

## Quick API Methods Reference

### Market Overview
| Method | Returns | Description |
|--------|---------|-------------|
| `getMarketStatus()` | dict | Market open/close status |
| `getSummary()` | list | Market summary statistics |
| `getLiveMarket()` | list | Live market data |
| `getPriceVolume()` | list | Price/volume for all securities |
| `getSupplyDemand()` | dict | Supply/demand statistics |

### Company & Security Data
| Method | Returns | Description |
|--------|---------|-------------|
| `getCompanyList()` | list | All listed companies |
| `getSecurityList()` | list | All active securities |
| `getSectorScrips()` | dict | Securities grouped by sector |
| `getCompanyDetails(symbol)` | dict | Detailed company info |
| `getSymbolMarketDepth(symbol)` | dict | Order book depth |

### Indices
| Method | Returns | Description |
|--------|---------|-------------|
| `getNepseIndex()` | list | NEPSE main index |
| `getNepseSubIndices()` | list | All sector indices |
| `getDailyNepseIndexGraph()` | list | NEPSE index graph data |

### Top Performers
| Method | Returns | Description |
|--------|---------|-------------|
| `getTopGainers()` | list | Top gaining stocks |
| `getTopLosers()` | list | Top losing stocks |
| `getTopTenTradeScrips()` | list | Top by trade volume |
| `getTopTenTransactionScrips()` | list | Top by transactions |
| `getTopTenTurnoverScrips()` | list | Top by turnover value |

### Historical Data
| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `getCompanyPriceVolumeHistory()` | symbol, start_date, end_date | dict | Historical prices |
| `getDailyScripPriceGraph()` | symbol | list | Intraday price graph |
| `getFloorSheet()` | show_progress | list | Full day's transactions |
| `getFloorSheetOf()` | symbol, business_date | list | Symbol's transactions |

## CLI Commands

```bash
# Show version
nepse-cli --version

# Start Flask server
nepse-cli --start-server

# Get market status
nepse-cli --show-status

# Download floorsheet to JSON
nepse-cli --get-floorsheet --output-file floor.json

# Download floorsheet to CSV
nepse-cli --get-floorsheet --to-csv --output-file floor.csv
```

## Async Usage

```python
import asyncio
from nepse import AsyncNepse

async def main():
    nepse = AsyncNepse()
    nepse.setTLSVerification(False)
    
    # Use await with any method
    data = await nepse.getCompanyList()
    floorsheet = await nepse.getFloorSheet(show_progress=True)

asyncio.run(main())
```

## Common Code Snippets

### Get Top Gainers Over 5%
```python
gainers = nepse.getTopGainers()
big_gainers = [s for s in gainers if s['percentageChange'] > 5]
for stock in big_gainers:
    print(f"{stock['symbol']}: +{stock['percentageChange']}%")
```

### Get Company Details
```python
details = nepse.getCompanyDetails("NABIL")
print(f"LTP: {details['lastTradedPrice']}")
print(f"Volume: {details['totalTradedQuantity']}")
```

### Download Historical Data
```python
from datetime import date, timedelta

end = date.today()
start = end - timedelta(days=30)
history = nepse.getCompanyPriceVolumeHistory("NABIL", start, end)
```

### Check Market Status
```python
status = nepse.getMarketStatus()
if status['isOpen'] == 'OPEN':
    print("Market is open!")
```

### Get Sector-wise Data
```python
sectors = nepse.getSectorScrips()
for sector, symbols in sectors.items():
    print(f"{sector}: {len(symbols)} companies")
```

## Error Handling

```python
from nepse.Errors import NepseInvalidClientRequest, NepseNetworkError

try:
    data = nepse.getCompanyDetails("SYMBOL")
except NepseInvalidClientRequest:
    print("Invalid symbol or request")
except NepseNetworkError:
    print("Network error occurred")
```

## Server Endpoints (when using --start-server)

Visit `http://localhost:8000/` to see all endpoints, including:

- `/Summary` - Market summary
- `/TopGainers` - Top gaining stocks
- `/TopLosers` - Top losing stocks
- `/CompanyList` - All companies
- `/LiveMarket` - Live market data
- `/DailyScripPriceGraph/<symbol>` - Symbol price graph
- `/MarketDepth/<symbol>` - Order book for symbol

## Tips

1. **Use Async for Speed**: FloorSheet downloads are 10x faster with `AsyncNepse`
2. **Cache Lists**: Company/security lists change rarely - cache them
3. **Symbol Case**: All symbols are auto-converted to uppercase
4. **Date Format**: Use `YYYY-MM-DD` string or Python `date` objects

For complete documentation, see [README.md](README.md)
