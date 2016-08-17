import sys, socket
from peewee import PostgresqlDatabase

hostname = socket.gethostname()

if sys.platform == 'win32':
    DATABASE = PostgresqlDatabase('postgres',
                                  **{'port': 5432, 'host': 'localhost', 'password': 'postgres', 'user': 'postgres',
                                     'dbname': 'DI'})
elif sys.platform == 'linux':
    if hostname == 'esb':
        DATABASE = PostgresqlDatabase('postgres',
                                        **{'port': 5432, 'host': 'new-pdb.gosbroker.pro', 'password': 'Ghbuyhjgj123s',
                                           'user': 'dev', 'dbname': 'DI'})
    elif hostname == 'test-esb':
        DATABASE = PostgresqlDatabase('postgres',
                                        **{'port': 5432, 'host': 'test-pdb.gosbroker.pro', 'password': 'Ghbuyhjgj123s',
                                           'user': 'dev','dbname': 'DI'})