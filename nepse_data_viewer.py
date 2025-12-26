"""
NEPSE Interactive Data Viewer
==============================
Interactive menu-based console application to view and analyze NEPSE database data.
"""

import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date, timedelta
from collections import defaultdict
import os

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'i6W4?M<?[fs1'
}


class NepseDataViewer:
    """Interactive data viewer for NEPSE database"""
    
    def __init__(self, db_config):
        self.db_config = db_config
        self.conn = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            return True
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def query(self, sql, params=None):
        """Execute query and return results"""
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception as e:
            print(f"❌ Query error: {e}")
            return []
    
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80)
    
    def print_subheader(self, title):
        """Print formatted subheader"""
        print("\n" + "-" * 80)
        print(f"  {title}")
        print("-" * 80)
    
    def wait_for_enter(self):
        """Wait for user to press Enter"""
        input("\nPress Enter to continue...")
    
    # ==================== MENU 1: MARKET OVERVIEW ====================
    
    def show_market_overview(self):
        """Display comprehensive market overview"""
        self.clear_screen()
        self.print_header("📊 MARKET OVERVIEW")
        
        # Today's market summary
        summary = self.query("""
            SELECT 
                trading_date,
                nepse_index,
                total_turnover,
                total_volume,
                total_trades,
                updated_at
            FROM market_summary
            ORDER BY trading_date DESC
            LIMIT 1
        """)
        
        if summary:
            s = summary[0]
            print(f"\n📅 Trading Date: {s['trading_date']}")
            print(f"📈 NEPSE Index: {s['nepse_index']:,.2f}")
            print(f"💰 Total Turnover: Rs. {s['total_turnover']:,.2f}")
            print(f"📦 Total Volume: {s['total_volume']:,} shares")
            print(f"🔄 Total Trades: {s['total_trades']:,} transactions")
            print(f"🕐 Last Updated: {s['updated_at']}")
        
        # Index values
        self.print_subheader("📊 Index Values")
        indices = self.query("""
            SELECT 
                i.index_name,
                iv.index_value,
                iv.absolute_change,
                iv.percentage_change
            FROM index_values iv
            JOIN indices i ON iv.index_id = i.index_id
            WHERE iv.trading_date = (SELECT MAX(trading_date) FROM index_values)
            ORDER BY 
                CASE 
                    WHEN i.index_code = 'NEPSE' THEN 1
                    WHEN i.index_code = 'SENSITIVE' THEN 2
                    WHEN i.index_code = 'FLOAT' THEN 3
                    WHEN i.index_code = 'SENFLOAT' THEN 4
                    ELSE 5
                END,
                i.index_name
        """)
        
        if indices:
            print(f"\n{'Index Name':<35} {'Value':>12} {'Change':>12} {'%Change':>10}")
            print("-" * 80)
            for idx in indices:
                change_sign = '+' if idx['percentage_change'] >= 0 else ''
                change_color = '🟢' if idx['percentage_change'] >= 0 else '🔴'
                print(f"{idx['index_name']:<35} {idx['index_value']:>12.2f} "
                      f"{idx['absolute_change']:>12.2f} {change_color} {change_sign}{idx['percentage_change']:>9.2f}%")
        
        # Sector summary
        self.print_subheader("🏢 Sector Statistics")
        sectors = self.query("""
            SELECT 
                s.sector_name,
                COUNT(c.company_id) as company_count,
                COUNT(sec.security_id) as security_count
            FROM sectors s
            LEFT JOIN companies c ON s.sector_id = c.sector_id AND c.is_delisted = FALSE
            LEFT JOIN securities sec ON c.company_id = sec.company_id AND sec.is_tradable = TRUE
            GROUP BY s.sector_name
            ORDER BY company_count DESC
        """)
        
        if sectors:
            print(f"\n{'Sector':<40} {'Companies':>12} {'Securities':>12}")
            print("-" * 80)
            for sector in sectors:
                print(f"{sector['sector_name']:<40} {sector['company_count']:>12} {sector['security_count']:>12}")
        
        self.wait_for_enter()
    
    # ==================== MENU 2: TOP PERFORMERS ====================
    
    def show_top_performers(self):
        """Display top performing stocks by various metrics"""
        self.clear_screen()
        self.print_header("🏆 TOP PERFORMERS")
        
        print("\n1. By Turnover (Today)")
        print("2. By Volume (Today)")
        print("3. By Number of Trades (Today)")
        print("4. By Price Gainers (Today)")
        print("5. By Price Losers (Today)")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            self._show_top_by_turnover()
        elif choice == '2':
            self._show_top_by_volume()
        elif choice == '3':
            self._show_top_by_trades()
        elif choice == '4':
            self._show_top_gainers()
        elif choice == '5':
            self._show_top_losers()
    
    def _show_top_by_turnover(self):
        """Show top stocks by turnover"""
        self.clear_screen()
        self.print_header("💰 TOP STOCKS BY TURNOVER (Today)")
        
        data = self.query("""
            SELECT 
                c.symbol,
                c.name,
                COUNT(*) as trade_count,
                SUM(t.trade_quantity) as total_volume,
                SUM(t.trade_amount) as total_turnover,
                AVG(t.trade_price) as avg_price
            FROM transactions t
            JOIN securities s ON t.security_id = s.security_id
            JOIN companies c ON s.company_id = c.company_id
            WHERE t.trade_date = (SELECT MAX(trade_date) FROM transactions)
            GROUP BY c.symbol, c.name
            ORDER BY total_turnover DESC
            LIMIT 20
        """)
        
        if data:
            print(f"\n{'#':<4} {'Symbol':<10} {'Company':<35} {'Trades':>8} {'Volume':>12} {'Turnover (Rs)':>18} {'Avg Price':>12}")
            print("-" * 120)
            for idx, row in enumerate(data, 1):
                print(f"{idx:<4} {row['symbol']:<10} {row['name'][:34]:<35} {row['trade_count']:>8,} "
                      f"{row['total_volume']:>12,} {row['total_turnover']:>18,.2f} {row['avg_price']:>12,.2f}")
        else:
            print("\n⚠️  No transaction data available for today.")
        
        self.wait_for_enter()
    
    def _show_top_by_volume(self):
        """Show top stocks by volume"""
        self.clear_screen()
        self.print_header("📦 TOP STOCKS BY VOLUME (Today)")
        
        data = self.query("""
            SELECT 
                c.symbol,
                c.name,
                COUNT(*) as trade_count,
                SUM(t.trade_quantity) as total_volume,
                SUM(t.trade_amount) as total_turnover
            FROM transactions t
            JOIN securities s ON t.security_id = s.security_id
            JOIN companies c ON s.company_id = c.company_id
            WHERE t.trade_date = (SELECT MAX(trade_date) FROM transactions)
            GROUP BY c.symbol, c.name
            ORDER BY total_volume DESC
            LIMIT 20
        """)
        
        if data:
            print(f"\n{'#':<4} {'Symbol':<10} {'Company':<35} {'Volume':>15} {'Trades':>8} {'Turnover (Rs)':>18}")
            print("-" * 110)
            for idx, row in enumerate(data, 1):
                print(f"{idx:<4} {row['symbol']:<10} {row['name'][:34]:<35} {row['total_volume']:>15,} "
                      f"{row['trade_count']:>8,} {row['total_turnover']:>18,.2f}")
        else:
            print("\n⚠️  No transaction data available for today.")
        
        self.wait_for_enter()
    
    def _show_top_by_trades(self):
        """Show top stocks by number of trades"""
        self.clear_screen()
        self.print_header("🔄 TOP STOCKS BY NUMBER OF TRADES (Today)")
        
        data = self.query("""
            SELECT 
                c.symbol,
                c.name,
                COUNT(*) as trade_count,
                SUM(t.trade_quantity) as total_volume,
                SUM(t.trade_amount) as total_turnover
            FROM transactions t
            JOIN securities s ON t.security_id = s.security_id
            JOIN companies c ON s.company_id = c.company_id
            WHERE t.trade_date = (SELECT MAX(trade_date) FROM transactions)
            GROUP BY c.symbol, c.name
            ORDER BY trade_count DESC
            LIMIT 20
        """)
        
        if data:
            print(f"\n{'#':<4} {'Symbol':<10} {'Company':<35} {'# Trades':>10} {'Volume':>12} {'Turnover (Rs)':>18}")
            print("-" * 110)
            for idx, row in enumerate(data, 1):
                print(f"{idx:<4} {row['symbol']:<10} {row['name'][:34]:<35} {row['trade_count']:>10,} "
                      f"{row['total_volume']:>12,} {row['total_turnover']:>18,.2f}")
        else:
            print("\n⚠️  No transaction data available for today.")
        
        self.wait_for_enter()
    
    def _show_top_gainers(self):
        """Show top gainers based on latest price data"""
        self.clear_screen()
        self.print_header("📈 TOP GAINERS (Latest)")
        
        data = self.query("""
            WITH latest_prices AS (
                SELECT 
                    security_id,
                    close_price,
                    previous_close,
                    trading_date,
                    ROW_NUMBER() OVER (PARTITION BY security_id ORDER BY trading_date DESC) as rn
                FROM security_prices
                WHERE close_price IS NOT NULL AND previous_close IS NOT NULL
            )
            SELECT 
                c.symbol,
                c.name,
                lp.close_price,
                lp.previous_close,
                (lp.close_price - lp.previous_close) as price_change,
                ((lp.close_price - lp.previous_close) / lp.previous_close * 100) as percent_change,
                lp.trading_date
            FROM latest_prices lp
            JOIN securities s ON lp.security_id = s.security_id
            JOIN companies c ON s.company_id = c.company_id
            WHERE lp.rn = 1 AND lp.close_price != lp.previous_close
            ORDER BY percent_change DESC
            LIMIT 20
        """)
        
        if data:
            print(f"\n{'#':<4} {'Symbol':<10} {'Company':<30} {'Close':>10} {'Prev Close':>12} {'Change':>10} {'% Change':>12} {'Date':>12}")
            print("-" * 120)
            for idx, row in enumerate(data, 1):
                print(f"{idx:<4} {row['symbol']:<10} {row['name'][:29]:<30} {row['close_price']:>10.2f} "
                      f"{row['previous_close']:>12.2f} {row['price_change']:>10.2f} 🟢 "
                      f"{row['percent_change']:>10.2f}% {row['trading_date']}")
        else:
            print("\n⚠️  No price data available.")
        
        self.wait_for_enter()
    
    def _show_top_losers(self):
        """Show top losers based on latest price data"""
        self.clear_screen()
        self.print_header("📉 TOP LOSERS (Latest)")
        
        data = self.query("""
            WITH latest_prices AS (
                SELECT 
                    security_id,
                    close_price,
                    previous_close,
                    trading_date,
                    ROW_NUMBER() OVER (PARTITION BY security_id ORDER BY trading_date DESC) as rn
                FROM security_prices
                WHERE close_price IS NOT NULL AND previous_close IS NOT NULL
            )
            SELECT 
                c.symbol,
                c.name,
                lp.close_price,
                lp.previous_close,
                (lp.close_price - lp.previous_close) as price_change,
                ((lp.close_price - lp.previous_close) / lp.previous_close * 100) as percent_change,
                lp.trading_date
            FROM latest_prices lp
            JOIN securities s ON lp.security_id = s.security_id
            JOIN companies c ON s.company_id = c.company_id
            WHERE lp.rn = 1 AND lp.close_price != lp.previous_close
            ORDER BY percent_change ASC
            LIMIT 20
        """)
        
        if data:
            print(f"\n{'#':<4} {'Symbol':<10} {'Company':<30} {'Close':>10} {'Prev Close':>12} {'Change':>10} {'% Change':>12} {'Date':>12}")
            print("-" * 120)
            for idx, row in enumerate(data, 1):
                print(f"{idx:<4} {row['symbol']:<10} {row['name'][:29]:<30} {row['close_price']:>10.2f} "
                      f"{row['previous_close']:>12.2f} {row['price_change']:>10.2f} 🔴 "
                      f"{row['percent_change']:>10.2f}% {row['trading_date']}")
        else:
            print("\n⚠️  No price data available.")
        
        self.wait_for_enter()
    
    # ==================== MENU 3: COMPANY/SECURITY LOOKUP ====================
    
    def show_company_lookup(self):
        """Search and display company information"""
        self.clear_screen()
        self.print_header("🔍 COMPANY/SECURITY LOOKUP")
        
        search_term = input("\nEnter company symbol or name (partial match): ").strip().upper()
        
        if not search_term:
            return
        
        companies = self.query("""
            SELECT 
                c.company_id,
                c.symbol,
                c.name,
                s.sector_name,
                c.is_delisted,
                c.is_suspended
            FROM companies c
            LEFT JOIN sectors s ON c.sector_id = s.sector_id
            WHERE UPPER(c.symbol) LIKE %s OR UPPER(c.name) LIKE %s
            ORDER BY c.symbol
            LIMIT 50
        """, (f'%{search_term}%', f'%{search_term}%'))
        
        if not companies:
            print(f"\n⚠️  No companies found matching '{search_term}'")
            self.wait_for_enter()
            return
        
        print(f"\n{'#':<4} {'Symbol':<10} {'Company Name':<45} {'Sector':<25} {'Status':<12}")
        print("-" * 110)
        
        for idx, company in enumerate(companies, 1):
            status = '🔴 Delisted' if company['is_delisted'] else ('⚠️  Suspended' if company['is_suspended'] else '✅ Active')
            print(f"{idx:<4} {company['symbol']:<10} {company['name'][:44]:<45} "
                  f"{(company['sector_name'] or 'N/A')[:24]:<25} {status:<12}")
        
        # Option to view details
        choice = input("\nEnter number to view details (or press Enter to go back): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(companies):
            self._show_company_details(companies[int(choice) - 1]['symbol'])
    
    def _show_company_details(self, symbol):
        """Show detailed information about a specific company"""
        self.clear_screen()
        self.print_header(f"📋 COMPANY DETAILS: {symbol}")
        
        # Basic info
        company = self.query("""
            SELECT 
                c.*,
                s.sector_name
            FROM companies c
            LEFT JOIN sectors s ON c.sector_id = s.sector_id
            WHERE c.symbol = %s
        """, (symbol,))
        
        if not company:
            print(f"\n⚠️  Company {symbol} not found.")
            self.wait_for_enter()
            return
        
        c = company[0]
        
        print(f"\n📊 Basic Information:")
        print(f"  Symbol: {c['symbol']}")
        print(f"  Company Name: {c['name']}")
        print(f"  Sector: {c['sector_name'] or 'N/A'}")
        print(f"  Status: {'🔴 Delisted' if c['is_delisted'] else ('⚠️  Suspended' if c['is_suspended'] else '✅ Active')}")
        print(f"  Created: {c['created_at']}")
        print(f"  Last Updated: {c['updated_at']}")
        
        # Latest price
        latest_price = self.query("""
            SELECT 
                sp.*
            FROM security_prices sp
            JOIN securities s ON sp.security_id = s.security_id
            WHERE s.company_id = %s
            ORDER BY sp.trading_date DESC
            LIMIT 1
        """, (c['company_id'],))
        
        if latest_price:
            p = latest_price[0]
            print(f"\n💰 Latest Price Data ({p['trading_date']}):")
            print(f"  Close Price: Rs. {p['close_price']:,.2f}")
            print(f"  Open: Rs. {p['open_price']:,.2f}")
            print(f"  High: Rs. {p['high_price']:,.2f}")
            print(f"  Low: Rs. {p['low_price']:,.2f}")
            print(f"  Previous Close: Rs. {p['previous_close']:,.2f}")
            print(f"  Volume: {p['total_traded_quantity']:,} shares")
            print(f"  Turnover: Rs. {p['total_traded_value']:,.2f}")
            print(f"  Trades: {p['total_trades']:,}")
        
        # Recent price history
        price_history = self.query("""
            SELECT 
                sp.trading_date,
                sp.close_price,
                sp.total_traded_quantity,
                sp.total_traded_value
            FROM security_prices sp
            JOIN securities s ON sp.security_id = s.security_id
            WHERE s.company_id = %s
            ORDER BY sp.trading_date DESC
            LIMIT 10
        """, (c['company_id'],))
        
        if price_history:
            print(f"\n📈 Recent Price History (Last 10 Trading Days):")
            print(f"  {'Date':<12} {'Close Price':>12} {'Volume':>15} {'Turnover':>18}")
            print("  " + "-" * 60)
            for p in price_history:
                print(f"  {p['trading_date']} {p['close_price']:>12.2f} {p['total_traded_quantity']:>15,} "
                      f"Rs. {p['total_traded_value']:>14,.2f}")
        
        # Transaction summary for today
        tx_summary = self.query("""
            SELECT 
                COUNT(*) as trade_count,
                SUM(t.trade_quantity) as total_volume,
                SUM(t.trade_amount) as total_turnover,
                MIN(t.trade_price) as min_price,
                MAX(t.trade_price) as max_price,
                AVG(t.trade_price) as avg_price
            FROM transactions t
            JOIN securities s ON t.security_id = s.security_id
            WHERE s.company_id = %s
            AND t.trade_date = (SELECT MAX(trade_date) FROM transactions)
        """, (c['company_id'],))
        
        if tx_summary and tx_summary[0]['trade_count'] > 0:
            tx = tx_summary[0]
            print(f"\n🔄 Today's Transaction Summary:")
            print(f"  Total Trades: {tx['trade_count']:,}")
            print(f"  Total Volume: {tx['total_volume']:,} shares")
            print(f"  Total Turnover: Rs. {tx['total_turnover']:,.2f}")
            print(f"  Price Range: Rs. {tx['min_price']:,.2f} - Rs. {tx['max_price']:,.2f}")
            print(f"  Average Price: Rs. {tx['avg_price']:,.2f}")
        
        self.wait_for_enter()
    
    # ==================== MENU 4: SECTOR ANALYSIS ====================
    
    def show_sector_analysis(self):
        """Display sector-wise analysis"""
        self.clear_screen()
        self.print_header("🏢 SECTOR ANALYSIS")
        
        # List all sectors
        sectors = self.query("""
            SELECT 
                s.sector_id,
                s.sector_name,
                COUNT(DISTINCT c.company_id) as company_count,
                COUNT(DISTINCT sec.security_id) as security_count
            FROM sectors s
            LEFT JOIN companies c ON s.sector_id = c.sector_id AND c.is_delisted = FALSE
            LEFT JOIN securities sec ON c.company_id = sec.company_id AND sec.is_tradable = TRUE
            GROUP BY s.sector_id, s.sector_name
            ORDER BY company_count DESC
        """)
        
        if not sectors:
            print("\n⚠️  No sector data available.")
            self.wait_for_enter()
            return
        
        print(f"\n{'#':<4} {'Sector Name':<45} {'Companies':>12} {'Securities':>12}")
        print("-" * 80)
        
        for idx, sector in enumerate(sectors, 1):
            print(f"{idx:<4} {sector['sector_name']:<45} {sector['company_count']:>12} {sector['security_count']:>12}")
        
        # Option to view sector details
        choice = input("\nEnter number to view sector details (or press Enter to go back): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(sectors):
            self._show_sector_details(sectors[int(choice) - 1]['sector_id'], sectors[int(choice) - 1]['sector_name'])
    
    def _show_sector_details(self, sector_id, sector_name):
        """Show detailed information about a specific sector"""
        self.clear_screen()
        self.print_header(f"🏢 SECTOR DETAILS: {sector_name}")
        
        # Companies in this sector
        companies = self.query("""
            SELECT 
                c.symbol,
                c.name,
                c.is_delisted,
                c.is_suspended
            FROM companies c
            WHERE c.sector_id = %s
            ORDER BY c.symbol
        """, (sector_id,))
        
        if companies:
            print(f"\n📋 Companies in {sector_name} ({len(companies)} total):")
            print(f"  {'Symbol':<10} {'Company Name':<50} {'Status':<12}")
            print("  " + "-" * 75)
            for c in companies[:30]:  # Show first 30
                status = '🔴 Delisted' if c['is_delisted'] else ('⚠️  Suspended' if c['is_suspended'] else '✅ Active')
                print(f"  {c['symbol']:<10} {c['name'][:49]:<50} {status:<12}")
            
            if len(companies) > 30:
                print(f"\n  ... and {len(companies) - 30} more companies")
        
        # Sector performance based on transactions
        sector_stats = self.query("""
            SELECT 
                COUNT(DISTINCT t.transaction_id) as total_trades,
                SUM(t.trade_quantity) as total_volume,
                SUM(t.trade_amount) as total_turnover
            FROM transactions t
            JOIN securities s ON t.security_id = s.security_id
            JOIN companies c ON s.company_id = c.company_id
            WHERE c.sector_id = %s
            AND t.trade_date = (SELECT MAX(trade_date) FROM transactions)
        """, (sector_id,))
        
        if sector_stats and sector_stats[0]['total_trades']:
            st = sector_stats[0]
            print(f"\n📊 Today's Sector Performance:")
            print(f"  Total Trades: {st['total_trades']:,}")
            print(f"  Total Volume: {st['total_volume']:,} shares")
            print(f"  Total Turnover: Rs. {st['total_turnover']:,.2f}")
        
        # Top performers in this sector
        top_in_sector = self.query("""
            SELECT 
                c.symbol,
                c.name,
                SUM(t.trade_amount) as turnover
            FROM transactions t
            JOIN securities s ON t.security_id = s.security_id
            JOIN companies c ON s.company_id = c.company_id
            WHERE c.sector_id = %s
            AND t.trade_date = (SELECT MAX(trade_date) FROM transactions)
            GROUP BY c.symbol, c.name
            ORDER BY turnover DESC
            LIMIT 10
        """, (sector_id,))
        
        if top_in_sector:
            print(f"\n🏆 Top 10 by Turnover (Today):")
            print(f"  {'#':<4} {'Symbol':<10} {'Company':<40} {'Turnover (Rs)':>18}")
            print("  " + "-" * 75)
            for idx, row in enumerate(top_in_sector, 1):
                print(f"  {idx:<4} {row['symbol']:<10} {row['name'][:39]:<40} {row['turnover']:>18,.2f}")
        
        self.wait_for_enter()
    
    # ==================== MENU 5: PRICE HISTORY ====================
    
    def show_price_history(self):
        """Display price history for a specific stock"""
        self.clear_screen()
        self.print_header("📈 PRICE HISTORY")
        
        symbol = input("\nEnter company symbol: ").strip().upper()
        
        if not symbol:
            return
        
        # Check if company exists
        company = self.query("""
            SELECT company_id, symbol, name FROM companies WHERE symbol = %s
        """, (symbol,))
        
        if not company:
            print(f"\n⚠️  Company '{symbol}' not found.")
            self.wait_for_enter()
            return
        
        c = company[0]
        
        print(f"\nSelect time period:")
        print("1. Last 7 days")
        print("2. Last 30 days")
        print("3. Last 90 days")
        print("4. All available data")
        
        choice = input("\nSelect option: ").strip()
        
        days_map = {'1': 7, '2': 30, '3': 90, '4': None}
        days = days_map.get(choice)
        
        self.clear_screen()
        self.print_header(f"📈 PRICE HISTORY: {symbol} - {c['name']}")
        
        # Fetch price data
        if days:
            price_data = self.query("""
                SELECT 
                    sp.*
                FROM security_prices sp
                JOIN securities s ON sp.security_id = s.security_id
                WHERE s.company_id = %s
                AND sp.trading_date >= CURRENT_DATE - INTERVAL '%s days'
                ORDER BY sp.trading_date DESC
            """, (c['company_id'], days))
        else:
            price_data = self.query("""
                SELECT 
                    sp.*
                FROM security_prices sp
                JOIN securities s ON sp.security_id = s.security_id
                WHERE s.company_id = %s
                ORDER BY sp.trading_date DESC
            """, (c['company_id'],))
        
        if not price_data:
            print(f"\n⚠️  No price data available for {symbol}.")
            self.wait_for_enter()
            return
        
        print(f"\nTotal records: {len(price_data)}")
        print(f"\n{'Date':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10} {'Volume':>12} {'Turnover':>15} {'Trades':>8}")
        print("-" * 115)
        
        for p in price_data[:50]:  # Show first 50
            print(f"{p['trading_date']} {p['open_price']:>10.2f} {p['high_price']:>10.2f} "
                  f"{p['low_price']:>10.2f} {p['close_price']:>10.2f} {p['total_traded_quantity']:>12,} "
                  f"Rs. {p['total_traded_value']:>12,.2f} {p['total_trades']:>8,}")
        
        if len(price_data) > 50:
            print(f"\n... and {len(price_data) - 50} more records (showing first 50)")
        
        # Summary statistics
        if price_data:
            closes = [p['close_price'] for p in price_data if p['close_price']]
            if closes:
                print(f"\n📊 Summary Statistics:")
                print(f"  Highest Close: Rs. {max(closes):,.2f}")
                print(f"  Lowest Close: Rs. {min(closes):,.2f}")
                print(f"  Average Close: Rs. {sum(closes)/len(closes):,.2f}")
        
        self.wait_for_enter()
    
    # ==================== MENU 6: TRANSACTION ANALYSIS ====================
    
    def show_transaction_analysis(self):
        """Display transaction/floorsheet analysis"""
        self.clear_screen()
        self.print_header("🔄 TRANSACTION ANALYSIS")
        
        print("\n1. Transaction Summary")
        print("2. Search Transactions by Symbol")
        print("3. Top Buyers")
        print("4. Top Sellers")
        print("5. Recent Transactions")
        print("0. Back to Main Menu")
        
        choice = input("\nSelect option: ").strip()
        
        if choice == '1':
            self._show_transaction_summary()
        elif choice == '2':
            self._search_transactions()
        elif choice == '3':
            self._show_top_buyers()
        elif choice == '4':
            self._show_top_sellers()
        elif choice == '5':
            self._show_recent_transactions()
    
    def _show_transaction_summary(self):
        """Show overall transaction summary"""
        self.clear_screen()
        self.print_header("🔄 TRANSACTION SUMMARY")
        
        summary = self.query("""
            SELECT 
                COUNT(*) as total_transactions,
                COUNT(DISTINCT security_id) as unique_securities,
                SUM(trade_quantity) as total_volume,
                SUM(trade_amount) as total_turnover,
                MIN(trade_date) as earliest_date,
                MAX(trade_date) as latest_date
            FROM transactions
        """)
        
        if summary:
            s = summary[0]
            print(f"\n📊 Overall Statistics:")
            print(f"  Total Transactions: {s['total_transactions']:,}")
            print(f"  Unique Securities: {s['unique_securities']:,}")
            print(f"  Total Volume: {s['total_volume']:,} shares")
            print(f"  Total Turnover: Rs. {s['total_turnover']:,.2f}")
            print(f"  Date Range: {s['earliest_date']} to {s['latest_date']}")
        
        # Today's summary
        today_summary = self.query("""
            SELECT 
                COUNT(*) as total_transactions,
                COUNT(DISTINCT security_id) as unique_securities,
                SUM(trade_quantity) as total_volume,
                SUM(trade_amount) as total_turnover
            FROM transactions
            WHERE trade_date = (SELECT MAX(trade_date) FROM transactions)
        """)
        
        if today_summary and today_summary[0]['total_transactions']:
            ts = today_summary[0]
            print(f"\n📅 Latest Trading Day:")
            print(f"  Transactions: {ts['total_transactions']:,}")
            print(f"  Unique Securities: {ts['unique_securities']:,}")
            print(f"  Volume: {ts['total_volume']:,} shares")
            print(f"  Turnover: Rs. {ts['total_turnover']:,.2f}")
        
        self.wait_for_enter()
    
    def _search_transactions(self):
        """Search transactions by symbol"""
        self.clear_screen()
        self.print_header("🔍 SEARCH TRANSACTIONS")
        
        symbol = input("\nEnter company symbol: ").strip().upper()
        
        if not symbol:
            return
        
        transactions = self.query("""
            SELECT 
                t.trade_date,
                t.trade_time,
                c.symbol,
                t.trade_quantity,
                t.trade_price,
                t.trade_amount,
                t.buyer_member_id,
                t.seller_member_id
            FROM transactions t
            JOIN securities s ON t.security_id = s.security_id
            JOIN companies c ON s.company_id = c.company_id
            WHERE c.symbol = %s
            ORDER BY t.trade_date DESC, t.trade_time DESC
            LIMIT 100
        """, (symbol,))
        
        if not transactions:
            print(f"\n⚠️  No transactions found for {symbol}.")
            self.wait_for_enter()
            return
        
        print(f"\nShowing latest 100 transactions for {symbol}")
        print(f"\n{'Date':<12} {'Time':<10} {'Quantity':>12} {'Price':>12} {'Amount':>15} {'Buyer':>8} {'Seller':>8}")
        print("-" * 95)
        
        for t in transactions[:50]:  # Show first 50
            print(f"{t['trade_date']} {str(t['trade_time']):<10} {t['trade_quantity']:>12,} "
                  f"{t['trade_price']:>12.2f} Rs. {t['trade_amount']:>12,.2f} "
                  f"{t['buyer_member_id']:>8} {t['seller_member_id']:>8}")
        
        if len(transactions) > 50:
            print(f"\n... and {len(transactions) - 50} more transactions (showing first 50)")
        
        self.wait_for_enter()
    
    def _show_top_buyers(self):
        """Show top buyers by volume"""
        self.clear_screen()
        self.print_header("👥 TOP BUYERS (By Volume)")
        
        buyers = self.query("""
            SELECT 
                buyer_member_id,
                COUNT(*) as trade_count,
                SUM(trade_quantity) as total_volume,
                SUM(trade_amount) as total_amount
            FROM transactions
            WHERE trade_date = (SELECT MAX(trade_date) FROM transactions)
            GROUP BY buyer_member_id
            ORDER BY total_volume DESC
            LIMIT 20
        """)
        
        if buyers:
            print(f"\n{'#':<4} {'Buyer ID':>10} {'Trades':>10} {'Volume':>15} {'Amount (Rs)':>18}")
            print("-" * 70)
            for idx, b in enumerate(buyers, 1):
                print(f"{idx:<4} {b['buyer_member_id']:>10} {b['trade_count']:>10,} "
                      f"{b['total_volume']:>15,} Rs. {b['total_amount']:>14,.2f}")
        else:
            print("\n⚠️  No transaction data available.")
        
        self.wait_for_enter()
    
    def _show_top_sellers(self):
        """Show top sellers by volume"""
        self.clear_screen()
        self.print_header("👥 TOP SELLERS (By Volume)")
        
        sellers = self.query("""
            SELECT 
                seller_member_id,
                COUNT(*) as trade_count,
                SUM(trade_quantity) as total_volume,
                SUM(trade_amount) as total_amount
            FROM transactions
            WHERE trade_date = (SELECT MAX(trade_date) FROM transactions)
            GROUP BY seller_member_id
            ORDER BY total_volume DESC
            LIMIT 20
        """)
        
        if sellers:
            print(f"\n{'#':<4} {'Seller ID':>10} {'Trades':>10} {'Volume':>15} {'Amount (Rs)':>18}")
            print("-" * 70)
            for idx, s in enumerate(sellers, 1):
                print(f"{idx:<4} {s['seller_member_id']:>10} {s['trade_count']:>10,} "
                      f"{s['total_volume']:>15,} Rs. {s['total_amount']:>14,.2f}")
        else:
            print("\n⚠️  No transaction data available.")
        
        self.wait_for_enter()
    
    def _show_recent_transactions(self):
        """Show most recent transactions"""
        self.clear_screen()
        self.print_header("🕐 RECENT TRANSACTIONS")
        
        transactions = self.query("""
            SELECT 
                t.trade_date,
                t.trade_time,
                c.symbol,
                t.trade_quantity,
                t.trade_price,
                t.trade_amount
            FROM transactions t
            JOIN securities s ON t.security_id = s.security_id
            JOIN companies c ON s.company_id = c.company_id
            ORDER BY t.trade_date DESC, t.trade_time DESC
            LIMIT 50
        """)
        
        if transactions:
            print(f"\n{'Date':<12} {'Time':<10} {'Symbol':<10} {'Quantity':>12} {'Price':>12} {'Amount (Rs)':>18}")
            print("-" * 90)
            for t in transactions:
                print(f"{t['trade_date']} {str(t['trade_time']):<10} {t['symbol']:<10} "
                      f"{t['trade_quantity']:>12,} {t['trade_price']:>12.2f} Rs. {t['trade_amount']:>14,.2f}")
        else:
            print("\n⚠️  No transaction data available.")
        
        self.wait_for_enter()
    
    # ==================== MENU 7: DATABASE STATISTICS ====================
    
    def show_database_stats(self):
        """Display database statistics"""
        self.clear_screen()
        self.print_header("📊 DATABASE STATISTICS")
        
        tables = [
            'sectors', 'companies', 'securities', 'security_types',
            'market_summary', 'security_prices', 'indices', 'index_values',
            'transactions', 'brokers', 'broker_branches'
        ]
        
        print(f"\n{'Table Name':<25} {'Row Count':>15} {'Status':>10}")
        print("-" * 60)
        
        for table in tables:
            try:
                count = self.query(f"SELECT COUNT(*) as count FROM {table}")
                row_count = count[0]['count'] if count else 0
                status = '✅' if row_count > 0 else '⚠️ '
                print(f"{table:<25} {row_count:>15,} {status:>10}")
            except:
                print(f"{table:<25} {'ERROR':>15} {'❌':>10}")
        
        # Data freshness
        print("\n" + "=" * 60)
        print("DATA FRESHNESS")
        print("=" * 60)
        
        freshness_checks = [
            ("Latest Market Summary", "SELECT MAX(trading_date) as date FROM market_summary"),
            ("Latest Index Values", "SELECT MAX(trading_date) as date FROM index_values"),
            ("Latest Security Prices", "SELECT MAX(trading_date) as date FROM security_prices"),
            ("Latest Transactions", "SELECT MAX(trade_date) as date FROM transactions")
        ]
        
        for label, query in freshness_checks:
            result = self.query(query)
            if result and result[0]['date']:
                latest_date = result[0]['date']
                days_old = (date.today() - latest_date).days
                status = '✅ Current' if days_old == 0 else f'⚠️  {days_old} days old'
                print(f"{label:<30}: {latest_date} ({status})")
            else:
                print(f"{label:<30}: No data available")
        
        self.wait_for_enter()
    
    # ==================== MAIN MENU ====================
    
    def show_main_menu(self):
        """Display main menu"""
        self.clear_screen()
        self.print_header("📈 NEPSE DATA VIEWER - Main Menu")
        
        print("\n1. 📊 Market Overview")
        print("2. 🏆 Top Performers")
        print("3. 🔍 Company/Security Lookup")
        print("4. 🏢 Sector Analysis")
        print("5. 📈 Price History")
        print("6. 🔄 Transaction Analysis")
        print("7. 📊 Database Statistics")
        print("0. 🚪 Exit")
        
        choice = input("\nSelect option: ").strip()
        return choice
    
    def run(self):
        """Main application loop"""
        if not self.connect():
            return
        
        try:
            while True:
                choice = self.show_main_menu()
                
                if choice == '0':
                    self.clear_screen()
                    print("\n👋 Thank you for using NEPSE Data Viewer!\n")
                    break
                elif choice == '1':
                    self.show_market_overview()
                elif choice == '2':
                    self.show_top_performers()
                elif choice == '3':
                    self.show_company_lookup()
                elif choice == '4':
                    self.show_sector_analysis()
                elif choice == '5':
                    self.show_price_history()
                elif choice == '6':
                    self.show_transaction_analysis()
                elif choice == '7':
                    self.show_database_stats()
                else:
                    print("\n⚠️  Invalid option. Please try again.")
                    self.wait_for_enter()
                    
        except KeyboardInterrupt:
            self.clear_screen()
            print("\n\n👋 Application interrupted. Goodbye!\n")
        finally:
            self.close()


def main():
    """Entry point"""
    viewer = NepseDataViewer(DB_CONFIG)
    viewer.run()


if __name__ == "__main__":
    main()
