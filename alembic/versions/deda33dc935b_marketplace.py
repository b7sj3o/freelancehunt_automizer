"""marketplace

Revision ID: deda33dc935b
Revises: 98681ab6f076
Create Date: 2025-11-03 21:13:59.013827

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'deda33dc935b'
down_revision: Union[str, None] = '98681ab6f076'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Змінюємо enum значення з великих літер на маленькі
    # Колонка marketplace вже існує (додана в попередній міграції 98681ab6f076)
    
    # Перейменовуємо старий enum
    op.execute("ALTER TYPE marketplace RENAME TO marketplace_old")
    
    # Створюємо новий enum з правильними значеннями (lowercase)
    marketplace_enum = sa.Enum('freelancehunt', 'freelancer', name='marketplace', create_type=True)
    marketplace_enum.create(op.get_bind())
    
    # Конвертуємо дані з великих літер на маленькі
    op.execute("""
        ALTER TABLE projects 
        ALTER COLUMN marketplace TYPE marketplace 
        USING CASE 
            WHEN marketplace::text = 'FREELANCEHUNT' THEN 'freelancehunt'::marketplace
            WHEN marketplace::text = 'FREELANCER' THEN 'freelancer'::marketplace
            ELSE 'freelancehunt'::marketplace
        END
    """)
    
    # Видаляємо старий enum
    op.execute("DROP TYPE marketplace_old")


def downgrade() -> None:
    # Повертаємо старий enum з великими літерами
    # Перейменовуємо поточний enum
    op.execute("ALTER TYPE marketplace RENAME TO marketplace_new")
    
    # Створюємо старий enum з великими літерами
    marketplace_enum_old = sa.Enum('FREELANCEHUNT', 'FREELANCER', name='marketplace', create_type=True)
    marketplace_enum_old.create(op.get_bind())
    
    # Конвертуємо дані назад на великі літери
    op.execute("""
        ALTER TABLE projects 
        ALTER COLUMN marketplace TYPE marketplace 
        USING CASE 
            WHEN marketplace::text = 'freelancehunt' THEN 'FREELANCEHUNT'::marketplace
            WHEN marketplace::text = 'freelancer' THEN 'FREELANCER'::marketplace
            ELSE 'FREELANCEHUNT'::marketplace
        END
    """)
    
    # Видаляємо новий enum
    op.execute("DROP TYPE marketplace_new")
