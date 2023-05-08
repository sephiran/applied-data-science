## same content as db_ops.ipynb
## transfered content to this py script to be able to execute it on docker container startup

import pandas as pd
import psycopg2 as ps
from sqlalchemy import create_engine

# DB CONFIG
db_name = "adsproject"
db_user = "ads"
db_password = "admin123!"
db_host = "postgres"
db_port = "5432"

table_name = 'airbnb'

# Create a connection to the PostgreSQL database
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')
# Read csv into df
df = pd.read_csv('/home/jovyan/jupyter_data/data/airbnb_rental_prices_combined.csv', sep=";")
# Save the DataFrame as a table in the PostgreSQL database
df.to_sql(table_name, engine, if_exists='replace', index=False)

def read_table_to_dataframe(db_name, db_user, db_password, db_host, db_port, table_name):
    # Establish a connection to the PostgreSQL database
    conn = ps.connect(database=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
    # Read the table from the PostgreSQL database into a DataFrame
    df = pd.read_sql(f'SELECT * FROM {table_name};', conn) # type: ignore
    # Close the connection
    conn.close()
    return df

# Call the function to read the table from the PostgreSQL database into a DataFrame
df = read_table_to_dataframe(db_name, db_user, db_password, db_host, db_port, table_name)

# Display the DataFrame
print(df)
