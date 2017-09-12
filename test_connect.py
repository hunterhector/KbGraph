from neo4jrestclient.client import GraphDatabase

db_url = "http://accra.sp.cs.cmu.edu:7474/db/data/"
gdb = GraphDatabase(db_url, username='hector', password='hector')

person = gdb.labels.create("Person")
hector = gdb.nodes.create(name="hector", position="student")
person.add(hector)


for node in person.all():
    print("Removing %s. " % node.get("name"))
    node.delete()