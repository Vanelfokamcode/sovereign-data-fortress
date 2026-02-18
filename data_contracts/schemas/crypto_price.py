# data_contracts/schemas/crypto_price.py
"""
Data Contract Schema for Crypto Price Data

This is our formal agreement with the API:
- What fields we expect
- What types they should be
- What constraints they must satisfy
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class CryptoPriceContract(BaseModel):
    """
    Contract for crypto price data from external API
    
    This schema ensures:
    - Price is always a positive number
    - Symbol is always uppercase
    - Timestamp is valid
    - Volume is non-negative
    """
    
    # Required fields with constraints
    symbol: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="Cryptocurrency symbol (e.g., BTC, ETH)"
    )
    
    price: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Current price in USD (must be positive)"
    )
    
    timestamp: datetime = Field(
        ...,
        description="When the price was recorded"
    )
    
    volume: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Trading volume (if available, must be non-negative)"
    )
    
    # Optional metadata
    market_cap: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Market capitalization"
    )
    
    # Validators (custom business logic)
    
    @validator('symbol')
    def symbol_must_be_uppercase(cls, v):
        """Enforce uppercase symbols"""
        if not v.isupper():
            raise ValueError(f"Symbol must be uppercase, got: {v}")
        return v
    
    @validator('price')
    def price_must_be_reasonable(cls, v):
        """Detect obviously wrong prices"""
        # Bitcoin will never be $1 million (probably)
        # and never be $0.01
        if v > 1_000_000:
            raise ValueError(f"Price suspiciously high: ${v}")
        if v < 0.01:
            raise ValueError(f"Price suspiciously low: ${v}")
        return v
    
    @validator('timestamp')
    def timestamp_must_be_recent(cls, v):
        """Ensure data is not too old"""
        now = datetime.now()
        age_hours = (now - v).total_seconds() / 3600
        
        # Data older than 24 hours is suspicious
        if age_hours > 24:
            raise ValueError(
                f"Data is {age_hours:.1f} hours old. "
                f"Expected recent data."
            )
        
        # Data from the future is obviously wrong
        if v > now:
            raise ValueError(f"Timestamp is in the future: {v}")
        
        return v
    
    class Config:
        # Example valid data
        schema_extra = {
            "example": {
                "symbol": "BTC",
                "price": 42000.50,
                "timestamp": "2024-02-17T10:00:00Z",
                "volume": 1234567.89,
                "market_cap": 800000000000.00
            }
        }

# Example invalid data that would be REJECTED:

INVALID_EXAMPLES = [
    {
        "reason": "Price negative",
        "data": {"symbol": "BTC", "price": -100, "timestamp": datetime.now()}
    },
    {
        "reason": "Symbol lowercase",
        "data": {"symbol": "btc", "price": 42000, "timestamp": datetime.now()}
    },
    {
        "reason": "Price too high (anomaly)",
        "data": {"symbol": "BTC", "price": 5_000_000, "timestamp": datetime.now()}
    },
    {
        "reason": "Timestamp in future",
        "data": {"symbol": "BTC", "price": 42000, "timestamp": datetime(2030, 1, 1)}
    },
    {
        "reason": "Volume negative",
        "data": {"symbol": "BTC", "price": 42000, "timestamp": datetime.now(), "volume": -100}
    }
]
