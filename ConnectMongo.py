## Для работы программы используются пакета pymongo(версия 2.4), sshtunnel и bson
##Сначала удаляем pip uninstall pymongo
##Потом устанавливаем pip install pymongo==2.4


from pprint import pprint
from sshtunnel import SSHTunnelForwarder
import pymongo
from bson.dbref import DBRef


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
                    get_orgid_name = self.getGroupAndOrg(conn, 'artixcs', 'organization', '_id', 'name')
                    DbrefsIdAndIP = self.geGroupAndFsrar(conn, 'artixcs', 'shop', 'organizationExcise', '$id', 'displayCode')
                    fsrar_and_org = self.innerDict(get_orgid_name, DbrefsIdAndIP)
                    conn.close()
                    return fsrar_and_org
                except:
                    conn.close()
                    print("Повторите обращение к МонгоДБ")
        except:
            print("Ошибка подключения")

    def geGroupAndFsrar(self, conn, bdMongo, collection, dbrefsid, id, name):
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
        return glossary

    def getGroupAndOrg(self, conn, bdMongo, collection, id, name):
        """Получаем ИД группы и организацию"""
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
        resault = {}
        for i in get_group_id_title:
            for j in DbrefsIdAndIP:
                if i == DbrefsIdAndIP[j]:
                    glossary[j] = get_group_id_title[i]
        for fsrar in glossary:
            fsrar_edit = 'cash-' + str(fsrar[1:]) + '-' + str(fsrar[1:]) + '1'
            org = glossary[fsrar]
            if org in resault:
                resault[org].append(fsrar_edit)
            else:
                resault[org] = [fsrar_edit]
        # for i in resault:
        #     print("{} - {}".format(i, str(len(resault[i]))))
        return resault
