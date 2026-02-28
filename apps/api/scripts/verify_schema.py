"""
Verification script to confirm all 10 core tables exist in the database.

This script checks the database schema and verifies that all required tables
have been created successfully via Alembic migrations. It connects to the
database using SQLAlchemy and inspects the available tables.

Expected tables:
- companies
- listings
- provider_raw_snapshots
- financial_statements_annual
- derived_metrics
- screen_definitions
- screen_runs
- screen_results
- alert_rules
- alert_events

Exit codes:
    0: All tables exist
    1: One or more tables are missing
"""

import sys
from typing import Set

from sqlalchemy import inspect

from app.core.config import settings
from app.core.db import engine


# Define all expected tables
EXPECTED_TABLES: Set[str] = {
    "companies",
    "listings",
    "provider_raw_snapshots",
    "financial_statements_annual",
    "derived_metrics",
    "screen_definitions",
    "screen_runs",
    "screen_results",
    "alert_rules",
    "alert_events",
}


def verify_schema() -> bool:
    """
    Verify that all required tables exist in the database.

    Returns:
        bool: True if all tables exist, False otherwise
    """
    # Create an inspector to examine the database schema
    inspector = inspect(engine)

    # Get all table names from the database
    existing_tables: Set[str] = set(inspector.get_table_names())

    # Calculate missing and unexpected tables
    missing_tables = EXPECTED_TABLES - existing_tables
    unexpected_tables = existing_tables - EXPECTED_TABLES

    # Print header
    print("=" * 70)
    print("DATABASE SCHEMA VERIFICATION")
    print("=" * 70)
    print(f"Database URL: {settings.database_url_str}")
    print(f"Expected tables: {len(EXPECTED_TABLES)}")
    print(f"Found tables: {len(existing_tables)}")
    print()

    # Print verification results for each expected table
    print("Table Verification Status:")
    print("-" * 70)
    for table_name in sorted(EXPECTED_TABLES):
        status = "✓ EXISTS" if table_name in existing_tables else "✗ MISSING"
        print(f"  {table_name:<35} {status}")
    print()

    # Print missing tables if any
    if missing_tables:
        print("Missing Tables:")
        print("-" * 70)
        for table_name in sorted(missing_tables):
            print(f"  ✗ {table_name}")
        print()

    # Print unexpected tables if any (informational only)
    if unexpected_tables:
        print("Unexpected Tables (not in expected list):")
        print("-" * 70)
        for table_name in sorted(unexpected_tables):
            print(f"  ! {table_name}")
        print()

    # Print summary
    print("=" * 70)
    if not missing_tables:
        print("SUCCESS: All 10 required tables exist")
        print("=" * 70)
        return True
    else:
        print(f"FAILURE: {len(missing_tables)} table(s) missing")
        print("=" * 70)
        return False


def main() -> None:
    """Main entry point for the verification script."""
    try:
        success = verify_schema()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"ERROR: Failed to verify schema: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
