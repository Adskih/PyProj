from peewee import PostgresqlDatabase, RawQuery, Model, ProgrammingError, IntegerField, BooleanField, CharField
import glob
import os

DATABASE = PostgresqlDatabase('postgres',
                              **{'port': 5432, 'host': 'localhost', 'password': 'postgres', 'user': 'postgres',
                                 'dbname': 'DI'})

database = DATABASE

class BaseModel(Model):
    class Meta:
        database = database

class Result(BaseModel): pass


class Migrations(BaseModel):
    id = IntegerField(primary_key=True, db_column='id')
    name = CharField(db_column='name')
    success = BooleanField(null=True)

    class Meta:
        db_table = '_migrations'
        schema = 'public'

path = r'C:\soft\GIT\db\migrations'

for file in sorted(glob.glob(os.path.join(path, '*up.sql'))):
    print(file)
    filename = file.split(os.sep)[-1:][0]
    try:
        migrat = Migrations.select().where(Migrations.name == filename).get()
    except Migrations.DoesNotExist:
        migrat = Migrations.create(name=file.split(os.sep)[-1:][0])

    if not migrat.success:
        f = open(file, 'r', encoding='utf-8')
        string = f.read()
        rq = RawQuery(Result, query=string)
        try:
            rq.execute()
            migrat.success = True
            migrat.save()
        except ProgrammingError as X:
            print(X)
            migrat.success = False
            migrat.save()
            raise ProgrammingError
        finally:
            f.close()