"""many to many categories and authors

Revision ID: 357b8f822a02
Revises: 80d3d2bff9f1
Create Date: 2025-03-03 01:29:05.219406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '357b8f822a02'
down_revision: Union[str, None] = '80d3d2bff9f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('book_authors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_book_authors_author_id'), 'book_authors', ['author_id'], unique=False)
    op.create_index(op.f('ix_book_authors_book_id'), 'book_authors', ['book_id'], unique=False)
    op.create_table('book_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_book_categories_book_id'), 'book_categories', ['book_id'], unique=False)
    op.create_index(op.f('ix_book_categories_category_id'), 'book_categories', ['category_id'], unique=False)
    op.drop_constraint('books_category_fkey', 'books', type_='foreignkey')
    op.drop_column('books', 'category')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('books', sa.Column('category', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('books_category_fkey', 'books', 'categories', ['category'], ['id'])
    op.drop_index(op.f('ix_book_categories_category_id'), table_name='book_categories')
    op.drop_index(op.f('ix_book_categories_book_id'), table_name='book_categories')
    op.drop_table('book_categories')
    op.drop_index(op.f('ix_book_authors_book_id'), table_name='book_authors')
    op.drop_index(op.f('ix_book_authors_author_id'), table_name='book_authors')
    op.drop_table('book_authors')
    # ### end Alembic commands ###
