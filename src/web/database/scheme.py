import sqlalchemy.types
from sqlalchemy import Column
from sqlalchemy.sql.visitors import Traversible
from pandas.io.json import build_table_schema


type_mapping = {}
for key, type_class in sqlalchemy.types.__dict__.items():
    if type(type_class) is type(Traversible):
        if hasattr(type_class, "__visit_name__"):
            type_mapping[type_class.__visit_name__] = type_class
    type_mapping['number'] = sqlalchemy.types.Numeric
    # type_mapping['string'] = sqlalchemy.types.String(length=255)


def get_columns_from_schema(schema: dict):
    table_columns = []
    for column in schema['fields']:
        is_primary_key = column['name'] in schema['primaryKey']
        table_columns.append(
            Column(
                column['name'],
                type_mapping[column['type']],
                primary_key=is_primary_key,
                nullable=not is_primary_key
            )
        )
    return table_columns
