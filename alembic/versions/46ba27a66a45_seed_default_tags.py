"""seed default tags

Revision ID: 46ba27a66a45
Revises: 43df29b2b3cd
Create Date: 2026-11-13 16:15:35.002594

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "46ba27a66a45"
down_revision: Union[str, Sequence[str], None] = "43df29b2b3cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.execute(
        sa.text(
            """
            INSERT INTO tags (name)
            VALUES
                ('Technology'),
                ('Education'),
                ('Entertainment'),
                ('Business'),
                ('Social'),
                ('News'),
                ('Health'),
                ('Sports'),
                ('Lifestyle'),
                ('Other')
            ON CONFLICT (name) DO NOTHING
        """
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.execute(
        sa.text(
            """
            DELETE FROM tags
            WHERE name IN (
                'Technology',
                'Education',
                'Entertainment',
                'Business',
                'Social',
                'News',
                'Health',
                'Sports',
                'Lifestyle',
                'Other'
            )
        """
        )
    )
