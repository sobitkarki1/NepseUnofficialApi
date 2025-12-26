"""Test script to explore NepseUnofficialApi features"""
import json
import sys
from nepse import Nepse

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Initialize Nepse
nepse = Nepse()
nepse.setTLSVerification(False)

print("=" * 80)
print("Testing NEPSE Unofficial API - Gathering Sample Data")
print("=" * 80)

# Test basic market status
print("\n1. Testing Market Status...")
try:
    market_status = nepse.getMarketStatus()
    print(f"   [OK] Market Status: {json.dumps(market_status, indent=2)[:200]}...")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test summary
print("\n2. Testing Summary...")
try:
    summary = nepse.getSummary()
    print(f"   [OK] Summary (first 3 items): {json.dumps(summary[:3] if isinstance(summary, list) else summary, indent=2)}")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test company list
print("\n3. Testing Company List...")
try:
    companies = nepse.getCompanyList()
    print(f"   [OK] Total Companies: {len(companies)}")
    print(f"   [OK] Sample Company: {json.dumps(companies[0], indent=2) if companies else 'No data'}")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test security list
print("\n4. Testing Security List...")
try:
    securities = nepse.getSecurityList()
    print(f"   [OK] Total Securities: {len(securities)}")
    print(f"   [OK] Sample Security: {json.dumps(securities[0], indent=2) if securities else 'No data'}")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test top gainers
print("\n5. Testing Top Gainers...")
try:
    gainers = nepse.getTopGainers()
    print(f"   [OK] Top Gainers: {json.dumps(gainers[:2] if isinstance(gainers, list) else gainers, indent=2)}")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test top losers
print("\n6. Testing Top Losers...")
try:
    losers = nepse.getTopLosers()
    print(f"   [OK] Top Losers: {json.dumps(losers[:2] if isinstance(losers, list) else losers, indent=2)}")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test Nepse Index
print("\n7. Testing NEPSE Index...")
try:
    nepse_index = nepse.getNepseIndex()
    print(f"   [OK] NEPSE Index: {json.dumps(nepse_index[:2] if isinstance(nepse_index, list) else nepse_index, indent=2)}")
except Exception as e:
    print(f"   [ERROR] {e}")

# Test with a specific symbol
print("\n8. Testing Symbol-Specific Methods...")
try:
    # Get a sample symbol from companies
    companies = nepse.getCompanyList()
    if companies:
        sample_symbol = companies[0]['symbol']
        print(f"   Using symbol: {sample_symbol}")
        
        # Test company details
        try:
            details = nepse.getCompanyDetails(sample_symbol)
            print(f"   [OK] Company Details keys: {list(details.keys()) if isinstance(details, dict) else 'N/A'}")
        except Exception as e:
            print(f"   [ERROR] Company Details: {e}")
        
        # Test market depth
        try:
            depth = nepse.getSymbolMarketDepth(sample_symbol)
            print(f"   [OK] Market Depth keys: {list(depth.keys()) if isinstance(depth, dict) else 'N/A'}")
        except Exception as e:
            print(f"   [ERROR] Market Depth: {e}")
except Exception as e:
    print(f"   [ERROR] {e}")

print("\n" + "=" * 80)
print("Testing Complete!")
print("=" * 80)
