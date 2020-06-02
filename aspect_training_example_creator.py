import json
from collections import Counter

import jsonpickle
from pykson import JsonObject, StringField, IntegerField, ListField, ObjectListField, ObjectField, Pykson, BooleanField
from typing import Set, Any, List, Dict, Tuple, Optional
from trec_car.read_data import iter_paragraphs, iter_pages, Paragraph, ParaLink, ParaText, iter_annotations, Para, Page, Section
import hashlib
import sys

def get_filter_words():
    return {"see also", "reference", "discography", "awards", "other", "gallery", "publications", "track listing", "sources", "cast", "references", "notes", "further reading", "external links", "bibliography"}

class RecursivePath(object):
    def __init__(self, heading_path, id_path):
        self.heading_path = heading_path[:]
        self.id_path = id_path[:]

    def update(self, next_heading: str, next_id: str):
        nheading = self.heading_path + [next_heading]
        nid = self.id_path + [next_id]
        return RecursivePath(nheading, nid)


class AspectDatum(object):
    def __init__(self,
                 pid: str,
                 sent_content: str,
                 para_content: str,
                 page_id: str,
                 page_title: str,
                 mention: str,
                 linked_entity_aspect: str,
                 linked_entity_id: str,
                 id_path: str,
                 path: List[str],
                 sent_entities: List[str],
                 para_entities: List[str],
                 sent_entities_coords,
                 para_entities_coords,
                 mention_start,
                 mention_end
                 ):

        self.pid = pid
        self.sent_content = sent_content
        self.para_content = para_content
        self.page_id = page_id
        self.page_title = page_title
        self.mention = mention
        self.section_path_id = id_path
        self.section_path = path
        self.linked_entity_aspect = linked_entity_aspect
        self.linked_entity_id = linked_entity_id
        self.sent_entities = sent_entities
        self.sent_entities_coords = sent_entities_coords
        self.para_entities = para_entities
        self.para_entities_coords = para_entities_coords
        self.mention_start = mention_start
        self.mention_end =  mention_end


class Location(JsonObject):
    location_id: str = StringField()
    page_id: str = StringField()
    page_title: str = StringField()
    paragraph_id: str = StringField()
    section_id: List[str] = ListField(str)
    section_headings: List[str] = ListField(item_type=str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subsections = []


class EntityMention(JsonObject):
    entity_name: str = StringField()
    entity_id: str = StringField()
    mention: str = StringField()
    target_mention: bool = BooleanField()
    entity_aspect: str
    start: int = IntegerField()
    end: int = IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entity_aspect = ""


class AnnotatedText(JsonObject):
    content: str = StringField()
    entities: List[EntityMention] = ObjectListField(EntityMention)


class Context(JsonObject):
    target_entity: str = StringField()
    location: Location = ObjectField(Location)
    sentence: AnnotatedText = ObjectField(AnnotatedText)
    paragraph: AnnotatedText = ObjectField(AnnotatedText)


class Aspect(JsonObject):
    aspect_id: str = StringField()
    aspect_name: str = StringField()
    location: Location = ObjectField(Location)
    aspect_content: AnnotatedText = ObjectField(AnnotatedText)

class AspectLinkExample(JsonObject):
    unhashed_id: str = StringField()
    id: str = StringField()
    context: Context = ObjectField(Context)
    true_aspect: str = StringField()
    candidate_aspects: List[Aspect] = ObjectListField(Aspect)


def run(loc, out_loc):
    data = {}
    linked_page_ids = set()
    total_results = 0
    page_counter = 0
    out_writer = open(out_loc, "w")
    seen_hashed_ids = set()
    stats = Counter()
    with open(loc, 'rb') as f:
        for page in iter_annotations(f):
            page_counter += 1
            p = page
            examples = extract_section_links(p, stats)
            if page_counter % 1000 == 0:
                print(stats)
                print("Pages Parse / Example Created: {} / {}".format(page_counter, total_results))
            parse(examples, data, linked_page_ids)
            total_results += len(examples)

    with open(loc, 'rb') as f:
        page_counter = 0
        for page in iter_pages(f):
            page_counter += 1
            # if page_counter % 1000 == 0:
            #     print(stats)
            #     print("Pages Parse / Example Created: {} / {}".format(page_counter, total_results))
            get_examples_with_path(out_writer, page, data, linked_page_ids, seen_hashed_ids, stats)


    out_writer.close()

def extract_section_links(p: Page, stats):
    rpath_base = RecursivePath([p.page_name], [p.page_id])
    results = find_section_links_in_children(p.skeleton, rpath_base, stats)
    return results


def find_section_links_in_children(children, rpath:RecursivePath, stats):
    section_links = []
    for child in children:
        if isinstance(child, Para):
            section_links.extend(find_section_links_in_paragraph(child.paragraph, rpath, stats))

        elif isinstance(child, Section):
            if child.heading.lower() in get_filter_words():
                continue
            new_rpath = rpath.update(child.heading, child.headingId)
            section_links.extend(find_section_links_in_children(child.children, new_rpath, stats))

    return section_links


def find_section_links_in_paragraph(paragraph: Paragraph, rpath: RecursivePath, stats):
    para_links = []
    ptext = paragraph.get_text()
    if len(ptext) <= 25:
        return []

    entities = []
    start = 0
    for body in paragraph.bodies:
        if isinstance(body, ParaText):
            start += len(body.text)
        elif isinstance(body, ParaLink):
            entity = {}
            entity["entity_name"] = body.page
            entity["entity_id"] = body.pageid
            entity["mention"] = body.anchor_text
            entity["entity_aspect"] = body.link_section
            entity["section_path_id"] = rpath.id_path
            entity["section_path"] = rpath.heading_path
            entity["pid"] = paragraph.para_id
            pstart = ptext.index(body.anchor_text)
            pend = pstart + len(body.anchor_text)
            entity["start"] = pstart
            entity["end"] = pend
            if body.link_section is not None:
                if body.pageid == rpath.id_path[0]:
                    stats["self_links"] += 1
                else:
                    stats["non_self_links"] += 1
            entities.append(entity)


    for body in paragraph.bodies:
        if isinstance(body, ParaLink):
            if body.link_section is not None:
                cur_entity = None
                for entity in entities:
                    if entity["mention"] == body.anchor_text:
                        cur_entity = entity

                plink = {}
                for (k, v) in cur_entity.items():
                    plink[k] = v
                plink["entities"] = entities
                plink["text"] = ptext
                plink["section_path"] = rpath.heading_path
                plink["section_path_id"] = rpath.id_path
                para_links.append(plink)
    return para_links

def parse(examples, data, linked_page_ids):
    for ex in examples:
        if len(ex["text"]) < 50:
            continue

        sentence, mentioned_entity, sent_entities, para_entities, sent_entities_coords, para_entities_coords = grab_sentence(ex)
        datum = AspectDatum(
            pid=ex["pid"],
            sent_content=sentence,
            para_content=ex["text"],
            mention=mentioned_entity["mention"],
            linked_entity_id=mentioned_entity["entity_id"],
            linked_entity_aspect=mentioned_entity["entity_aspect"].replace("_", " "),
            # page_mentioned_in=ex["eid"],
            path=mentioned_entity["section_path"],
            id_path=mentioned_entity["section_path_id"],
            page_id=ex["section_path_id"][0],
            page_title=ex["section_path"][0],
            sent_entities=sent_entities,
            sent_entities_coords=sent_entities_coords,
            para_entities=para_entities,
            para_entities_coords=para_entities_coords,
            mention_start=mentioned_entity["start"],
            mention_end=mentioned_entity["end"]
        )

        id = mentioned_entity["entity_id"]
        linked_page_ids.add(id.replace("enwiki:", ""))
        if id not in data:
            data[id] = []
        data[id].append(datum)
    return data, linked_page_ids

def grab_sentence(entry):
    # note : -> Changed so that entry contains linked entity (don't have to go searching for it now in entities entry)
    start = int(entry["start"])
    end = int(entry["end"])
    text = entry["text"]
    while start > 0:
        start -= 1
        if text[start] == ".":
            start += 1
            break

    while end < len(text) - 1:
        end += 1
        if text[end] == ".":
            break
    end += 1
    sentence = text[start:end].strip()

    # Also check to see if there were other entities in the sentence
    sent_entities = set()
    sent_entities_coords = []
    for sent_entity in entry["entities"]:
        try:
            sent_index = sentence.index(sent_entity["mention"])
        except ValueError:
            continue

        copied_entity = dict(sent_entity.items())
        copied_entity["start"] = sent_index
        copied_entity["end"] = sent_index + len(copied_entity["mention"])
        sent_entities.add(copied_entity["entity_id"])
        sent_entities_coords.append(copied_entity)

    # And grab all entities in paragraph
    para_entities = set()
    para_entities_coords = []
    mentioned_entity = None
    for para_entity in entry["entities"]:
        mention = para_entity["mention"]
        if mention == entry["mention"] and para_entity["entity_aspect"] is not None:
            mentioned_entity = para_entity
        tindex = text.index(mention)
        para_entity["start"] = tindex
        para_entity["end"] = tindex + len(mention)
        para_entities.add(para_entity["entity_id"])
        para_entities_coords.append(para_entity)
    return sentence, mentioned_entity, list(sent_entities), list(para_entities), sent_entities_coords, para_entities_coords

def do_hash(unhashed_id):
    hashed_id = hashlib.md5()
    hashed_id.update(unhashed_id.encode())
    return str(hashed_id.hexdigest())

def get_examples_with_path(out_writer, page, data: Dict[str, List[AspectDatum]], linked_page_ids, seen_hashed_ids, stats):
    n_id = page.page_id.replace("enwiki:", "")
    if n_id in linked_page_ids:
        possible_examples = data[page.page_id]
        # candidates = recursive_get_page_candidates(page)
        candidates = get_top_level_candidates(page)
        if len(candidates) < 3:
            return
        for datum in possible_examples:
            target_candidate = None
            for candidate in candidates:
                aspect = datum.linked_entity_aspect.replace("_", " ")
                if aspect in candidate.location.section_headings or aspect in candidate.location.subsections:
                    target_candidate = candidate
                    break

            # Found a match in either top-level section or a child section
            # if target_candidate is not None and target_candidate["aspect_headings"][1] not in filter_words:
            if target_candidate is not None:
                link_example = AspectLinkExample()
                link_example.true_aspect = target_candidate.aspect_id
                link_example.candidate_aspects = candidates

                # Raw Context ID (before using MD5 hash)
                final_id = [datum.page_id, "/".join(datum.section_path_id) + "/" + datum.pid, datum.linked_entity_id, datum.mention,
                            "(" + str(datum.mention_start) + "," + str(datum.mention_end) + ")"]
                final_id = "".join(final_id).replace(" ", "%20")
                link_example.unhashed_id = final_id

                # Context ID (output of MD5 hash)
                hashed_id = do_hash(final_id)

                # Stupid fix for odd problem where some of the examples are duplicates. Makes sure we don't add them.
                if hashed_id in seen_hashed_ids:
                    continue
                seen_hashed_ids.add(hashed_id)
                link_example.id = hashed_id
                example_context = Context()

                # create location and add it to the context
                example_location = Location()
                example_location.page_id = datum.page_id
                example_location.page_title = datum.page_title
                example_location.paragraph_id = datum.pid
                example_location.section_id = datum.section_path_id
                example_location.section_headings = [datum.section_path[-1]]
                example_location.location_id = do_hash("/".join(datum.section_path_id) + "/" + datum.pid)
                example_context.location = example_location
                example_context.target_entity = datum.linked_entity_id

                # make note if the entity in the sentence is our mention
                sentence = AnnotatedText()
                sentence.content = datum.sent_content
                sentence.entities = [entity_to_em(entity, datum.mention) for entity in datum.sent_entities_coords]
                example_context.sentence = sentence

                paragraph = AnnotatedText()
                paragraph.content = datum.para_content
                paragraph.entities = [entity_to_em(entity, datum.mention) for entity in datum.para_entities_coords]
                example_context.paragraph = paragraph


                link_example.context = example_context

                if link_example.context.location.page_id == link_example.context.target_entity:
                    stats["self_link"] += 1
                else:
                    stats["non_self_link"] += 1

                jstring = Pykson().to_json(link_example)
                jdict = json.loads(jstring)



                # remove null entries and target_mention fields
                for candidate in jdict["candidate_aspects"]:
                    pid = candidate["location"]["paragraph_id"]
                    if pid is None or pid == "null":
                        del candidate["location"]["paragraph_id"]
                    for entity in candidate["aspect_content"]["entities"]:
                        del entity["target_mention"]

                jstring = json.dumps(jdict) + "\n"
                out_writer.write(jstring)

def entity_to_em(entity, mention) -> EntityMention:
    em = EntityMention()
    em.mention = entity["mention"]
    em.start = entity["start"]
    em.end = entity["end"]
    em.entity_id = entity["entity_id"]
    em.entity_name = entity["entity_name"]
    em.target_mention = (entity["mention"] == mention) and entity["entity_aspect"] is not None

    # this is only a temporary field that does not get written to a json
    em.entity_aspect = entity["entity_aspect"]
    return em

def verify_valid_target_mention(entities: List[EntityMention]):
    mention_count = 0
    for entity in entities:
        mention_count += entity.target_mention

    if mention_count != 1:
        print("PROBLEM!")
        raise RuntimeError("Incorrect number of entity counts: {}".format(mention_count))


def add_entity_positions(candidate):
    text = candidate["content"]
    entities = candidate["entities"]
    for entity in entities:
        mention = entity["mention"]
        c_start = text.index(mention)
        c_end = c_start + len(mention)
        entity["start"] = c_start
        entity["end"] = c_end


def get_top_level_candidates(page: Page) -> List[Aspect]:
    candidates = []
    filter_words = get_filter_words()
    for section in page.skeleton:
        if isinstance(section, Section):
            try:
                sub_ids, sub_headings = zip(*get_sub_sections(section))
            except ValueError:
                sub_ids, sub_headings = [], []

            # Remove candidates with undesirable headings (like references or external links)
            bad_candidate = False
            for heading in list(sub_headings) + [section.heading]:
                if heading.lower() in filter_words:
                    bad_candidate = True
                    break
            if bad_candidate:
                continue

            loc = Location()
            loc.page_title = page.page_name
            loc.page_id = page.page_id
            loc.paragraph_id = None
            loc.section_id = [page.page_id] + [section.headingId]
            loc.section_headings = [section.heading]
            loc.subsections = list(sub_headings)
            loc.location_id = do_hash(page.page_id + "/" + "/".join(loc.section_headings))

            anno = AnnotatedText()
            anno.content = section.get_text_with_headings()
            entities = get_entities(section)
            seen = set()
            filtered_entities = []
            for entity in entities:
                if entity.entity_id in seen:
                    continue
                seen.add(entity.entity_id)

                start = anno.content.index(entity.mention)
                end = start + len(entity.mention)
                entity.start = start
                entity.end = end
                if not entity.mention == anno.content[start:end]:
                    print("Problem")
                filtered_entities.append(entity)
            anno.entities = filtered_entities

            ac = Aspect()
            ac.aspect_id = page.page_id + "/" + section.headingId
            ac.aspect_name = section.heading
            ac.location = loc
            ac.aspect_content = anno
            candidates.append(ac)
    return candidates

def get_sub_sections(section: Section) -> List[Tuple[str, str]]:
    sub_sections = []
    for child in section.children:
        if isinstance(child, Section):
            sub_sections.append((child.headingId, child.heading))
            sub_sections.extend(get_sub_sections(child))
    return sub_sections

def get_entities(section: Section) -> List[EntityMention]:
    entities = []
    for child in section.children:
        if isinstance(child, Para):
            for body in child.paragraph.bodies:
                if isinstance(body, ParaLink):
                    em = EntityMention()
                    em.mention = body.anchor_text
                    em.entity_name = body.page
                    em.entity_id = body.pageid
                    em.entity_aspect = body.link_section
                    entities.append(em)
        elif isinstance(child, Section):
            entities.extend(get_entities(child))
    return entities


def get_candidate_entities(candidate: Section):
    entities = set()
    for child in candidate.children:
        if isinstance(child, Para):
            for body in child.paragraph.bodies:
                if isinstance(body, ParaLink):
                    entities.add(body.pageid)
        elif isinstance(child, Section):
            more_entities = get_candidate_entities(child)
            for entity in more_entities:
                entities.add(entity)
    return list(entities)

if __name__ == '__main__':
    pyk = Pykson()
    cbor_loc, out_loc = sys.argv[1:3]
    run(cbor_loc, out_loc)
    # cbor_loc = "/home/jsc57/data/unprocessedAllButBenchmark.cbor/unprocessedAllButBenchmark.cbor"



    # cbor_loc = "/home/jsc57/data/test200/test200-train/train.pages.cbor"
    # cbor_loc = "/mnt/grapes/share/wiki2020/car-wiki2020-01-01/enwiki2020.cbor"
    # cbor_loc = "/home/jsc57/data/old_v1_5_corpus/train/train.fold1.cbor"
    # run(cbor_loc, out_loc)
    # print(jsonpickle.encode(a, unpicklable=False))

    # run(cbor_loc, "wiki_2016.jsonl")
    # run(cbor_loc, "wiki_old_aspects.jsonl")
    # run(cbor_loc, "wiki_2020.jsonl")
    # with open("/mnt/grapes/share/entity_aspect_datasets/water_quality_2020.jsonl") as f:
    # with open("wiki_old_aspects.jsonl") as f:


