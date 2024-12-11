import os
from database.mongodb import MongoDBHandler
from neo4j import GraphDatabase
from typing import List, Dict
import warnings

warnings.filterwarnings("ignore")

def get_data():
    dbhandler = MongoDBHandler()
    db = dbhandler.get_database()
    col = db[os.environ['COL_XY']]
    data = col.find({})
    data = [i for i in data]
    return data

class Neo4jHandler:

    def __init__(self):
        KG_URI = os.environ['KG_URI']
        AUTH = (os.environ['KG_USERNAME'], os.environ['KG_PWD'])

        with GraphDatabase.driver(KG_URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            print("Connection established.")
        self.driver = driver

    def close(self):
        self.driver.close()

    def create_graph(self, data: List[Dict]):
        with self.driver.session() as session:
            for document in data:
                for key, equation in document.items():
                    if key.startswith("Equation"):
                        x_variables = equation["Independent Variables (X)"]
                        y_variable = equation["Dependent Variable (Y)"]

                        # Create unique Y node
                        session.run(
                            """
                            MERGE (y:Y {name: $y_name})
                            """,
                            y_name=y_variable
                        )

                        # Create X nodes and relationships
                        for x in x_variables:
                            session.run(
                                """
                                MERGE (x:X {name: $x_name})
                                MERGE (y:Y {name: $y_name})
                                MERGE (x)-[:X]->(y)
                                """,
                                x_name=x,
                                y_name=y_variable
                            )

if __name__ == '__main__':

    data = get_data()
    neo4j_handler = Neo4jHandler()
    neo4j_handler.create_graph(data)