"""
Python module for packaging data in lancedb database.
"""

import pathlib

import duckdb
import lancedb
import pandas as pd
import pyarrow as pa
from constants import DATA_FILES_W_COLNAMES

# specify a dir where the lancedb database may go and create lancedb client
lancedb_dir = pathlib.Path("5.data_packaging/packaged/lancedb/mitocheck_data")
ldb = lancedb.connect(lancedb_dir)


def get_arrow_tbl_from_csv(filename_read: str) -> str:
    """
    Get an Arrow table from a CSV file through DuckDB.
    """

    # try to read a typed arrow table
    # falling back to a high-memory (string-focused) pandas
    # dataframe read converted to arrow
    try:
        with duckdb.connect() as ddb:
            return ddb.execute(
                f"""
                    SELECT *
                    FROM read_csv('{filename_read}');
                    """
            ).arrow()
    except duckdb.duckdb.ConversionException:
        return pa.Table.from_pandas(
            df=pd.read_csv(filepath_or_buffer=filename_read, low_memory=False),
        )
    except:
        raise


# send csv file data as arrow tables to a lancedb database
for filename in DATA_FILES_W_COLNAMES:
    table = get_arrow_tbl_from_csv(filename_read=filename)
    ldb.create_table(
        name=f"{filename.replace('/','.')}",
        data=table,
        schema=table.schema,
        mode="overwrite",
    )
