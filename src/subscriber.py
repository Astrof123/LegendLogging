import paho.mqtt.client as mqtt_client
import platform
import json
import requests
import logging
import sys
import time

from logging.handlers import TimedRotatingFileHandler

FORMATTER_STRING = "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "tmp/subscriber.log"  # use fancy libs to make proper temp file

def requester():
    uri = "http://127.0.0.1:8001/auth"
    try:
        response = requests.get(uri)
        if (response.status_code == 200):
            jsn = json.loads(response.text)
            return jsn["user_id"]
        else:
            logger.debug(f"{platform.platform()} — Статус код: {response.status_code}")
            logger.error(f"{platform.platform()} — Непредвиденная ошибка с сервером")
    except Exception as exception:
        logger.error(f"{platform.platform()} — Ошибка с сервером: {exception}")

def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    logger.addHandler(file_handler)

    return logger

def on_message(client, userdata, message):
    time.sleep(1)
    data = str(message.payload.decode("utf-8"))
    logger.info(f"{platform.platform()} — sub_id: {user_id[0:6]}... — Полученное сообщение: \"{data}\"")


logger = get_logger("subscriber_logger")


broker = "broker.emqx.io"

with open("id/subscriber_id.txt", "a+", encoding="utf-8") as f:
    f.seek(0)
    if f.readline() == "":
        user_id = requester()
        logger.info(f"{platform.platform()} — Подписчик получил id: {user_id[0:6]}...")
        f.write(user_id)
    else:
        f.seek(0)
        user_id = f.readline()
        logger.info(f"{platform.platform()} — Подписчик запустил приложение с id: {user_id[0:6]}...")


client = mqtt_client.Client(
   mqtt_client.CallbackAPIVersion.VERSION1,
   user_id
)
client.on_message=on_message

try:
    logger.info(f"{platform.platform()} — sub_id: {user_id[0:6]}... — Подключение к брокеру {broker}")
    client.connect(broker)
    client.loop_start()
    topic = "lab/leds/glebiks"
    logger.info(f"{platform.platform()} — sub_id: {user_id[0:6]}... — Идет прослушка по теме {topic}")
    client.subscribe(topic)
    time.sleep(1800)
    logger.info(f"{platform.platform()} — sub_id: {user_id[0:6]}... — Прослушка закончена")
    client.disconnect()
    client.loop_stop()
except KeyboardInterrupt:
    logger.warning(f"{platform.platform()} — sub_id: {user_id[0:6]}... — Прослушка закончена раньше времени")
