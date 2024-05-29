import time
import paho.mqtt.client as mqtt_client
import random
import json
import requests
import logging
import sys
import platform

from logging.handlers import TimedRotatingFileHandler

FORMATTER_STRING = "%(asctime)s — %(name)s — %(levelname)s — %(message)s"
FORMATTER = logging.Formatter(FORMATTER_STRING)
LOG_FILE = "tmp/publisher.log"

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
            exit

    except Exception as exception:
        logger.error(f"{platform.platform()} — Ошибка с сервером: {exception}")
        exit

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


logger = get_logger("publisher_logger")

broker = "broker.emqx.io"

with open("id/publisher_id.txt", "a+", encoding="utf-8") as f:
    f.seek(0)
    if f.readline() == "":
        user_id = requester()
        logger.info(f"{platform.platform()} — Издатель получил id: {user_id[0:6]}...")
        f.write(user_id)
    else:
        f.seek(0)
        user_id = f.readline()
        logger.info(f"{platform.platform()} — Издатель запустил приложение с id: {user_id[0:6]}...")

client = mqtt_client.Client(
   mqtt_client.CallbackAPIVersion.VERSION1,
   user_id
)


try:
    logger.info(f"{platform.platform()} — pub_id: {user_id[0:6]}... — Подключение к брокеру {broker}")
    client.connect(broker)
    client.loop_start()
    topic = "lab/leds/glebiks"

    n = int(input("Сколько раз вы хотите опубликовать сообщения?: "))
    logger.info(f"{platform.platform()} — pub_id: {user_id[0:6]}... — Будет {n} публикаций")
    state = input("Введите сообщение: ")
    logger.info(f"{platform.platform()} — pub_id: {user_id[0:6]}... — Идет публикация по теме {topic} с таким сообщением: \"{state}\"")
    for i in range(n):
        logger.info(f"{platform.platform()} — pub_id: {user_id[0:6]}... — Отправлено сообщение \"{state}\" #{i+1}")
        client.publish(topic, state)
        time.sleep(2)

    logger.info(f"{platform.platform()} — pub_id: {user_id[0:6]}... — Публикация закончена")
    client.disconnect()
    client.loop_stop()
except KeyboardInterrupt:
    logger.warning(f"{platform.platform()} — pub_id: {user_id[0:6]}... — Публикация прервана")