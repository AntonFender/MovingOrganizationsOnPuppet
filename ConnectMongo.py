## Для работы программы используются пакета pymongo(версия 2.4), sshtunnel и bson
##Сначала удаляем pip uninstall pymongo
##Потом устанавливаем pip install pymongo==2.4


from pprint import pprint
from sshtunnel import SSHTunnelForwarder
import pymongo
from bson.dbref import DBRef
import configparser
import copy

class pymongoClass():
    def ssh_pyMongo(self):
        mongo_port = 27017
        mongo_host = '127.0.0.1'

        # Подключение по SSH
        ssh_host = 'cashsrv2'
        ssh_user = 'root'
        ssh_port = 22
        ssh_password = 'Ma4u-Pik4u'

        try:
            print("Пытаюсь установить соединение")
            with SSHTunnelForwarder(
                    (ssh_host, ssh_port),
                    ssh_username=ssh_user,
                    ssh_password=ssh_password,
                    remote_bind_address=(mongo_host, mongo_port)) as tunnel:

                try:
                    conn = pymongo.MongoClient(host=mongo_host, port=tunnel.local_bind_port)
                    print("Соединение установлено!")
                except:
                    print("Соединение не установлено!")
                try:
                    get_title_fsrar = self.getGroupAndOrg(conn, 'artixcs', 'shop', 'displayCode', 'title')
                    get_orgid_name = self.getGroupAndOrg(conn, 'artixcs', 'organization', '_id', 'name')
                    id_and_fsrar_del_umul, id_and_fsrar = self.getGroupAndFsrar(conn, 'artixcs', 'shop', 'organizationExcise', '$id', 'displayCode')
                    fsrarEdit_and_org_del_umul, fsrarOrig_and_org_del_umul  = self.innerDict(get_orgid_name, id_and_fsrar_del_umul)
                    fsrarEdit_and_org, fsrarOrig_and_org = self.innerDict(get_orgid_name, id_and_fsrar)
                    conn.close()
                    return fsrarEdit_and_org_del_umul, fsrarOrig_and_org_del_umul, fsrarOrig_and_org, get_title_fsrar
                except:
                    conn.close()
                    print("Повторите обращение к МонгоДБ")
        except:
            print("Ошибка подключения")

    def getGroupAndFsrar(self, conn, bdMongo, collection, dbrefsid, id, name):
        """# 1.Коннект 2.База в монго 3.Нужная коллекция 4.DBrefs 5.Что нужно из DBrefs 6.Нужное значение в коллекции"""
        glossary = dict()       # Создаем пустой словарь
        db = conn[bdMongo]      # Выбираем базу данных в МОНГО
        coll = db[collection]   # Выбираем коллекцию в МОНГО
        varName = coll.find()   # Помещаем в переменнную ссылку на результирующий набор запроса

        for men in varName:
            try:
                dbrefs = men.get(dbrefsid)                  # Получаем DBRef parent
                resDbRefs = DBRef.as_doc(dbrefs).get(id)    # Вытаскиваем значение из выбраного DBRef
                glossary[men[name]] = resDbRefs
            except:
                pass
        try:
            del glossary['All']
        except:
            pass
        varName.close()
        # Удаляем все ФСРАР ИД, которые находятся в эмуляторе(зверинец)
        list_del_emul = self.getFsrarUmulator(copy.deepcopy(glossary))
        return list_del_emul, glossary

    def getGroupAndOrg(self, conn, bdMongo, collection, id, name):
        """Получаем ИД организации и имя организацию"""
        glossary = dict()       # Создаем пустой словарь
        db = conn[bdMongo]      # Выбираем базу данных в МОНГО
        coll = db[collection]   # Выбираем коллекцию в МОНГО
        varName = coll.find()   # Помещаем в переменнную ссылку на результирующий набор запроса

        for men in varName:
            try:
                if men[name] != 'Тамада ООО':
                    glossary[men[id]] = men[name]
            except:
                pass
        varName.close()
        return glossary

    def innerDict(self, get_group_id_title, DbrefsIdAndIP):
        """Объеденяем два словаря"""
        glossary = {}
        resault_edit_fsrar = {}
        resault_orig_fsrar = {}
        for i in get_group_id_title:
            for j in DbrefsIdAndIP:
                if i == DbrefsIdAndIP[j]:
                    glossary[j] = get_group_id_title[i]
        for fsrar in glossary:
            fsrar_edit = 'cash-' + str(fsrar[1:]) + '-' + str(fsrar[1:]) + '1'
            org = glossary[fsrar]
            if org in resault_edit_fsrar:
                resault_edit_fsrar[org].append(fsrar_edit)
            else:
                resault_edit_fsrar[org] = [fsrar_edit]
            if org in resault_orig_fsrar:
                resault_orig_fsrar[org].append(fsrar)
            else:
                resault_orig_fsrar[org] = [fsrar]
        return resault_edit_fsrar, resault_orig_fsrar

    def getFsrarUmulator(self, glossary):
        """Получаем фсрар ид из эмулятора и убираем эти фсрар из списка полученого из монгоДБ"""
        list_emul_fsrar = []
        path = r'\\172.16.253.7\SysWOW64\pkcs11Emulators.ini'
        path2 = r'\\172.16.253.13\SysWOW64\pkcs11Emulators.ini'
        config = configparser.ConfigParser()
        config2 = configparser.ConfigParser()
        config.read(path)
        config2.read(path2)
        for i in config:
            try:
                FSRAR = config.get(i, 'Name')
                list_emul_fsrar.append(FSRAR)
            except:
                pass
        for i in config2:
            try:
                FSRAR = config2.get(i, 'Name')
                list_emul_fsrar.append(FSRAR)
            except:
                pass
        for i in list_emul_fsrar:
            try:
                del glossary[i]
            except:
                pass
        return glossary


# qwe = pymongoClass()
# q = qwe.ssh_pyMongo()
