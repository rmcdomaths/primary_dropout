import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from pathlib import Path

year = str(2000)

states = pd.read_csv(Path().cwd() / 'states.csv', delimiter=',')
states_key = dict(zip(states.State, states.Abbreviation))

URL = 'https://www.thegreenpapers.com/PCC/'
ext = 'html'
response = requests.get(URL, params={})
response_text = response.text
soup = BeautifulSoup(response_text, 'html.parser')
all_url = [URL + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

for p, party in zip(['R', 'D'], ['Republican', 'Democrat']):
    infos = []
    for state in states_key.keys():
        s = states_key[state]
        url = URL + s + '-' + p + '.html'
        if url in all_url:
            candidates = []

            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")

            table = soup.find('table')
            rows = table.find_all('tr')

            # Extract data from each row and store it in a list of dictionaries
            data = []
            for row in rows:
                cells = row.find_all(['th', 'td'])
                row_data = [cell.get_text(strip=True) for cell in cells]
                data.append(row_data)
            date = data[0][1][data[0][1].index(':') + 2:data[0][1].index(year) + 4]
            if '-' in date:
                date = date[date.index('-') + 2:]
            info = {'state': s,
                    'date': datetime.strptime(date, '%A, %B %d, %Y'),
                    'type': data[0][1].split(party, 1)[1][0]}
            infos.append(info)
            cands = []
            for d in data[3:]:
                if d[0] != 'Total':
                    cand = {'name': d[0][:d[0].find(',')] if d[0].find(',') != -1 else d[0],
                            'other_name': d[0][d[0].find(',') + 2:] if d[0].find(',') != -1 else '',
                            'votes': int(d[1].split('\xa0\xa0', 1)[0].replace(',', ''))
                            if len(d[1]) > 0 and d[1].find('\xa0\xa0') > -1
                            else int(d[1].split('\xa0', 1)[0].replace(',', '')) if len(d[1]) > 0
                            else '',
                            'percentage': int(d[1].split('\xa0\xa0', 1)[1].replace('%', ''))
                            if len(d[1]) > 0 and d[1].find('\xa0\xa0') > -1
                            else int(d[1].split('\xa0', 1)[1].replace('%', '')) if len(d[1]) > 0
                            else '',
                            'delegates': 0 if len(d[3]) == 0 else int(d[3].split('.', 1)[0])}
                    cands.append(cand)
                else:
                    info['total_votes'] = int(d[1].split('\xa0', 1)[0].replace(',', '')) if len(d[1]) > 0 else ''
                    info['total_delegates'] = int(d[2].split('.\xa0', 1)[0])
                    break


            pd.DataFrame(cands).to_csv('./2000/' + p + '_' + s + '.csv', index=False)
    pd.DataFrame(infos).to_csv('./2000/' + p + '_info.csv', index=False)

breakpoint()