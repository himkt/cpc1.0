# Cookpad Parsed Corpus v1.0

Cookpad Parsed Corpus (CPC) is a dataset of linguistically annotated recipes written in Japanese.
We annotated titles and cooking steps of recipes with morphemes, named entities, and dependency relations.
Each recipe in CPC was randomly extracted from [Cookpad Recipe Dataset](https://www.aclweb.org/anthology/L16-1389/).

This repository consists of a set of scripts that were used in the following paper:

- Harashima and Hiramatsu, [Cookpad Parsed Corpus: Linguistic Annotations of Japanese Recipes](https://www.aclweb.org/anthology/2020.law-1.8/), LAW, 2020.


# 1. Download dataset

First of all, you have to download cpc1.0.
Please contact to jun-harashima@cookpad.com and himkt@cookpad.com for requesting the dataset.
We will send you a URL to download `cpc1.0.zip`.

After downloading and extracting the zip file, place it at the root of this repository.


# 2. Quick start

Using Docker, you can replicate our experiments simply by:

```
# Please make sure that `cpc1.0` exists at the root of the repository.
# The output of `ls` should be:
#
#  > ls
#  Dockerfile     Makefile       README.md      cpc1.0         poetry.lock    pyproject.toml
#

docker build -t cookpad/cpc1.0 .
docker run --rm -t cookpad/cpc1.0 poetry run python bin/summary.py  # show basic staticstics of CPC.
docker run --rm -t cookpad/cpc1.0 make
```

Note that the results of the commands could be slightly different from those reported in the paper.


# 3. Setup manually

If you want to run experiments on your local environment,
you have to install [MeCab](https://taku910.github.io/mecab/),
[CaboCha](https://taku910.github.io/cabocha/),
and [KyTea](http://www.phontron.com/kytea/index-ja.html).

After installing these softwares, next step is to setup Python environment.
We use `poetry` for dependency management.
You can install poetry and create Python environment by the following commands.

```
pip install poetry  # install poetry
poetry install  # install libraries
make  # run experiments
```

# 4. Usage of scripts

We recommend to launch bash on Docker by `docker run --rm cookpad/cpc1.0 -it bash` and run each command described below.

## 4.1 Corpus statistics

`poetry run python bin/summary.py`

## 4.2 Splitting dataset

`make split` divides our corpus into 400 recipes for a training set, 50 recipes for a validation set,
and 50 recipes for a test set.

## 4.3 Morphological analysis

```
make mecab  # for morphological analysis
make mecab-learn  # training a model
make macab-test-gen  # for evaluation
make mecab-eval  # for evaluation
```

## 4.4 Named entity recognition

```
make pwner
make pwner-learn
make pwner-test-gen
make pwner-eval
```

** Note **

Besides the PWNER, a named-entity recognizer based on [Lample+, 2016](https://www.aclweb.org/anthology/N16-1030/) was also evaluated in our experiments.
However, we do not contain any scripts for the recognizer in this repository
because we implemented it using [pyner](https://github.com/himkt/pyner), which depends on obsolete softwares.

## 4.5 Dependency parsing

```
make cabocha
make cabocha-learn
make cabocha-test-gen
make cabocha-eval
```


# 6. Citing CPC

If you use our dataset for your research, please cite the following paper:

```
@inproceedings{Harashima2020,
 author    = "Jun Harashima and Makoto Hiramatsu",
 title     = "{Cookpad Parsed Corpus: Linguistic Annotations of Japanese Recipes}",
 booktitle = "Proceedings of the 14th Linguistic Annotation Workshop (LAW 2020)",
 pages     = "87-92",
 year      = "2020",
}
```
