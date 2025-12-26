"""
Real-time NEPSE Market Monitor
Displays live market data with auto-refresh
"""

import os
import time
from datetime import datetime
from nepse import Nepse


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def format_number(num, decimals=2):
    """Format number with commas and decimals"""
    if num is None:
        return "N/A"
    try:
        return f"{float(num):,.{decimals}f}"
    except:
        return str(num)


def format_change(change):
    """Format percentage change with color indicator"""
    try:
        change_val = float(change)
        if change_val > 0:
            return f"+{change_val:.2f}% ↑"
        elif change_val < 0:
            return f"{change_val:.2f}% ↓"
        else:
            return f"{change_val:.2f}% ="
    except:
        return str(change)


def print_header():
    """Print the header banner"""
    print("=" * 100)
    print(" " * 30 + "🚀 NEPSE REAL-TIME MARKET MONITOR 🚀")
    print("=" * 100)


def print_market_status(nepse):
    """Print current market status and summary"""
    try:
        status = nepse.getMarketStatus()
        summary = nepse.getSummary()
        
        print(f"\n⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Market Status: {status.get('isOpen', 'UNKNOWN')}")
        
        if summary:
            print("\n" + "=" * 100)
            print("📈 MARKET SUMMARY")
            print("=" * 100)
            for item in summary:
                detail = item.get('detail', 'N/A')
                value = item.get('value', 'N/A')
                print(f"  {detail:.<50} {value:>45}")
    except Exception as e:
        print(f"❌ Error fetching market status: {e}")


def print_nepse_index(nepse):
    """Print NEPSE main index"""
    try:
        index_data = nepse.getNepseIndex()
        if index_data:
            print("\n" + "=" * 100)
            print("🎯 NEPSE INDEX")
            print("=" * 100)
            print(f"  Index: {format_number(index_data.get('index', 0))}")
            print(f"  Change: {format_change(index_data.get('percentageChange', 0))}")
            print(f"  Point Change: {format_number(index_data.get('pointChange', 0))}")
    except Exception as e:
        print(f"❌ Error fetching index: {e}")


def print_top_gainers_losers(nepse):
    """Print top gainers and losers side by side"""
    try:
        gainers = nepse.getTopGainers()
        losers = nepse.getTopLosers()
        
        print("\n" + "=" * 100)
        print("💹 TOP 10 GAINERS" + " " * 30 + "📉 TOP 10 LOSERS")
        print("=" * 100)
        
        max_rows = max(len(gainers), len(losers))
        for i in range(min(10, max_rows)):
            # Gainer
            if i < len(gainers):
                g = gainers[i]
                gainer_text = f"{i+1:2d}. {g.get('symbol', 'N/A')[:8]:8s} Rs.{format_number(g.get('ltp', 0), 2):>10s} {format_change(g.get('percentageChange', 0)):>12s}"
            else:
                gainer_text = " " * 48
            
            # Loser
            if i < len(losers):
                l = losers[i]
                loser_text = f"{i+1:2d}. {l.get('symbol', 'N/A')[:8]:8s} Rs.{format_number(l.get('ltp', 0), 2):>10s} {format_change(l.get('percentageChange', 0)):>12s}"
            else:
                loser_text = ""
            
            print(f"  {gainer_text}    {loser_text}")
    except Exception as e:
        print(f"❌ Error fetching top gainers/losers: {e}")


def print_most_active(nepse):
    """Print most active stocks"""
    try:
        turnover_stocks = nepse.getTopTenTurnoverScrips()
        trade_stocks = nepse.getTopTenTradeScrips()
        
        print("\n" + "=" * 100)
        print("💰 TOP TURNOVER" + " " * 32 + "📊 TOP VOLUME")
        print("=" * 100)
        
        max_rows = max(len(turnover_stocks), len(trade_stocks))
        for i in range(min(10, max_rows)):
            # Turnover
            if i < len(turnover_stocks):
                t = turnover_stocks[i]
                turnover_text = f"{i+1:2d}. {t.get('symbol', 'N/A')[:8]:8s} Rs.{format_number(t.get('turnover', 0), 0):>15s}"
            else:
                turnover_text = " " * 48
            
            # Volume
            if i < len(trade_stocks):
                v = trade_stocks[i]
                volume_text = f"{i+1:2d}. {v.get('symbol', 'N/A')[:8]:8s} {format_number(v.get('shareTraded', 0), 0):>15s} shares"
            else:
                volume_text = ""
            
            print(f"  {turnover_text}    {volume_text}")
    except Exception as e:
        print(f"❌ Error fetching most active stocks: {e}")


def print_live_market_sample(nepse):
    """Print sample of live market data"""
    try:
        live_data = nepse.getLiveMarket()
        if live_data and len(live_data) > 0:
            print("\n" + "=" * 100)
            print("🔴 LIVE MARKET DATA (Sample - First 15 stocks)")
            print("=" * 100)
            print(f"  {'Symbol':<10} {'LTP':>12} {'Change':>12} {'High':>12} {'Low':>12} {'Volume':>15}")
            print("-" * 100)
            
            for i, stock in enumerate(live_data[:15]):
                symbol = stock.get('symbol', 'N/A')[:10]
                ltp = format_number(stock.get('lastTradedPrice', 0), 2)
                change = format_change(stock.get('percentageChange', 0))
                high = format_number(stock.get('highPrice', 0), 2)
                low = format_number(stock.get('lowPrice', 0), 2)
                volume = format_number(stock.get('totalTradeQuantity', 0), 0)
                
                print(f"  {symbol:<10} Rs.{ltp:>9} {change:>12} Rs.{high:>9} Rs.{low:>9} {volume:>15}")
    except Exception as e:
        print(f"❌ Error fetching live market: {e}")


def print_sub_indices(nepse):
    """Print sub-indices"""
    try:
        sub_indices = nepse.getNepseSubIndices()
        if sub_indices and len(sub_indices) > 0:
            print("\n" + "=" * 100)
            print("📊 SECTOR INDICES")
            print("=" * 100)
            
            # Display in 2 columns
            for i in range(0, len(sub_indices), 2):
                left = sub_indices[i]
                left_text = f"{left.get('index', 'N/A')[:25]:25s}: {format_number(left.get('indexValue', 0)):>12s} ({format_change(left.get('percentageChange', 0))})"
                
                if i + 1 < len(sub_indices):
                    right = sub_indices[i + 1]
                    right_text = f"{right.get('index', 'N/A')[:25]:25s}: {format_number(right.get('indexValue', 0)):>12s} ({format_change(right.get('percentageChange', 0))})"
                else:
                    right_text = ""
                
                print(f"  {left_text:48s}  {right_text}")
    except Exception as e:
        print(f"❌ Error fetching sub-indices: {e}")


def display_realtime_data(nepse, refresh_interval=10):
    """Main display function with auto-refresh"""
    
    print("\n🚀 Starting Real-time Market Monitor...")
    print(f"⏱️  Refresh Interval: {refresh_interval} seconds")
    print("⌨️  Press Ctrl+C to stop\n")
    time.sleep(2)
    
    iteration = 0
    
    try:
        while True:
            iteration += 1
            clear_screen()
            
            print_header()
            print_market_status(nepse)
            print_nepse_index(nepse)
            print_top_gainers_losers(nepse)
            print_most_active(nepse)
            print_sub_indices(nepse)
            print_live_market_sample(nepse)
            
            print("\n" + "=" * 100)
            print(f"🔄 Refresh #{iteration} | Next refresh in {refresh_interval} seconds | Press Ctrl+C to stop")
            print("=" * 100)
            
            time.sleep(refresh_interval)
            
    except KeyboardInterrupt:
        print("\n\n✋ Stopped by user")
        print("👋 Thank you for using NEPSE Real-time Monitor!")
    except Exception as e:
        print(f"\n❌ Critical Error: {e}")


def main():
    """Main entry point"""
    print("🔧 Initializing NEPSE API...")
    
    try:
        nepse = Nepse()
        nepse.setTLSVerification(False)
        
        print("✅ API initialized successfully!")
        
        # Check if market is open
        status = nepse.getMarketStatus()
        if status.get('isOpen') == 'OPEN':
            print("✅ Market is OPEN - Starting real-time monitoring...")
            display_realtime_data(nepse, refresh_interval=10)
        else:
            print("⚠️  Market is CLOSED, but showing latest available data...")
            print("📊 Data will be from the last trading session\n")
            time.sleep(2)
            display_realtime_data(nepse, refresh_interval=30)
            
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        print("💡 Make sure you have internet connection and the NEPSE website is accessible")


if __name__ == "__main__":
    main()
