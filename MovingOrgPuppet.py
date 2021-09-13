# Скрипт для перемещения организация на puppet
# api documentation https://apidocs.theforeman.org/foreman/2.5/apidoc/v2.html
import os

import requests
import urllib3
from pprint import pprint
from ConnectMongo import pymongoClass
from time import sleep
from traceback import format_exc
import pandas as pd

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
        writeLog("Не получили ID окружений. Выход из программы")
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
        writeLog("Не получили ID хостгрупп. Выход из программы")
        exit(0)

def writeLog(data):
    """Запись лог файла перемещения"""
    with open("log.txt", 'a', encoding='utf8') as f:
        f.write(str(data) + '\n')

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
        print('Неверно указано куда перемещаем host {}({})'.format(host, envgroup))
    if update_host:
        if update_host.status_code == 200:
            writeLog(list_host)
            writeLog(update_host.json())
            print('Узел {} успешно перемещен в {}({})'.format(host, envgroup, update_host.status_code))
            writeLog('Узел {} успешно перемещен в {}({})'.format(host, envgroup, update_host.status_code))
        else:
            print('Узел {} не перемещен в {}. Не известная ошибка({})...'.format(host, envgroup, update_host.status_code))
            writeLog('Узел {} не перемещен в {}. Не известная ошибка({})...'.format(host, envgroup, update_host.status_code))
    else:
        print('Узел {} не перемещен в {}. Не выполнился update_host'.format(host, envgroup))
        writeLog('Узел {} не перемещен в {}. Не выполнился update_host'.format(host, envgroup))

def getDataMongo():
    """Получаем данные с МонгоДб"""
    app = pymongoClass()
    while True:
        try:
            dict_org_host, fsrar_orig_del_umul, fsrar_orig, get_title_fsrar = app.ssh_pyMongo()
            if dict_org_host:
                return dict_org_host, fsrar_orig_del_umul, fsrar_orig, get_title_fsrar
        except:
            continue

def createExcelFile(fsrar_orig_del_umul, fsrar_orig, get_title_fsrar, org):
    """Формируем Excel файл с выходными данными"""
    del get_title_fsrar['All']
    fsrar_in_umul = list(set(fsrar_orig[org]) - set(fsrar_orig_del_umul[org]))
    fsrar_not_umul = fsrar_orig_del_umul[org]
    list_fsrar_in_umul = [[get_title_fsrar[i], i, 'Всегда в эмуляторе'] for i in fsrar_in_umul]
    list_fsrar_not_umul = [[get_title_fsrar[i], i, 'Перемещены в эмулятор'] for i in fsrar_not_umul]
    frame = pd.concat([pd.DataFrame(list_fsrar_not_umul), pd.DataFrame(list_fsrar_in_umul)])
    frame.rename(columns={0: 'ТТ', 1: 'ФСРАР', 2: 'Статус ТТ'}, inplace=True)
    frame.to_excel('Результат.xlsx', index=False)


# Удаляем лог файл
if os.path.exists('log.txt'):
    os.remove('log.txt')

# Просим пользователя выбрать куда перемещаем хосты в Foreman
list_foreman_group = {1: 'egaisoff', 2: 'work-group'}
move_host = int(input("Куда будем перемещать узлы foreman\n1)egaisoff\n2)work-group\nВведите число: "))
if move_host not in list_foreman_group:
    exit(0)

# Получаем данные с МонгоДб и общаемся с пользователем
foreman_group = list_foreman_group[move_host]
text = ''
numbering_org = {}
data_org_fsrar, fsrar_orig_del_umul, fsrar_orig, get_title_fsrar = getDataMongo()
for n, org in enumerate(data_org_fsrar):
    count_org = str(len(data_org_fsrar[org]))
    numbering_org[n] = org
    text = text + "{}) {} - {}\n".format(n, org, count_org)
select_org = int(input("\nВыбирите организацию:\n" + text + "Введите число:"))
fsrar_move = data_org_fsrar[numbering_org[select_org]]
print("\nОбщая информация:\nВыбрана организация: {}\nБудет перемещено в {}\n".format(numbering_org[select_org], foreman_group))

# Формируем Excel файл
createExcelFile(fsrar_orig_del_umul, fsrar_orig, get_title_fsrar, numbering_org[select_org])

# Общение с пользователем
check = int(input("Выберите следущий пункт\n1)Начать перенос\n2)Завершить программу\nВведите число:"))

# Здесь мы создаем сессию и подлкючаемся к API Foreman
ss = authForeman()
if not ss.get(show_status).json()['status'] == 200:
    writeLog('Нет доступа к API. Выход')
    exit(0)


# Здесь мы начинаем обновлять хосты на foreman
if check == 1:
    for fsrar_id_host in fsrar_move:
        try:
            resault = updateHost(ss, foreman_group, fsrar_id_host)     # 1) Сессия 2) Куда перемещаем 3) Имя узла
            sleep(3)
        except:
            print('Исключение - ошибка перемещения хоста {}'.format(fsrar_id_host))
            writeLog('Исключение - ошибка перемещения хоста {}\n{}'.format(fsrar_id_host, format_exc()))
print('Все действия закончены')
writeLog('Все действия закончены')