## Для работы программы используются пакета pymongo(версия 2.4), sshtunnel и bson
##Сначала удаляем pip uninstall pymongo
##Потом устанавливаем pip install pymongo==2.4


from pprint import pprint
from sshtunnel import SSHTunnelForwarder
import pymongo
from bson.dbref import DBRef


Mass = []

class pymongoClass():

    ##Подключение к MOMGO
    def ssh_pyMongo(self):
        mongo_port = 27017
        mongo_host = '127.0.0.1'

        # Подключение по SSH
        ssh_host = 'cashsrv2'
        ssh_user = 'root'
        ssh_port = 22
        ssh_password = 'Ma4u-Pik4u'
        i = 0


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
                    get_group_id_title = self.getGroupAndOrg(conn, 'artixcs', 'group', '_id', 'title')
                    DbrefsIdAndIP = self.geGroupAndFsrar(conn, 'artixcs', 'shop', 'parent', '$id', 'displayCode')
                    self.innerDict(get_group_id_title, DbrefsIdAndIP)
                    conn.close()
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
                for i in men:
                    if (i in id):
                        Mass.append([men[name], men[id]])
                        glossary[men[id]] = men[name]
            except:
                pass
        try:
            del glossary['_group_32_3870b6e4']
            del glossary['1']
        except:
            pass
        varName.close()
        return glossary

    def innerDict(self, get_group_id_title, DbrefsIdAndIP):
        """Объеденяем два словаря"""





qwe = pymongoClass()
qwe.ssh_pyMongo()

