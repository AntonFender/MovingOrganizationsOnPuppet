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
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ru,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Host': '192.168.0.11',
    'Origin': 'https://192.168.0.11',
    'Referer': 'https://192.168.0.11/hosts/cash-20000679030-200006790301/edit',
    'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Yandex";v="21"',
    'sec-ch-ua-mobile': '?0',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 YaBrowser/21.8.1.468 Yowser/2.5 Safari/537.36'
}


def authForeman():
    """Аутентификация в foreman"""
    urllib3.disable_warnings()  # Отключаем warning
    ss = requests.session()
    ss.auth = ('admin', 'foreman')
    ss.verify = False
    return ss


def createInfoHost(list_host, csrf_token):
    """Информация о хосте"""
    resaul_list_host = {}
    list_param_host = ['name', 'puppet_proxy_id', 'puppet_ca_proxy_id', 'managed', 'enabled', 'model_id',
                       'comment', 'overwrite', 'is_owned_by']
    for param in list_param_host:
        try:
            val = list_host[param]
            if list_host[param] == False and isinstance(list_host[param], bool):
                val = 'false'
            if list_host[param] == True and isinstance(list_host[param], bool):
                val = 'true'
        except KeyError:
            if param == 'is_owned_by':
                val = '4-Users'
            elif param == 'overwrite':
                val = 'false'
            else:
                val = ''
        key_list = "host[{}]".format(param)
        resaul_list_host[key_list] = val

    # Добавляем дополнительные значения к словарю resaul_list_host
    resaul_list_host['host[hostgroup_id]'] = 1
    resaul_list_host['host[environment_id]'] = 1
    resaul_list_host['host[puppetclass_ids][]'] = ''
    resaul_list_host['host[progress_report_id]'] = str(uuid.uuid1())
    resaul_list_host['authenticity_token'] = csrf_token
    resaul_list_host['_method: patch'] = 'patch'
    return resaul_list_host

def createInterfaceList(list_host):
    """Создание интерфейс листа"""
    resaul_list_interface = {}
    list_param_interface = ['_destroy', 'mac', 'identifier', 'name', 'domain_id', 'ip', 'ip6', 'managed',
                           'primary', 'provision', 'tag', 'attached_to', 'id']

    list_interfaces = list_host['interfaces']
    for n, interface in enumerate(list_interfaces):
        for param in list_param_interface:
            try:
                val = interface[param]
                if interface[param] == False and isinstance(interface[param], bool):
                    val = 'false'
                if interface[param] == True and isinstance(interface[param], bool):
                    val = 'true'
                if interface[param] is None:
                    val = ''
            except KeyError:
                if param == '_destroy':
                    val = 0
                else:
                    val = ''

            key_list = "host[interfaces_attributes][{}][{}]".format(n, param)
            resaul_list_interface[key_list] = val

    return resaul_list_interface

def csrfTokenGet(ss):
    """Получаем csrf токен и какой то AUTH"""
    csrf_token = False
    content_foreman = ss.get('https://192.168.0.11').content
    soup = BeautifulSoup(content_foreman, 'html.parser')
    for i in soup.find_all('meta'):
        try:
            if i.get("name") == 'csrf-token':
                csrf_token = i.get("content")
        except:
            csrf_token = False

    pattern = re.compile(r"var AUTH_TOKEN = '(.*?)';$", re.MULTILINE | re.DOTALL)
    script = soup.find("script", text=pattern)
    auth = pattern.search(script.text).group(1)

    return csrf_token, auth


ss = authForeman()
csrf_token, auth = csrfTokenGet(ss)


if ss.get(show_status).json()['status'] == 200:
    print('Доступ к API puppet получен')
else:
    print('Нет доступа к API. Выход')
    exit(0)

list_host = ss.get(api_hosts + '/cash-20000679030-200006790301').json()
id_host = str(list_host['id'])

list_host['environment_id'] = 1
list_host['hostgroup_id'] = 1
list_host['environment_name'] = 'production'
list_host['hostgroup_name'] = 'work-group'
list_host['hostgroup_title'] = 'work-group'
pprint(list_host)


update_host = ss.put(api_hosts + '/' + id_host, params=list_host, headers=HEADERS)
print(update_host.status_code)
print(update_host.text)



# list_interface = createInterfaceList(list_host)
# list_host_data = createInfoHost(list_host, csrf_token)
# inner_list = {**list_host_data, **list_interface}
# HEADERS['X-CSRF-Token'] = csrf_token
# r = json.dumps(inner_list)
# l = json.loads(r)

# update_host = ss.put(api_hosts + '/' + id_host, data=l, headers=HEADERS)
# print(update_host.status_code)
# print(update_host.headers)
# print(update_host.text)
# print(update_host.request.headers)
# print(update_host.request.body)



# list_environments = ss.get(api_environments).json()
# list_hostgroups = ss.get(api_hostgroups).json()
# list_http_proxies = ss.get(api_http_proxies).json()
# list_puppetclass_ids = ss.get(api_orchestration).json()
# print(list_puppetclass_ids)