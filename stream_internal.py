import logging

from cassandra.cluster import Cluster
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType

# logging.basicConfig(level=logging.INFO)

def create_keyspace(session):
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS spark_streams
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '1'};
    """)

    print("Keyspace created successfully!")

def create_table(session):
    session.execute("""
    CREATE TABLE IF NOT EXISTS spark_streams.created_users (
        id UUID PRIMARY KEY,
        first_name TEXT,
        last_name TEXT,
        gender TEXT,
        address TEXT,
        post_code TEXT,
        email TEXT,
        username TEXT,
        registered_date TEXT,
        phone TEXT,
        picture TEXT);
    """)

    print("Table created successfully!")

def create_spark_connection():
    s_conn = None

    try:
        s_conn = SparkSession.builder \
            .appName('SparkDataStreaming') \
            .config('spark.jars.packages', "com.datastax.spark:spark-cassandra-connector_2.12:3.4.1,"
                                           "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1") \
            .config('spark.cassandra.connection.host', 'cassandra') \
            .getOrCreate()

        s_conn.sparkContext.setLogLevel("ERROR")
        logging.info("Spark connection created successfully!")
    except Exception as e:
        logging.error(f"Couldn't create the spark session due to exception {e}")

    return s_conn

def connect_to_kafka(spark_conn):
    spark_df = None
    try:
        spark_df = spark_conn.readStream \
            .format('kafka') \
            .option('kafka.bootstrap.servers', 'broker:29092') \
            .option('subscribe', 'users_created') \
            .option('startingOffsets', 'earliest') \
            .load()
        logging.info("kafka dataframe created successfully")
    except Exception as e:
        logging.warning(f"kafka dataframe could not be created because: {e}")

    return spark_df

def create_cassandra_connection():
    try:
        # connecting to the cassandra cluster
        cluster = Cluster(['cassandra'])

        cas_session = cluster.connect()

        return cas_session
    except Exception as e:
        logging.error(f"Could not create cassandra connection due to {e}")
        return None

def create_selection_df_from_kafka(spark_df):
    schema = StructType([
        StructField("id", StringType(), False),
        StructField("first_name", StringType(), False),
        StructField("last_name", StringType(), False),
        StructField("gender", StringType(), False),
        StructField("address", StringType(), False),
        StructField("post_code", StringType(), False),
        StructField("email", StringType(), False),
        StructField("username", StringType(), False),
        StructField("registered_date", StringType(), False),
        StructField("phone", StringType(), False),
        StructField("picture", StringType(), False)
    ])

    sel = spark_df.selectExpr("CAST(value AS STRING)") \
        .select(from_json(col('value'), schema).alias('data')).select("data.*")
    print(sel)

    return sel

if __name__ == "__main__":
    # create spark connection
    spark_conn = create_spark_connection()
    spark_conn.sparkContext.setLogLevel("WARN")
    if spark_conn is not None:
        # connect to kafka with spark connection
        spark_df = connect_to_kafka(spark_conn)
        if spark_df is None:
            print("spark_df is None")
        selection_df = create_selection_df_from_kafka(spark_df)
        if selection_df is None:
            print("selection_df is None")
        session = create_cassandra_connection()

        if session is not None:
            create_keyspace(session)
            create_table(session)

            streaming_query = (selection_df.writeStream.format("org.apache.spark.sql.cassandra")
                               .option('checkpointLocation', '/tmp/checkpoint')
                               .option('keyspace', 'spark_streams')
                               .option('table', 'created_users')
                               .start())

            logging.info("Streaming is being started...")

            streaming_query.awaitTermination()
