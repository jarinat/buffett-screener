"""Initial schema with all core entities

Revision ID: 001
Revises:
Create Date: 2026-02-28 12:33:23.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply migration changes."""
    # Create companies table (foundational entity)
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('legal_name', sa.String(length=500), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('domicile_market_scope', sa.String(length=50), nullable=True),
        sa.Column('sector', sa.String(length=100), nullable=True),
        sa.Column('industry', sa.String(length=200), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_name'), 'companies', ['name'], unique=False)
    op.create_index(op.f('ix_companies_is_active'), 'companies', ['is_active'], unique=False)

    # Create listings table
    op.create_table(
        'listings',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('exchange', sa.String(length=50), nullable=True),
        sa.Column('mic', sa.String(length=4), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_listings_company_id'), 'listings', ['company_id'], unique=False)
    op.create_index(op.f('ix_listings_ticker'), 'listings', ['ticker'], unique=False)
    op.create_index(op.f('ix_listings_is_active'), 'listings', ['is_active'], unique=False)

    # Create provider_raw_snapshots table
    op.create_table(
        'provider_raw_snapshots',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('provider_name', sa.String(length=100), nullable=False),
        sa.Column('provider_entity_type', sa.String(length=100), nullable=False),
        sa.Column('provider_entity_key', sa.String(length=255), nullable=False),
        sa.Column('fetched_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('payload_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('http_status', sa.Integer(), nullable=True),
        sa.Column('ingestion_run_id', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_provider_raw_snapshots_provider_name'), 'provider_raw_snapshots', ['provider_name'], unique=False)
    op.create_index(op.f('ix_provider_raw_snapshots_provider_entity_key'), 'provider_raw_snapshots', ['provider_entity_key'], unique=False)
    op.create_index(op.f('ix_provider_raw_snapshots_fetched_at'), 'provider_raw_snapshots', ['fetched_at'], unique=False)
    op.create_index(op.f('ix_provider_raw_snapshots_ingestion_run_id'), 'provider_raw_snapshots', ['ingestion_run_id'], unique=False)

    # Create financial_statements_annual table
    op.create_table(
        'financial_statements_annual',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('revenue', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('gross_profit', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('net_income', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('operating_income', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('eps_diluted', sa.Numeric(precision=10, scale=4), nullable=True),
        sa.Column('total_assets', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('total_liabilities', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('shareholders_equity', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('free_cash_flow', sa.Numeric(precision=20, scale=2), nullable=True),
        sa.Column('source_provider', sa.String(length=100), nullable=False),
        sa.Column('source_snapshot_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_snapshot_id'], ['provider_raw_snapshots.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_financial_statements_annual_company_id'), 'financial_statements_annual', ['company_id'], unique=False)
    op.create_index(op.f('ix_financial_statements_annual_fiscal_year'), 'financial_statements_annual', ['fiscal_year'], unique=False)
    op.create_index(op.f('ix_financial_statements_annual_source_snapshot_id'), 'financial_statements_annual', ['source_snapshot_id'], unique=False)

    # Create derived_metrics table
    op.create_table(
        'derived_metrics',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Numeric(precision=20, scale=6), nullable=True),
        sa.Column('metric_version', sa.String(length=50), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('source_statement_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_statement_id'], ['financial_statements_annual.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_derived_metrics_company_id'), 'derived_metrics', ['company_id'], unique=False)
    op.create_index(op.f('ix_derived_metrics_fiscal_year'), 'derived_metrics', ['fiscal_year'], unique=False)
    op.create_index(op.f('ix_derived_metrics_metric_name'), 'derived_metrics', ['metric_name'], unique=False)
    op.create_index(op.f('ix_derived_metrics_metric_version'), 'derived_metrics', ['metric_version'], unique=False)
    op.create_index(op.f('ix_derived_metrics_calculated_at'), 'derived_metrics', ['calculated_at'], unique=False)
    op.create_index(op.f('ix_derived_metrics_source_statement_id'), 'derived_metrics', ['source_statement_id'], unique=False)

    # Create screen_definitions table
    op.create_table(
        'screen_definitions',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('criteria_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_screen_definitions_name'), 'screen_definitions', ['name'], unique=False)
    op.create_index(op.f('ix_screen_definitions_created_at'), 'screen_definitions', ['created_at'], unique=False)
    op.create_index(op.f('ix_screen_definitions_updated_at'), 'screen_definitions', ['updated_at'], unique=False)
    op.create_index(op.f('ix_screen_definitions_is_active'), 'screen_definitions', ['is_active'], unique=False)

    # Create screen_runs table
    op.create_table(
        'screen_runs',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('screen_definition_id', sa.Integer(), nullable=False),
        sa.Column('rule_version_bundle', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('executed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('companies_evaluated', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('companies_passed', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.ForeignKeyConstraint(['screen_definition_id'], ['screen_definitions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_screen_runs_screen_definition_id'), 'screen_runs', ['screen_definition_id'], unique=False)
    op.create_index(op.f('ix_screen_runs_executed_at'), 'screen_runs', ['executed_at'], unique=False)

    # Create screen_results table
    op.create_table(
        'screen_results',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('screen_run_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('passed', sa.Boolean(), nullable=False),
        sa.Column('result_details_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(['screen_run_id'], ['screen_runs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_screen_results_screen_run_id'), 'screen_results', ['screen_run_id'], unique=False)
    op.create_index(op.f('ix_screen_results_company_id'), 'screen_results', ['company_id'], unique=False)
    op.create_index(op.f('ix_screen_results_passed'), 'screen_results', ['passed'], unique=False)

    # Create alert_rules table
    op.create_table(
        'alert_rules',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('condition_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alert_rules_name'), 'alert_rules', ['name'], unique=False)
    op.create_index(op.f('ix_alert_rules_company_id'), 'alert_rules', ['company_id'], unique=False)
    op.create_index(op.f('ix_alert_rules_created_at'), 'alert_rules', ['created_at'], unique=False)
    op.create_index(op.f('ix_alert_rules_updated_at'), 'alert_rules', ['updated_at'], unique=False)
    op.create_index(op.f('ix_alert_rules_is_active'), 'alert_rules', ['is_active'], unique=False)

    # Create alert_events table
    op.create_table(
        'alert_events',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('alert_rule_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('event_data_json', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.ForeignKeyConstraint(['alert_rule_id'], ['alert_rules.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alert_events_alert_rule_id'), 'alert_events', ['alert_rule_id'], unique=False)
    op.create_index(op.f('ix_alert_events_company_id'), 'alert_events', ['company_id'], unique=False)
    op.create_index(op.f('ix_alert_events_triggered_at'), 'alert_events', ['triggered_at'], unique=False)


def downgrade() -> None:
    """Revert migration changes."""
    # Drop tables in reverse order to respect foreign key constraints
    op.drop_index(op.f('ix_alert_events_triggered_at'), table_name='alert_events')
    op.drop_index(op.f('ix_alert_events_company_id'), table_name='alert_events')
    op.drop_index(op.f('ix_alert_events_alert_rule_id'), table_name='alert_events')
    op.drop_table('alert_events')

    op.drop_index(op.f('ix_alert_rules_is_active'), table_name='alert_rules')
    op.drop_index(op.f('ix_alert_rules_updated_at'), table_name='alert_rules')
    op.drop_index(op.f('ix_alert_rules_created_at'), table_name='alert_rules')
    op.drop_index(op.f('ix_alert_rules_company_id'), table_name='alert_rules')
    op.drop_index(op.f('ix_alert_rules_name'), table_name='alert_rules')
    op.drop_table('alert_rules')

    op.drop_index(op.f('ix_screen_results_passed'), table_name='screen_results')
    op.drop_index(op.f('ix_screen_results_company_id'), table_name='screen_results')
    op.drop_index(op.f('ix_screen_results_screen_run_id'), table_name='screen_results')
    op.drop_table('screen_results')

    op.drop_index(op.f('ix_screen_runs_executed_at'), table_name='screen_runs')
    op.drop_index(op.f('ix_screen_runs_screen_definition_id'), table_name='screen_runs')
    op.drop_table('screen_runs')

    op.drop_index(op.f('ix_screen_definitions_is_active'), table_name='screen_definitions')
    op.drop_index(op.f('ix_screen_definitions_updated_at'), table_name='screen_definitions')
    op.drop_index(op.f('ix_screen_definitions_created_at'), table_name='screen_definitions')
    op.drop_index(op.f('ix_screen_definitions_name'), table_name='screen_definitions')
    op.drop_table('screen_definitions')

    op.drop_index(op.f('ix_derived_metrics_source_statement_id'), table_name='derived_metrics')
    op.drop_index(op.f('ix_derived_metrics_calculated_at'), table_name='derived_metrics')
    op.drop_index(op.f('ix_derived_metrics_metric_version'), table_name='derived_metrics')
    op.drop_index(op.f('ix_derived_metrics_metric_name'), table_name='derived_metrics')
    op.drop_index(op.f('ix_derived_metrics_fiscal_year'), table_name='derived_metrics')
    op.drop_index(op.f('ix_derived_metrics_company_id'), table_name='derived_metrics')
    op.drop_table('derived_metrics')

    op.drop_index(op.f('ix_financial_statements_annual_source_snapshot_id'), table_name='financial_statements_annual')
    op.drop_index(op.f('ix_financial_statements_annual_fiscal_year'), table_name='financial_statements_annual')
    op.drop_index(op.f('ix_financial_statements_annual_company_id'), table_name='financial_statements_annual')
    op.drop_table('financial_statements_annual')

    op.drop_index(op.f('ix_provider_raw_snapshots_ingestion_run_id'), table_name='provider_raw_snapshots')
    op.drop_index(op.f('ix_provider_raw_snapshots_fetched_at'), table_name='provider_raw_snapshots')
    op.drop_index(op.f('ix_provider_raw_snapshots_provider_entity_key'), table_name='provider_raw_snapshots')
    op.drop_index(op.f('ix_provider_raw_snapshots_provider_name'), table_name='provider_raw_snapshots')
    op.drop_table('provider_raw_snapshots')

    op.drop_index(op.f('ix_listings_is_active'), table_name='listings')
    op.drop_index(op.f('ix_listings_ticker'), table_name='listings')
    op.drop_index(op.f('ix_listings_company_id'), table_name='listings')
    op.drop_table('listings')

    op.drop_index(op.f('ix_companies_is_active'), table_name='companies')
    op.drop_index(op.f('ix_companies_name'), table_name='companies')
    op.drop_table('companies')
