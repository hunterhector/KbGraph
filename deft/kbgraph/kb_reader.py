import sys


class KbReader:
    def __init__(self, kb_path):
        self.path = kb_path
        pass

    def __parse_entity(self, fields):
        identifier = fields[0]
        id_parts = identifier.split("_")

        source = None

        if identifier.startswith(":Entity_sent"):
            eid = identifier
            source = "sent"
        elif identifier.startswith(":Entity_NIL"):
            eid = id_parts[1]
            source = "EDL"
        elif identifier.startswith(":Entity_m"):
            eid = ".".join(id_parts[1:-1])
            source = "EDL"
        elif identifier.startswith(":Entity_inst"):
            eid = identifier
            source = "inst"
        else:
            eid = fields[0]
            print("Unknown identifier: " + eid)

        if len(fields) == 3:
            return "entity_property_" + fields[1], {"id": identifier, "source": source, "value": fields[2],
                                                    "entity_id": eid}
        elif len(fields) == 5:
            if ":" in fields[1]:
                return "relation_entity", \
                       {"arg1": fields[0], "arg2": fields[2], "relation": fields[1], "provenance": fields[3]}
            elif "mention" in fields[1]:
                return "entity_mention_" + fields[1], {"id": identifier, "source": source, "text": fields[2],
                                                       "mention_category": fields[1], "provenance": fields[3],
                                                       "entity_id": eid}

        # Indicate this line is not handled.
        return None

    def __get_arg_event_id(self, full_id):
        if full_id.startswith(":Event"):
            id_parts = full_id.split("_")
            short_id = []
            for part in id_parts[1:]:
                if part == 'evarg':
                    break
                short_id.append(part)
            short_id.append(id_parts[-1])
            return "_".join(short_id)

    def __parse_event_arg(self, fields):
        identifier = fields[0]
        arg_event_id = self.__get_arg_event_id(identifier)

        if len(fields) == 3:
            return "event_argument_property", {"id": identifier, "property": fields[1], "value": fields[2],
                                               "event": arg_event_id}
        elif len(fields) == 5:
            if ":" in fields[1]:
                return "relation_event_argument", \
                       {"arg1": identifier, "arg2": fields[2], "relation": fields[1], "provenance": fields[3],
                        "event": arg_event_id}
            else:
                return "event_argument_mention", {"id": identifier, "realis": fields[1].split(".")[1],
                                                  "provenance": fields[3], "text": fields[2], "event": arg_event_id,
                                                  "mention_category": fields[1]}

    def __parse_event_nugget(self, fields):
        identifier = fields[0]

        id_parts = identifier.split("_")
        event_id = "_".join(id_parts[2:])

        # print("Event id for nugget " + event_id)
        # input()

        if len(fields) == 3:
            return "event_nugget_property", {"id": event_id, "property": fields[1], "value": fields[2]}
        elif len(fields) == 5:
            if "mention" in fields[1]:
                return "event_nugget_" + fields[1], {"id": event_id, "realis": fields[1].split(".")[1],
                                                     "provenance": fields[3], "text": fields[2],
                                                     "mention_category": fields[1]}

    def __parse_event_string_arg(self, fields):
        identifier = fields[0]

        if len(fields) == 3:
            return "event_string_arg_property", {"id": identifier, "property": fields[1], "value": fields[2]}
        elif len(fields) == 5:
            if "mention" in fields[1]:
                return "event_string_arg", {"id": identifier, "type": fields[1], "provenance": fields[3],
                                            "text": fields[2], "mention_category": fields[1]}

    def __parse_string_relation(self, fields):
        identifier = fields[0]
        if len(fields) == 3:
            return "relation_arg_property", {"id": identifier, "property": fields[1], "value": fields[2]}
        elif len(fields) == 5:
            if "mention" in fields[1]:
                return "relation_arg_string", {"id": identifier, "type": fields[1], "provenance": fields[3],
                                               "text": fields[2], "mention_category": fields[1]}

    def __parse_entry(self, entry_str):
        parts = entry_str.split("\t")
        if parts[0].startswith(":Entity"):
            result = self.__parse_entity(parts)
            if result:
                return result
            else:
                print("Unhandled entity line %s with %d fields." % (entry_str, len(parts)))
                input()
        elif parts[0].startswith(":Event_evnug"):
            result = self.__parse_event_nugget(parts)
            if result:
                return result
            else:
                print("Unhandled event nugget line %s with %d fields." % (entry_str, len(parts)))
                input()
        elif parts[0].startswith(":Event") and "evarg" in parts[0]:
            result = self.__parse_event_arg(parts)
            if result:
                return result
            else:
                print("Unhandled event argument line %s with %d fields." % (entry_str, len(parts)))
                input()
        elif parts[0].startswith(":String_evarg"):
            result = self.__parse_event_string_arg(parts)
            if result:
                return result
            else:
                print("Unhandled event string line %s with %d fields." % (entry_str, len(parts)))
                input()
        elif parts[0].startswith(":String_arg"):
            result = self.__parse_string_relation(parts)
            if result:
                return result
            else:
                print("Unhandled string argument line %s with %d fields." % (entry_str, len(parts)))
        else:
            print("Remaining stuff: " + entry_str)
            input()
        return None

    def traversal(self):
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line.startswith(":"):
                    yield self.__parse_entry(line)
