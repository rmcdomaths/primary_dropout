import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from pathlib import Path
import numpy as np

year = str(2016)

states = pd.read_csv(Path().cwd() / 'states.csv', delimiter=',')
states_key = dict(zip(states.State, states.Abbreviation))

URL = 'https://www.thegreenpapers.com/P16/'


for p, party in zip(['R', 'D'], ['Republican', 'Democrat']):

    infos = []
    for state in states_key.keys():
        s = states_key[state]
        url = URL + s + '-' + p + '.html'

        # First get the info of each state: date, type
        if s not in ['MP']:
            candidates = []

            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            # Find date
            table = soup.find('thead')
            rows = table.find_all('tr')
            data = []
            for row in rows:
                cells = row.find_all(['th', 'td'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                data.append(row_data)

            alt_find = lambda st, sub: st.find(sub) if st.find(sub) != -1 else np.inf

            pi = alt_find(data[0][1], 'Primary:')
            ci = alt_find(data[0][1], 'Caucus:')
            cis = alt_find(data[0][1], 'Caucuses:')
            cvi = alt_find(data[0][1], 'Convention:')
            cvis = alt_find(data[0][1], 'Conventions:')

            find_date = min([pi, ci, cis, cvi, cvis])

            if pi < np.inf:
                date = data[0][1][pi + 9:]
                date = date[:date.index(year)]
                date = date.split('\xa0')
                date = ' '.join(date) + year
            elif ci == find_date:
                date = data[0][1][ci + 8:]
                date = date[:date.index(year)]
                date = date.split('\xa0')
                date = ' '.join(date) + year
            elif cis == find_date:
                date = data[0][1][cis + 10:]
                date = date[:date.index(year)]
                date = date.split('\xa0')
                date = ' '.join(date) + year
            elif cvis == find_date:
                date = data[0][1][cvis + 13:]
                date = date[:date.index(year)]
                date = date.split('\xa0')
                date = ' '.join(date) + year
            elif cvi == find_date:
                date = data[0][1][cvi + 12:]
                date = date[:date.index(year)]
                date = date.split('\xa0')
                date = ' '.join(date) + year
            else:
                breakpoint()
            if '-' in date:
                date = date[date.index('-') + 2:]

            info = {'state': s,
                    'date': datetime.strptime(date, '%A %d %B %Y'),
                    'type': 'P' if pi > -1 else 'C'}

            # Get candidate votes, percentages and delegates
            candidates = []
            table = soup.findAll('table')[5]
            rows = table.find_all('td')
            # Extract data from each row and store it in a list of dictionaries
            data = []
            row_data = [row.get_text(strip=True) for row in rows]
            read = False
            c = 0
            for d in row_data:
                if d == '%':
                    read = True
                    continue
                if read:
                    if c == 0:
                        cand = {}
                        # get cand name
                        full_name = d.split(' ')
                        if len(full_name) > 1 and full_name[-2][-1] == ',':
                            cand['name'] = full_name[-2][:-1]
                            cand['other_name'] = ' '.join(full_name[:-2]) + ', ' + full_name[-1]
                        else:
                            cand['name'] = full_name[-1]
                            cand['other_name'] = ' '.join(full_name[:-1])
                        c = c + 1
                        continue
                    if c == 1:
                        cand['votes'] = int(d.replace(',', '')) if len(d) > 0 and '.' not in d else 0
                        c = c + 1
                        continue
                    if c == 2:
                        cand['percentage'] = float(d.replace('%', '')) if len(d) > 0 else 0
                        cand['delegates'] = 0
                        candidates.append(cand)
                        cand = {}
                        c = 0
                        continue

            # Look at the main table and add in delegate numbers as necessary
            table = soup.find('tbody')
            rows = table.find_all('tr')

            # Extract data from each row and store it in a list of dictionaries
            data = []
            for row in rows:
                cells = row.find_all(['th', 'td'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                data.append(row_data)

            for d in data[3:]:
                name = d[0][:d[0].find(',')] if d[0].find(',') != -1 else d[0]
                delegates = int(d[1].split('\xa0\xa0', 1)[0]) \
                if d[1].find('\xa0\xa0') > -1 and name != 'Total' and len(d[1]) > 0 \
                else 0 if len(d[1]) <= 0 \
                    else int(d[1].split('\xa0', 1)[0])
                found = False
                for cand in candidates:
                    if cand['name'] == name:
                        cand['delegates'] = delegates
                        found = True
                if not found:
                    cand = {'name': name,
                            'delegates': delegates,
                            'votes': -99}
                candidates.append(cand)

            infos.append(info)

            pd.DataFrame(candidates).to_csv('./' + str(year) + '/' + p + '_' + s + '.csv', index=False)

    pd.DataFrame(infos).to_csv('./' + str(year) + '/' + p + '_info.csv', index=False)

breakpoint()