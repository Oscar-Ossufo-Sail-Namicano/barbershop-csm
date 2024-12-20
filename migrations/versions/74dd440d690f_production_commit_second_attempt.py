"""production commit (second attempt)

Revision ID: 74dd440d690f
Revises: 25707fef9e1f
Create Date: 2024-10-15 22:29:13.570254

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '74dd440d690f'
down_revision = '25707fef9e1f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('establishments',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('apelido', sa.String(length=150), nullable=False),
    sa.Column('msg_boas_vindas', sa.String(length=500), nullable=True),
    sa.Column('msg_secundaria', sa.String(length=1000), nullable=True),
    sa.Column('horas_aberto', sa.String(length=50), nullable=True),
    sa.Column('horas_fechado', sa.String(length=50), nullable=True),
    sa.Column('dias_funcionamento', sa.String(length=150), nullable=True),
    sa.Column('descricao_do_bairro', sa.String(length=300), nullable=True),
    sa.Column('bairro', sa.String(length=100), nullable=True),
    sa.Column('provincia', sa.String(length=100), nullable=True),
    sa.Column('distrito', sa.String(length=100), nullable=True),
    sa.Column('telefone', sa.String(length=100), nullable=True),
    sa.Column('email', sa.String(length=150), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('apelido')
    )
    op.create_table('establishments_images',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('lugar', sa.Text(), nullable=False),
    sa.Column('estabelecimento_id', sa.Integer(), nullable=True),
    sa.Column('buffer_data', sa.Text(), nullable=False),
    sa.Column('name', sa.Text(), nullable=False),
    sa.Column('mimeType', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['estabelecimento_id'], ['establishments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('services',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('servico', sa.String(), nullable=False),
    sa.Column('preco', sa.String(length=150), nullable=True),
    sa.Column('estabelecimento_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['estabelecimento_id'], ['establishments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.add_column(sa.Column('estabelecimento_id', sa.Integer(), nullable=True))
        batch_op.drop_constraint('admins_email_key', type_='unique')
        batch_op.drop_constraint('admins_telefone_key', type_='unique')
        batch_op.create_foreign_key(None, 'establishments', ['estabelecimento_id'], ['id'])

    with op.batch_alter_table('employers', schema=None) as batch_op:
        batch_op.add_column(sa.Column('estabelecimento_id', sa.Integer(), nullable=True))
        batch_op.alter_column('nome',
               existing_type=sa.VARCHAR(),
               nullable=True)
        batch_op.alter_column('telefone',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
        batch_op.alter_column('senha',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
        batch_op.alter_column('tipo_documento',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
        batch_op.alter_column('numero_documento',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
        batch_op.alter_column('data_nascimento',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
        batch_op.alter_column('local_nascimento',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
        batch_op.alter_column('funcao',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
        batch_op.alter_column('contrato',
               existing_type=sa.VARCHAR(length=150),
               nullable=True)
        batch_op.drop_constraint('employers_email_key', type_='unique')
        batch_op.drop_constraint('employers_telefone_key', type_='unique')
        batch_op.create_foreign_key(None, 'establishments', ['estabelecimento_id'], ['id'])

    with op.batch_alter_table('schedules', schema=None) as batch_op:
        batch_op.add_column(sa.Column('estabelecimento_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'establishments', ['estabelecimento_id'], ['id'])

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint('users_email_key', type_='unique')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.create_unique_constraint('users_email_key', ['email'])

    with op.batch_alter_table('schedules', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('estabelecimento_id')

    with op.batch_alter_table('employers', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_unique_constraint('employers_telefone_key', ['telefone'])
        batch_op.create_unique_constraint('employers_email_key', ['email'])
        batch_op.alter_column('contrato',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
        batch_op.alter_column('funcao',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
        batch_op.alter_column('local_nascimento',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
        batch_op.alter_column('data_nascimento',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
        batch_op.alter_column('numero_documento',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
        batch_op.alter_column('tipo_documento',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
        batch_op.alter_column('senha',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
        batch_op.alter_column('email',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
        batch_op.alter_column('telefone',
               existing_type=sa.VARCHAR(length=150),
               nullable=False)
        batch_op.alter_column('nome',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.drop_column('estabelecimento_id')

    with op.batch_alter_table('admins', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_unique_constraint('admins_telefone_key', ['telefone'])
        batch_op.create_unique_constraint('admins_email_key', ['email'])
        batch_op.drop_column('estabelecimento_id')

    op.drop_table('services')
    op.drop_table('establishments_images')
    op.drop_table('establishments')
    # ### end Alembic commands ###
