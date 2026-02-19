# ingestion/connectors/crypto_api.py
"""
Crypto API Connector - Airbyte-style

This connector extracts data from CoinGecko API
and follows Airbyte patterns:
- Check connection
- Discover schema
- Read records (with state)
"""

import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

class CryptoAPIConnector:
    """
    Source connector for CoinGecko API
    
    Airbyte concepts implemented:
    - check_connection()
    - discover_schema()
    - read_records()
    - supports incremental sync
    """
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or ['bitcoin', 'ethereum', 'solana']
        self.last_sync_time = None
    
    def check_connection(self) -> Dict[str, Any]:
        """
        Test if we can connect to the API
        (Airbyte standard method)
        """
        try:
            response = requests.get(
                f"{self.BASE_URL}/ping",
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "status": "success",
                    "message": "Connection successful"
                }
            else:
                return {
                    "status": "failed",
                    "message": f"API returned {response.status_code}"
                }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Connection error: {str(e)}"
            }
    
    def discover_schema(self) -> Dict[str, Any]:
        """
        Discover available data schema
        (Airbyte standard method)
        """
        return {
            "streams": [
                {
                    "name": "crypto_prices",
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "symbol": {"type": "string"},
                            "name": {"type": "string"},
                            "current_price": {"type": "number"},
                            "market_cap": {"type": "number"},
                            "total_volume": {"type": "number"},
                            "price_change_24h": {"type": "number"},
                            "last_updated": {"type": "string"}
                        }
                    },
                    "supported_sync_modes": ["full_refresh", "incremental"]
                }
            ]
        }
    
    def read_records(
        self,
        sync_mode: str = "full_refresh",
        state: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Read records from API
        
        Args:
            sync_mode: 'full_refresh' or 'incremental'
            state: Last sync state (for incremental)
        
        Returns:
            List of records
        """
        
        print(f"📥 Extracting data (mode: {sync_mode})...")
        
        # Get price data for multiple coins
        symbols_param = ','.join(self.symbols)
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/coins/markets",
                params={
                    'vs_currency': 'usd',
                    'ids': symbols_param,
                    'order': 'market_cap_desc',
                    'per_page': 100,
                    'page': 1,
                    'sparkline': False
                },
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            records = []
            for coin in data:
                record = {
                    "id": coin.get("id"),
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name"),
                    "current_price": coin.get("current_price"),
                    "market_cap": coin.get("market_cap"),
                    "total_volume": coin.get("total_volume"),
                    "price_change_24h": coin.get("price_change_percentage_24h"),
                    "last_updated": coin.get("last_updated"),
                    "_airbyte_extracted_at": datetime.now().isoformat()
                }
                records.append(record)
            
            print(f"✅ Extracted {len(records)} records")
            return records
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API Error: {e}")
            return []
        except Exception as e:
            print(f"❌ Extraction error: {e}")
            return []
    
    def get_state(self) -> Dict[str, Any]:
        """Return current sync state"""
        return {
            "last_sync": datetime.now().isoformat(),
            "symbols": self.symbols
        }

def demo_connector():
    """Demo the connector (Airbyte-style workflow)"""
    
    print("🔌 CRYPTO API CONNECTOR DEMO")
    print("=" * 60)
    
    # Initialize connector
    connector = CryptoAPIConnector(
        symbols=['bitcoin', 'ethereum', 'solana', 'cardano']
    )
    
    # Step 1: Check connection
    print("\n1️⃣  Checking connection...")
    connection_status = connector.check_connection()
    print(f"   Status: {connection_status['status']}")
    print(f"   Message: {connection_status['message']}")
    
    if connection_status['status'] != 'success':
        print("❌ Cannot connect to API. Exiting.")
        return
    
    # Step 2: Discover schema
    print("\n2️⃣  Discovering schema...")
    schema = connector.discover_schema()
    print(f"   Available streams: {len(schema['streams'])}")
    stream = schema['streams'][0]
    print(f"   Stream name: {stream['name']}")
    print(f"   Sync modes: {stream['supported_sync_modes']}")
    
    # Step 3: Read records
    print("\n3️⃣  Reading records...")
    records = connector.read_records(sync_mode='full_refresh')
    
    if records:
        print(f"\n📊 Sample records:")
        for record in records[:3]:  # Show first 3
            print(f"\n   {record['symbol']} ({record['name']})")
            print(f"   Price: ${record['current_price']:,.2f}")
            print(f"   Market Cap: ${record['market_cap']:,.0f}")
            print(f"   24h Change: {record['price_change_24h']:.2f}%")
    
    # Step 4: Get state
    print("\n4️⃣  Sync state:")
    state = connector.get_state()
    print(f"   Last sync: {state['last_sync']}")
    print(f"   Symbols tracked: {', '.join(state['symbols'])}")
    
    print("\n" + "=" * 60)
    print("✅ Connector demo complete!")
    print("\n💡 This is how Airbyte connectors work:")
    print("   1. Check connection")
    print("   2. Discover what data is available")
    print("   3. Extract records")
    print("   4. Track state for incremental syncs")

if __name__ == "__main__":
    demo_connector()
