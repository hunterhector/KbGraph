from neo4j.v1 import GraphDatabase, basic_auth
from neo4jrestclient.client import GraphDatabase

class NeoV1Manager:
    def __init__(self, bolt_url, usr, passwd):
        self.driver = GraphDatabase.driver(bolt_url, auth=basic_auth(usr, passwd))

    def execute(self, query):
        session = self.driver.session()
        result = session.run(query)
        session.close()
        return result

    def clear(self):
        """
        Delete everything! Try not to use it.
        :return: 
        """
        self.execute("MATCH (n)"
                     "DETACH DELETE n")


if __name__ == '__main__':
    manager = NeoV1Manager("bolt://accra.sp.cs.cmu.edu:7687", "hector", "hector")
    manager.clear()
