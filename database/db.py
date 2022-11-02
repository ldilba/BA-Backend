import os

from mysql.connector import pooling

mysql_host = os.environ.get('MYSQL_HOST')
mysql_port = os.environ.get('MYSQL_PORT')

db_conf = {
    "host": mysql_host,
    "port": mysql_port,
    "user": "root",
    "password": "admin",
    "database": "db_logs",
}

cnxpool = pooling.MySQLConnectionPool(pool_name="pool", pool_size=2, autocommit=True, **db_conf)
