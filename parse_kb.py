from deft.kbgraph.kb_reader import KbReader
import sys
from deft.kbgraph.utils import Collector
from collections import defaultdict

event_arg_collector = Collector("type", "mention")
mention_collector = Collector("provenance", "type")
relation_arg_collector = Collector("type", "mention", "relation")


def process_relation(relations, relation):
    # print("New relation: ")
    # print(relation)
    # input()
    relations.append((relation['arg1'], relation['arg2'], relation['relation'], relation['provenance']))


def process_entity(entities, collector, s, key, value):
    ready = mention_collector.add_arg(s, key, value)
    if ready:
        entity_content = collector.pop(s)
        # print(entity_content)
        provenance = entity_content['provenance']
        entities[s] = {"text": provenance['text'], 'provenance': provenance['provenance'],
                       'type': entity_content['type']}


def read_data(kb_path):
    print("Going to read the KB.")
    count = 0

    kb = KbReader(kb_path)

    entities = {}
    relations = []
    event_args = defaultdict(list)

    for entry in kb.traversal():
        entry_type, content = entry
        count += 1
        # sys.stdout.write("\rRead %d lines." % count)

        if entry_type == "entity_property_type":
            process_entity(entities, mention_collector, content['id'], "type", content['value'])
        elif entry_type.startswith("entity_mention"):
            value = {'source': content['source'], 'provenance': content['provenance'],
                     'entity_id': content['entity_id'], 'text': content['text']}
            process_entity(entities, mention_collector, content['id'], "provenance", value)
        elif entry_type == "relation_event_argument":
            arg2 = content['arg2']
            event_id = content['event']
            relation_name = content['relation']
            event_type = relation_name.split(":")[0]
            relation_type = relation_name.split(":")[1].split(".")[0]

            relation_mention = (content['event'], arg2, event_type, relation_type, content['provenance'])

            event_args[event_id].append(relation_mention)

        elif entry_type == "event_string_arg":
            process_entity(entities, mention_collector, content['id'], "provenance", content)
        elif entry_type == "event_string_arg_property":
            process_entity(entities, mention_collector, content['id'], "type", content['value'])
        elif entry_type == "relation_entity":
            process_relation(relations, content)
        elif entry_type == "event_argument_mention":
            event = content['event']
        elif entry_type == "relation_arg_string":
            relation_arg_collector.add_arg(content['id'], "mention",
                                           {"text": content['text'], "provenance": content['provenance']})
        elif entry_type == "event_argument_property":
            if content["property"] == "type":
                event = content['event']
    print("Done reading.")

    return entities, event_args, relations


def main(kb_path):
    entities, event_args, relations = read_data(kb_path)
    count = 0
    for eid, arguments in event_args.items():
        print("Event argument of " + eid)

        if len(arguments) > 1:
            good_arg_count = 0
            for argument in arguments:
                arg2 = argument[1]
                event_type = argument[2]
                arg_type = argument[3]

                if arg2.startswith(":Entity_m"):
                    good_arg_count += 1
            if good_arg_count > 1:
                count += 1

    print("%d useful events found." % count)


if __name__ == '__main__':
    kb_path = sys.argv[1]
    main(kb_path)
