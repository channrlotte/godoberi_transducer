# Morphological transducer for Godoberi

## Background

The Godoberi language (ISO 639-3: GDO, Glottocode: ghod1238) belongs to the Andic group of the Avar-Andic-Tsezic branch of the Nakh-Daghestanian language family. According to the 2020–2021 Russian Census, it is spoken by approximately 3,000 people living in the Botlikhsky District of Dagestan.

## POS coverage of the morphological transducer

At the moment morphological transducer covers:

- Cardinal, collective, distributive, ordinal and multiplicative numerals
- Personal, reflexive, interrogative and demonstrative pronouns
- Adjectives
- Nouns

## Usage

The following commands will work on some versions of Linux and in Google Colab (just change the dollar sign with the exclamation mark).

In order to use the parser you need to install [`lexd`](https://github.com/apertium/lexd) and [`hfst`](https://github.com/hfst/hfst):

```
$ curl -sS https://apertium.projectjj.com/apt/install-nightly.sh | sudo bash
$ apt install lexd hfst
```

After you can clone the repository and compile it:

```
$ git clone git@github.com:channrlotte/godoberi_transducer.git
$ godoberi_transducer
$ make
```

If everything is fine, you can

- analyze some form
```
$ echo "илулIи" | hfst-lookup analyzer.hfstol

> илулIи	ила<NOUN>><obl>><gen>	0.000000
илулIи	ила<NOUN>><obl>><inter>	0.000000
```

- analyze some form and translate the stem into Russian
```
$ echo "ила<NOUN>><obl>><gen>" | hfst-lookup generator.hfstol

> ила<NOUN>><obl>><gen>	ил>у>лIи
```

- generate some form
```
$ echo "илулIи" | hfst-lookup analyzer_stem_translation.hfstol

> илулIи	мать<NOUN>><obl>><gen>	0.000000
илулIи	мать<NOUN>><obl>><inter>	0.000000
```

- generate the paradigm:
```
$ make substring_search REGEX="и л а %<NOUN%> ?*"
```

- generate the subparadigm:
```
$ make substring_search REGEX="и л а %<NOUN%> ?* %<gen%> ?*"
```

- calculate number of the distinct forms in the paradigm:
```
$ make substring_search REGEX="и л а %<NOUN%> ?*" | wc -l

hfst-compose-intersect: Warning: 
Found output symbols (e.g. "@_IDENTITY_SYMBOL_@") in transducer in
file <stdin> which will be filtered out because they are
not found on the input tapes of transducers in file
generator.hfst.
904
```

- analyze phrase
```
$ echo "илулIи ахIиди" | hfst-proc -x analyzer_stem_translation.hfstol

илулIи	мать<NOUN>><obl>><gen>
илулIи	мать<NOUN>><obl>><inter>

ахIиди	клич<NOUN>><erg>
ахIиди	тревога<NOUN>><erg>
```

As you see, there are some unusual for the most theoretical linguists hfst conventions:

- analysis by default returns lemma instead of a translation;
- lemma is followed by POS-tag in capitals;
- glosses are listed in angle brackets `<...>`;
- morpheme boundary is marked with the angle bracket `>`.

## References

- П. А. Саидова. Годоберинский язык: грамматический очерк, тексты, словарь. Махачкала: Дагестанский филиал АН СССР, 1973.
- П. А. Саидова. Годоберинско-русский словарь. Махачкала: Изд-во ДНЦ РАН, 2006.
- A. E. Kibrik (ed.), S. G. Tatevosov, A. Eulenberg (assistant eds.). Godoberi. Lincom Studies in Caucasian Linguistics. Vol. 2. München: Lincom Europa, 1996.
