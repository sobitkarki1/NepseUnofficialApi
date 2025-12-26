# NEPSE API Usage Examples

Comprehensive examples for using the NepseUnofficialApi library.

## Table of Contents

- [Basic Setup](#basic-setup)
- [Market Data Examples](#market-data-examples)
- [Company Information Examples](#company-information-examples)
- [Analysis Examples](#analysis-examples)
- [Async Examples](#async-examples)
- [Data Export Examples](#data-export-examples)
- [Advanced Examples](#advanced-examples)

---

## Basic Setup

```python
from nepse import Nepse

# Initialize
nepse = Nepse()
nepse.setTLSVerification(False)  # Required for SSL issue workaround
```

---

## Market Data Examples

### Example 1: Check Market Status

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

status = nepse.getMarketStatus()
if status['isOpen'] == 'OPEN':
    print("✓ Market is currently OPEN")
    
    # Get current summary
    summary = nepse.getSummary()
    for item in summary:
        print(f"{item['detail']}: {item['value']}")
else:
    print("✗ Market is CLOSED")
```

### Example 2: Get Today's Top Performers

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

print("=" * 60)
print("TOP 10 GAINERS")
print("=" * 60)
gainers = nepse.getTopGainers()
for i, stock in enumerate(gainers, 1):
    print(f"{i:2d}. {stock['symbol']:10s} | "
          f"LTP: Rs.{stock['ltp']:8.2f} | "
          f"Change: +{stock['percentageChange']:6.2f}%")

print("\n" + "=" * 60)
print("TOP 10 LOSERS")
print("=" * 60)
losers = nepse.getTopLosers()
for i, stock in enumerate(losers, 1):
    print(f"{i:2d}. {stock['symbol']:10s} | "
          f"LTP: Rs.{stock['ltp']:8.2f} | "
          f"Change: {stock['percentageChange']:6.2f}%")
```

### Example 3: Most Active Stocks

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

print("MOST ACTIVE STOCKS (By Turnover)")
print("-" * 70)
top_turnover = nepse.getTopTenTurnoverScrips()
for stock in top_turnover:
    turnover = stock.get('turnover', 0)
    print(f"{stock['symbol']:10s} | Turnover: Rs.{turnover:15,.2f}")

print("\nMOST TRADED STOCKS (By Volume)")
print("-" * 70)
top_trade = nepse.getTopTenTradeScrips()
for stock in top_trade:
    volume = stock.get('shareTraded', 0)
    print(f"{stock['symbol']:10s} | Volume: {volume:12,} shares")
```

---

## Company Information Examples

### Example 4: Get Company Details

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

symbol = "NABIL"
details = nepse.getCompanyDetails(symbol)

print(f"Company: {symbol}")
print("-" * 50)
print(f"Last Traded Price: Rs.{details.get('lastTradedPrice', 0):.2f}")
print(f"Open Price: Rs.{details.get('openPrice', 0):.2f}")
print(f"High Price: Rs.{details.get('highPrice', 0):.2f}")
print(f"Low Price: Rs.{details.get('lowPrice', 0):.2f}")
print(f"Close Price: Rs.{details.get('closePrice', 0):.2f}")
print(f"Volume: {details.get('totalTradedQuantity', 0):,} shares")
print(f"Turnover: Rs.{details.get('totalTurnover', 0):,.2f}")
print(f"Number of Trades: {details.get('totalTrades', 0):,}")
print(f"52-Week High: Rs.{details.get('fiftyTwoWeekHigh', 0):.2f}")
print(f"52-Week Low: Rs.{details.get('fiftyTwoWeekLow', 0):.2f}")
```

### Example 5: Market Depth Analysis

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

symbol = "NABIL"
depth = nepse.getSymbolMarketDepth(symbol)

print(f"Market Depth for {symbol}")
print("=" * 60)

if 'buyDepth' in depth:
    print("\nBUY ORDERS:")
    print("-" * 60)
    print(f"{'Price':>10s} | {'Quantity':>10s}")
    print("-" * 60)
    for order in depth['buyDepth'][:10]:  # Top 10 buy orders
        print(f"{order['price']:>10.2f} | {order['quantity']:>10,}")

if 'sellDepth' in depth:
    print("\nSELL ORDERS:")
    print("-" * 60)
    print(f"{'Price':>10s} | {'Quantity':>10s}")
    print("-" * 60)
    for order in depth['sellDepth'][:10]:  # Top 10 sell orders
        print(f"{order['price']:>10.2f} | {order['quantity']:>10,}")
```

### Example 6: List All Companies in a Sector

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

# Get companies grouped by sector
sectors = nepse.getSectorScrips()

# Display a specific sector
sector_name = "Commercial Banks"
if sector_name in sectors:
    print(f"{sector_name} ({len(sectors[sector_name])} companies):")
    print("-" * 50)
    for symbol in sorted(sectors[sector_name]):
        print(f"  • {symbol}")

# Display all sectors with counts
print("\n" + "=" * 50)
print("ALL SECTORS")
print("=" * 50)
for sector, symbols in sorted(sectors.items()):
    print(f"{sector:40s}: {len(symbols):3d} companies")
```

---

## Analysis Examples

### Example 7: Find Stocks with Specific Criteria

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

# Get all gainers
gainers = nepse.getTopGainers()

# Filter criteria
MIN_CHANGE = 5.0  # Minimum 5% gain
MIN_VOLUME = 10000  # Minimum 10,000 shares traded

print(f"Stocks with >{MIN_CHANGE}% gain and >{MIN_VOLUME:,} volume:")
print("=" * 70)

filtered_stocks = [
    stock for stock in gainers 
    if stock['percentageChange'] > MIN_CHANGE 
    and stock.get('totalTradedQuantity', 0) > MIN_VOLUME
]

for stock in filtered_stocks:
    print(f"{stock['symbol']:10s} | "
          f"+{stock['percentageChange']:6.2f}% | "
          f"Vol: {stock.get('totalTradedQuantity', 0):8,} | "
          f"LTP: Rs.{stock['ltp']:8.2f}")
```

### Example 8: Sector-wise Performance

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

# Get sector scrips and price volume data
sectors = nepse.getSectorScrips()
price_volume = {s['symbol']: s for s in nepse.getPriceVolume()}

print("SECTOR-WISE PERFORMANCE")
print("=" * 80)
print(f"{'Sector':40s} | {'Companies':>8s} | {'Total Turnover':>15s}")
print("-" * 80)

sector_data = []
for sector, symbols in sectors.items():
    total_turnover = sum(
        price_volume.get(symbol, {}).get('totalTurnover', 0) 
        for symbol in symbols
    )
    sector_data.append((sector, len(symbols), total_turnover))

# Sort by turnover
for sector, count, turnover in sorted(sector_data, key=lambda x: x[2], reverse=True):
    print(f"{sector:40s} | {count:8d} | Rs.{turnover:15,.2f}")
```

### Example 9: Compare Multiple Stocks

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

symbols = ["NABIL", "SCB", "NICA", "EBL", "NIB"]

print("BANKING SECTOR COMPARISON")
print("=" * 100)
print(f"{'Symbol':10s} | {'LTP':>10s} | {'Volume':>12s} | "
      f"{'Turnover':>15s} | {'Trades':>8s}")
print("-" * 100)

for symbol in symbols:
    try:
        details = nepse.getCompanyDetails(symbol)
        ltp = details.get('lastTradedPrice', 0)
        volume = details.get('totalTradedQuantity', 0)
        turnover = details.get('totalTurnover', 0)
        trades = details.get('totalTrades', 0)
        
        print(f"{symbol:10s} | Rs.{ltp:8.2f} | {volume:12,} | "
              f"Rs.{turnover:13,.2f} | {trades:8,}")
    except Exception as e:
        print(f"{symbol:10s} | Error: {e}")
```

---

## Async Examples

### Example 10: Async Floorsheet Download

```python
import asyncio
from nepse import AsyncNepse
import json

async def download_floorsheet():
    nepse = AsyncNepse()
    nepse.setTLSVerification(False)
    
    print("Downloading today's floorsheet...")
    floorsheet = await nepse.getFloorSheet(show_progress=True)
    
    print(f"\nDownloaded {len(floorsheet)} transactions")
    
    # Save to file
    with open('floorsheet.json', 'w') as f:
        json.dump(floorsheet, f, indent=2)
    
    # Show some statistics
    symbols = set(tx['stockSymbol'] for tx in floorsheet)
    total_value = sum(tx.get('contractAmount', 0) for tx in floorsheet)
    
    print(f"Unique symbols: {len(symbols)}")
    print(f"Total transaction value: Rs.{total_value:,.2f}")

asyncio.run(download_floorsheet())
```

### Example 11: Fetch Multiple Companies Concurrently

```python
import asyncio
from nepse import AsyncNepse

async def fetch_multiple_companies():
    nepse = AsyncNepse()
    nepse.setTLSVerification(False)
    
    symbols = ["NABIL", "SCB", "NICA", "EBL", "NIB", 
               "ADBL", "KBL", "BOKL", "NCCB", "SBI"]
    
    print(f"Fetching data for {len(symbols)} companies...")
    
    # Fetch all concurrently
    tasks = [nepse.getCompanyDetails(symbol) for symbol in symbols]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Display results
    print("\nRESULTS:")
    print("=" * 70)
    for symbol, data in zip(symbols, results):
        if isinstance(data, Exception):
            print(f"{symbol:10s} | Error: {data}")
        else:
            ltp = data.get('lastTradedPrice', 0)
            change = data.get('percentageChange', 0)
            print(f"{symbol:10s} | LTP: Rs.{ltp:8.2f} | Change: {change:+6.2f}%")

asyncio.run(fetch_multiple_companies())
```

### Example 12: Real-time Market Monitor

```python
import asyncio
from nepse import AsyncNepse
from datetime import datetime

async def monitor_market(interval=30, max_iterations=10):
    """Monitor market every 'interval' seconds"""
    nepse = AsyncNepse()
    nepse.setTLSVerification(False)
    
    for i in range(max_iterations):
        try:
            status = await nepse.getMarketStatus()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"[{timestamp}] Market Status: {status['isOpen']}")
            
            if status['isOpen'] == 'OPEN':
                # Get quick stats
                summary = await nepse.getSummary()
                for item in summary[:3]:  # Show first 3 items
                    print(f"  {item['detail']}: {item['value']}")
            else:
                print("  Market is closed. Stopping monitor.")
                break
            
            # Wait before next check
            if i < max_iterations - 1:
                await asyncio.sleep(interval)
                
        except Exception as e:
            print(f"Error: {e}")
            await asyncio.sleep(interval)

asyncio.run(monitor_market(interval=30, max_iterations=10))
```

---

## Data Export Examples

### Example 13: Export to CSV

```python
import csv
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

# Get top gainers
gainers = nepse.getTopGainers()

# Export to CSV
with open('top_gainers.csv', 'w', newline='', encoding='utf-8') as f:
    if gainers:
        fieldnames = gainers[0].keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(gainers)

print("Exported top gainers to top_gainers.csv")
```

### Example 14: Export Historical Data

```python
from nepse import Nepse
from datetime import date, timedelta
import json

nepse = Nepse()
nepse.setTLSVerification(False)

symbol = "NABIL"
end_date = date.today()
start_date = end_date - timedelta(days=90)  # Last 90 days

print(f"Downloading {symbol} historical data...")
history = nepse.getCompanyPriceVolumeHistory(symbol, start_date, end_date)

# Save to JSON
filename = f"{symbol}_history_{start_date}_to_{end_date}.json"
with open(filename, 'w') as f:
    json.dump(history, f, indent=2)

print(f"Saved to {filename}")
print(f"Records: {len(history.get('content', []))}")
```

---

## Advanced Examples

### Example 15: Portfolio Tracker

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

# Your portfolio
portfolio = {
    "NABIL": {"quantity": 10, "avg_price": 950.0},
    "SCB": {"quantity": 15, "avg_price": 420.0},
    "NICA": {"quantity": 20, "avg_price": 780.0},
}

print("PORTFOLIO SUMMARY")
print("=" * 90)
print(f"{'Symbol':10s} | {'Qty':>6s} | {'Avg Price':>10s} | "
      f"{'LTP':>10s} | {'Current Value':>15s} | {'P/L':>12s}")
print("-" * 90)

total_investment = 0
total_current_value = 0

for symbol, holding in portfolio.items():
    try:
        details = nepse.getCompanyDetails(symbol)
        ltp = details.get('lastTradedPrice', 0)
        
        qty = holding['quantity']
        avg_price = holding['avg_price']
        
        investment = qty * avg_price
        current_value = qty * ltp
        profit_loss = current_value - investment
        pl_percent = (profit_loss / investment * 100) if investment > 0 else 0
        
        total_investment += investment
        total_current_value += current_value
        
        print(f"{symbol:10s} | {qty:6d} | Rs.{avg_price:8.2f} | "
              f"Rs.{ltp:8.2f} | Rs.{current_value:13,.2f} | "
              f"{profit_loss:+11,.2f} ({pl_percent:+.2f}%)")
              
    except Exception as e:
        print(f"{symbol:10s} | Error: {e}")

total_pl = total_current_value - total_investment
total_pl_percent = (total_pl / total_investment * 100) if total_investment > 0 else 0

print("-" * 90)
print(f"{'TOTAL':10s} | {'':6s} | {'':10s} | {'':10s} | "
      f"Rs.{total_current_value:13,.2f} | "
      f"{total_pl:+11,.2f} ({total_pl_percent:+.2f}%)")
```

### Example 16: Alert System

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

# Define alerts
alerts = {
    "NABIL": {"target_low": 900, "target_high": 1100},
    "SCB": {"target_low": 400, "target_high": 500},
}

print("CHECKING PRICE ALERTS")
print("=" * 70)

for symbol, targets in alerts.items():
    try:
        details = nepse.getCompanyDetails(symbol)
        ltp = details.get('lastTradedPrice', 0)
        
        if ltp <= targets['target_low']:
            print(f"🔽 ALERT: {symbol} is at Rs.{ltp:.2f} "
                  f"(below target of Rs.{targets['target_low']:.2f})")
        elif ltp >= targets['target_high']:
            print(f"🔼 ALERT: {symbol} is at Rs.{ltp:.2f} "
                  f"(above target of Rs.{targets['target_high']:.2f})")
        else:
            print(f"✓ {symbol}: Rs.{ltp:.2f} (within range)")
            
    except Exception as e:
        print(f"✗ {symbol}: Error - {e}")
```

### Example 17: Volume Analysis

```python
from nepse import Nepse

nepse = Nepse()
nepse.setTLSVerification(False)

print("HIGH VOLUME STOCKS (Above Average)")
print("=" * 80)

# Get all price/volume data
all_data = nepse.getPriceVolume()

# Calculate average volume
volumes = [s.get('totalTradedQuantity', 0) for s in all_data if s.get('totalTradedQuantity', 0) > 0]
avg_volume = sum(volumes) / len(volumes) if volumes else 0

print(f"Average Trading Volume: {avg_volume:,.0f} shares\n")

# Filter high volume stocks
high_volume = [
    s for s in all_data 
    if s.get('totalTradedQuantity', 0) > avg_volume * 2  # 2x average
]

# Sort by volume
high_volume.sort(key=lambda x: x.get('totalTradedQuantity', 0), reverse=True)

print(f"{'Symbol':10s} | {'Volume':>15s} | {'% of Avg':>10s} | {'LTP':>10s}")
print("-" * 80)

for stock in high_volume[:20]:  # Top 20
    symbol = stock.get('symbol', 'N/A')
    volume = stock.get('totalTradedQuantity', 0)
    ltp = stock.get('lastTradedPrice', 0)
    pct_of_avg = (volume / avg_volume * 100) if avg_volume > 0 else 0
    
    print(f"{symbol:10s} | {volume:15,} | {pct_of_avg:9.1f}% | Rs.{ltp:8.2f}")
```

---

## Tips for Best Results

1. **Always set TLS verification to False** (current SSL issue)
2. **Use AsyncNepse for bulk operations** (much faster)
3. **Handle exceptions** appropriately (network issues can occur)
4. **Cache data when possible** (company lists don't change often)
5. **Be respectful** of the API (don't spam requests)

For more information, see the full [README.md](README.md)
