from pymongo import MongoClient
import os
import pandas as pd
import json
import json_repair
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(override=True)

class MongoDBHandler:
    def __init__(self):
        super().__init__()
        self.DB_URL = os.environ['MONGODB_URL']
        self.client = MongoClient(self.DB_URL)

    def get_database(self, DB=os.environ['DATABASE']):
        """
        :param DB: Your mongodb database, default is local
        """
        db = self.client[DB]
        return db

    def insert_db(self, data, col_name, dbs_name='AIDF_NLP_Capstone'):

        if isinstance(data, pd.DataFrame):
            DB = self.get_database(DB=dbs_name)
            collection = DB[col_name]
            collection.insert_many(data.to_dict('records'))
        if isinstance(data, list):
            DB = self.get_database(DB=dbs_name)
            collection = DB[col_name]
            collection.insert_many(data)

if __name__ == '__main__':

    mongodb_handler = MongoDBHandler()
    db = mongodb_handler.get_database()
    col = db[os.environ['COL']]
    md_path = os.path.join(os.getcwd(), '../', 'output_dir')
    contents = os.listdir(md_path)
    for output in contents:
        jsons_path = os.path.join(md_path, output)
        jsons_ls = os.listdir(jsons_path)
        for json_data in jsons_ls:
            if 'xy' in json_data:
                file_path = os.path.join(jsons_path, json_data)
                with open(file_path, "r") as file:
                    data = json.load(file)
                data = json_repair.loads(data)
                data['rp_title'] = output
                col.insert_one(data)
