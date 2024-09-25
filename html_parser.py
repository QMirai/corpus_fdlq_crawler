from bs4 import BeautifulSoup
import pandas as pd


def parser():
    with open('Chercher dans le Fonds _ Fonds de données linguistiques du Québec.html', 'r', encoding='utf-8') as f:
        page = f.read()

    soup = BeautifulSoup(page, 'lxml')

    # Find the table
    table = soup.find('table')

    if table is None:
        return "Error: Could not find the table on the page"

    # Extract data from each row
    data = []
    for row in table.find('tbody').find_all('tr'):
        cells = row.find_all('td')
        if len(cells) >= 5:
            document = cells[1].text.strip()
            contexte_avant = cells[2].text.strip()
            pivot = cells[3].text.strip()
            contexte_apres = cells[4].text.strip()

            data.append({
                'document': document,
                'contexte_avant': contexte_avant,
                'pivot': pivot,
                'contexte_apres': contexte_apres
            })
    return data


def make_excel(dicts):
    doc = [d['document'] for d in dicts]
    cv = [d['contexte_avant'] for d in dicts]
    pv = [d['pivot'] for d in dicts]
    cp = [d['contexte_apres'] for d in dicts]

    data = {"Document": doc,
            "contexte_avant": cv,
            "pivot": pv,
            "contexte_apres": cp}

    tb = pd.DataFrame.from_dict(data)
    tb.to_excel('5.xlsx', index=False)


dicts = parser()
make_excel(dicts)