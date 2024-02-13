import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from pathlib import Path

year = str(2008)

states = pd.read_csv(Path().cwd() / 'states.csv', delimiter=',')
states_key = dict(zip(states.State, states.Abbreviation))

URL = 'https://www.thegreenpapers.com/P08/'


for p, party in zip(['R', 'D'], ['Republican', 'Democrat']):
    infos = []
    for state in states_key.keys():
        s = states_key[state]
        url = URL + s + '-' + p + '.html'

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
            date = ' '.join(data[0][1][data[0][1].index(':') + 2:data[0][1].index(year) + 4].split('\xa0'))
            if '-' in date:
                date = date[date.index('-') + 2:]

            info = {'state': s,
                    'date': datetime.strptime(date, '%A %d %B %Y'),
                    'type': data[0][1][data[0][1].index('\xa0') + 1: data[0][1].index('\xa0') + 2]}

            # Now find vote totals
            table = soup.find('tbody')
            rows = table.find_all('tr')

            # Extract data from each row and store it in a list of dictionaries
            data = []
            for row in rows:
                cells = row.find_all(['th', 'td'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                data.append(row_data)

            cands = []
            for d in data[3:]:
                if d[0] != 'Total':
                    cand = {'name': d[0][:d[0].find(',')] if d[0].find(',') != -1 else d[0],
                            'other_name': d[0][d[0].find(',') + 2:] if d[0].find(',') != -1 else '',
                            'votes': int(d[1].split('\xa0\xa0', 1)[0].replace(',', ''))
                            if len(d[1]) > 0 and d[1].find('\xa0\xa0') > -1
                            else int(d[1].split('\xa0', 1)[0].replace(',', '')) if len(d[1]) > 0
                            else '',
                            'percentage': float(d[1].split('\xa0\xa0', 1)[1].replace('%', ''))
                            if len(d[1]) > 0 and d[1].find('\xa0\xa0') > -1
                            else int(d[1].split('\xa0', 1)[1].replace('%', '')) if len(d[1]) > 0
                            else '',
                            'delegates': 0 if len(d[2]) == 0 else int(float(d[2].split('\xa0', 1)[0]))}
                    cands.append(cand)
                else:
                    info['total_votes'] = int(d[1].split('\xa0', 1)[0].replace(',', '')) if len(d[1]) > 0 else ''
                    info['total_delegates'] = int(float((d[2].split('\xa0', 1)[0])))
                    break

            infos.append(info)

            pd.DataFrame(cands).to_csv('./' + str(year) + '/' + p + '_' + s + '.csv', index=False)
    pd.DataFrame(infos).to_csv('./' + str(year) + '/' + p + '_info.csv', index=False)

breakpoint()