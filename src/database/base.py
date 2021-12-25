import os
import databases
import sqlalchemy
from sqlalchemy.orm import sessionmaker


username = os.getenv('POSTGRES_USER', "postgres")
password = os.getenv('POSTGRES_PASSWORD', 'postgres')
hostname = os.getenv('POSTGRES_HOST', 'postgres')
database_name = os.getenv('POSTGRES_DATABASE', 'birbs_db')
port = os.getenv('POSTGRES_PORT', '8807')

DATABASE_URL = "postgresql+psycopg2://%s:%s@%s:%s/%s?charset=utf8mb4" % (username, password, hostname, port, database_name)

database = databases.Database(DATABASE_URL)

engine = sqlalchemy.create_engine(
    DATABASE_URL,
    encoding='utf8',
    pool_size = 5,
    max_overflow = 1
)
Session = sessionmaker(bind=engine)
