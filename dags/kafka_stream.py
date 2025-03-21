import uuid
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflowMaster',
    'start_date': datetime(2024, 3, 17, 10, 00)
}

def get_data():
    import requests

    res = requests.get("https://randomuser.me/api/")
    res = res.json()
    res = res['results'][0]

    return res

def format_data(res):
    data = {}
    location = res['location']
    data['id'] = str(uuid.uuid4())
    data['first_name'] = res['name']['first']
    data['last_name'] = res['name']['last']
    data['gender'] = res['gender']
    data['address'] = f"{str(location['street']['number'])} {location['street']['name']}, " \
                      f"{location['city']}, {location['state']}, {location['country']}"
    data['post_code'] = location['postcode']
    data['email'] = res['email']
    data['username'] = res['login']['username']
    data['dob'] = res['dob']['date']
    data['registered_date'] = res['registered']['date']
    data['phone'] = res['phone']
    data['picture'] = res['picture']['medium']

    return data

def stream_data():
    import json
    from kafka import KafkaProducer
    import time
    import logging

    # listener_int - DAG triggered from airflow UI running on container
    # listener_ext - when stream_data() function called from local terminal
    listener_int = 'broker:29092'
    listener_ext = 'localhost:9092'
    producer = KafkaProducer(bootstrap_servers=[listener_int], max_block_ms=5000)
    curr_time = time.time()

    while True:
        if time.time() > curr_time + 300: # 5 minutes
            break
        try:
            res = get_data()
            res = format_data(res)
            producer.send('users_created', json.dumps(res).encode('utf-8'))
            logging.info("Message sent to Kafka topic 'users_created'.")
        except Exception as e:
            logging.error(f'An error occurred: {e}')
            continue
        finally:
            producer.flush()
    producer.close()

with DAG('user_automation',
         default_args=default_args,
         schedule='@daily',
         catchup=False) as dag:

    streaming_task = PythonOperator(
        task_id='stream_data_from_api',
        python_callable=stream_data
    )

# stream_data()
