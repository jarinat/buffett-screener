"""Financial statement data models."""
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field
class FinancialStatement(BaseModel):
    """Base class for financial statements."""
    period_end_date: date = Field(..., description="End date of the reporting period")
    fiscal_year: int = Field(..., description="Fiscal year")
    fiscal_period: str = Field(..., description="Fiscal period (Q1, Q2, Q3, Q4, FY)")
    currency: str = Field(default="USD", description="Currency code")
class IncomeStatement(FinancialStatement):
    """Income statement data."""
    revenue: Optional[float] = Field(None, description="Total revenue")
    cost_of_revenue: Optional[float] = Field(None, description="Cost of goods sold")
    gross_profit: Optional[float] = Field(None, description="Gross profit")
    operating_expenses: Optional[float] = Field(None, description="Operating expenses")
    operating_income: Optional[float] = Field(None, description="Operating income")
    net_income: Optional[float] = Field(None, description="Net income")
    earnings_per_share: Optional[float] = Field(None, description="Earnings per share (basic)")
    earnings_per_share_diluted: Optional[float] = Field(None, description="Earnings per share (diluted)")
class BalanceSheet(FinancialStatement):
    """Balance sheet data."""
    total_assets: Optional[float] = Field(None, description="Total assets")
    current_assets: Optional[float] = Field(None, description="Current assets")
    cash_and_equivalents: Optional[float] = Field(None, description="Cash and cash equivalents")
    total_liabilities: Optional[float] = Field(None, description="Total liabilities")
    current_liabilities: Optional[float] = Field(None, description="Current liabilities")
    long_term_debt: Optional[float] = Field(None, description="Long-term debt")
    shareholders_equity: Optional[float] = Field(None, description="Shareholders' equity")
class CashFlow(FinancialStatement):
    """Cash flow statement data."""
    operating_cash_flow: Optional[float] = Field(None, description="Cash from operating activities")
    investing_cash_flow: Optional[float] = Field(None, description="Cash from investing activities")
    financing_cash_flow: Optional[float] = Field(None, description="Cash from financing activities")
    free_cash_flow: Optional[float] = Field(None, description="Free cash flow")
    capital_expenditure: Optional[float] = Field(None, description="Capital expenditures")
