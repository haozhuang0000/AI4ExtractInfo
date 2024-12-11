from langchain.chains import GraphCypherQAChain
from langchain.llms import OpenAI
from langchain.graphs import Neo4jGraph
import os
from dotenv import load_dotenv
load_dotenv()

class Neo4jLangChainHandler:

    llm = OpenAI(temperature=0)

    def __init__(self):
        # Load Neo4j credentials from environment variables
        self.graph = Neo4jGraph(
            url=os.getenv("KG_URI"),
            username=os.getenv("KG_USERNAME"),
            password=os.getenv("KG_PWD")
        )
        print("LangChain Neo4j Graph initialized successfully.")

    def query_graph(self, query: str):
        chain = GraphCypherQAChain.from_llm(llm=self.llm, graph=self.graph, allow_dangerous_requests=True)
        result = chain.run(query)
        return result

if __name__ == '__main__':

    neo4j_langchain_handler = Neo4jLangChainHandler()
    query = "List all X for the node **Post-Earnings-Announcement Drift (DRIFT)**."
    result = neo4j_langchain_handler.query_graph(query)
    print(result)