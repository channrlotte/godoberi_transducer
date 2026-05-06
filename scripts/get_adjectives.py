import csv
from pathlib import Path

stressed = {'á': 'а', 'é': 'е', 'ó': 'о', 'ý': 'у',
            'а́': 'а', 'е́': 'е', 'и́': 'и', 'о́': 'о', 'у́': 'у', 'э́': 'э', 'ю́': 'ю', 'я́': 'я',
            'ā́': 'а̄', 'ḗ': 'е̄', 'ṓ': 'о̄', 'ȳ́': 'ӯ',
            'а̄́': 'а̄', 'е̄́': 'е̄', 'ӣ́': 'ӣ', 'о̄́': 'о̄', 'ȳ́': 'ȳ', 'э̄́': 'э̄', 'ю̄́': 'ю̄', 'я̄́': 'я̄'}
long = {'ā': 'а̄', 'ē': 'е̄', 'ō': 'о̄', 'ȳ': 'ӯ'}

m = set()
f = set()
n = set()
hpl = set()
npl = set()
common = set()
obl_m = set()
obl_f = set()
obl_n = set()
obl_hpl = set()
obl_npl = set()
obl_common_c = set()
obl_common_v = set()
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


def get_class(description: str):
    if description[:5] == 'I, II':
        return None
    if description[:3] == 'III':
        return 3
    if description[:2] == 'II':
        return 2
    if description[0] == 'I':
        return 1
    return None


def add_base(lemma: str, stem: str, ma: int=0, fe: int=0, ne: int=0, hupl: int=0, nhupl: int=0, obl: int=0):
    if ma:
        m.add(f'{lemma}<ADJ>><m>:{stem + '>в'}')
    if fe:
        f.add(f'{lemma}<ADJ>><f>:{stem + '>й'}')
    if ne:
        n.add(f'{lemma}<ADJ>><n>:{stem + '>б'}')
    if hupl:
        hpl.add(f'{lemma}<ADJ>><h><pl>:{stem + '>б'}')
    if nhupl:
        npl.add(f'{lemma}<ADJ>><n><pl>:{stem + '>р'}')
    if obl:
        if any(stem.endswith(v) for v in ('е', 'и', 'а', 'о', 'у', 'а̄', 'е̄', 'ӣ', 'о̄', 'ӯ', 'э̄', 'ю̄', 'аᵸ', 'еᵸ', 'иᵸ', 'оᵸ', 'уᵸ', 'эᵸ', 'юᵸ')):
            obl_common_v.add(f'{lemma}<ADJ>:{stem}')
        else:
            obl_common_c.add(f'{lemma}<ADJ>:{stem}')


with (open('godoberi.csv', 'rt', encoding='utf-8') as file):
    for line in csv.reader(file):
        if line[11] != 'adj' or ('(зиб.)' in line[6]):
            continue

        word = correct(line[4])
        morphology = correct(line[9])
        translation = line[21]

        c = get_class(line[6])
        if c == 2:
            if word.startswith('й/'):
                lemma = word.replace('/', '')
                f.add(f'<f>>{lemma}<ADJ>:{word.replace('/', '>')}')
                hpl.add(f'<h><pl>>{lemma}<ADJ>:{word.replace('й/', 'б>')}')
                obl_f.add(f'<f>>{lemma}<ADJ>:{word.replace('/', '>')}')
                obl_hpl.add(f'<h><pl>>{lemma}<ADJ>:{word.replace('й/', 'б>')}')
            else:
                lemma = word.replace('/', '')
                stem = word.replace('/й', '')
                add_base(lemma, stem, fe=1, hupl=1)
                obl_f.add(f'{lemma}<ADJ>:{stem}')
                obl_hpl.add(f'{lemma}<ADJ>:{stem}')
            translations.append(f'{lemma}<ADJ>:{translation}<ADJ>')

        elif morphology.startswith('(-й II, '):
            lemma = word.replace('/', '')
            stem = word.replace('/в', '')
            add_base(lemma, stem, ma=1, fe=1)
            if morphology.endswith('-б//-л мн. I)'):
                hpl.add(f'{lemma}<ADJ>><h><pl>:{stem + '>б'}')
                hpl.add(f'{lemma}<ADJ>><h><pl>:{stem + '>л'}')
            elif morphology.endswith('-л мн. I)'):
                hpl.add(f'{lemma}<ADJ>><h><pl>:{stem + '>л'}')
            else:
                hpl.add(f'{lemma}<ADJ>><h><pl>:{stem + '>б'}')
            obl_m.add(f'{lemma}<ADJ>:{stem}')
            obl_f.add(f'{lemma}<ADJ>:{stem}')
            obl_hpl.add(f'{lemma}<ADJ>:{stem}')
            translations.append(f'{lemma}<ADJ>:{translation}<ADJ>')

        elif morphology in ('(и мн. I, -р//-л мн. II)', '(и мн. I, -л мн. II)'):
            lemma = word.replace('/б', 'в')
            stem = word.replace('/б', '')
            add_base(lemma, stem, ma=1, fe=1, ne=1, hupl=1, obl=1)
            npl.add(f'{lemma}<ADJ>><n><pl>:{stem + '>л'}')
            if morphology.endswith('-р//-л мн. II)'):
                npl.add(f'{lemma}<ADJ>><n><pl>:{stem + '>р'}')
            translations.append(f'{lemma}<ADJ>:{translation}<ADJ>')

        elif morphology.startswith('(-б//-л мн. I'):
            lemma = word.replace('/б', 'в')
            stem =  word.replace('/б', '')
            add_base(lemma, stem, ma=1, fe=1, ne=1, hupl=1, obl=1)
            if morphology.endswith('-р//-л мн. II)'):
                npl.add(f'{lemma}<ADJ>><n><pl>:{stem + '>р'}')
                npl.add(f'{lemma}<ADJ>><n><pl>:{stem + '>л'}')
            elif morphology.endswith('-л мн. II)'):
                npl.add(f'{lemma}<ADJ>><n><pl>:{stem + '>л'}')
            else:
                npl.add(f'{lemma}<ADJ>><n><pl>:{stem + '>р'}')
            translations.append(f'{lemma}<ADJ>:{translation}<ADJ>')

        elif morphology.startswith('(-л мн. I'):
            lemma = word.replace('/б', 'в')
            stem = word.replace('/б', '')
            add_base(lemma, stem, ma=1, fe=1, ne=1, obl=1)
            hpl.add(f'{lemma}<ADJ>><h><pl>:{stem + '>л'}')
            if morphology.endswith(', II)'):
                npl.add(f'{lemma}<ADJ>><n><pl>:{stem + '>л'}')
            else:
                npl.add(f'{lemma}<ADJ>><n><pl>:{stem + '>р'}')
            translations.append(f'{lemma}<ADJ>:{translation}<ADJ>')

        elif word.count('/') > 1:
            exceptions.append((word, morphology, translation))

        elif morphology == '':
            if ' ' in word:
                exceptions.append((word, morphology, translation))
                continue

            if word.startswith('б/'):
                lemma = word.replace('б/', 'в')
                m.add(f'<m>>{lemma}<ADJ>:{word.replace('б/', 'в>')}')
                f.add(f'<f>>{lemma}<ADJ>:{word.replace('б/', 'й>')}')
                n.add(f'<n>>{lemma}<ADJ>:{word.replace('/', '>')}')
                hpl.add(f'<h><pl>>{lemma}<ADJ>:{word.replace('/', '>')}')
                npl.add(f'<n><pl>>{lemma}<ADJ>:{word.replace('б/', 'р>')}')
                if not word.endswith('ссу'):
                    if word.endswith('н') or word.endswith('н'):
                        obl_m.add(f'<m>>{lemma}<ADJ>:{word.replace('б/', 'в>')}а')
                        obl_f.add(f'<f>>{lemma}<ADJ>:{word.replace('б/', 'й>')}а')
                        obl_n.add(f'<n>>{lemma}<ADJ>:{word.replace('/', '>')}а')
                        obl_hpl.add(f'<h><pl>>{lemma}<ADJ>:{word.replace('/', '>')}а')
                        obl_npl.add(f'<n><pl>>{lemma}<ADJ>:{word.replace('б/', 'р>')}а')
                    else:
                        obl_m.add(f'<m>>{lemma}<ADJ>:{word.replace('б/', 'в>')}')
                        obl_f.add(f'<f>>{lemma}<ADJ>:{word.replace('б/', 'й>')}')
                        obl_n.add(f'<n>>{lemma}<ADJ>:{word.replace('/', '>')}')
                        obl_hpl.add(f'<h><pl>>{lemma}<ADJ>:{word.replace('/', '>')}')
                        obl_npl.add(f'<n><pl>>{lemma}<ADJ>:{word.replace('б/', 'р>')}')

            elif word.endswith('/б'):
                lemma = word.replace('/б', 'в')
                stem = word.replace('/б', '')
                add_base(lemma, stem, ma=1, fe=1, ne=1, hupl=1, nhupl=1, obl=1)

            else:
                lemma = word
                common.add(f'{lemma}<ADJ>:{lemma}')
                if not word.endswith('ссу'):
                    add_base(lemma, lemma, obl=1)

            translations.append(f'{lemma}<ADJ>:{translation}<ADJ>')

        elif morphology.startswith('(и мн. I, '):
            morph = morphology.split()

            if '-' in word or len(morph) < 8:
                exceptions.append((word, morphology, translation))
                continue

            b = word.replace('/', '')
            lemma = morph[3]
            if not b.startswith('б'):
                m.add(f'{lemma}<ADJ><m>:{lemma}')
                f.add(f'{lemma}<ADJ><f>:{morph[5]}')
                n.add(f'{lemma}<ADJ><n>:{b}')
                hpl.add(f'{lemma}<ADJ><h><pl>:{b}')
                npl.add(f'{lemma}<ADJ><n><mpl>:{morph[7]}')
                if not word.endswith('ссу'):
                    obl_m.add(f'{lemma}<ADJ><m>:{lemma}')
                    obl_f.add(f'{lemma}<ADJ><f>:{morph[5]}')
                    obl_n.add(f'{lemma}<ADJ><n>:{b}')
                    obl_hpl.add(f'{lemma}<ADJ><h><pl>:{b}')
                    obl_npl.add(f'{lemma}<ADJ><n><mpl>:{morph[7]}')
            elif b.endswith('аб'):
                def insert_border(s):
                    return s[:2] + '>' + s[2:-1] + '>' + s[-1]

                m.add(f'<m>>{lemma}<ADJ>><m>:{insert_border(lemma)}')
                f.add(f'<f>>{lemma}<ADJ>><f>:{insert_border(morph[5])}')
                n.add(f'<n>>{lemma}<ADJ>><n>:{insert_border(b)}')
                hpl.add(f'<h><pl>>{lemma}<ADJ>><h><pl>:{insert_border(b)}')
                npl.add(f'<n><pl>>{lemma}<ADJ>><n><mpl>:{insert_border(morph[7])}')
                obl_m.add(f'<m>>{lemma}<ADJ>:{insert_border(lemma)[:-2]}')
                obl_f.add(f'<f>>{lemma}<ADJ>:{insert_border(morph[5])[:-2]}')
                obl_n.add(f'<n>>{lemma}<ADJ>:{insert_border(b)[:-2]}')
                obl_hpl.add(f'<h><pl>>{lemma}<ADJ>:{insert_border(b)[:-2]}')
                obl_npl.add(f'<n><pl>>{lemma}<ADJ>:{insert_border(morph[7])[:-2]}')

            else:
                def insert_border(s):
                    return s[:2] + '>' + s[2:]

                m.add(f'<m>>{lemma}<ADJ>:{insert_border(lemma)}')
                f.add(f'<f>>{lemma}<ADJ>:{insert_border(morph[5])}')
                n.add(f'<n>>{lemma}<ADJ>:{insert_border(b)}')
                hpl.add(f'<h><pl>>{lemma}<ADJ>:{insert_border(b)}')
                npl.add(f'<n><pl>>{lemma}<ADJ>:{insert_border(morph[7])}')
                if not word.endswith('ссу'):
                    obl_m.add(f'<m>>{lemma}<ADJ>:{insert_border(lemma)}')
                    obl_f.add(f'<f>>{lemma}<ADJ>:{insert_border(morph[5])}')
                    obl_n.add(f'<n>>{lemma}<ADJ>:{insert_border(b)}')
                    obl_hpl.add(f'<h><pl>>{lemma}<ADJ>:{insert_border(b)}')
                    obl_npl.add(f'<n><pl>>{lemma}<ADJ>:{insert_border(morph[7])}')

            translations.append(f'{lemma}<ADJ>:{translation}<ADJ>')

        else:
            exceptions.append((word, morphology, translation))

items = {
    'm': (m, 'AdjectiveM'),
    'f': (f, 'AdjectiveF'),
    'n': (n, 'AdjectiveN'),
    'hpl': (hpl, 'AdjectiveHPL'),
    'npl': (npl, 'AdjectiveNPL'),
    'common': (common, 'Adjective'),
    'obl_m': (obl_m, 'AdjectiveOblM'),
    'obl_f': (obl_f, 'AdjectiveOblF'),
    'obl_n': (obl_n, 'AdjectiveOblN'),
    'obl_hpl': (obl_hpl, 'AdjectiveOblHPL'),
    'obl_npl': (obl_npl, 'AdjectiveOblNPL'),
    'obl_common_c': (obl_common_c, 'AdjectiveOblC'),
    'obl_common_v': (obl_common_v, 'AdjectiveOblV'),
    'translations': (translations, 'Translations')
}

for name, data in items.items():
    with open(Path('../adjectives/regular') / f'{name}.txt', 'wt', encoding='utf-8') as f:
        f.write('\n')
        f.write(f'LEXICON {data[1]}\n')
        for s in data[0]:
            f.write(str(s) + '\n')

with open (Path('../adjectives/exceptions') / 'exceptions.csv', 'wt', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(exceptions)
