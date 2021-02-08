FROM  ubuntu:18.04
LABEL maintainer himkt@cookpad.com

ENV LANG="ja_JP.UTF-8"
ENV LC_ALL="ja_JP.UTF-8"
ENV LC_CTYPE="ja_JP.UTF-8"
ENV LD_LIBRARY_PATH=/usr/local/lib

ENV MECAB_IPADIC "0B4y35FiV1wh7MWVlSDBCSXZMTXM"
ENV MECAB_IPADIC_MODEL "0B4y35FiV1wh7bnc5aFZSTE9qNnM"
ENV CRFPP "0B4y35FiV1wh7QVR6VXJ5dWExSTQ"
ENV CABOCHA "0B4y35FiV1wh7SDd1Q1dUQkZQaUU"

RUN apt update -y && \
      apt install -y --no-install-recommends \
      autoconf curl wget make \
      automake libtool git g++ \
      module-init-tools \
      python3-dev python3-setuptools python3-pip \
      language-pack-ja locales \
      patch && \
      rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

RUN locale-gen ja_JP.UTF-8

# Environment
WORKDIR /work
COPY ./pyproject.toml ./pyproject.toml
COPY ./poetry.lock    ./poetry.lock

# Python
RUN pip3 install -U pip
RUN pip3 install poetry
RUN poetry install

# MeCab
RUN apt update -y && \
      apt install -y --no-install-recommends \
      mecab mecab-ipadic-utf8 libmecab-dev && \
      rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

# MeCab-IPADic
WORKDIR /tmp
RUN wget "https://drive.google.com/uc?export=download&id=${MECAB_IPADIC}" -O mecab-ipadic-2.7.0-20070801.tar.gz && \
      tar xvf mecab-ipadic-2.7.0-20070801.tar.gz

WORKDIR /tmp/mecab-ipadic-2.7.0-20070801
RUN `mecab-config --libexecdir`/mecab-dict-index

# MeCab pretrained model
WORKDIR /tmp
RUN wget "https://drive.google.com/uc?export=download&id=${MECAB_IPADIC_MODEL}" -O mecab-ipadic-2.7.0-20070801.model.bz2 && \
	bunzip2 mecab-ipadic-2.7.0-20070801.model.bz2

# CRF++
WORKDIR /tmp
RUN wget "https://drive.google.com/uc?export=download&id=${CRFPP}" -O CRF++-0.58.tar.gz \
      && tar zxf CRF++-0.58.tar.gz \
      && cd CRF++-0.58 \
      && ./configure \
      && make \
      && make install

# CaboCha
RUN wget --save-cookies=/tmp/cookie "https://drive.google.com/uc?export=download&id=${CABOCHA}" > /dev/null \
      && wget --load-cookies=/tmp/cookie "https://drive.google.com/uc?export=download&confirm=$(awk '/_warning_/ {print $NF}' /tmp/cookie)&id=${CABOCHA}" -O cabocha-0.69.tar.bz2 \
      && tar jxf cabocha-0.69.tar.bz2 && cd cabocha-0.69 \
      && ./configure --with-mecab-config=`which mecab-config` --with-charset=utf8 \
      && make \
      && make install

# Kytea
RUN git clone https://github.com/neubig/kytea.git && \
      cd kytea && git checkout 73a94c4a3045087a7e90f27700f3b870a72625e7 && autoreconf -i && \
      ./configure && make -j4 && make install

# PWNER
RUN wget http://www.lsta.media.kyoto-u.ac.jp/resource/tool/PWNER/data/PWNER.tar.gz && \
      tar zxvf PWNER.tar.gz

# Experiments
WORKDIR /work
COPY ./cpc1.0   ./cpc1.0
COPY ./Makefile ./Makefile
COPY ./bin      ./bin
COPY ./static   ./static

RUN patch /tmp/PWNER/bin/NESearch.pl ./static/patch
