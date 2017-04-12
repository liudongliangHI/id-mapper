# coding=utf-8
# Copyright 2014 Novo Nordisk Foundation Center for Biosustainability, DTU.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from id_mapper.metanetx import make_pairs
from id_mapper.graph import insert_pairs
from py2neo import Graph

from multiprocessing import Pool

N_PROCESSES = 20
N_LINES = 100

with open('chem_xref_mini_1.tsv') as f:
    lines = list(f.readlines())


def process_piece(chunk):
    for line in chunk:
        x, y = make_pairs(line)
        if x.metabolite != y.metabolite:
            insert_pairs(graph, 'Metabolite', x, y)

graph = Graph(host=os.environ['DB_PORT_7687_TCP_ADDR'], password=os.environ['NEO4J_PASSWORD'])

with Pool(processes=N_PROCESSES) as pool:
    pool.map(process_piece, [lines[i:i+N_LINES] for i in range(0, len(lines), N_LINES)])

