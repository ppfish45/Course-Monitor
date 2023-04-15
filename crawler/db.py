from pymongo import MongoClient
import configparser
import os

# list MongoDB credentials at Course-Monitor/.course-monitor

PROJECT_PATH = os.path.join(os.path.dirname(__file__), "..")
CONFIG_PATH = os.path.join(PROJECT_PATH, ".course-monitor")

class DBClient(object):
    _instance = None

    def __new__(cls):
        if cls._instance == None:
            print("creating db instance...")
            cls._instance = super(DBClient, cls).__new__(cls)
            cls._instance.init()
        return cls._instance

    def init(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        connStr = config["mongodb"]["connstr"]

        print('connstr = ', connStr)
        self.client = MongoClient(connStr)

        print("switch to db: ", config["mongodb"]["dbname"])
        self.db = self.client[config["mongodb"]["dbname"]]

    def GetCollection(self, name):
        return self.db[name]

client = DBClient()
