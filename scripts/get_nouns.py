import csv
from pathlib import Path

stressed = {'á': 'а', 'é': 'е', 'ó': 'о', 'ý': 'у',
            'а́': 'а', 'е́': 'е', 'и́': 'и', 'о́': 'о', 'у́': 'у', 'э́': 'э', 'ю́': 'ю', 'я́': 'я',
            'ā́': 'а̄', 'ḗ': 'е̄', 'ṓ': 'о̄', 'ȳ́': 'ӯ',
            'а̄́': 'а̄', 'е̄́': 'е̄', 'ӣ́': 'ӣ', 'о̄́': 'о̄', 'ȳ́': 'ȳ', 'э̄́': 'э̄', 'ю̄́': 'ю̄', 'я̄́': 'я̄'}
long = {'ā': 'а̄', 'ē': 'е̄', 'ō': 'о̄', 'ȳ': 'ӯ'}

common = set()
obl_common = set()
obl_m = set()
obl_f = set()
obl_hpl = set()
translations = []
exceptions = []


def correct(s: str):
    s = s.lower()
    s = s.replace('ᴴ', 'ᵸ')
    s = s.replace('i', 'I')
    for old, new in stressed.items():
        s = s.replace(old, new)
    for old, new in long.items():
        s = s.replace(old, new)
    s = s.replace('я', '\'а')
    return s


def get_variants(s: str):
    i = s.find('(')
    j = s.find('//')
    if i != -1:
        return [s[:i].strip(), s.replace('(', '').replace(')', '').strip()]
    elif j != -1:
        return list(map(str.strip, s.split('//')))
    else:
        return [s.strip()]


def get_class(description: str):
    if description[:2] in ('1 ', '2 ', '3 ', '4 '):
        description = description[2:]
    if description[:5] == 'I, II':
        return 4
    if description[:3] == 'III':
        return 3
    if description[:2] == 'II':
        return 2
    if description[0] == 'I':
        return 1
    return None


def get_stem(word: str):
    i = word.find('/')
    if i == -1:
        return word
    return word[:i]


def add_sg(c, lemma: str, stem: str, morphology: str):
    if lemma.endswith('в') and c == 1:
        common.add(f'{lemma}<NOUN>><m>:{lemma[:-1]}>в')
    elif lemma.endswith('й') and c == 2:
        common.add(f'{lemma}<NOUN>><f>:{lemma[:-1]}>й')
    elif lemma.endswith('л') and morphology == '-рдуб':
        common.add(f'{lemma}<NOUN>><h><pl>:{lemma[:-1]}>л')
    else:
        common.add(f'{lemma}<NOUN>:{lemma}')

    if not morphology.startswith('-'):
        stem = morphology[:-3]
        if stem.endswith('алълъи'):
            obl_f.add(f'{lemma}<NOUN>><obl>:{stem[:-6]}>а')
        else:
            obl_common.add(f'{lemma}<NOUN><obl>:{stem}')

    else:
        if morphology.endswith('щуб'):
            obl = morphology[1:-3]
            to = obl_m
        elif morphology.endswith('лълъилIи'):
            obl = morphology[1:-8]
            to = obl_f
        else:
            obl = morphology[1:-3]
            to = obl_common

        if obl and stem + obl != lemma:
            to.add(f'{lemma}<NOUN>><obl>:{stem}>{obl}')
        elif obl:
            to.add(f'{lemma}<NOUN>:{lemma}')
        else:
            to.add(f'{lemma}<NOUN>:{stem}')


def add_pl(lemma: str, stem: str, morphology: str):
    if not morphology.startswith('-'):
        if morphology[-4:] in ('алди'):
            common.add(f'{lemma}<NOUN>><pl>:{morphology[:-4]}>алди')
            obl_common.add(f'{lemma}<NOUN>><pl>><obl>:{morphology[:-4]}>алд>а')
        elif morphology[-4:] in ('агIи', 'забе'):
            common.add(f'{lemma}<NOUN>><pl>:{morphology[:-4]}>{morphology[-4:]}')
            obl_common.add(f'{lemma}<NOUN>><pl>:{morphology[:-4]}>{morphology[-4:]}')
        elif morphology.endswith('ал'):
            common.add(f'{lemma}<NOUN>><pl>:{morphology[:-1]}>л')
            obl_hpl.add(f'{lemma}<NOUN>><pl>><obl><h><pl>:{morphology[:-1]}>рду')
        elif morphology.endswith('ди'):
            common.add(f'{lemma}<NOUN>><pl>:{morphology[:-2]}>ди')
            obl_common.add(f'{lemma}<NOUN>><pl>><obl>:{morphology[:-2]}>д>а')
        elif morphology[-2:] in ('бе', 'ме'):
            common.add(f'{lemma}<NOUN>><pl>:{morphology[:-2]}>{morphology[-2:]}')
            obl_common.add(f'{lemma}<NOUN>><pl>:{morphology[:-2]}>{morphology[-2:]}')
        elif morphology.endswith('е'):
            common.add(f'{lemma}<NOUN>><pl>:{morphology[:-1]}>е')
            obl_common.add(f'{lemma}<NOUN>><pl>:{morphology[:-1]}>ē')
        else:
            common.add(f'{lemma}<NOUN><pl>:{morphology}')
            obl_common.add(f'{lemma}<NOUN><pl>:{morphology}')

    elif morphology[-4:] in ('алди', 'беди'):
        obl = morphology[1:-4]
        if obl == "'":
            common.add(f"{lemma}<NOUN>><pl>:{stem}'>{morphology[-4:]}")
            obl_common.add(f"{lemma}<NOUN>><pl>><obl>:{stem}'>{morphology[-4:-1]}>а")
        elif obl:
            common.add(f'{lemma}<NOUN>><obl>><pl>:{stem}>{obl}>{morphology[-4:]}')
            obl_common.add(f'{lemma}<NOUN>><obl>><pl>><obl>:{stem}>{obl}>{morphology[-4:-1]}>а')
        else:
            common.add(f'{lemma}<NOUN>><pl>:{stem}>{morphology[-4:]}')
            obl_common.add(f'{lemma}<NOUN>><pl>><obl>:{stem}>{morphology[-4:-1]}>а')

    elif morphology[-4:] in ('агIи', 'забе'):
        common.add(f'{lemma}<NOUN>><pl>:{stem}>{morphology[1:]}')
        obl_common.add(f'{lemma}<NOUN>><pl>:{stem}>{morphology[1:]}')

    elif morphology.endswith('ал'):
        common.add(f'{lemma}<NOUN>><obl>><pl>:{stem}>а>л')
        obl_hpl.add(f'{lemma}<NOUN>><obl>><obl><h><pl>:{stem}>а>рду')

    elif morphology.endswith('ди'):
        obl = morphology[1:-2]
        if obl and stem + obl != lemma:
            common.add(f'{lemma}<NOUN>><obl>><pl>:{stem}>{obl}>ди')
            obl_common.add(f'{lemma}<NOUN>><obl>><pl>><obl>:{stem}>{obl}>д>а')
        elif obl:
            common.add(f'{lemma}<NOUN>><pl>:{lemma}>ди')
            obl_common.add(f'{lemma}<NOUN>><pl>><obl>:{lemma}>д>а')
        else:
            common.add(f'{lemma}<NOUN>><pl>:{stem}>ди')
            obl_common.add(f'{lemma}<NOUN>><pl>><obl>:{stem}>д>а')

    elif morphology.endswith('бе') or morphology.endswith('ме'):
        obl = morphology[1:-2]
        if obl and stem + obl != lemma:
            common.add(f'{lemma}<NOUN>><obl>><pl>:{stem}>{obl}>{morphology[-2:]}')
            obl_common.add(f'{lemma}<NOUN>><obl>><pl>:{stem}>{obl}>{morphology[-2:]}')
        elif obl:
            common.add(f'{lemma}<NOUN>><pl>:{lemma}>{morphology[-2:]}')
            obl_common.add(f'{lemma}<NOUN>><pl>:{lemma}>{morphology[-2:]}')
        else:
            common.add(f'{lemma}<NOUN>><pl>:{stem}>{morphology[-2:]}')
            obl_common.add(f'{lemma}<NOUN>><pl>:{stem}>{morphology[-2:]}')

    elif morphology.endswith('е'):
        common.add(f'{lemma}<NOUN>><pl>:{stem}>{morphology[1:]}')
        obl_common.add(f'{lemma}<NOUN>><pl>:{stem}>{morphology[1:-1]}ē')

    else:
        common.add(f'{lemma}<NOUN>><obl>><pl>:{stem}>л')
        obl_hpl.add(f'{lemma}<NOUN>><obl><h><pl>:{stem}>рду')


with open('godoberi.csv', 'rt', encoding='utf-8') as f:
    for line in csv.reader(f):
        if line[11] != 'noun' or ('зиб.' in line[6]) or ' ' in line[4]:
            continue

        word = correct(line[4])
        c = get_class(line[6])
        morphology = correct(line[9])[1:-1].split(', ')
        translation = line[21].replace(' ', '_')

        if '/' in word[:2] or 'II' in line[9]:
            exceptions.append((word, morphology, translation))
            continue

        for w in get_variants(word):
            lemma = w.replace('/', '')
            stem = get_stem(w)

            if 'собир.' in morphology or 'тк. ед.' in morphology:
                add_sg(c, lemma, stem, morphology[0])

            elif 'тк. мн.' in morphology:
                if morphology[0] != '-лIи':
                    obl = morphology[0][1:-3]
                    if lemma.endswith('ди'):
                        common.add(f'{lemma}<NOUN>><pl>:{lemma[:-2]}>ди')
                        obl_common.add(f'{lemma}<NOUN>><pl>><obl>:{lemma[:-2]}>д>{obl}')
                    else:
                        common.add(f'{lemma}<NOUN><pl>:{lemma}')
                        obl_common.add(f'{lemma}<NOUN><pl>><obl>:{stem}>{obl}')
                elif lemma[-4:] in ('алди', 'забе'):
                    common.add(f'{lemma}<NOUN>><pl>:{lemma[:-4]}>{lemma[-4:]}')
                    obl_common.add(f'{lemma}<NOUN>><pl>:{lemma[:-4]}>{lemma[-4:]}')
                elif lemma[-2:] in ('ал', 'бе', 'ме', 'ди'):
                    common.add(f'{lemma}<NOUN>><pl>:{lemma[:-2]}>{lemma[-2:]}')
                    obl_common.add(f'{lemma}<NOUN>><pl>:{lemma[:-2]}>{lemma[-2:]}')
                else:
                    common.add(f'{lemma}<NOUN><pl>:{lemma}')
                    obl_common.add(f'{lemma}<NOUN><pl>:{lemma}')

            elif len(morphology) == 3:
                add_sg(c, lemma, stem, morphology[0])
                add_sg(c, lemma, stem, morphology[1])
                add_pl(lemma, stem, morphology[2])

            elif len(morphology) == 2:
                if c == 4:
                    add_sg(c, lemma, stem, morphology[0])
                    add_sg(c, lemma, stem, morphology[1])
                else:
                    for m in get_variants(morphology[0]):
                        add_sg(c, lemma, stem, m)
                    for m in get_variants(morphology[1]):
                        if m.endswith('огр. мн. ч.'):
                            add_pl(lemma, stem, m[:-12])
                        else:
                            add_pl(lemma, stem, m)

            elif not morphology[0].endswith('рдуб'):
                for m in get_variants(morphology[0]):
                    m = m if m else '-лIи'
                    add_sg(c, lemma, stem, m)

            elif lemma.endswith('ал'):
                add_pl(lemma, stem, lemma)

            elif lemma[-2:] in ('бе', 'ди'):
                common.add(f'{lemma}<NOUN>><pl>:{lemma[:-2]}>{lemma[-2:]}')
                obl_hpl.add(f'{lemma}<NOUN>><pl>:{stem}>{morphology[0][1:-1]}')

            else:
                common.add(f'{lemma}<NOUN><pl>:{lemma}')
                obl_hpl.add(f'{lemma}<NOUN><pl>><obl>:{stem}>{morphology[0][1:-1]}')

            translations.append(f'{lemma}<NOUN>:{translation}<NOUN>')

items = {
    'common': (common, 'Noun'),
    'obl_common': (obl_common, 'NounObl'),
    'obl_m': (obl_m, 'NounOblM'),
    'obl_f': (obl_f, 'NounOblF'),
    'obl_hpl': (obl_hpl, 'NounOblHPl'),
    'translations': (translations, 'Translations')
}

for name, data in items.items():
    with open(Path('../nouns/regular') / f'{name}.txt', 'wt', encoding='utf-8') as f:
        f.write('\n')
        f.write(f'LEXICON {data[1]}\n')
        for s in data[0]:
            f.write(str(s) + '\n')

with open (Path('../nouns/exceptions') / 'exceptions.csv', 'wt', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(exceptions)
