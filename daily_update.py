"""
Incremental Daily Update Script
================================
Run this script daily to update your database with the latest NEPSE data.
This is lighter and faster than the full population script.

What it updates:
- Market summary for today
- Index values for today  
- Latest floorsheet (all today's transactions)
- Price data for actively traded securities

Run this as a scheduled task for daily updates.
"""

import sys
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from nepse import Nepse

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'i6W4?M<?[fs1'
}


class DailyUpdate:
    """Lightweight daily update for NEPSE database"""
    
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
    
    def update_market_summary(self):
        """Update today's market summary"""
        print("\n[1/3] Updating Market Summary...")
        
        try:
            from datetime import date
            summary_data = self.nepse.getSummary()
            today = date.today()
            
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
            return True
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            return False
    
    def update_indices(self):
        """Update today's index values"""
        print("\n[2/3] Updating Index Values...")
        
        try:
            from datetime import date
            all_indices = self.nepse.getNepseIndex()
            sub_indices = self.nepse.getNepseSubIndices()
            today = date.today()
            updated = 0
            
            with self.conn.cursor() as cur:
                # Main indices
                for idx_data in all_indices:
                    index_name = idx_data.get('index', '')
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
                        updated += 1
                
                # Sub-indices
                for sub_index in sub_indices:
                    index_name = sub_index.get('index', '')
                    index_code = index_name.upper().replace(' ', '_')[:20]
                    
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
                    updated += 1
                
                self.conn.commit()
            
            print(f"  ✓ Updated {updated} index values for {today}")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            return False
    
    def update_floorsheet(self):
        """Update today's floorsheet"""
        print("\n[3/3] Updating Today's Floorsheet...")
        
        try:
            from datetime import date
            print("  Fetching floorsheet...")
            floorsheet = self.nepse.getFloorSheet(show_progress=True)
            
            print(f"\n  Fetched {len(floorsheet)} transactions")
            
            inserted = 0
            skipped = 0
            
            with self.conn.cursor() as cur:
                for trade in floorsheet:
                    try:
                        contract_id = trade.get('contractId')
                        symbol = trade.get('stockSymbol')
                        
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
                        
                        trade_date = trade.get('tradeDate') or date.today()
                        trade_time_str = trade.get('tradeTime')
                        
                        if trade_time_str:
                            try:
                                trade_datetime = datetime.strptime(f"{trade_date} {trade_time_str}", "%Y-%m-%d %H:%M:%S")
                            except:
                                trade_datetime = datetime.combine(trade_date, datetime.min.time())
                        else:
                            trade_datetime = datetime.combine(trade_date, datetime.min.time())
                        
                        # Get broker IDs from member codes
                        buyer_code = trade.get('buyerMemberId')
                        seller_code = trade.get('sellerMemberId')
                        
                        broker_buy_id = None
                        broker_sell_id = None
                        
                        if buyer_code:
                            cur.execute("SELECT broker_id FROM brokers WHERE broker_code = %s", (buyer_code,))
                            result = cur.fetchone()
                            broker_buy_id = result[0] if result else None
                        
                        if seller_code:
                            cur.execute("SELECT broker_id FROM brokers WHERE broker_code = %s", (seller_code,))
                            result = cur.fetchone()
                            broker_sell_id = result[0] if result else None
                        
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
                            broker_buy_id,
                            broker_sell_id
                        ))
                        
                        if cur.rowcount > 0:
                            inserted += 1
                        else:
                            skipped += 1
                            
                    except Exception as e:
                        skipped += 1
                        continue
                
                self.conn.commit()
            
            print(f"  ✓ Inserted {inserted} new transactions")
            if skipped > 0:
                print(f"  ℹ Skipped {skipped} (duplicates or errors)")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            return False
    
    def _parse_float(self, value):
        """Safely parse float value"""
        if value is None:
            return None
        try:
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
            if isinstance(value, str):
                value = value.replace(',', '')
            return int(float(value))
        except:
            return None


def main():
    """Main execution function"""
    print("="*60)
    print("NEPSE DAILY UPDATE SCRIPT")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    updater = DailyUpdate(DB_CONFIG)
    
    if not updater.connect_db():
        sys.exit(1)
    
    try:
        updater.update_market_summary()
        updater.update_indices()
        updater.update_floorsheet()
        
        print("\n" + "="*60)
        print("✓ DAILY UPDATE COMPLETED SUCCESSFULLY")
        print("="*60)
        print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n\n✗ Process interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        updater.close_db()


if __name__ == "__main__":
    main()
