import collections
import glob
import os.path
import re
from typing import Dict
from typing import List
from typing import TextIO

import click
from seqeval import metrics

DEP_PATTERN = r"^\*\s-?\d+\s-?\d+([DPAIOR])\s\d+/\d+\s(.*)"
STP_PATTERN = r"^\# Step-ID:(.*)"
STC_PATTERN = r"^\# Sentence-ID:(.*)"
TTL_PATTERN = r"^\# Title-ID:(.*)"


class Token:
    # ref. https://hayashibe.jp/tr/mecab/dictionary/ipadic
    def __init__(self, surface, pos1, pos2, netag):
        self.surface = surface
        self.pos1 = pos1  # 品詞 (e.g. 名詞)
        self.pos2 = pos2  # 品詞細分類1 (e.g. 普通名詞)
        self.netag = netag

    def __repr__(self):
        return f"#Token({self.surface},{self.pos1},{self.pos2},{self.netag})"


def retrieve_recipes(root: str):
    """Search recipe dirs by searching from given root dir.

    root (str): full path to root directory of copurs
    """
    for _dir in glob.glob(os.path.join(root, "*")):
        if not os.path.isdir(_dir):
            continue
        yield _dir


def retrieve_words(filename: str, entity: bool = False) -> List[str]:
    def extract_words(file: TextIO):
        sentences: List[List[Token]] = []
        words: List[Token] = []

        for line in file:
            line = line.rstrip("\n")
            # match if line represents dependency arc
            dep_ret = re.match(DEP_PATTERN, line)
            stp_ret = re.match(STP_PATTERN, line)
            stc_ret = re.match(STC_PATTERN, line)
            ttl_ret = re.match(TTL_PATTERN, line)

            if dep_ret or stp_ret or stc_ret or ttl_ret:
                continue

            if line == "EOS":
                sentences.append(words)
                words = []
                continue

            word, features, netag = line.split("\t")
            pos1, pos2, *_ = features.split(",")
            token = Token(word, pos1, pos2, netag)
            words.append(token)

        if entity:
            list_entities = []
            for words in sentences:
                netag_sentence = [word.netag for word in words]
                entities = metrics.sequence_labeling.get_entities(netag_sentence)  # NOQA
                entities = [span[0] for span in entities]
                list_entities.append(entities)
            return list_entities

        else:
            word_sentences = []
            for words in sentences:
                word_sentence = [word.surface for word in words]
                word_sentences.append(word_sentence)
            return word_sentences

    with open(filename) as f:
        words = extract_words(f)

    return words


def retrieve_deps(file_name: str) -> List[str]:
    """Open and retrieve dependency arcs.

    file_name (str): file name to be opened
    """

    def _count(file: TextIO) -> List[str]:
        arcs = []
        for line in file:
            line = line.rstrip("\n")
            # match if line represents dependency arc
            ret = re.match(DEP_PATTERN, line)
            if not ret:
                continue
            arc_type = ret.group(2)
            arcs.append(arc_type)
        return arcs

    with open(file_name) as fp:
        return _count(fp)


def retrieve_chunks(file_name: str) -> List[str]:
    """Open and retrieve dependency arcs.

    file_name (str): file name to be opened
    """

    def _count(file: TextIO) -> List[str]:
        arcs = []
        for line in file:
            line = line.rstrip("\n")
            # match if line represents dependency arc
            ret = re.match(DEP_PATTERN, line)
            if not ret:
                continue
            arc_type = ret.group(1)
            arcs.append(arc_type)
        return arcs

    with open(file_name) as fp:
        return _count(fp)


@click.command()
@click.option("--corpus-root", default="./cpc1.0")
def main(corpus_root: str):
    """Read annotated recipes and count number of arcs and their types.

    corpus_root (str): full path to root directory of corpus
    """

    def _merge_counter(source_counter: Dict[str, int], target_counter: Dict[str, int]):
        for key, value in source_counter.items():
            target_counter[key] = target_counter.get(key, 0) + value

        return target_counter

    # counter
    word_counter: Dict[str, int] = {}
    netag_counter: Dict[str, int] = {}
    dep_counter: Dict[str, int] = {}
    chunk_counter: Dict[str, int] = {}

    for recipe_dir in retrieve_recipes(corpus_root):
        title_file_name = os.path.join(recipe_dir, "title.txt")
        step_file_name = os.path.join(recipe_dir, "step.txt")

        for file_name in [title_file_name, step_file_name]:
            list_words = retrieve_words(file_name)
            _word_counter = collections.Counter(sum(list_words, []))
            _merge_counter(_word_counter, word_counter)
            list_netags = retrieve_words(file_name, entity=True)
            _netag_counter = collections.Counter(sum(list_netags, []))
            _merge_counter(_netag_counter, netag_counter)
            deps = retrieve_deps(file_name)
            _dep_counter = collections.Counter(deps)
            _merge_counter(_dep_counter, dep_counter)
            chunks = retrieve_chunks(file_name)
            _chunk_counter = collections.Counter(chunks)
            _merge_counter(_chunk_counter, chunk_counter)

    n_words = sum(word_counter.values())
    n_vocab = len(word_counter)
    n_netags = sum(netag_counter.values())
    n_netag_vocab = len(netag_counter)
    n_deps = sum(dep_counter.values())
    n_dep_vocab = len(dep_counter)
    n_chunks = sum(chunk_counter.values())
    n_chunk_vocab = len(chunk_counter)

    print("# word")
    print(n_words, n_vocab)
    print("---\n")

    print("# netag")
    for key, value in sorted(netag_counter.items()):
        print(f"{key}\t{value:,}")
    print(f"n_netags\t{n_netags:,}")
    print(f"n_netag_vocab\t{n_netag_vocab:,}")
    print("---\n")

    print("# dependency")
    for key, value in sorted(dep_counter.items()):
        print(f"{key}\t{value:,}")
    print(f"n_deps\t{n_deps:,}")
    print(f"n_dep_vocab,{n_dep_vocab:,}")
    print(f"n_chunks\t{n_chunks:,}")
    print("---\n")
    print("# chunk")
    for key, value in sorted(chunk_counter.items()):
        print(f"{key}\t{value:,}")
    print(f"n_chunk_vocab,{n_chunk_vocab:,}")


if __name__ == "__main__":
    main()
