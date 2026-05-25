.PHONY: all

all: analyzer.hfstol generator.hfstol

substring_search: generator.hfst
	@echo "$(REGEX)" | hfst-regexp2fst | hfst-compose-intersect generator.hfst | hfst-fst2strings

%.hfstol: %.hfst
	hfst-fst2fst -O $< -o $@

analyzer.hfst: generator.hfst remove_hyphen.hfst
	hfst-compose-intersect $^ | hfst-invert -o $@

remove_hyphen.hfst: remove_hyphen.twol
	hfst-twolc -q $< -o $@

generator.hfst: numerals.hfst pronouns.hfst adjectives.hfst nouns.hfst
	hfst-union numerals.hfst pronouns.hfst | hfst-union adjectives.hfst | hfst-union nouns.hfst -o $@

%.hfst: %.lexd
	lexd $< | hfst-txt2fst -o $@

%.lexd: %_formation.lexd %_lexicon.lexd
	cat $^ > $@

adjectives_lexicon.lexd: adjectives/regular/m.txt adjectives/exceptions/m.txt \
						 adjectives/regular/f.txt adjectives/exceptions/f.txt \
						 adjectives/regular/n.txt adjectives/exceptions/n.txt \
						 adjectives/regular/hpl.txt adjectives/exceptions/hpl.txt \
						 adjectives/regular/npl.txt adjectives/exceptions/npl.txt \
						 adjectives/regular/common.txt \
						 adjectives/regular/obl_m.txt adjectives/exceptions/obl_m.txt \
						 adjectives/regular/obl_f.txt adjectives/exceptions/obl_f.txt \
						 adjectives/regular/obl_n.txt adjectives/exceptions/obl_n.txt \
						 adjectives/regular/obl_hpl.txt adjectives/exceptions/obl_hpl.txt \
						 adjectives/regular/obl_npl.txt adjectives/exceptions/obl_npl.txt \
						 adjectives/regular/obl_common_c.txt adjectives/regular/obl_common_v.txt
	cat $+ > $@

nouns_lexicon.lexd: nouns/regular/common.txt nouns/exceptions/common.txt \
					nouns/regular/obl_common.txt nouns/exceptions/obl_common.txt \
					nouns/regular/obl_m.txt nouns/exceptions/obl_m.txt \
					nouns/regular/obl_f.txt nouns/exceptions/obl_f.txt \
					nouns/regular/obl_hpl.txt
	cat $+ > $@
