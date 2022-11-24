import os

from mysql.connector import pooling

mysql_host = os.environ.get('MYSQL_HOST')
mysql_port = os.environ.get('MYSQL_PORT')

db_conf = {
    "host": mysql_host,
    "port": mysql_port,
    "user": "root",
    "password": "admin"
}

try:
    cnxpool_logs = pooling.MySQLConnectionPool(pool_name="pool", pool_size=10, autocommit=True, database="db_logs", **db_conf)
    cnxpool_services = pooling.MySQLConnectionPool(pool_name="pool", pool_size=2, autocommit=True, database="db_logs", **db_conf)

except Exception as e:
    print("error", "[Server, Database]: " + str(e))
