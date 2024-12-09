import os
from database.mongodb import MongoDBHandler
from neo4j import GraphDatabase
from langchain.chains import GraphCypherQAChain
from langchain.llms import OpenAI
from langchain.graphs import Neo4jGraph
from typing import List, Dict
import pandas as pd
def get_data():
    dbhandler = MongoDBHandler()
    db = dbhandler.get_database()
    col = db['test']
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

class Neo4jLangChainHandler:
    def __init__(self):
        # Load Neo4j credentials from environment variables
        self.graph = Neo4jGraph(
            url=os.getenv("KG_URI"),
            username=os.getenv("KG_USERNAME"),
            password=os.getenv("KG_PWD")
        )
        print("LangChain Neo4j Graph initialized successfully.")

    def query_graph(self, cypher_query: str):
        result = self.graph.query(cypher_query)
        return result

if __name__ == '__main__':

    data = get_data()
    neo4j_handler = Neo4jHandler()
    neo4j_handler.create_graph(data)
    neo4j_langchain_handler = Neo4jLangChainHandler()
    llm = OpenAI(temperature=0)
    chain = GraphCypherQAChain.from_llm(llm=llm, graph=neo4j_langchain_handler.graph, allow_dangerous_requests=True)
    query = "List all X for the node **Average excess net-buy of small trades**."
    result = chain.run(query)
    print(result)