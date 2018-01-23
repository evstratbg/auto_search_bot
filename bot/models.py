from peewee import *
from datetime import datetime as dt
from config import PG_CONN
from playhouse.shortcuts import RetryOperationalError
from playhouse.pool import PostgresqlDatabase


class MyRetryDB(RetryOperationalError, PostgresqlDatabase):
    pass


db = MyRetryDB('asb', **PG_CONN)


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    id = PrimaryKeyField()
    telegram_id = IntegerField(unique=True, null=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    dt = DateTimeField(default=dt.now())


if __name__ == '__main__':
    Users.create_table()