import pykson
import json
import sys
from typing import List, Dict
import random

from aspect_training_example_creator import AspectLinkExample


class AspectFilterer(object):
    def __init__(self, file_path):
        self.entity_count: Dict[str, int] = {}
        self.entities = set()
        self.file_path: str = file_path
        random.seed(1)
        self.pyk = pykson.Pykson()


    def read_links(self):
        pyk = pykson.Pykson()
        counter = 0
        with open(self.file_path) as f:
            for line in f:
                counter += 1
                if counter % 10000 == 0:
                    print(counter)
                # link = pyk.from_json(line, AspectLinkExample)
                link = json.loads(line)
                # self.entities.add(link.context.target_entity)
                self.entities.add(link["context"]["target_entity"])
                self.count_frequency(link)


    def create_files(self):
        w1, f1 = self.count_most_frequent()
        w2, f2 = self.count_least_frequent()
        w3, f3 = self.write_subsample(1000, "eal-v2.4-en-01-01-2020.test.jsonl")
        w4, f4 = self.write_subsample(1000, "eal-v2.4-en-01-01-2020.val.jsonl")
        w5, f5 = self.write_subsample(len(self.entities), "eal-v2.4-en-01-01-2020.train.jsonl")
        counter = 0

        with open(self.file_path) as f:
            for line in f:
                counter += 1
                if counter % 10000 == 0:
                    print(counter)
                for f in [f1, f2, f3, f4, f5]:
                    f(line)
        for writer in [w1, w2, w3, w4, w5]:
            writer.close()


    def register_write_matching_jsons(self, target_entities, writer):
        def do_register(line):
            # link = self.pyk.from_json(line, AspectLinkExample)
            link = json.loads(line)
            # if link.context.target_entity in target_entities:
            #     writer.write(self.pyk.to_json(link) + "\n")
            if link["context"]["target_entity"] in target_entities:
                writer.write(line)
        return do_register

    def count_most_frequent(self):
        writer = open("eal-v2.4-en-01-01-2020.frequent-entities.jsonl", "w")
        target_entities = set()
        for (entity, freq) in self.entity_count.items():
            if freq >= 1000:
                target_entities.add(entity)
                self.entities.remove(entity)
        return writer, self.register_write_matching_jsons(target_entities, writer)

    def count_least_frequent(self):
        target_entities = set()
        writer = open("eal-v2.4-en-01-01-2020.few-aspect-entities.jsonl", "w")
        for (entity, freq) in self.entity_count.items():
            if freq <= 2:
                self.entities.remove(entity)
                target_entities.add(entity)
        return writer, self.register_write_matching_jsons(target_entities, writer)

    def write_subsample(self, n: int, name: str):
        target_entities = set()
        writer = open(name, "w")
        entities = list(self.entities)
        random.shuffle(entities)
        for entity in entities[0:n]:
            self.entities.remove(entity)
            target_entities.add(entity)
        return writer, self.register_write_matching_jsons(target_entities, writer)






    def count_frequency(self, link):
        # entity = link.context.target_entity
        entity = link["context"]["target_entity"]
        if entity not in self.entity_count:
            self.entity_count[entity] = 0
        self.entity_count[entity] += 1

if __name__ == '__main__':
    path = sys.argv[1]
    # path = "/mnt/grapes/share/entity_aspect_datasets/eal-v2.4-en-01-01-2020.jsonl"
    af = AspectFilterer(path)
    af.read_links()
    af.create_files()



