import glob
import logging
import os
from typing import List

import click


def read_corpus(annotated_file: str) -> List[List[str]]:
    sentences: List[List[str]] = []
    words: List[str] = []

    with open(annotated_file) as fp:
        for line in fp:
            line = line.rstrip("\n")

            if line == "EOS":
                if words:
                    words.append("EOS")
                    sentences.append(words)
                    words = []
                continue

            if line.startswith("# Title"):
                continue

            if line.startswith("# Sentence"):
                continue

            if line.startswith("# Step"):
                continue

            if not line.startswith("* "):
                line = "\t".join(line.split("\t")[:-1])

            else:
                line = line.replace("-2", "-1")
                line = " ".join(line.split(" ")[:4])

            words.append(line)

        if words:
            sentences.append(words)
    return sentences


def write(dataset, output_dir, target):
    sentences = []
    for document in dataset:
        for words in document:
            sentences.append("\n".join(words))

    with open(os.path.join(output_dir, f"cabocha.{target}"), "w") as fp:
        print("\n".join(sentences), file=fp)


@click.command()
@click.option("--data-dir")
@click.option("--output-dir")
def main(data_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    logging.info("Created a directory %s", output_dir)

    dataset = []
    for globed in glob.glob(os.path.join(data_dir, "*")):
        if not os.path.isdir(globed):
            continue

        parsed_recipe = read_corpus(os.path.join(globed, "title.txt"))
        parsed_recipe += read_corpus(os.path.join(globed, "step.txt"))
        dataset.append(parsed_recipe)

    data_for = os.path.basename(data_dir)
    if data_for == "valid":
        data_for = "testa"
    if data_for == "test":
        data_for = "testb"

    write(dataset, output_dir, data_for)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
