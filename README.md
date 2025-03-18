# Realtime User Data Streaming 

## Table of Contents
- [Introduction](#introduction)
- [Workflow](#workflow)
- [Technologies Used](#technologies-used)
- [Instructions](#instructions)



## Introduction

This project showcases the development of a complete end-to-end data engineering pipeline, covering every stage from data ingestion to processing and storage. It leverages a powerful tech stack, including Apache Airflow, Python, Apache Kafka, Apache Zookeeper, Apache Spark, and Cassandra. The entire solution is containerized with Docker, ensuring seamless deployment and scalability.

## Workflow

The project is structured with the following components:

- **Data Source**: The pipeline uses the [randomuser.me](https://randomuser.me/) API to generate random user data.
- **Apache Airflow**: Orchestrates tasks to stream data into Kafka topics and uses a **PostgreSQL** database to store metadata.
- **Apache Kafka and Zookeeper**: Facilitates real-time data streaming by receiving data from Airflow and making it available for Spark processing.
- **Control Center and Schema Registry**: Enable **monitoring** and **schema management** for Kafka streams.
- **Apache Spark**: Performs **data processing** using master and worker nodes in a standalone cluster run in client mode.
- **Cassandra**: Serves as the final sink for storing the processed data.

## Technologies Used

- Apache Airflow
- Apache Kafka
- Apache Spark
- Cassandra
- PostgreSQL
- Docker

## Instructions

### Commands
```commandline
1. git clone git@github.com:drbals/user-data-pipeline.git
2. cd user-data-pipeline
3. docker compose up -d
4. docker exec -it <container id or name> bash
5. spark-submit --master spark://spark-master:7077 \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1,\
com.datastax.spark:spark-cassandra-connector_2.12:3.4.1 stream_internal.py
6. docker exec -it cassandra cqlsh -u cassandra -p cassandra localhost 9042
7. select * from spark_streams.created_users;
```
### Actions
1. Run the first three commands provided to start all necessary applications.
2. Trigger the `user_automation` DAG from the **Airflow UI** at [http://localhost:8080/](http://localhost:8080/).
3. Verify the data produced in the Kafka topic `users_created` via **Control Center** at [http://localhost:9021/](http://localhost:9021/).
4. Use command-4 to access the bash terminal of any Spark cluster node. Verify `stream_internal.py` script is present.
5. Execute command-5 in a node's shell to submit the job, with **Spark Master** UI accessible at [http://localhost:9090/](http://localhost:9090/).
6. Utilize the last two commands to log into **Cassandra DB** and view the processed records in the table.
