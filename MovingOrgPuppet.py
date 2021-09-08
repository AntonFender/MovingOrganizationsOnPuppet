# Скрипт для перемещения организация на puppet


import os
import requests
from bs4 import BeautifulSoup
import certifi
import urllib3


# Инициализация переменных
host = "https://192.168.0.11"
show_available_api_links = "https://192.168.0.11/api"
show_status = "https://192.168.0.11/api/status"
list_hosts = "https://192.168.0.11/api/hosts"
update_host = "https://192.168.0.11/api/hosts/:id"
cert1 = r"certs\confsrv2.puppet.ru.pem"
cert2 = r"public_keys\confsrv2.puppet.ru.pem"


def authForeman():
    """Аутентификация в foreman"""
    urllib3.disable_warnings()  # Отключаем warning
    ss = requests.session()
    ss.auth = ('admin', 'foreman')
    ss.verify = False
    return ss

ss = authForeman()
res1 = ss.get(show_status)
print(res1.text)
