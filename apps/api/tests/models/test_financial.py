"""Tests for financial statement data models."""

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.models.financial import (
    BalanceSheet,
    CashFlow,
    FinancialStatement,
    IncomeStatement,
)


class TestFinancialStatement:
    """Tests for FinancialStatement base model."""

    def test_financial_statement_base_valid_data(self):
        """Test creating a base FinancialStatement with valid data."""
        statement = FinancialStatement(
            company_id="AAPL",
            fiscal_year=2023,
            period_end_date=date(2023, 9, 30),
            currency="USD",
            source_provider="yahoo",
        )
        assert statement.company_id == "AAPL"
        assert statement.fiscal_year == 2023
        assert statement.period_end_date == date(2023, 9, 30)
        assert statement.currency == "USD"
        assert statement.source_provider == "yahoo"
        assert statement.source_snapshot_id is None

    def test_financial_statement_with_snapshot_id(self):
        """Test FinancialStatement with optional source_snapshot_id."""
        statement = FinancialStatement(
            company_id="MSFT",
            fiscal_year=2023,
            period_end_date=date(2023, 6, 30),
            currency="USD",
            source_provider="yahoo",
            source_snapshot_id="snapshot_xyz_123",
        )
        assert statement.source_snapshot_id == "snapshot_xyz_123"

    def test_financial_statement_missing_required_field(self):
        """Test FinancialStatement validation error when required field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            FinancialStatement(
                company_id="AAPL",
                fiscal_year=2023,
                # missing period_end_date, currency, source_provider
            )
        errors = str(exc_info.value)
        assert "period_end_date" in errors or "currency" in errors


class TestIncomeStatement:
    """Tests for IncomeStatement model."""

    def test_income_statement_valid_data(self):
        """Test creating IncomeStatement with valid data."""
        income = IncomeStatement(
            company_id="AAPL",
            fiscal_year=2023,
            period_end_date=date(2023, 9, 30),
            currency="USD",
            source_provider="yahoo",
            revenue=Decimal("383285000000"),
            cost_of_revenue=Decimal("214137000000"),
            gross_profit=Decimal("169148000000"),
            operating_expenses=Decimal("54848000000"),
            operating_income=Decimal("114300000000"),
            net_income=Decimal("96995000000"),
            eps_diluted=Decimal("6.16"),
        )
        assert income.revenue == Decimal("383285000000")
        assert income.net_income == Decimal("96995000000")
        assert income.eps_diluted == Decimal("6.16")

    def test_income_statement_minimal_data(self):
        """Test creating IncomeStatement with minimal required fields."""
        income = IncomeStatement(
            company_id="TEST",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="test_provider",
        )
        assert income.company_id == "TEST"
        assert income.revenue is None
        assert income.net_income is None
        assert income.eps_basic is None

    def test_income_statement_serialization(self):
        """Test IncomeStatement serialization to dict."""
        income = IncomeStatement(
            company_id="MSFT",
            fiscal_year=2023,
            period_end_date=date(2023, 6, 30),
            currency="USD",
            source_provider="yahoo",
            revenue=Decimal("211915000000"),
            net_income=Decimal("72738000000"),
        )
        data = income.model_dump()
        assert data["company_id"] == "MSFT"
        assert data["revenue"] == Decimal("211915000000")
        assert data["net_income"] == Decimal("72738000000")

    def test_income_statement_json_round_trip(self):
        """Test IncomeStatement JSON serialization and deserialization."""
        original = IncomeStatement(
            company_id="GOOGL",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="yahoo",
            revenue=Decimal("307394000000"),
            net_income=Decimal("73795000000"),
            eps_diluted=Decimal("5.80"),
        )
        json_str = original.model_dump_json()
        restored = IncomeStatement.model_validate_json(json_str)
        assert restored.company_id == original.company_id
        assert restored.revenue == original.revenue
        assert restored.net_income == original.net_income

    def test_income_statement_example_config(self):
        """Test that example from Config can be instantiated."""
        example = IncomeStatement.model_config["json_schema_extra"]["example"]
        income = IncomeStatement(**example)
        assert income.company_id == "AAPL"
        assert income.revenue == Decimal("383285000000")

    def test_income_statement_decimal_precision(self):
        """Test IncomeStatement handles decimal precision correctly."""
        income = IncomeStatement(
            company_id="TEST",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="test",
            eps_diluted=Decimal("6.123456789"),
        )
        assert income.eps_diluted == Decimal("6.123456789")

    def test_income_statement_all_fields(self):
        """Test IncomeStatement with all optional fields populated."""
        income = IncomeStatement(
            company_id="FULL",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="test",
            source_snapshot_id="snap_123",
            revenue=Decimal("1000000"),
            cost_of_revenue=Decimal("400000"),
            gross_profit=Decimal("600000"),
            operating_expenses=Decimal("200000"),
            operating_income=Decimal("400000"),
            interest_expense=Decimal("50000"),
            income_before_tax=Decimal("350000"),
            income_tax_expense=Decimal("70000"),
            net_income=Decimal("280000"),
            eps_basic=Decimal("2.80"),
            eps_diluted=Decimal("2.75"),
            shares_outstanding_basic=100000,
            shares_outstanding_diluted=101818,
        )
        assert income.revenue == Decimal("1000000")
        assert income.shares_outstanding_basic == 100000
        assert income.shares_outstanding_diluted == 101818


class TestBalanceSheet:
    """Tests for BalanceSheet model."""

    def test_balance_sheet_valid_data(self):
        """Test creating BalanceSheet with valid data."""
        balance = BalanceSheet(
            company_id="AAPL",
            fiscal_year=2023,
            period_end_date=date(2023, 9, 30),
            currency="USD",
            source_provider="yahoo",
            total_assets=Decimal("352755000000"),
            current_assets=Decimal("143566000000"),
            total_liabilities=Decimal("290437000000"),
            current_liabilities=Decimal("145308000000"),
            shareholders_equity=Decimal("62318000000"),
        )
        assert balance.total_assets == Decimal("352755000000")
        assert balance.shareholders_equity == Decimal("62318000000")

    def test_balance_sheet_minimal_data(self):
        """Test creating BalanceSheet with minimal required fields."""
        balance = BalanceSheet(
            company_id="TEST",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="test_provider",
        )
        assert balance.company_id == "TEST"
        assert balance.total_assets is None
        assert balance.total_liabilities is None
        assert balance.shareholders_equity is None

    def test_balance_sheet_serialization(self):
        """Test BalanceSheet serialization to dict."""
        balance = BalanceSheet(
            company_id="MSFT",
            fiscal_year=2023,
            period_end_date=date(2023, 6, 30),
            currency="USD",
            source_provider="yahoo",
            total_assets=Decimal("411976000000"),
            total_liabilities=Decimal("205753000000"),
            shareholders_equity=Decimal("206223000000"),
        )
        data = balance.model_dump()
        assert data["total_assets"] == Decimal("411976000000")
        assert data["shareholders_equity"] == Decimal("206223000000")

    def test_balance_sheet_json_round_trip(self):
        """Test BalanceSheet JSON serialization and deserialization."""
        original = BalanceSheet(
            company_id="GOOGL",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="yahoo",
            total_assets=Decimal("402392000000"),
            shareholders_equity=Decimal("256144000000"),
        )
        json_str = original.model_dump_json()
        restored = BalanceSheet.model_validate_json(json_str)
        assert restored.total_assets == original.total_assets

    def test_balance_sheet_example_config(self):
        """Test that example from Config can be instantiated."""
        example = BalanceSheet.model_config["json_schema_extra"]["example"]
        balance = BalanceSheet(**example)
        assert balance.company_id == "AAPL"
        assert balance.total_assets == Decimal("352755000000")

    def test_balance_sheet_all_asset_fields(self):
        """Test BalanceSheet with all asset fields populated."""
        balance = BalanceSheet(
            company_id="ASSET",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="test",
            cash_and_equivalents=Decimal("100000"),
            short_term_investments=Decimal("50000"),
            accounts_receivable=Decimal("75000"),
            inventory=Decimal("25000"),
            current_assets=Decimal("250000"),
            property_plant_equipment=Decimal("150000"),
            intangible_assets=Decimal("100000"),
            total_assets=Decimal("500000"),
        )
        assert balance.cash_and_equivalents == Decimal("100000")
        assert balance.intangible_assets == Decimal("100000")

    def test_balance_sheet_all_liability_equity_fields(self):
        """Test BalanceSheet with all liability and equity fields populated."""
        balance = BalanceSheet(
            company_id="LIAB",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="test",
            accounts_payable=Decimal("30000"),
            short_term_debt=Decimal("20000"),
            current_liabilities=Decimal("50000"),
            long_term_debt=Decimal("100000"),
            total_liabilities=Decimal("150000"),
            common_stock=Decimal("10000"),
            retained_earnings=Decimal("340000"),
            shareholders_equity=Decimal("350000"),
            total_assets=Decimal("500000"),
        )
        assert balance.long_term_debt == Decimal("100000")
        assert balance.retained_earnings == Decimal("340000")


class TestCashFlow:
    """Tests for CashFlow model."""

    def test_cash_flow_valid_data(self):
        """Test creating CashFlow with valid data."""
        cash_flow = CashFlow(
            company_id="AAPL",
            fiscal_year=2023,
            period_end_date=date(2023, 9, 30),
            currency="USD",
            source_provider="yahoo",
            operating_cash_flow=Decimal("110543000000"),
            capital_expenditures=Decimal("-10959000000"),
            free_cash_flow=Decimal("99584000000"),
            dividends_paid=Decimal("-14841000000"),
            stock_repurchased=Decimal("-77550000000"),
        )
        assert cash_flow.operating_cash_flow == Decimal("110543000000")
        assert cash_flow.free_cash_flow == Decimal("99584000000")

    def test_cash_flow_minimal_data(self):
        """Test creating CashFlow with minimal required fields."""
        cash_flow = CashFlow(
            company_id="TEST",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="test_provider",
        )
        assert cash_flow.company_id == "TEST"
        assert cash_flow.operating_cash_flow is None
        assert cash_flow.free_cash_flow is None

    def test_cash_flow_serialization(self):
        """Test CashFlow serialization to dict."""
        cash_flow = CashFlow(
            company_id="MSFT",
            fiscal_year=2023,
            period_end_date=date(2023, 6, 30),
            currency="USD",
            source_provider="yahoo",
            operating_cash_flow=Decimal("87582000000"),
            free_cash_flow=Decimal("56118000000"),
        )
        data = cash_flow.model_dump()
        assert data["operating_cash_flow"] == Decimal("87582000000")
        assert data["free_cash_flow"] == Decimal("56118000000")

    def test_cash_flow_json_round_trip(self):
        """Test CashFlow JSON serialization and deserialization."""
        original = CashFlow(
            company_id="GOOGL",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="yahoo",
            operating_cash_flow=Decimal("101736000000"),
            capital_expenditures=Decimal("-32281000000"),
            free_cash_flow=Decimal("69455000000"),
        )
        json_str = original.model_dump_json()
        restored = CashFlow.model_validate_json(json_str)
        assert restored.operating_cash_flow == original.operating_cash_flow

    def test_cash_flow_example_config(self):
        """Test that example from Config can be instantiated."""
        example = CashFlow.model_config["json_schema_extra"]["example"]
        cash_flow = CashFlow(**example)
        assert cash_flow.company_id == "AAPL"
        assert cash_flow.operating_cash_flow == Decimal("110543000000")

    def test_cash_flow_negative_values(self):
        """Test CashFlow handles negative values correctly."""
        cash_flow = CashFlow(
            company_id="NEG",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="test",
            capital_expenditures=Decimal("-50000"),
            dividends_paid=Decimal("-10000"),
            stock_repurchased=Decimal("-25000"),
            debt_repaid=Decimal("-15000"),
        )
        assert cash_flow.capital_expenditures == Decimal("-50000")
        assert cash_flow.dividends_paid == Decimal("-10000")

    def test_cash_flow_all_operating_fields(self):
        """Test CashFlow with all operating activity fields."""
        cash_flow = CashFlow(
            company_id="OPS",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="test",
            net_income=Decimal("100000"),
            depreciation_amortization=Decimal("20000"),
            changes_in_working_capital=Decimal("-5000"),
            operating_cash_flow=Decimal("115000"),
        )
        assert cash_flow.net_income == Decimal("100000")
        assert cash_flow.depreciation_amortization == Decimal("20000")

    def test_cash_flow_all_investing_fields(self):
        """Test CashFlow with all investing activity fields."""
        cash_flow = CashFlow(
            company_id="INV",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="test",
            capital_expenditures=Decimal("-30000"),
            acquisitions=Decimal("-50000"),
            investment_purchases=Decimal("-20000"),
            investment_sales=Decimal("15000"),
            investing_cash_flow=Decimal("-85000"),
        )
        assert cash_flow.acquisitions == Decimal("-50000")
        assert cash_flow.investment_sales == Decimal("15000")

    def test_cash_flow_all_financing_fields(self):
        """Test CashFlow with all financing activity fields."""
        cash_flow = CashFlow(
            company_id="FIN",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="test",
            dividends_paid=Decimal("-10000"),
            stock_repurchased=Decimal("-25000"),
            debt_issued=Decimal("50000"),
            debt_repaid=Decimal("-20000"),
            financing_cash_flow=Decimal("-5000"),
        )
        assert cash_flow.debt_issued == Decimal("50000")
        assert cash_flow.financing_cash_flow == Decimal("-5000")

    def test_cash_flow_summary_fields(self):
        """Test CashFlow with summary fields."""
        cash_flow = CashFlow(
            company_id="SUM",
            fiscal_year=2023,
            period_end_date=date(2023, 12, 31),
            currency="USD",
            source_provider="test",
            operating_cash_flow=Decimal("115000"),
            capital_expenditures=Decimal("-30000"),
            free_cash_flow=Decimal("85000"),
            net_change_in_cash=Decimal("25000"),
        )
        assert cash_flow.free_cash_flow == Decimal("85000")
        assert cash_flow.net_change_in_cash == Decimal("25000")
