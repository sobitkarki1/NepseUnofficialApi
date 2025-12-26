"""
Fast Security Prices Update Script
===================================
Only updates security prices using parallel API calls for maximum speed.
"""

from datetime import datetime, date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import psycopg2
from nepse import Nepse

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'i6W4?M<?[fs1'
}

class FastPriceUpdater:
    def __init__(self, db_config, days_back=365):
        self.db_config = db_config
        self.days_back = days_back
        self.conn = None
        self.nepse = Nepse()
        self.nepse.setTLSVerification(False)
        
    def connect_db(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            print("✓ Database connected")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
    
    
    def fetch_security_price(self, security_id, symbol, start_date, end_date):
        """Fetch price data for a single security"""
        try:
            history = self.nepse.getCompanyPriceVolumeHistory(
                symbol, 
                start_date=start_date, 
                end_date=end_date
            )
            
            if not history or 'content' not in history:
                return security_id, symbol, []
            
            return security_id, symbol, history.get('content', [])
        except Exception as e:
            return security_id, symbol, []
    
    def fetch_all_prices_parallel(self, securities, start_date, end_date, max_workers=20):
        """Fetch prices for all securities using thread pool"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_security = {
                executor.submit(
                    self.fetch_security_price, 
                    sec[0], sec[2], start_date, end_date
                ): sec for sec in securities
            }
            
            # Process completed tasks
            completed = 0
            for future in as_completed(future_to_security):
                security_id, symbol, price_data = future.result()
                results.append((security_id, symbol, price_data))
                
                completed += 1
                if completed % 20 == 0:
                    print(f"  Progress: {completed}/{len(securities)} securities fetched...")
        
        return results
    
    def populate_security_prices(self):
        """Populate security prices using async"""
        print(f"\n{'='*60}")
        print(f"FAST SECURITY PRICE UPDATE - {self.days_back} DAYS")
        print(f"{'='*60}\n")
        
        try:
            # Get all tradable securities
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT s.security_id, s.security_symbol, c.symbol 
                    FROM securities s
                    JOIN companies c ON s.company_id = c.company_id
                    WHERE s.is_tradable = TRUE
                    ORDER BY s.security_symbol
                """)
                securities = cur.fetchall()
            
            print(f"Fetching prices for {len(securities)} securities...")
            
            end_date = date.today()
            start_date = end_date - timedelta(days=self.days_back)
            print(f"Date range: {start_date} to {end_date}\n")
            
            # Fetch all prices in parallel using thread pool
            print("Fetching data in parallel (20 concurrent requests)...")
            results = self.fetch_all_prices_parallel(securities, start_date, end_date)
            
            # Process and insert results
            total_inserted = 0
            successful = 0
            failed = 0
            
            print("\nInserting into database...")
            with self.conn.cursor() as cur:
                for security_id, symbol, price_data in results:
                    if not price_data:
                        failed += 1
                        continue
                    
                    records_for_security = 0
                    for record in price_data:
                        business_date = record.get('businessDate')
                        if not business_date:
                            continue
                        
                        try:
                            cur.execute("""
                                INSERT INTO security_prices 
                                (security_id, trading_date, high_price, low_price, close_price,
                                 total_traded_quantity, total_traded_value, total_trades)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (security_id, trading_date) 
                                DO UPDATE SET
                                    high_price = EXCLUDED.high_price,
                                    low_price = EXCLUDED.low_price,
                                    close_price = EXCLUDED.close_price,
                                    total_traded_quantity = EXCLUDED.total_traded_quantity,
                                    total_traded_value = EXCLUDED.total_traded_value,
                                    total_trades = EXCLUDED.total_trades,
                                    updated_at = CURRENT_TIMESTAMP
                            """, (
                                security_id,
                                business_date,
                                record.get('highPrice'),
                                record.get('lowPrice'),
                                record.get('closePrice'),
                                record.get('totalTradedQuantity'),
                                record.get('totalTradedValue'),
                                record.get('totalTrades')
                            ))
                            records_for_security += 1
                            total_inserted += 1
                        except Exception as e:
                            if failed == 0:  # Print error for first failure only
                                print(f"  First error ({symbol} {business_date}): {e}")
                            continue
                    
                    successful += 1
                    if successful % 50 == 0:
                        print(f"  Progress: {successful}/{len(securities)} securities ({total_inserted:,} records)...")
                
                self.conn.commit()
            
            print(f"\n{'='*60}")
            print(f"✓ Successfully fetched: {successful} securities")
            print(f"✗ Failed: {failed} securities")
            print(f"✓ Total price records inserted/updated: {total_inserted:,}")
            
            # Get final count
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM security_prices")
                total_count = cur.fetchone()[0]
                print(f"✓ Total records in database: {total_count:,}")
            
            print(f"{'='*60}\n")
            return True
            
        except Exception as e:
            print(f"\n✗ Failed to populate security prices: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")


def main():
    start_time = datetime.now()
    print(f"\nStarted at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    updater = FastPriceUpdater(DB_CONFIG, days_back=365)
    
    if not updater.connect_db():
        return
    
    try:
        updater.populate_security_prices()
    finally:
        updater.close_db()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    print(f"\nFinished at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)\n")


if __name__ == "__main__":
    main()
