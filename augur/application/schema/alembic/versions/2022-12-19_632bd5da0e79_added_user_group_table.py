"""Added user group table

Revision ID: 632bd5da0e79
Revises: 1
Create Date: 2022-12-19 11:00:37.509132

"""
import logging

from alembic import op
import sqlalchemy as sa
from augur.application.db.session import DatabaseSession



# revision identifiers, used by Alembic.
revision = '632bd5da0e79'
down_revision = '1'
branch_labels = None
depends_on = None


def upgrade():






    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_groups',
        sa.Column('user_group_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['augur_operations.users.user_id'], name='user_group_user_id_fkey'),
        sa.PrimaryKeyConstraint('user_group_id'),
        sa.UniqueConstraint('user_id', 'name', name='user_group_unique'),
        schema='augur_operations'
    )

    logger = logging.getLogger(__name__)

    
    with DatabaseSession(logger) as session:
        user_id_query = sa.sql.text("""SELECT DISTINCT(user_id) FROM user_repos;""")
        user_groups = session.fetchall_data_from_sql_text(user_id_query)
        for row in user_groups:
            row.update({"name": "default"})
            del row["repo_id"]

        result = session.insert_data(user_groups, UserGroup, ["user_id", "name"], return_columns=["group_id", "user_id"])


        user_group_id_mapping = {}
        for row in result:
            user_group_id_mapping[row["user_id"]] = row["group_id"]
        

        user_repo_query = sa.sql.text("""SELECT * FROM user_repos;""")
        user_repo_data = session.fetchall_data_from_sql_text(user_repo_query)
        for row in user_repo_data:
            row.update({"group_id": user_group_id_mapping[row["user_id"]]})
            del row["user_id"]



        # remove data from table before modifiying it
        remove_data_from_user_repos_query = sa.sql.text("""DELETE FROM user_repos;""")
        session.execute_sql(remove_data_from_user_repos_query)
        

    op.add_column('user_repos', sa.Column('group_id', sa.BigInteger(), nullable=False), schema='augur_operations')
    op.drop_constraint('user_repos_repo_id_fkey', 'user_repos', schema='augur_operations', type_='foreignkey')
    op.drop_constraint('user_repos_user_id_fkey', 'user_repos', schema='augur_operations', type_='foreignkey')
    op.create_foreign_key('user_repo_user_id_fkey', 'user_repos', 'repo', ['repo_id'], ['repo_id'], source_schema='augur_operations', referent_schema='augur_data')
    op.create_foreign_key('user_repo_group_id_fkey', 'user_repos', 'user_groups', ['group_id'], ['user_group_id'], source_schema='augur_operations', referent_schema='augur_operations')
    op.drop_column('user_repos', 'user_id', schema='augur_operations')


    session.insert_data(user_repo_data, UserRepo, ["group_id", "repo_id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_repos', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False), schema='augur_operations')
    op.drop_constraint('user_repo_group_id_fkey', 'user_repos', schema='augur_operations', type_='foreignkey')
    op.drop_constraint('user_repo_user_id_fkey', 'user_repos', schema='augur_operations', type_='foreignkey')
    op.create_foreign_key('user_repos_user_id_fkey', 'user_repos', 'users', ['user_id'], ['user_id'], source_schema='augur_operations', referent_schema='augur_operations')
    op.create_foreign_key('user_repos_repo_id_fkey', 'user_repos', 'repo', ['repo_id'], ['repo_id'], source_schema='augur_operations')
    op.drop_column('user_repos', 'group_id', schema='augur_operations')
    op.drop_table('user_groups', schema='augur_operations')
    # ### end Alembic commands ###