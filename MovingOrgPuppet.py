# Скрипт для перемещения организация на puppet
# api documentation https://apidocs.theforeman.org/foreman/2.5/apidoc/v2.html

import requests
import urllib3
from pprint import pprint


# Инициализация переменных
show_status = "https://192.168.0.11/api/status"
api_hosts = "https://192.168.0.11/api/hosts"
api_environments = "https://192.168.0.11/api/environments"
api_hostgroups = "https://192.168.0.11/api/hostgroups"
HEADERS = {'Content-Type': 'application/json'}


def authForeman():
    """Аутентификация в foreman"""
    urllib3.disable_warnings()  # Отключаем warning
    ss = requests.session()
    ss.auth = ('admin', 'foreman')
    ss.verify = False
    return ss

def environmentsGet(ss):
    """Получаем нужные id окружения"""
    id_egaisoff = ''
    id_production = ''
    list_environments = ss.get(api_environments).json()['results']
    for env in list_environments:
        if env['name'] == 'egaisoff':
            id_egaisoff = env['id']
        if env['name'] == 'production':
            id_production = env['id']
    if id_egaisoff and id_production:
        return id_production, id_egaisoff
    else:
        print("Не получили ID окружений. Выход из программы")
        exit(0)

def hostgroupsGet(ss):
    """Получаем нужные id хостгрупп"""
    id_work_group = ''
    id_work_group_no_egais = ''
    list_hostgroups = ss.get(api_hostgroups).json()['results']
    for groups in list_hostgroups:
        if groups['name'] == 'work-group':
            id_work_group = groups['id']
        if groups['name'] == 'work-group-no-egais':
            id_work_group_no_egais = groups['id']
    if id_work_group and id_work_group_no_egais:
        return id_work_group, id_work_group_no_egais
    else:
        print("Не получили ID окружений. Выход из программы")
        exit(0)

def updateHost(ss, envgroup, host):
    """Выполняем обновление хоста"""
    update_host = ''
    id_production, id_egaisoff = environmentsGet(ss)
    id_work_group, id_work_group_no_egais = hostgroupsGet(ss)
    list_egaisoff = {'host[hostgroup_id]': id_work_group_no_egais, 'host[environment_id]': id_egaisoff}
    list_work_group = {'host[hostgroup_id]': id_work_group, 'host[environment_id]': id_production}

    list_host = ss.get(api_hosts + '/' + host).json()
    id_host = str(list_host['id'])

    if envgroup == 'work-group':
        update_host = ss.put(api_hosts + '/' + id_host, params=list_work_group, headers=HEADERS)
    elif envgroup == 'egaisoff':
        update_host = ss.put(api_hosts + '/' + id_host, params=list_egaisoff, headers=HEADERS)
    else:
        print('Неверно указано куда перемещаем host({})'.format(envgroup))
    if update_host:
        if update_host.status_code == 200:
            print('Узел успешно перемещен в {}({})'.format(envgroup, update_host.status_code))
        else:
            print('Узел не перемещен в {}. Не известная ошибка({})...'.format(envgroup, update_host.status_code))
    else:
        print('Узел не перемещен в {}. Не выполнился update_host'.format(envgroup))



ss = authForeman()
if ss.get(show_status).json()['status'] == 200:
    print('Доступ к API puppet получен')
else:
    print('Нет доступа к API. Выход')
    exit(0)

# Передаем методу: 1) Сессию 2) В какую группу перемещаем 3) имя узла
resault = updateHost(ss, 'egaisoff', 'cash-20000679030-200006790301')
