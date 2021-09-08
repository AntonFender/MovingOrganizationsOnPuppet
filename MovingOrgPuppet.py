# Скрипт для перемещения организация на puppet
# api documentation https://apidocs.theforeman.org/foreman/2.5/apidoc/v2.html

import requests
import urllib3
from pprint import pprint
import uuid
from bs4 import BeautifulSoup
import re
import json

# Инициализация переменных
show_status = "https://192.168.0.11/api/status"
api_hosts = "https://192.168.0.11/api/hosts"
api_environments = "https://192.168.0.11/api/environments"
api_hostgroups = "https://192.168.0.11/api/hostgroups"
api_http_proxies = 'https://192.168.0.11/api/smart_proxies'
api_puppetclass_ids = 'https://192.168.0.11/api/hosts/cash-20000679030-200006790301/puppetclass_ids'
api_orchestration = 'https://192.168.0.11/api/orchestration/cash-20000679030-200006790301/tasks'
HEADERS = {
    'Content-Type': 'application/json'
}


def authForeman():
    """Аутентификация в foreman"""
    urllib3.disable_warnings()  # Отключаем warning
    ss = requests.session()
    ss.auth = ('admin', 'foreman')
    ss.verify = False
    return ss


ss = authForeman()
if ss.get(show_status).json()['status'] == 200:
    print('Доступ к API puppet получен')
else:
    print('Нет доступа к API. Выход')
    exit(0)

list_host = ss.get(api_hosts + '/cash-20000679030-200006790301').json()
id_host = str(list_host['id'])
payload = {'host[hostgroup_id]': 1, 'host[environment_id]': 1}

update_host = ss.put(api_hosts + '/' + id_host, params=payload, headers=HEADERS)
print(update_host.status_code)
print(update_host.text)
