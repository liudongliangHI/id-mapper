import os
from id_mapper.metanetx import make_pairs, Pair
from id_mapper.graph import insert_pairs
from py2neo import Graph
import re

from multiprocessing import Pool

N_PROCESSES = 20
N_LINES = 100

with open('ecodata.txt') as f:
    lines = list(f.readlines())

DATABASES = ['ecogene', 'eck', 'name', 'syn', 'genbank', 'sp', 'blattner', 'asap', 'genobase', 'cg']


def process_piece(chunk):
    for line in chunk:
        info = dict(zip(DATABASES, line.split('\t')))
        to_delete = []
        for key, value in info.items():
            if value in ('None', 'Null', 'Null\n', 'null', 'null\n'):
                to_delete.append(key)
            else:
                info[key] = info[key].strip("'; ").strip()
                info[key] = re.sub('\(\w\.\w\.\)', '', info[key])
        for key in to_delete:
            info.pop(key)
        info['name'] = [info['name']]
        if 'syn' in info:
            info['name'].extend(info['syn'].split(', '))
            info.pop('syn')
            info['name'] = [i.strip() for i in info['name']]
        pair_1 = Pair(info['blattner'], 'blattner')
        for key, value in info.items():
            if key != 'blattner':
                if key != 'name':
                    insert_pairs(graph, 'Gene', pair_1, Pair(value, key), organism='ecoli')
                else:
                    for n in value:
                        insert_pairs(graph, 'Gene', pair_1, Pair(n, key), organism='ecoli')


graph = Graph(host=os.environ['DB_PORT_7687_TCP_ADDR'], password=os.environ['NEO4J_PASSWORD'])

with Pool(processes=N_PROCESSES) as pool:
    pool.map(process_piece, [lines[i:i+N_LINES] for i in range(0, len(lines), N_LINES)])
