
all: prepare train eval

prepare: split mecab conll2003 pwner cabocha test-gen
test-gen: mecab-test-gen pwner-test-gen cabocha-test-gen
train: mecab-learn pwner-learn cabocha-learn
eval: mecab-eval pwner-eval cabocha-eval

.PHONY: prepare train eval mecab-learn pwner-learn cabocha-learn mecab-eval pwner-eval cabocha-eval

split:
	poetry run python bin/split_dataset.py --corpus-dir cpc1.0 --output-dir outputs --proportion 8:1:1

mecab:
	poetry run python bin/build_mecab.py --data-dir outputs/train --output-dir outputs/mecab
	poetry run python bin/build_mecab.py --data-dir outputs/valid --output-dir outputs/mecab
	poetry run python bin/build_mecab.py --data-dir outputs/test  --output-dir outputs/mecab
	# charset encoding conversion
	cat outputs/mecab/mecab.train| iconv -f UTF-8 -t EUC-JP//TRANSLIT > outputs/mecab/mecab.eucjp.train

conll2003:
	poetry run python bin/build_conll2003.py --data-dir outputs/train --output-dir outputs/conll2003
	poetry run python bin/build_conll2003.py --data-dir outputs/valid --output-dir outputs/conll2003
	poetry run python bin/build_conll2003.py --data-dir outputs/test  --output-dir outputs/conll2003

pwner:
	poetry run python bin/build_pwner.py --data-dir outputs/train --output-dir outputs/pwner
	poetry run python bin/build_pwner.py --data-dir outputs/valid --output-dir outputs/pwner
	poetry run python bin/build_pwner.py --data-dir outputs/test  --output-dir outputs/pwner

cabocha:
	poetry run python bin/build_cabocha.py --data-dir outputs/train --output-dir outputs/cabocha
	poetry run python bin/build_cabocha.py --data-dir outputs/valid --output-dir outputs/cabocha
	poetry run python bin/build_cabocha.py --data-dir outputs/test  --output-dir outputs/cabocha

mecab-test-gen:
	`mecab-config --libexecdir`/mecab-test-gen < outputs/mecab/mecab.testb > outputs/mecab/test.sent

pwner-test-gen:
	poetry run python bin/pwner-test-gen.py < outputs/pwner/eng.iob.testb > outputs/pwner/testb.sent

cabocha-test-gen:
	poetry run python bin/cabocha-test-gen.py -O2 < outputs/cabocha/cabocha.testb > outputs/cabocha/testb.sent

mecab-learn:
	mkdir -p outputs/mecab/mecab.dict.new
	# retrain
	`mecab-config --libexecdir`/mecab-cost-train \
		-M /tmp/mecab-ipadic-2.7.0-20070801.model \
		-d /tmp/mecab-ipadic-2.7.0-20070801 \
		outputs/mecab/mecab.eucjp.train outputs/mecab/mecab.model
	# dict-gen
	`mecab-config --libexecdir`/mecab-dict-gen \
		-d /tmp/mecab-ipadic-2.7.0-20070801 \
		-o outputs/mecab/mecab.dict.new \
		-m outputs/mecab/mecab.model
	# index gen
	`mecab-config --libexecdir`/mecab-dict-index \
		-d outputs/mecab/mecab.dict.new \
		-o outputs/mecab/mecab.dict.new \
		-m outputs/mecab/mecab.model \
		-f euc-jp \
		-t utf-8  # use "-t utf-8" because retraining a model can only run for EUC-JP texts
	# infer
	mecab < outputs/mecab/test.sent > outputs/mecab/mecab.testb.pretrain
	mecab -d outputs/mecab/mecab.dict.new < outputs/mecab/test.sent > outputs/mecab/mecab.testb.transfer

pwner-learn:
	# train
	train-kytea \
		-nows \
		-full outputs/pwner/eng.iob.train \
		-global 1 \
		-solver 6 \
		-model outputs/pwner/model.knm
	# LR+DP: LR
	kytea \
		-model outputs/pwner/model.knm \
		-nows \
		-tagmax 0 \
		-out conf \
		< outputs/pwner/testb.sent \
		> outputs/pwner/_pwner.testb.conf
	# LR+DP: DP
	perl /tmp/PWNER/bin/NESearch.pl \
		static/IREX \
		outputs/pwner/_pwner.testb.conf \
		outputs/pwner/_pwner.testb
	# convert prediction into CoNLL format for eval
	poetry run python bin/pwner-to-conll2003.py \
		--gold-file outputs/pwner/eng.iob.testb \
		--pred-file outputs/pwner/_pwner.testb \
		> outputs/pwner/pwner.testb

cabocha-learn:
	# train
	`cabocha-config --libexecdir`/cabocha-learn outputs/cabocha/cabocha.train outputs/cabocha/cookpad.cabocha
	# infer
	cabocha -I2 -f1 \
		< outputs/cabocha/testb.sent \
		> outputs/cabocha/cabocha.testb.pretrain
	cabocha -I2 -f1 \
		-m outputs/cabocha/cookpad.cabocha \
		< outputs/cabocha/testb.sent \
		> outputs/cabocha/cabocha.testb.transfer

mecab-eval:
	-`mecab-config --libexecdir`/mecab-system-eval \
		outputs/mecab/mecab.testb.pretrain \
		outputs/mecab/mecab.testb
	-`mecab-config --libexecdir`/mecab-system-eval \
		outputs/mecab/mecab.testb.transfer \
		outputs/mecab/mecab.testb

pwner-eval:
	curl https://www.clips.uantwerpen.be/conll2000/chunking/conlleval.txt > conlleval.pl
	perl ./conlleval.pl < outputs/pwner/pwner.testb

cabocha-eval:
	-`cabocha-config --libexecdir`/cabocha-system-eval \
		-e dep \
		outputs/cabocha/cabocha.testb.pretrain \
		outputs/cabocha/cabocha.testb
	-`cabocha-config --libexecdir`/cabocha-system-eval \
		-e dep \
		outputs/cabocha/cabocha.testb.transfer \
		outputs/cabocha/cabocha.testb
