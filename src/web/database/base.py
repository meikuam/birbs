import pandas as pd
from pandas.io.json import build_table_schema
from sqlalchemy import MetaData, Table
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from src.web.database.scheme import get_columns_from_schema


def create_table(table_name: str, schema: dict, engine: Engine):
    metadata = MetaData(engine)
    # Create a table with the appropriate Columns
    table = Table(
        table_name,
        metadata,
        *get_columns_from_schema(schema=schema)
    )
    metadata.create_all(checkfirst=True)


def drop_table(table_name: str, engine: Engine):
    Base = declarative_base()
    metadata = MetaData()
    metadata.reflect(bind=engine)
    table = metadata.tables[table_name]
    if table is not None:
        Base.metadata.drop_all(engine, [table], checkfirst=True)


def push_data(
        data: pd.DataFrame,
        table_name: str,
        engine: Engine,
        **kwargs
):
    """
    Push DataFrame to database, create if not exist
    :param data:
    :param table_name:
    :param engine:
    :param kwargs:
    :return:
    """
    if not engine.has_table(table_name):
        create_table(
            table_name=table_name,
            schema=build_table_schema(
                data,
                index=True,
                version=False
            ),
            engine=engine
        )
    data.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",
        index=True,
        **kwargs
    )


def fetch_data(
        table_name: str,
        engine: Engine,
        index_col: str = None,
        query: int = None,
        **kwargs
):
    """
    Fetch data from database
    :param table_name:
    :param engine:
    :param index_col:
    :param query:
    :param kwargs:
    :return:
    """
    if query is None:
        query = f"""
            SELECT * from {table_name}
        """
    data = pd.read_sql(
        sql=query,
        con=engine,
        index_col=index_col,
        **kwargs
    )
    return data