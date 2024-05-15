"""
Python module for gathering schema of data related to this project
for visibility of relative data.
"""

import pathlib
import pprint

import duckdb
import pandas as pd
import pyarrow as pa
from constants import DATA_FILES

# specify a dir where the schema may go
schema_dir = pathlib.Path("5.data_packaging/schema")

# if we don't have a schema dir, make it
if not schema_dir.is_dir():
    schema_dir.mkdir()


def get_arrow_schema_str_from_csv(filename_read: str) -> str:
    """
    Get an Arrow schema from a CSV file through DuckDB.

    Args:
        filename_read (str):
            The path to the CSV file to be read.

    Returns:
        str:
            A string representing the Arrow schema obtained from the CSV file.

    """

    # try to read a typed arrow table
    # falling back to a high-memory (string-focused) pandas
    # dataframe read converted to arrow
    try:
        with duckdb.connect() as ddb:
            return (
                ddb.execute(
                    f"""
                    SELECT *
                    FROM read_csv('{filename_read}');
                    """
                )
                .arrow()
                .schema.to_string()
            )
    except duckdb.duckdb.ConversionException:
        return pa.Table.from_pandas(
            df=pd.read_csv(filepath_or_buffer=filename_read, low_memory=False),
        ).schema.to_string()
    except:
        raise


def write_schema_str_to_file(filename_write: str, schema: str) -> str:
    """
    Write a schema string to a file.
    """

    with open(file=filename_write, mode="w", encoding="utf-8") as file:
        file.write(schema)

    return filename_write


# gather arrow schema strings and write them to file
schemas = [
    write_schema_str_to_file(
        filename_write=f"{schema_dir}/{filename.replace('/','.')}.arrow.schema.txt",
        schema=get_arrow_schema_str_from_csv(filename_read=filename),
    )
    for filename in DATA_FILES
]

# show the filenames of the schemas afterwards
print("Schema files:")
pprint.pp(schemas)
