import glob
import os.path
import random
import shutil

import click
import numpy.random
from sklearn import model_selection

random.seed(0)
numpy.random.seed(0)


@click.command()
@click.option("--corpus-dir", type=str, default="./cpc1.0")
@click.option("--output-dir", type=str, default="./outputs")
@click.option("--proportion", type=str, default="8:1:1")
def main(corpus_dir: str, output_dir: str, proportion: str):
    os.makedirs(output_dir, exist_ok=True)

    recipe_ids = []
    for glob_item in glob.glob(os.path.join(corpus_dir, "*")):
        if not os.path.isdir(glob_item):
            continue
        recipe_ids.append(glob_item)

    train, valid, test = map(lambda x: int(x) / 10, proportion.split(":"))
    assert train + valid + test == 1.0
    train_valid_recipe_ids, test_recipe_ids = model_selection.train_test_split(recipe_ids, test_size=test)
    train_recipe_ids, valid_recipe_ids = model_selection.train_test_split(
        train_valid_recipe_ids, test_size=valid / (train + valid)
    )

    n_train_recipes, n_valid_recipes, n_test_recipes = (
        len(train_recipe_ids),
        len(valid_recipe_ids),
        len(test_recipe_ids),
    )

    print(f"Total: {len(recipe_ids)} recipes found")
    print(f"Proportion: {proportion}")
    print(f"{n_train_recipes}, {n_valid_recipes}, {n_test_recipes}")

    def create_dataset(recipe_ids, target) -> None:
        target_dir = os.path.join(output_dir, target)
        os.makedirs(target_dir, exist_ok=True)

        for from_path in recipe_ids:
            dest_path = os.path.join(target_dir, os.path.basename(from_path))
            shutil.copytree(from_path, dest_path)
        print(f"Processed: {target}")

    create_dataset(train_recipe_ids, "train")
    create_dataset(valid_recipe_ids, "valid")
    create_dataset(test_recipe_ids, "test")


if __name__ == "__main__":
    main()
