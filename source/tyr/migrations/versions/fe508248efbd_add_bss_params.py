"""Add new bss parameters

Revision ID: fe508248efbd
Revises: ab54d9575a99
Create Date: 2021-04-20 16:26:16.071876

"""

# revision identifiers, used by Alembic.
revision = 'fe508248efbd'
down_revision = 'ab54d9575a99'

from alembic import op
import sqlalchemy as sa
from navitiacommon import default_values


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'instance',
        sa.Column(
            'bss_rent_duration',
            sa.Integer(),
            nullable=False,
            server_default=f'{default_values.bss_rent_duration}',
        ),
    )
    op.add_column(
        'instance',
        sa.Column(
            'bss_rent_penalty',
            sa.Integer(),
            nullable=False,
            server_default=f'{default_values.bss_rent_penalty}',
        ),
    )
    op.add_column(
        'instance',
        sa.Column(
            'bss_return_duration',
            sa.Integer(),
            nullable=False,
            server_default=f'{default_values.bss_return_duration}',
        ),
    )
    op.add_column(
        'instance',
        sa.Column(
            'bss_return_penalty',
            sa.Integer(),
            nullable=False,
            server_default=f'{default_values.bss_return_penalty}',
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('instance', 'bss_return_penalty')
    op.drop_column('instance', 'bss_return_duration')
    op.drop_column('instance', 'bss_rent_penalty')
    op.drop_column('instance', 'bss_rent_duration')
    # ### end Alembic commands ###
