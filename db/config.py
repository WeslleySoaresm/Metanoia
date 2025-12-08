import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
import json


db_config = {
    "user": 'postgres',
    "password": '101520',
    "host": 'localhost',
    "port": '5432',
    "database": 'CursoTeologia'
}

def get_db_engine(config):
    """Create a database engine using the provided configuration."""
    try:
        engine = create_engine(
            f"postgresql+psycopg2://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        )
        return engine
    except SQLAlchemyError as e:
        print(f"Error creating database engine: {e}")
        return None
    





