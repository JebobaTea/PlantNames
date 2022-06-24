from queue import Queue
from bs4 import BeautifulSoup
from os.path import exists
from Levenshtein import ratio
import os
import threading
import requests
import fuckit

fuckit(fuckit('COL'))
link = input('Link: ')

genera = []
with requests.Session() as session:
    page = requests.get(link, headers={'User-Agent': 'Beans'})
    soup = BeautifulSoup(page.text, 'html.parser')
    fam = soup.find('h1', {'class': 'c-summary__heading'})
    fam = fam.text.split(' ')
    fam = fam[0]
if exists('_save.txt'):
    with open('_save.txt') as f:
        genera = f.read().splitlines()
else:
    results = soup.find('ul', {'class': 'two-col'})
    children = results.findChildren('li', recursive=False)
    for child in children:
        children2 = child.find('a', href=True)
        if 'taxon' in str(children2['href']):
            genera.append('https://powo.science.kew.org' + str(children2['href']))

    with open('_save.txt', 'w+') as f:
        for l in genera:
            f.write(l + '\n')

spellings = []


def updateStatus():
    global spellings
    global genera
    os.system('clear')
    print('Genera remaining: ' + str(len(genera)))


q = Queue()


def getGenera(link):
    global spellings
    global genera
    KEW = []
    with requests.Session():
        page = requests.get(link, headers={'User-Agent': 'Beans'})
    soup = BeautifulSoup(page.text, 'html.parser')
    results = soup.findAll('ul', {'class': 'two-col'})
    genre = soup.find('h1', {'class': 'c-summary__heading'})
    if genre is None:
        return None
    genus = genre.text.split(' ')
    genus = genus[0]
    for result in results:
        children = result.findAll('a')
        for child in children:
            if str(genus) in child.text:
                n = child.text.split(' ')
                n = n[0] + ' ' + n[1]
                KEW.append(n)

    NGA = []
    searching = True
    i = 0
    form_data = {'u': 'USERNAME', 'p': 'PASSCODE'}
    with requests.Session() as session:
        session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'})
        session.get('https://garden.org/login.php')
        session.post('https://garden.org/i/ajax/users/login_check.php', form_data)
        session.get('https://garden.org/loggedin.php')
        while True:
            p = i * 20
            page = session.get('https://garden.org/plants/browse/plants/genus/' + str(genus) + '/?offset=' + str(p))
            soup = BeautifulSoup(page.text, 'html.parser')
            results = soup.find_all('td')
            if not results:
                searching = False
                break
            for result in results:
                children = result.findChildren('a', recursive=False)
                for child in children:
                    if child and child != '':
                        NGA.append(child.text)
            i += 1
    c = KEW[:]
    spl = []
    for pl in KEW:
        for plant in NGA:
            if pl.lower() in plant.lower():
                if pl in c:
                    c.remove(pl)
                    break
            elif 1 > ratio(pl, plant) > 0.9:
                spl.append([pl, plant])
    with requests.Session() as session:
        session.headers.update(
            {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0'})
        session.get('https://garden.org/login.php')
        session.post('https://garden.org/i/ajax/users/login_check.php', form_data)
        session.get('https://garden.org/loggedin.php')
        final = c[:]
        i = 0
        for t in c:
            i += 1
            updateStatus()
            dne = COL.search(t)
            if dne is False:
                if t in final:
                    final.remove(t)
                continue
            if dne[0]['usage']['status'] != 'accepted':
                if t in final:
                    final.remove(t)
                continue
            page = session.get('https://garden.org/plants/search/text/?q=' + t)
            if page.status_code != 200:
                print('Error scraping Garden.org')
            soup = BeautifulSoup(page.text, 'html.parser')
            if 'No plants were found for your search.' not in page.text:
                if t in final:
                    final.remove(t)
                continue
            syn = COL.getSynonyms(t)
            with fuckit:
                if "No synonym" not in syn[0]:
                    for synonym in syn:
                        page = session.get('https://garden.org/plants/search/text/?q=' + str(synonym))
                        soup = BeautifulSoup(page.text, 'html.parser')
                        results = soup.find_all('td')
                        if len(results) > 0:
                            if t in final:
                                final.remove(t)
                            continue
    if final:
        spl1 = []
        spl2 = []
        for s in spl:
            if s[0] in final:
                spl1.append(s[0])
                spl2.append(s[1])
        with open('Sorted/' + fam + '.txt', 'a') as f:
            for plant in final:
                try:
                    if plant not in spl1:
                        f.write(plant + '\n')
                    else:
                        f.write('W ' + plant + ' = ' + spl2[spl1.index(plant)] + '?\n')
                except:
                    f.write(plant + '\n')
    genera.remove(link)
    if len(genera) > 0:
        with open('_save.txt', 'w+') as f:
            for l in genera:
                f.write(l + '\n')
    else:
        os.remove('_save.txt')


for l in genera:
    q.put(l)


def worker():
    while True:
        item = q.get()
        getGenera(item)
        q.task_done()


for i in range(5):
    t = threading.Thread(target=worker)
    t.daemon = True
    t.start()

q.join()
