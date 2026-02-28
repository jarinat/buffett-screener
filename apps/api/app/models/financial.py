"""
Financial statement data models.

Defines canonical financial statement models that all providers must return.
These models are independent of any specific data source and follow a normalized
structure for income statements, balance sheets, and cash flow statements.
"""

from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class FinancialStatement(BaseModel):
    """Base class for all financial statement types."""

    company_id: str = Field(
        description="Unique identifier for the company (matches CompanyInfo.company_id)"
    )
    fiscal_year: int = Field(
        description="Fiscal year for this statement (e.g., 2023)"
    )
    period_end_date: date = Field(
        description="End date of the reporting period"
    )
    currency: str = Field(
        description="Currency of reported values (ISO 4217 code, e.g., 'USD')"
    )
    source_provider: str = Field(
        description="Data provider that supplied this statement (e.g., 'yahoo', 'sec')"
    )
    source_snapshot_id: Optional[str] = Field(
        default=None,
        description="Reference to the raw provider snapshot, if available",
    )


class IncomeStatement(FinancialStatement):
    """Income statement (Profit & Loss) data model."""

    revenue: Optional[Decimal] = Field(
        default=None,
        description="Total revenue (top line) for the period",
    )
    cost_of_revenue: Optional[Decimal] = Field(
        default=None,
        description="Direct costs attributable to revenue generation",
    )
    gross_profit: Optional[Decimal] = Field(
        default=None,
        description="Revenue minus cost of revenue",
    )
    operating_expenses: Optional[Decimal] = Field(
        default=None,
        description="Total operating expenses (SG&A, R&D, etc.)",
    )
    operating_income: Optional[Decimal] = Field(
        default=None,
        description="Income from operations before interest and taxes (EBIT)",
    )
    interest_expense: Optional[Decimal] = Field(
        default=None,
        description="Interest paid on debt obligations",
    )
    income_before_tax: Optional[Decimal] = Field(
        default=None,
        description="Income before income tax expense",
    )
    income_tax_expense: Optional[Decimal] = Field(
        default=None,
        description="Income tax expense for the period",
    )
    net_income: Optional[Decimal] = Field(
        default=None,
        description="Bottom line net income after all expenses and taxes",
    )
    eps_basic: Optional[Decimal] = Field(
        default=None,
        description="Basic earnings per share",
    )
    eps_diluted: Optional[Decimal] = Field(
        default=None,
        description="Diluted earnings per share (includes potential dilution)",
    )
    shares_outstanding_basic: Optional[int] = Field(
        default=None,
        description="Basic weighted average shares outstanding",
    )
    shares_outstanding_diluted: Optional[int] = Field(
        default=None,
        description="Diluted weighted average shares outstanding",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_id": "AAPL",
                "fiscal_year": 2023,
                "period_end_date": "2023-09-30",
                "currency": "USD",
                "source_provider": "yahoo",
                "source_snapshot_id": "snapshot_123",
                "revenue": "383285000000",
                "cost_of_revenue": "214137000000",
                "gross_profit": "169148000000",
                "operating_expenses": "54848000000",
                "operating_income": "114300000000",
                "net_income": "96995000000",
                "eps_diluted": "6.16",
            }
        }
    )


class BalanceSheet(FinancialStatement):
    """Balance sheet data model."""

    # Assets
    cash_and_equivalents: Optional[Decimal] = Field(
        default=None,
        description="Cash and cash equivalents",
    )
    short_term_investments: Optional[Decimal] = Field(
        default=None,
        description="Short-term marketable securities",
    )
    accounts_receivable: Optional[Decimal] = Field(
        default=None,
        description="Amounts owed by customers",
    )
    inventory: Optional[Decimal] = Field(
        default=None,
        description="Inventory on hand",
    )
    current_assets: Optional[Decimal] = Field(
        default=None,
        description="Total current assets (assets expected to be converted to cash within one year)",
    )
    property_plant_equipment: Optional[Decimal] = Field(
        default=None,
        description="Net property, plant, and equipment (PP&E)",
    )
    intangible_assets: Optional[Decimal] = Field(
        default=None,
        description="Goodwill and other intangible assets",
    )
    total_assets: Optional[Decimal] = Field(
        default=None,
        description="Total assets",
    )

    # Liabilities
    accounts_payable: Optional[Decimal] = Field(
        default=None,
        description="Amounts owed to suppliers",
    )
    short_term_debt: Optional[Decimal] = Field(
        default=None,
        description="Debt due within one year",
    )
    current_liabilities: Optional[Decimal] = Field(
        default=None,
        description="Total current liabilities (obligations due within one year)",
    )
    long_term_debt: Optional[Decimal] = Field(
        default=None,
        description="Debt due after one year",
    )
    total_liabilities: Optional[Decimal] = Field(
        default=None,
        description="Total liabilities",
    )

    # Equity
    common_stock: Optional[Decimal] = Field(
        default=None,
        description="Common stock par value",
    )
    retained_earnings: Optional[Decimal] = Field(
        default=None,
        description="Accumulated retained earnings",
    )
    shareholders_equity: Optional[Decimal] = Field(
        default=None,
        description="Total shareholders' equity (book value)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_id": "AAPL",
                "fiscal_year": 2023,
                "period_end_date": "2023-09-30",
                "currency": "USD",
                "source_provider": "yahoo",
                "source_snapshot_id": "snapshot_124",
                "total_assets": "352755000000",
                "current_assets": "143566000000",
                "total_liabilities": "290437000000",
                "current_liabilities": "145308000000",
                "shareholders_equity": "62318000000",
            }
        }
    )


class CashFlow(FinancialStatement):
    """Cash flow statement data model."""

    # Operating Activities
    net_income: Optional[Decimal] = Field(
        default=None,
        description="Net income (starting point for cash flow calculation)",
    )
    depreciation_amortization: Optional[Decimal] = Field(
        default=None,
        description="Non-cash depreciation and amortization expense",
    )
    changes_in_working_capital: Optional[Decimal] = Field(
        default=None,
        description="Net change in working capital accounts",
    )
    operating_cash_flow: Optional[Decimal] = Field(
        default=None,
        description="Net cash provided by operating activities",
    )

    # Investing Activities
    capital_expenditures: Optional[Decimal] = Field(
        default=None,
        description="Cash spent on PP&E and other capital investments (typically negative)",
    )
    acquisitions: Optional[Decimal] = Field(
        default=None,
        description="Cash spent on business acquisitions",
    )
    investment_purchases: Optional[Decimal] = Field(
        default=None,
        description="Cash spent on investment purchases",
    )
    investment_sales: Optional[Decimal] = Field(
        default=None,
        description="Cash received from investment sales",
    )
    investing_cash_flow: Optional[Decimal] = Field(
        default=None,
        description="Net cash used in investing activities",
    )

    # Financing Activities
    dividends_paid: Optional[Decimal] = Field(
        default=None,
        description="Cash paid as dividends to shareholders (typically negative)",
    )
    stock_repurchased: Optional[Decimal] = Field(
        default=None,
        description="Cash spent on share buybacks (typically negative)",
    )
    debt_issued: Optional[Decimal] = Field(
        default=None,
        description="Cash received from issuing debt",
    )
    debt_repaid: Optional[Decimal] = Field(
        default=None,
        description="Cash used to repay debt (typically negative)",
    )
    financing_cash_flow: Optional[Decimal] = Field(
        default=None,
        description="Net cash provided by (used in) financing activities",
    )

    # Summary
    net_change_in_cash: Optional[Decimal] = Field(
        default=None,
        description="Net change in cash and equivalents for the period",
    )
    free_cash_flow: Optional[Decimal] = Field(
        default=None,
        description="Operating cash flow minus capital expenditures",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "company_id": "AAPL",
                "fiscal_year": 2023,
                "period_end_date": "2023-09-30",
                "currency": "USD",
                "source_provider": "yahoo",
                "source_snapshot_id": "snapshot_125",
                "operating_cash_flow": "110543000000",
                "capital_expenditures": "-10959000000",
                "free_cash_flow": "99584000000",
                "dividends_paid": "-14841000000",
                "stock_repurchased": "-77550000000",
            }
        }
    )
