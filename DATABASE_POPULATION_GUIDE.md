# NEPSE Database Population Guide

## Overview

This project populates a local PostgreSQL database with data from the Nepal Stock Exchange (NEPSE) API. The database serves as a local mirror of NEPSE's trading data.

## What Has Been Populated

### ✅ Successfully Populated Tables

#### Phase 1: Core Master Data
- **sectors** (23 rows) - All NEPSE sectors
- **companies** (613 rows) - All listed companies
- **securities** (542 rows) - All tradable securities

#### Phase 2: Market Data
- **market_summary** (1 row) - Daily market summary
- **security_prices** (1,260 rows) - Last 30 days of price data for 50 securities
- **indices** (17 indices) - NEPSE main index and all sub-indices
- **index_values** (17 rows) - Current day index values

#### Phase 3: Transaction Data
- **transactions** (62,658 rows) - Today's complete floorsheet

### ❌ Tables Not Populated (Data Not Available from API)

- **brokers** - Broker information not available from public API
- **broker_branches** - Not available
- **orders** - Pre-trade order book not available
- **corporate_actions** - Dividends, bonus shares, etc. not available
- **announcements** - Company announcements not available
- **share_issues** (IPO/FPO) - Not available
- **settlements** - Settlement data not available

## Scripts Created

### 1. `populate_database.py`
Main ETL script that populates the database with NEPSE data.

**Usage:**
```bash
py populate_database.py
```

**What it does:**
- Fetches and populates sectors from company data
- Populates all companies and securities
- Updates market summary and index values
- Fetches price history for securities (currently limited to 50, configurable)
- Downloads and populates today's complete floorsheet (all transactions)

### 2. `test_db_connection.py`
Quick test to verify database connectivity.

**Usage:**
```bash
py test_db_connection.py
```

## Configuration

### Database Settings
Located in `populate_database.py`:
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'i6W4?M<?[fs1'
}
```

### Adjustable Parameters

**Number of securities for price history:**
In `populate_security_prices()` method, line ~378:
```python
LIMIT 50  # Change this to populate more securities
```
Remove `LIMIT 50` to populate ALL securities (will take longer).

**Days of historical data:**
In `main()` function, line ~641:
```python
etl.populate_security_prices(days_back=30)  # Change 30 to desired days
```

## Running Full Population

To populate ALL securities with historical data (will take 30+ minutes):

1. Edit `populate_database.py`
2. Find line ~378 and remove `LIMIT 50`:
   ```python
   # Before:
   WHERE s.is_tradable = TRUE
   LIMIT 50
   
   # After:
   WHERE s.is_tradable = TRUE
   ```
3. Run: `py populate_database.py`

## Incremental Updates

To update data daily:

1. **Quick Update** (market summary, indices, today's floorsheet):
   ```bash
   py populate_database.py
   ```
   This will update existing data and add new transactions.

2. **Full Price History Update** (if you removed LIMIT):
   - Run the script once per day
   - It uses `ON CONFLICT DO UPDATE` so it won't duplicate data

## Database Query Examples

### Get today's top 10 traded stocks:
```sql
SELECT 
    c.symbol, 
    c.name,
    COUNT(*) as trade_count,
    SUM(t.trade_quantity) as total_volume,
    SUM(t.trade_amount) as total_turnover
FROM transactions t
JOIN securities s ON t.security_id = s.security_id
JOIN companies c ON s.company_id = c.company_id
WHERE t.trade_date = CURRENT_DATE
GROUP BY c.symbol, c.name
ORDER BY total_turnover DESC
LIMIT 10;
```

### Get price history for a specific stock:
```sql
SELECT 
    trading_date,
    open_price,
    high_price,
    low_price,
    close_price,
    total_traded_quantity
FROM security_prices sp
JOIN securities s ON sp.security_id = s.security_id
JOIN companies c ON s.company_id = c.company_id
WHERE c.symbol = 'NABIL'
ORDER BY trading_date DESC
LIMIT 30;
```

### Get all index values for today:
```sql
SELECT 
    i.index_name,
    iv.index_value,
    iv.absolute_change,
    iv.percentage_change
FROM index_values iv
JOIN indices i ON iv.index_id = i.index_id
WHERE iv.trading_date = CURRENT_DATE
ORDER BY i.index_name;
```

### Get sector-wise company distribution:
```sql
SELECT 
    s.sector_name,
    COUNT(c.company_id) as company_count
FROM sectors s
LEFT JOIN companies c ON s.sector_id = c.sector_id
GROUP BY s.sector_name
ORDER BY company_count DESC;
```

## Future Enhancements

1. **Historical Data Backfill**: Script to fetch historical data for all securities
2. **Broker Information**: Manual entry or scraping (not available from API)
3. **Corporate Actions**: Manual entry from NEPSE website
4. **Automated Scheduling**: Windows Task Scheduler or cron job for daily updates
5. **Data Validation**: Scripts to verify data integrity
6. **Analytics Views**: Additional SQL views for common queries

## Troubleshooting

### SSL Certificate Error
If you see SSL errors, the script already handles this with:
```python
nepse.setTLSVerification(False)
```

### Database Connection Failed
- Verify PostgreSQL is running
- Check database credentials in `DB_CONFIG`
- Ensure database has been initialized with `db.sql`

### API Rate Limiting
The NEPSE API may have rate limits. The script includes retry logic for network errors.

### Memory Issues (Large Floorsheet)
If fetching floorsheet causes memory issues:
- The floorsheet can have 60,000+ transactions per day
- Consider batch processing or pagination

## Performance Notes

- **Initial population**: ~2-3 minutes (50 securities, 30 days, floorsheet)
- **Full population** (all 542 securities): ~30-45 minutes
- **Daily update**: ~2 minutes (just new data)
- **Database size**: Approximately 50-100 MB for 30 days of data

## License

This project uses the unofficial NEPSE API library. Use responsibly and in accordance with NEPSE's terms of service.
