"""Pydantic models for data validation and type safety."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, validator
import hashlib


class InstrumentType(str, Enum):
    """Supported instrument types."""
    STOCK = "stock"
    INDEX = "index"
    ETF = "etf"
    BOND = "bond"
    FUTURE = "future"
    OPTION = "option"


class ExchangeCode(str, Enum):
    """Supported exchange codes."""
    WSE = "WSE"
    NEW_CONNECT = "NewConnect"
    CATALYST = "Catalyst"
    BOND_SPOT = "BondSpot"
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    LSE = "LSE"


class JobStatus(str, Enum):
    """ETL job status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class SeverityLevel(str, Enum):
    """Data quality severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class BaseInstrument(BaseModel):
    """Base instrument model for validation."""
    symbol: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=255)
    instrument_type: InstrumentType
    exchange_id: int
    currency: str = Field(default="PLN", min_length=3, max_length=3)
    is_active: bool = True
    first_trading_date: Optional[date] = None
    last_trading_date: Optional[date] = None

    @validator('symbol')
    def symbol_must_be_uppercase(cls, v):
        return v.upper().strip()

    @validator('currency')
    def currency_must_be_uppercase(cls, v):
        return v.upper().strip()


class StockData(BaseModel):
    """Stock-specific data model."""
    instrument_id: int
    company_name: str = Field(..., min_length=1, max_length=255)
    sector_id: Optional[int] = None
    market_cap: Optional[int] = Field(None, ge=0)
    shares_outstanding: Optional[int] = Field(None, ge=0)
    dividend_yield: Optional[Decimal] = Field(None, ge=0, le=1)
    pe_ratio: Optional[Decimal] = Field(None, ge=0)
    book_value: Optional[Decimal] = Field(None, ge=0)
    stock_type: str = Field(default="common", max_length=10)


class IndexData(BaseModel):
    """Index-specific data model."""
    instrument_id: int
    methodology: str = Field(default="market_cap_weighted", max_length=100)
    base_value: Decimal = Field(..., gt=0)
    base_date: date
    constituent_count: Optional[int] = Field(None, ge=0)
    calculation_frequency: str = Field(default="real_time", max_length=20)
    index_family: Optional[str] = Field(None, max_length=100)


class StooqRecord(BaseModel):
    """Raw Stooq data record from modern CSV format."""
    trading_date: date = Field(..., alias="Date")
    open_price: Decimal = Field(..., alias="Open", ge=0)
    high_price: Decimal = Field(..., alias="High", ge=0)
    low_price: Decimal = Field(..., alias="Low", ge=0)
    close_price: Decimal = Field(..., alias="Close", ge=0)
    volume: Decimal = Field(..., alias="Volume", ge=0)
    
    # These will be set programmatically
    ticker: str = Field(default="")
    period: str = Field(default="D")

    @validator('trading_date', pre=True)
    def parse_trading_date(cls, v):
        """Parse date from string format."""
        if isinstance(v, str):
            return datetime.strptime(v, '%Y-%m-%d').date()
        return v

    @validator('open_price', 'high_price', 'low_price', 'close_price')
    def prices_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Prices must be non-negative')
        return v

    @validator('high_price')
    def high_must_be_highest(cls, v, values):
        """Validate OHLC relationships."""
        if 'open_price' in values and 'low_price' in values and 'close_price' in values:
            open_p, low_p, close_p = values['open_price'], values['low_price'], values['close_price']
            if v < max(open_p, close_p) or v < low_p:
                raise ValueError('High price must be >= open, close, and low prices')
        return v

    @validator('low_price')
    def low_must_be_lowest(cls, v, values):
        """Validate OHLC relationships."""
        if 'open_price' in values and 'close_price' in values:
            open_p, close_p = values['open_price'], values['close_price']
            if v > min(open_p, close_p):
                raise ValueError('Low price must be <= open and close prices')
        return v

    def calculate_hash(self) -> str:
        """Calculate hash for duplicate detection."""
        data_string = f"{self.ticker}{self.trading_date}{self.open_price}{self.high_price}{self.low_price}{self.close_price}{self.volume}"
        return hashlib.sha256(data_string.encode()).hexdigest()

    class Config:
        populate_by_name = True


class StockPrice(BaseModel):
    """Stock price model for database insertion."""
    stock_id: int
    trading_date_local: date
    trading_date_utc: date
    trading_date_epoch: int
    trading_datetime_utc: Optional[datetime] = None
    trading_datetime_epoch: Optional[int] = None
    open_price: Decimal = Field(..., ge=0)
    high_price: Decimal = Field(..., ge=0)
    low_price: Decimal = Field(..., ge=0)
    close_price: Decimal = Field(..., ge=0)
    volume: int = Field(..., ge=0)
    adjusted_close: Optional[Decimal] = Field(None, ge=0)
    split_factor: Decimal = Field(default=Decimal('1.0'), gt=0)
    dividend_amount: Decimal = Field(default=Decimal('0.0'), ge=0)
    data_source: str = Field(default="stooq", max_length=50)
    raw_data_hash: Optional[str] = Field(None, max_length=64)

    @validator('high_price')
    def validate_ohlc(cls, v, values):
        """Validate OHLC price relationships."""
        if all(k in values for k in ['open_price', 'low_price', 'close_price']):
            o, l, c = values['open_price'], values['low_price'], values['close_price']
            if not (v >= max(o, c) and v >= l and l <= min(o, c)):
                raise ValueError('Invalid OHLC price relationship')
        return v


class IndexPrice(BaseModel):
    """Index price model for database insertion."""
    index_id: int
    trading_date_local: date
    trading_date_utc: date
    trading_date_epoch: int
    trading_datetime_utc: Optional[datetime] = None
    trading_datetime_epoch: Optional[int] = None
    open_value: Decimal = Field(..., ge=0)
    high_value: Decimal = Field(..., ge=0)
    low_value: Decimal = Field(..., ge=0)
    close_value: Decimal = Field(..., ge=0)
    trading_volume: int = Field(default=0, ge=0)
    total_market_cap: Optional[Decimal] = Field(None, ge=0)
    constituents_traded: Optional[int] = Field(None, ge=0)
    data_source: str = Field(default="stooq", max_length=50)
    raw_data_hash: Optional[str] = Field(None, max_length=64)


class ETLJob(BaseModel):
    """ETL job tracking model."""
    job_name: str = Field(..., max_length=100)
    job_type: str = Field(..., max_length=50)
    target_instrument_type: Optional[InstrumentType] = None
    status: JobStatus = JobStatus.PENDING
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    records_processed: int = 0
    records_inserted: int = 0
    records_updated: int = 0
    records_failed: int = 0
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    source_files: List[str] = []
    target_date_range_start: Optional[date] = None
    target_date_range_end: Optional[date] = None
    airflow_dag_id: Optional[str] = Field(None, max_length=100)
    airflow_task_id: Optional[str] = Field(None, max_length=100)
    airflow_run_id: Optional[str] = Field(None, max_length=100)
    metadata: Optional[dict] = None


class DataQualityMetric(BaseModel):
    """Data quality metric model."""
    job_id: Optional[int] = None
    instrument_id: int
    symbol: str = Field(..., max_length=20)
    instrument_type: InstrumentType
    metric_date: date
    metric_name: str = Field(..., max_length=100)
    metric_value: Optional[Decimal] = None
    threshold_min: Optional[Decimal] = None
    threshold_max: Optional[Decimal] = None
    is_valid: bool
    severity: SeverityLevel = SeverityLevel.INFO
    description: Optional[str] = None
    automated_check: bool = True


class ETLJobDetail(BaseModel):
    """ETL job detail tracking model."""
    job_id: int
    instrument_id: Optional[int] = None
    symbol: str = Field(..., max_length=20)
    operation: str = Field(..., max_length=20)  # insert, update, skip, error
    date_processed: date
    records_count: int = 1
    file_processed: Optional[str] = Field(None, max_length=500)
    line_number: Optional[int] = None
    error_details: Optional[str] = None
    processing_time_ms: Optional[int] = None