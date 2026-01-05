"""Initial schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'economic_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_date', sa.DateTime(), nullable=False),
        sa.Column('importance', sa.String(length=20), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('country', sa.String(length=10), nullable=True),
        sa.Column('actual', sa.Float(), nullable=True),
        sa.Column('forecast', sa.Float(), nullable=True),
        sa.Column('previous', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_economic_events_id'), 'economic_events', ['id'], unique=False)
    op.create_index(op.f('ix_economic_events_event_date'), 'economic_events', ['event_date'], unique=False)
    op.create_index(op.f('ix_economic_events_importance'), 'economic_events', ['importance'], unique=False)
    op.create_index(op.f('ix_economic_events_currency'), 'economic_events', ['currency'], unique=False)

    op.create_table(
        'market_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('instrument', sa.String(length=20), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('interval', sa.String(length=10), nullable=False),
        sa.Column('open_price', sa.Float(), nullable=False),
        sa.Column('high_price', sa.Float(), nullable=False),
        sa.Column('low_price', sa.Float(), nullable=False),
        sa.Column('close_price', sa.Float(), nullable=False),
        sa.Column('volume', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Comment('Datos históricos de mercado (velas OHLCV)')
    )
    op.create_index(op.f('ix_market_data_id'), 'market_data', ['id'], unique=False)
    op.create_index(op.f('ix_market_data_instrument'), 'market_data', ['instrument'], unique=False)
    op.create_index(op.f('ix_market_data_timestamp'), 'market_data', ['timestamp'], unique=False)
    op.create_index(op.f('ix_market_data_interval'), 'market_data', ['interval'], unique=False)

    op.create_table(
        'daily_analyses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('instrument', sa.String(length=20), nullable=False),
        sa.Column('analysis_date', sa.DateTime(), nullable=False),
        sa.Column('previous_day_close', sa.Float(), nullable=False),
        sa.Column('current_day_close', sa.Float(), nullable=False),
        sa.Column('daily_change_percent', sa.Float(), nullable=False),
        sa.Column('daily_direction', sa.String(length=20), nullable=False),
        sa.Column('previous_day_high', sa.Float(), nullable=False),
        sa.Column('previous_day_low', sa.Float(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('analysis_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Comment('Análisis diarios de mercado guardados')
    )
    op.create_index(op.f('ix_daily_analyses_id'), 'daily_analyses', ['id'], unique=False)
    op.create_index(op.f('ix_daily_analyses_instrument'), 'daily_analyses', ['instrument'], unique=False)
    op.create_index(op.f('ix_daily_analyses_analysis_date'), 'daily_analyses', ['analysis_date'], unique=False)

    op.create_table(
        'trading_mode_recommendations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('instrument', sa.String(length=20), nullable=False),
        sa.Column('bond_symbol', sa.String(length=10), nullable=False),
        sa.Column('recommendation_date', sa.DateTime(), nullable=False),
        sa.Column('mode', sa.String(length=20), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('detailed_explanation', sa.Text(), nullable=True),
        sa.Column('reasons_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Comment('Recomendaciones de modo de trading históricas')
    )
    op.create_index(op.f('ix_trading_mode_recommendations_id'), 'trading_mode_recommendations', ['id'], unique=False)
    op.create_index(op.f('ix_trading_mode_recommendations_instrument'), 'trading_mode_recommendations', ['instrument'], unique=False)
    op.create_index(op.f('ix_trading_mode_recommendations_recommendation_date'), 'trading_mode_recommendations', ['recommendation_date'], unique=False)

    op.create_table(
        'market_alignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('alignment_date', sa.DateTime(), nullable=False),
        sa.Column('dxy_price', sa.Float(), nullable=False),
        sa.Column('dxy_previous_price', sa.Float(), nullable=False),
        sa.Column('dxy_change_percent', sa.Float(), nullable=False),
        sa.Column('bond_symbol', sa.String(length=10), nullable=False),
        sa.Column('bond_price', sa.Float(), nullable=False),
        sa.Column('bond_previous_price', sa.Float(), nullable=False),
        sa.Column('bond_change_percent', sa.Float(), nullable=False),
        sa.Column('alignment_status', sa.String(length=20), nullable=False),
        sa.Column('market_bias', sa.String(length=20), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Comment('Alineaciones DXY-Bonos históricas')
    )
    op.create_index(op.f('ix_market_alignments_id'), 'market_alignments', ['id'], unique=False)
    op.create_index(op.f('ix_market_alignments_alignment_date'), 'market_alignments', ['alignment_date'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_market_alignments_alignment_date'), table_name='market_alignments')
    op.drop_index(op.f('ix_market_alignments_id'), table_name='market_alignments')
    op.drop_table('market_alignments')
    op.drop_index(op.f('ix_trading_mode_recommendations_recommendation_date'), table_name='trading_mode_recommendations')
    op.drop_index(op.f('ix_trading_mode_recommendations_instrument'), table_name='trading_mode_recommendations')
    op.drop_index(op.f('ix_trading_mode_recommendations_id'), table_name='trading_mode_recommendations')
    op.drop_table('trading_mode_recommendations')
    op.drop_index(op.f('ix_daily_analyses_analysis_date'), table_name='daily_analyses')
    op.drop_index(op.f('ix_daily_analyses_instrument'), table_name='daily_analyses')
    op.drop_index(op.f('ix_daily_analyses_id'), table_name='daily_analyses')
    op.drop_table('daily_analyses')
    op.drop_index(op.f('ix_market_data_interval'), table_name='market_data')
    op.drop_index(op.f('ix_market_data_timestamp'), table_name='market_data')
    op.drop_index(op.f('ix_market_data_instrument'), table_name='market_data')
    op.drop_index(op.f('ix_market_data_id'), table_name='market_data')
    op.drop_table('market_data')
    op.drop_index(op.f('ix_economic_events_currency'), table_name='economic_events')
    op.drop_index(op.f('ix_economic_events_importance'), table_name='economic_events')
    op.drop_index(op.f('ix_economic_events_event_date'), table_name='economic_events')
    op.drop_index(op.f('ix_economic_events_id'), table_name='economic_events')
    op.drop_table('economic_events')

