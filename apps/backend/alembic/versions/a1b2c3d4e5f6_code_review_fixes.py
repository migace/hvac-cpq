"""code review fixes: ConfigurationStatus enum, JSON allowed_values, unified operator enum, quote_number_seq

Revision ID: a1b2c3d4e5f6
Revises: 7bd6e0ccd34b
Create Date: 2026-04-12 18:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "7bd6e0ccd34b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add ConfigurationStatus enum and migrate product_configurations.status
    op.execute("CREATE TYPE configuration_status_enum AS ENUM ('draft', 'active', 'archived')")
    op.execute(
        """
        ALTER TABLE product_configurations
        ALTER COLUMN status TYPE configuration_status_enum
        USING status::configuration_status_enum
        """
    )

    # 2. Migrate product_rules.allowed_values from TEXT to JSON array.
    #    string_to_array returns a native PG array; to_json wraps it as a JSON array.
    #    This is subquery-free and therefore valid in a USING expression.
    op.execute(
        """
        ALTER TABLE product_rules
        ALTER COLUMN allowed_values TYPE JSON
        USING CASE
            WHEN allowed_values IS NULL THEN NULL
            ELSE to_json(string_to_array(allowed_values, ','))
        END
        """
    )

    # 3. Migrate product_pricing_rules.operator to reuse rule_operator_enum
    #    (previously stored as pricing_rule_operator_enum with identical values)
    op.execute(
        """
        ALTER TABLE product_pricing_rules
        ALTER COLUMN operator TYPE rule_operator_enum
        USING operator::text::rule_operator_enum
        """
    )
    op.execute("DROP TYPE IF EXISTS pricing_rule_operator_enum")

    # 4. Add quote_number_seq for concurrency-safe quote numbering
    op.execute("CREATE SEQUENCE IF NOT EXISTS quote_number_seq START 1")


def downgrade() -> None:
    # 4. Drop quote_number_seq
    op.execute("DROP SEQUENCE IF EXISTS quote_number_seq")

    # 3. Restore pricing_rule_operator_enum
    op.execute(
        "CREATE TYPE pricing_rule_operator_enum AS ENUM "
        "('eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'in')"
    )
    op.execute(
        """
        ALTER TABLE product_pricing_rules
        ALTER COLUMN operator TYPE pricing_rule_operator_enum
        USING operator::text::pricing_rule_operator_enum
        """
    )

    # 2. Revert product_rules.allowed_values from JSON back to TEXT.
    #    json_array_elements_text is set-returning so we can't aggregate it in a USING clause.
    #    Use an explicit ADD/UPDATE/DROP/RENAME pattern instead.
    op.execute(
        "ALTER TABLE product_rules ADD COLUMN allowed_values_text TEXT"
    )
    op.execute(
        """
        UPDATE product_rules
        SET allowed_values_text = (
            SELECT string_agg(v, ',')
            FROM json_array_elements_text(allowed_values) AS v
        )
        WHERE allowed_values IS NOT NULL
        """
    )
    op.execute("ALTER TABLE product_rules DROP COLUMN allowed_values")
    op.execute(
        "ALTER TABLE product_rules RENAME COLUMN allowed_values_text TO allowed_values"
    )

    # 1. Revert product_configurations.status to VARCHAR
    op.execute(
        """
        ALTER TABLE product_configurations
        ALTER COLUMN status TYPE VARCHAR(50)
        USING status::text
        """
    )
    op.execute("DROP TYPE IF EXISTS configuration_status_enum")
