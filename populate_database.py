"""
NEPSE Database Population Script
=================================
This script fetches data from NEPSE API and populates the PostgreSQL database.

Phases:
1. Core Master Data: Sectors, Companies, Securities
2. Market Data: Summary, Prices, Indices
3. Transaction Data: Floorsheet
"""

import sys
import json
from datetime import datetime, date, timedelta
from collections import defaultdict
import psycopg2
from psycopg2.extras import execute_values, RealDictCursor
from nepse import Nepse

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'i6W4?M<?[fs1'
}


class NepseETL:
    """ETL class for NEPSE data to PostgreSQL"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None
        self.nepse = Nepse()
        self.nepse.setTLSVerification(False)
        
    def connect_db(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            print("✓ Database connection established")
            return True
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            return False
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a SQL query"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            print(f"✗ Query execution failed: {e}")
            return None if fetch else False
    
    def table_count(self, table_name):
        """Get row count for a table"""
        result = self.execute_query(f"SELECT COUNT(*) as count FROM {table_name}", fetch=True)
        return result[0]['count'] if result else 0
    
    # ==================== PHASE 1: CORE MASTER DATA ====================
    
    def populate_sectors(self):
        """Populate sectors table from API data"""
        print("\n[PHASE 1.1] Populating Sectors...")
        
        try:
            # Get sector information from companies
            companies = self.nepse.getCompanyList()
            sectors_dict = {}
            
            for company in companies:
                sector_name = company.get('sectorName')
                if sector_name and sector_name not in sectors_dict:
                    # Create a sector code from the name
                    sector_code = sector_name.upper().replace(' ', '_').replace('&', 'AND')[:10]
                    sectors_dict[sector_name] = sector_code
            
            # Insert sectors
            inserted = 0
            with self.conn.cursor() as cur:
                for sector_name, sector_code in sectors_dict.items():
                    try:
                        cur.execute("""
                            INSERT INTO sectors (sector_code, sector_name, is_active)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (sector_code) DO UPDATE 
                            SET sector_name = EXCLUDED.sector_name
                        """, (sector_code, sector_name, True))
                        inserted += 1
                    except Exception as e:
                        print(f"  Warning: Could not insert sector {sector_name}: {e}")
                        continue
                
                self.conn.commit()
            
            print(f"  ✓ Inserted/Updated {inserted} sectors")
            print(f"  Total sectors in DB: {self.table_count('sectors')}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to populate sectors: {e}")
            return False
    
    def populate_companies(self):
        """Populate companies table from API data"""
        print("\n[PHASE 1.2] Populating Companies...")
        
        try:
            companies = self.nepse.getCompanyList()
            print(f"  Fetched {len(companies)} companies from API")
            
            inserted = 0
            updated = 0
            
            with self.conn.cursor() as cur:
                for company in companies:
                    try:
                        symbol = company.get('symbol')
                        name = company.get('companyName') or company.get('securityName')
                        sector_name = company.get('sectorName')
                        
                        # Get sector_id
                        cur.execute("SELECT sector_id FROM sectors WHERE sector_name = %s", (sector_name,))
                        sector_result = cur.fetchone()
                        sector_id = sector_result[0] if sector_result else None
                        
                        # Check if company exists
                        cur.execute("SELECT company_id FROM companies WHERE symbol = %s", (symbol,))
                        existing = cur.fetchone()
                        
                        if existing:
                            # Update existing
                            cur.execute("""
                                UPDATE companies 
                                SET name = %s, sector_id = %s, updated_at = CURRENT_TIMESTAMP
                                WHERE symbol = %s
                            """, (name, sector_id, symbol))
                            updated += 1
                        else:
                            # Insert new
                            cur.execute("""
                                INSERT INTO companies (symbol, name, sector_id, is_delisted, is_suspended)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (symbol, name, sector_id, False, False))
                            inserted += 1
                            
                    except Exception as e:
                        print(f"  Warning: Could not process company {symbol}: {e}")
                        continue
                
                self.conn.commit()
            
            print(f"  ✓ Inserted {inserted} new companies")
            print(f"  ✓ Updated {updated} existing companies")
            print(f"  Total companies in DB: {self.table_count('companies')}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to populate companies: {e}")
            return False
    
    def populate_securities(self):
        """Populate securities table from API data"""
        print("\n[PHASE 1.3] Populating Securities...")
        
        try:
            securities = self.nepse.getSecurityList()
            print(f"  Fetched {len(securities)} securities from API")
            
            inserted = 0
            updated = 0
            
            with self.conn.cursor() as cur:
                # Get ORD security type
                cur.execute("SELECT security_type_id FROM security_types WHERE type_code = 'ORD'")
                ord_type = cur.fetchone()
                ord_type_id = ord_type[0] if ord_type else None
                
                for security in securities:
                    try:
                        symbol = security.get('symbol')
                        security_name = security.get('securityName')
                        
                        # Get company_id
                        cur.execute("SELECT company_id FROM companies WHERE symbol = %s", (symbol,))
                        company_result = cur.fetchone()
                        company_id = company_result[0] if company_result else None
                        
                        # Generate ISIN (dummy for now, as API doesn't provide it)
                        isin = f"NP{symbol:0<10}"[:12]
                        
                        # Check if security exists
                        cur.execute("SELECT security_id FROM securities WHERE isin_number = %s", (isin,))
                        existing = cur.fetchone()
                        
                        if existing:
                            # Update existing
                            cur.execute("""
                                UPDATE securities 
                                SET security_name = %s, is_active = %s, is_tradable = %s, 
                                    updated_at = CURRENT_TIMESTAMP
                                WHERE isin_number = %s
                            """, (security_name, True, True, isin))
                            updated += 1
                        else:
                            # Insert new
                            cur.execute("""
                                INSERT INTO securities 
                                (company_id, security_type_id, security_symbol, security_name, 
                                 isin_number, is_active, is_tradable)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)
                            """, (company_id, ord_type_id, symbol, security_name, isin, True, True))
                            inserted += 1
                            
                    except Exception as e:
                        print(f"  Warning: Could not process security {symbol}: {e}")
                        continue
                
                self.conn.commit()
            
            print(f"  ✓ Inserted {inserted} new securities")
            print(f"  ✓ Updated {updated} existing securities")
            print(f"  Total securities in DB: {self.table_count('securities')}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to populate securities: {e}")
            return False
    
    def populate_brokers(self, floorsheet_data=None):
        """Extract and populate brokers from floorsheet data"""
        print("\n[PHASE 1.4] Populating Brokers...")
        
        try:
            # If no floorsheet data provided, fetch it
            if not floorsheet_data:
                print("  Fetching floorsheet to extract broker information...")
                floorsheet_data = self.nepse.getFloorSheet(show_progress=False)
            
            # Extract unique brokers from floorsheet
            brokers_dict = {}
            
            for trade in floorsheet_data:
                # Get broker IDs and names separately
                buyer_id = trade.get('buyerMemberId', '')
                buyer_name = trade.get('buyerBrokerName', '')
                seller_id = trade.get('sellerMemberId', '')
                seller_name = trade.get('sellerBrokerName', '')
                
                # Add buyer broker
                if buyer_id and buyer_id.strip() and buyer_id not in brokers_dict:
                    brokers_dict[buyer_id] = buyer_name if buyer_name else buyer_id
                
                # Add seller broker
                if seller_id and seller_id.strip() and seller_id not in brokers_dict:
                    brokers_dict[seller_id] = seller_name if seller_name else seller_id
            
            print(f"  Found {len(brokers_dict)} unique brokers")
            
            # Insert brokers
            inserted = 0
            updated = 0
            
            with self.conn.cursor() as cur:
                for broker_code, broker_name in brokers_dict.items():
                    try:
                        # Check if broker exists
                        cur.execute("SELECT broker_id FROM brokers WHERE broker_code = %s", (broker_code,))
                        existing = cur.fetchone()
                        
                        if existing:
                            # Update existing
                            cur.execute("""
                                UPDATE brokers 
                                SET broker_name = %s, updated_at = CURRENT_TIMESTAMP
                                WHERE broker_code = %s
                            """, (broker_name, broker_code))
                            updated += 1
                        else:
                            # Insert new
                            cur.execute("""
                                INSERT INTO brokers (broker_code, broker_name, is_active)
                                VALUES (%s, %s, %s)
                            """, (broker_code, broker_name, True))
                            inserted += 1
                            
                    except Exception as e:
                        print(f"  Warning: Could not process broker {broker_code}: {e}")
                        continue
                
                self.conn.commit()
            
            print(f"  ✓ Inserted {inserted} new brokers")
            print(f"  ✓ Updated {updated} existing brokers")
            print(f"  Total brokers in DB: {self.table_count('brokers')}")
            return True, floorsheet_data  # Return floorsheet data for reuse
            
        except Exception as e:
            print(f"  ✗ Failed to populate brokers: {e}")
            return False, None
    
    # ==================== PHASE 2: MARKET DATA ====================
    
    def populate_market_summary(self):
        """Populate market summary for today"""
        print("\n[PHASE 2.1] Populating Market Summary...")
        
        try:
            summary_data = self.nepse.getSummary()
            today = date.today()
            
            # Parse summary data (it's a list of key-value pairs)
            summary_dict = {item['detail']: item['value'] for item in summary_data}
            
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO market_summary 
                    (trading_date, nepse_index, total_turnover, total_volume, total_trades)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (trading_date) DO UPDATE 
                    SET nepse_index = EXCLUDED.nepse_index,
                        total_turnover = EXCLUDED.total_turnover,
                        total_volume = EXCLUDED.total_volume,
                        total_trades = EXCLUDED.total_trades,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    today,
                    self._parse_float(summary_dict.get('Index', 0)),
                    self._parse_float(summary_dict.get('Turnover', 0)),
                    self._parse_int(summary_dict.get('Total Traded Shares', 0)),
                    self._parse_int(summary_dict.get('Total Transactions', 0))
                ))
                self.conn.commit()
            
            print(f"  ✓ Market summary updated for {today}")
            print(f"  Total records in DB: {self.table_count('market_summary')}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to populate market summary: {e}")
            return False
    
    def populate_index_values(self):
        """Populate index values for today"""
        print("\n[PHASE 2.2] Populating Index Values...")
        
        try:
            # Get main NEPSE index (returns a list of all indices)
            all_indices = self.nepse.getNepseIndex()
            sub_indices = self.nepse.getNepseSubIndices()
            
            today = date.today()
            inserted = 0
            
            with self.conn.cursor() as cur:
                # Process main indices (NEPSE, Sensitive, Float, Sensitive Float)
                for idx_data in all_indices:
                    index_name = idx_data.get('index', '')
                    
                    # Map to our index codes
                    index_code_map = {
                        'NEPSE Index': 'NEPSE',
                        'Sensitive Index': 'SENSITIVE',
                        'Float Index': 'FLOAT',
                        'Sensitive Float Index': 'SENFLOAT'
                    }
                    
                    index_code = index_code_map.get(index_name)
                    if not index_code:
                        continue
                    
                    cur.execute("SELECT index_id FROM indices WHERE index_code = %s", (index_code,))
                    index_result = cur.fetchone()
                    
                    if index_result:
                        index_id = index_result[0]
                        # Use currentValue if available, otherwise use close
                        index_value = idx_data.get('currentValue') or idx_data.get('close')
                        
                        cur.execute("""
                            INSERT INTO index_values 
                            (index_id, trading_date, index_value, absolute_change, percentage_change)
                            VALUES (%s, %s, %s, %s, %s)
                            ON CONFLICT (index_id, trading_date) DO UPDATE 
                            SET index_value = EXCLUDED.index_value,
                                absolute_change = EXCLUDED.absolute_change,
                                percentage_change = EXCLUDED.percentage_change
                        """, (
                            index_id, today,
                            self._parse_float(index_value),
                            self._parse_float(idx_data.get('change', 0)),
                            self._parse_float(idx_data.get('perChange', 0))
                        ))
                        inserted += 1
                
                # Sub-indices - need to create them first if they don't exist
                for sub_index in sub_indices:
                    index_name = sub_index.get('name', '')
                    index_code = index_name.upper().replace(' ', '_')[:20]
                    
                    # Insert or get index
                    cur.execute("""
                        INSERT INTO indices (index_code, index_name, is_active)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (index_code) DO NOTHING
                        RETURNING index_id
                    """, (index_code, index_name, True))
                    
                    result = cur.fetchone()
                    if result:
                        index_id = result[0]
                    else:
                        cur.execute("SELECT index_id FROM indices WHERE index_code = %s", (index_code,))
                        index_id = cur.fetchone()[0]
                    
                    # Insert index value
                    index_value = sub_index.get('currentValue') or sub_index.get('index')
                    
                    cur.execute("""
                        INSERT INTO index_values 
                        (index_id, trading_date, index_value, absolute_change, percentage_change)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (index_id, trading_date) DO UPDATE 
                        SET index_value = EXCLUDED.index_value,
                            absolute_change = EXCLUDED.absolute_change,
                            percentage_change = EXCLUDED.percentage_change
                    """, (
                        index_id, today,
                        self._parse_float(index_value),
                        self._parse_float(sub_index.get('change', 0)),
                        self._parse_float(sub_index.get('perChange', 0))
                    ))
                    inserted += 1
                
                self.conn.commit()
            
            print(f"  ✓ Inserted/Updated {inserted} index values for {today}")
            print(f"  Total records in DB: {self.table_count('index_values')}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to populate index values: {e}")
            return False
    
    def populate_security_prices(self, days_back=365):
        """Populate security prices for recent days"""
        print(f"\n[PHASE 2.3] Populating Security Prices (last {days_back} days)...")
        
        try:
            # Get all securities
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT s.security_id, s.security_symbol, c.symbol 
                    FROM securities s
                    JOIN companies c ON s.company_id = c.company_id
                    WHERE s.is_tradable = TRUE
                    LIMIT 500
                """)  # Limited to 500 for faster population - remove LIMIT for full population
                securities = cur.fetchall()
            
            print(f"  Processing {len(securities)} securities...")
            
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)
            
            total_inserted = 0
            
            for idx, sec in enumerate(securities, 1):
                security_id = sec[0]
                symbol = sec[2]
                
                try:
                    print(f"  [{idx}/{len(securities)}] Fetching data for {symbol}...", end=' ')
                    
                    # Get price history from API
                    history = self.nepse.getCompanyPriceVolumeHistory(
                        symbol, 
                        start_date=start_date, 
                        end_date=end_date
                    )
                    
                    if not history or 'content' not in history:
                        print("No data")
                        continue
                    
                    price_data = history.get('content', [])
                    
                    with self.conn.cursor() as cur:
                        for record in price_data:
                            business_date = record.get('businessDate')
                            if not business_date:
                                continue
                            
                            cur.execute("""
                                INSERT INTO security_prices 
                                (security_id, trading_date, high_price, low_price, close_price,
                                 total_traded_quantity, total_traded_value, total_trades)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (security_id, trading_date) DO UPDATE 
                                SET high_price = EXCLUDED.high_price,
                                    low_price = EXCLUDED.low_price,
                                    close_price = EXCLUDED.close_price,
                                    total_traded_quantity = EXCLUDED.total_traded_quantity,
                                    total_traded_value = EXCLUDED.total_traded_value,
                                    total_trades = EXCLUDED.total_trades,
                                    updated_at = CURRENT_TIMESTAMP
                            """, (
                                security_id, business_date,
                                self._parse_float(record.get('highPrice')),
                                self._parse_float(record.get('lowPrice')),
                                self._parse_float(record.get('closePrice')),
                                self._parse_int(record.get('totalTradedQuantity')),
                                self._parse_float(record.get('totalTradedValue')),
                                self._parse_int(record.get('totalTrades'))
                            ))
                            total_inserted += 1
                        
                        self.conn.commit()
                    
                    print(f"✓ {len(price_data)} records")
                    
                except Exception as e:
                    print(f"✗ Error: {e}")
                    continue
            
            print(f"\n  ✓ Total price records inserted/updated: {total_inserted}")
            print(f"  Total records in DB: {self.table_count('security_prices')}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to populate security prices: {e}")
            return False
    
    # ==================== PHASE 3: TRANSACTION DATA ====================
    
    def populate_floorsheet(self, floorsheet_data=None):
        """Populate transactions from floorsheet data"""
        print("\n[PHASE 3.1] Populating Floorsheet (Transactions)...")
        
        try:
            # If no floorsheet data provided, fetch it
            if not floorsheet_data:
                print("  Fetching today's floorsheet (this may take a while)...")
                floorsheet = self.nepse.getFloorSheet(show_progress=True)
            else:
                floorsheet = floorsheet_data
                print(f"  Using pre-fetched floorsheet data")
            
            print(f"\n  Processing {len(floorsheet)} transactions")
            
            inserted = 0
            skipped = 0
            
            # Build broker lookup cache
            with self.conn.cursor() as cur:
                cur.execute("SELECT broker_code, broker_id FROM brokers")
                broker_lookup = {row[0]: row[1] for row in cur.fetchall()}
            
            with self.conn.cursor() as cur:
                for trade in floorsheet:
                    try:
                        contract_id = trade.get('contractId')
                        symbol = trade.get('stockSymbol')
                        
                        # Get security_id
                        cur.execute("""
                            SELECT s.security_id 
                            FROM securities s
                            JOIN companies c ON s.company_id = c.company_id
                            WHERE c.symbol = %s
                            LIMIT 1
                        """, (symbol,))
                        sec_result = cur.fetchone()
                        security_id = sec_result[0] if sec_result else None
                        
                        if not security_id:
                            skipped += 1
                            continue
                        
                        # Get broker codes from member IDs
                        buyer_broker_code = trade.get('buyerMemberId', '')
                        seller_broker_code = trade.get('sellerMemberId', '')
                        
                        # Get broker IDs from lookup
                        buyer_broker_id = broker_lookup.get(buyer_broker_code)
                        seller_broker_id = broker_lookup.get(seller_broker_code)
                        
                        trade_date = trade.get('tradeDate') or date.today()
                        trade_time_str = trade.get('tradeTime')
                        
                        # Parse trade time
                        if trade_time_str:
                            try:
                                trade_datetime = datetime.strptime(f"{trade_date} {trade_time_str}", "%Y-%m-%d %H:%M:%S")
                            except:
                                trade_datetime = datetime.combine(trade_date, datetime.min.time())
                        else:
                            trade_datetime = datetime.combine(trade_date, datetime.min.time())
                        
                        # Insert transaction with broker IDs (trade_amount is auto-generated)
                        cur.execute("""
                            INSERT INTO transactions 
                            (trade_id, security_id, trade_price, trade_quantity,
                             trade_time, trade_date, trade_type, trade_session,
                             broker_buy_id, broker_sell_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (trade_id) DO NOTHING
                        """, (
                            str(contract_id),
                            security_id,
                            self._parse_float(trade.get('contractRate')),
                            self._parse_int(trade.get('contractQuantity')),
                            trade_datetime,
                            trade_date,
                            'NORMAL',
                            'CONTINUOUS',
                            buyer_broker_id,
                            seller_broker_id
                        ))
                        
                        if cur.rowcount > 0:
                            inserted += 1
                        else:
                            skipped += 1
                            
                    except Exception as e:
                        print(f"  Warning: Could not process trade {contract_id}: {e}")
                        skipped += 1
                        continue
                
                self.conn.commit()
            
            print(f"  ✓ Inserted {inserted} new transactions")
            print(f"  ✗ Skipped {skipped} transactions (duplicates or missing refs)")
            print(f"  Total transactions in DB: {self.table_count('transactions')}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to populate floorsheet: {e}")
            return False
    
    # ==================== UTILITY METHODS ====================
    
    def _parse_float(self, value):
        """Safely parse float value"""
        if value is None:
            return None
        try:
            # Remove commas and parse
            if isinstance(value, str):
                value = value.replace(',', '')
            return float(value)
        except:
            return None
    
    def _parse_int(self, value):
        """Safely parse integer value"""
        if value is None:
            return None
        try:
            # Remove commas and parse
            if isinstance(value, str):
                value = value.replace(',', '')
            return int(float(value))
        except:
            return None
    
    def print_database_stats(self):
        """Print database statistics"""
        print("\n" + "="*60)
        print("DATABASE STATISTICS")
        print("="*60)
        
        tables = [
            'sectors', 'companies', 'securities', 'security_types',
            'market_summary', 'security_prices', 'indices', 'index_values',
            'transactions', 'brokers'
        ]
        
        for table in tables:
            count = self.table_count(table)
            print(f"  {table:25s}: {count:>10,} rows")
        
        print("="*60)


def main():
    """Main execution function"""
    print("="*60)
    print("NEPSE DATABASE POPULATION SCRIPT")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    etl = NepseETL(DB_CONFIG)
    
    # Connect to database
    if not etl.connect_db():
        sys.exit(1)
    
    try:
        # Phase 1: Core Master Data
        print("\n" + "="*60)
        print("PHASE 1: CORE MASTER DATA")
        print("="*60)
        
        etl.populate_sectors()
        etl.populate_companies()
        etl.populate_securities()
        
        # Phase 2: Market Data
        print("\n" + "="*60)
        print("PHASE 2: MARKET DATA")
        print("="*60)
        
        etl.populate_market_summary()
        etl.populate_index_values()
        etl.populate_security_prices(days_back=365)  # Last 365 days
        
        # Phase 3: Transaction Data
        print("\n" + "="*60)
        print("PHASE 3: TRANSACTION DATA")
        print("="*60)
        
        # Populate brokers first (extracts from floorsheet)
        success, floorsheet_data = etl.populate_brokers()
        
        # Then populate transactions using the same floorsheet data
        if success and floorsheet_data:
            etl.populate_floorsheet(floorsheet_data)
        else:
            # Fallback: fetch floorsheet again if broker population failed
            etl.populate_floorsheet()
        
        # Print final statistics
        etl.print_database_stats()
        
        print("\n" + "="*60)
        print("✓ DATABASE POPULATION COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n\n✗ Process interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        etl.close_db()


if __name__ == "__main__":
    main()
