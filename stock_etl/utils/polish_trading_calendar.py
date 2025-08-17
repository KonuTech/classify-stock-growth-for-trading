"""
Polish Trading Calendar - Warsaw Stock Exchange

This module provides trading day validation for the Warsaw Stock Exchange (WSE),
including Polish public holidays and custom market closures.

WSE Trading Schedule:
- Trading Days: Monday-Friday
- Trading Hours: 9:00-17:00 CET/CEST
- Excludes: Polish public holidays and special market closures

Author: Stock ETL Pipeline
Created: 2025-08-17
"""

from datetime import datetime, date, timedelta
from typing import Set, List
import holidays


class PolishTradingCalendar:
    """Polish Stock Exchange trading calendar with holiday exclusions."""
    
    def __init__(self, years: List[int] = None):
        """
        Initialize Polish trading calendar.
        
        Args:
            years: List of years to include. Defaults to 1990-2030.
        """
        if years is None:
            # Cover historical data from 1990 to future years
            years = list(range(1990, 2031))
        
        self.years = years
        self.polish_holidays = holidays.Poland(years=years)
        
        # Additional WSE-specific closures (if any)
        self.custom_closures = self._get_custom_market_closures()
    
    def _get_custom_market_closures(self) -> Set[date]:
        """
        Get custom market closures not covered by standard Polish holidays.
        
        Returns:
            Set of additional closure dates
        """
        custom_closures = set()
        
        # Example: Special market closures (if any historical ones)
        # Add specific dates when WSE was closed but not a public holiday
        
        # Note: Add any known historical market closures here
        # e.g., custom_closures.add(date(2020, 3, 16))  # COVID-related closure
        
        return custom_closures
    
    def is_trading_day(self, check_date: date) -> bool:
        """
        Check if a given date is a trading day.
        
        Args:
            check_date: Date to check
            
        Returns:
            True if it's a trading day, False otherwise
        """
        # Check if it's a weekend
        if check_date.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
        
        # Check if it's a Polish public holiday
        if check_date in self.polish_holidays:
            return False
        
        # Check custom market closures
        if check_date in self.custom_closures:
            return False
        
        return True
    
    def get_trading_days_in_range(self, start_date: date, end_date: date) -> List[date]:
        """
        Get all trading days in a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of trading days in the range
        """
        trading_days = []
        current_date = start_date
        
        while current_date <= end_date:
            if self.is_trading_day(current_date):
                trading_days.append(current_date)
            current_date += timedelta(days=1)
        
        return trading_days
    
    def get_previous_trading_day(self, reference_date: date = None) -> date:
        """
        Get the previous trading day before the reference date.
        
        Args:
            reference_date: Reference date. Defaults to today.
            
        Returns:
            Previous trading day
        """
        if reference_date is None:
            reference_date = date.today()
        
        check_date = reference_date - timedelta(days=1)
        
        while not self.is_trading_day(check_date):
            check_date -= timedelta(days=1)
        
        return check_date
    
    def get_next_trading_day(self, reference_date: date = None) -> date:
        """
        Get the next trading day after the reference date.
        
        Args:
            reference_date: Reference date. Defaults to today.
            
        Returns:
            Next trading day
        """
        if reference_date is None:
            reference_date = date.today()
        
        check_date = reference_date + timedelta(days=1)
        
        while not self.is_trading_day(check_date):
            check_date += timedelta(days=1)
        
        return check_date
    
    def get_trading_days_this_month(self, year: int = None, month: int = None) -> List[date]:
        """
        Get all trading days in a specific month.
        
        Args:
            year: Year to check. Defaults to current year.
            month: Month to check. Defaults to current month.
            
        Returns:
            List of trading days in the month
        """
        if year is None:
            year = date.today().year
        if month is None:
            month = date.today().month
        
        # Get first and last day of month
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        return self.get_trading_days_in_range(first_day, last_day)
    
    def is_market_open_now(self) -> bool:
        """
        Check if the market is currently open (considering trading hours).
        
        Returns:
            True if market is open now, False otherwise
        """
        now = datetime.now()
        today = now.date()
        
        # Check if today is a trading day
        if not self.is_trading_day(today):
            return False
        
        # Check trading hours (9:00-17:00 CET/CEST)
        market_open = now.replace(hour=9, minute=0, second=0, microsecond=0)
        market_close = now.replace(hour=17, minute=0, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    def get_holiday_name(self, check_date: date) -> str:
        """
        Get the name of the holiday for a given date.
        
        Args:
            check_date: Date to check
            
        Returns:
            Holiday name if it's a holiday, empty string otherwise
        """
        if check_date in self.polish_holidays:
            return self.polish_holidays[check_date]
        elif check_date in self.custom_closures:
            return "Market Closure"
        else:
            return ""


# Global instance for easy import
polish_calendar = PolishTradingCalendar()


def should_run_etl_today(check_date: date = None) -> bool:
    """
    Convenience function to check if ETL should run for a given date.
    
    Args:
        check_date: Date to check. Defaults to today.
        
    Returns:
        True if ETL should run, False otherwise
    """
    if check_date is None:
        check_date = date.today()
    
    return polish_calendar.is_trading_day(check_date)


def get_etl_target_date(reference_date: date = None) -> date:
    """
    Get the target date for ETL processing.
    
    For daily runs: previous trading day
    For backfill: the execution date itself
    
    Args:
        reference_date: Reference date. Defaults to today.
        
    Returns:
        Target date for ETL processing
    """
    if reference_date is None:
        reference_date = date.today()
    
    # For daily incremental runs, we process the previous trading day's data
    return polish_calendar.get_previous_trading_day(reference_date)


if __name__ == "__main__":
    # Example usage and testing
    calendar = PolishTradingCalendar()
    
    today = date.today()
    print(f"Today ({today}): Trading day = {calendar.is_trading_day(today)}")
    
    if not calendar.is_trading_day(today):
        holiday_name = calendar.get_holiday_name(today)
        if holiday_name:
            print(f"Today is a holiday: {holiday_name}")
        else:
            print("Today is a weekend")
    
    prev_trading_day = calendar.get_previous_trading_day()
    print(f"Previous trading day: {prev_trading_day}")
    
    next_trading_day = calendar.get_next_trading_day()
    print(f"Next trading day: {next_trading_day}")
    
    # Check this month's trading days
    trading_days = calendar.get_trading_days_this_month()
    print(f"Trading days this month: {len(trading_days)}")
    
    # Market status
    market_open = calendar.is_market_open_now()
    print(f"Market open now: {market_open}")