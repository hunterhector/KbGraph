import sys


class Collector:
    def __init__(self, *relation_names):
        self.__target_fields = relation_names
        self.__validator = set(relation_names)
        self.__info = {}
        self.__count = {}

        sys.stdout.write("Will collect following relations:\n")
        for n in relation_names:
            sys.stdout.write("\t%s\n" % n)

    def add_arg(self, s, relation, o):
        r = str(relation)

        # print("Adding " + s + " " + relation)

        if r not in self.__validator:
            return False

        if s in self.__info:
            if r not in self.__info[s]:
                self.__info[s][r] = o
                self.__count[s] += 1
        else:
            self.__info[s] = {r: o}
            self.__count[s] = 1

        if self.__count[s] == len(self.__target_fields):
            return True
        else:
            return False

    def pop(self, s):
        if self.__count[s] == len(self.__target_fields):
            self.__count.pop(s)
            return self.__info.pop(s)

    def get(self, s):
        return self.__info[s]
