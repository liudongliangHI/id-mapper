from collections import deque
from py2neo import NodeSelector, Node, Relationship


class Is(Relationship): pass


class NoSuchNode(Exception):
    """
    Raised if no node for the object exists
    """
    def __init__(self, node_id, database):
        self.node = node_id
        self.database = database

    def __str__(self):
        return 'No node for object {} from database {}'.format(
            self.node,
            self.database,
        )


def insert_pairs(graph, label, pair1, pair2):
    """Merge nodes to database and create mutual IS relationships between

    :param graph: Graph
    :param label: "Metabolite" or "Reaction"
    :param pair1: node 1
    :param pair2: node 2
    :return:
    """
    nodes = [
        Node(
            label,
            id=pair.metabolite,
            db_name=pair.database
        )
        for pair in (pair1, pair2)
        ]
    for n in nodes:
        graph.merge(n)
    graph.merge(Is(nodes[0], nodes[1]))
    graph.merge(Is(nodes[1], nodes[0]))


def find_match(graph, object_id, db_from, db_to):
    """Return id for given metabolite from the corresponding database

    :param graph: Graph
    :param object_id: metabolite id
    :param db_from: database name, f.e "bigg"
    :param db_to: database name, f.e "mnx"
    :return:
    """
    selector = NodeSelector(graph)
    result = []
    found = False
    for labels in ('Metabolite', 'Reaction'):
        selected = list(selector.select(labels, id=object_id, db_name=db_from))
        assert len(selected) <= 1
        if selected:
            found = True
            result.extend(collect_matches(graph, selected[0], db_to))
    if not found:
        raise NoSuchNode(object_id, db_from)
    return result


def collect_matches(graph, node, db_to):
    """
    Perform BFS to find all the linked objects with the required database name
    """
    result = []
    visited = set()
    to_visit = deque([node])
    while to_visit:
        current = to_visit.pop()
        if current['db_name'] == db_to:
            result.append(current['id'])
        for rel in graph.match(start_node=current, rel_type='IS'):
            n = rel.end_node()
            if n['id'] + n['db_name'] not in visited:
                to_visit.appendleft(n)
                visited.add(n['id'] + n['db_name'])
    return result