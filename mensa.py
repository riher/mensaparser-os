import pycurl
from io import BytesIO
from bs4 import BeautifulSoup
import datetime


def translate_pictogram(string):
    tag_dict = {
        'icons/40.png': 'Geflügel',
        'icons/21.png': 'vegan',
        'icons/20.png': 'vegetarisch',
        'icons/19.gif': 'bio',
        'icons/17.gif': 'Knoblauch',
        'icons/15.gif': 'Alkohol',
        'icons/14.gif': 'Rindfleisch',
        'icons/13.gif': 'Schweinefleisch',
        'icons/12.gif': 'Mensa Vital',
    }
    try:
        return tag_dict[string]
    except KeyError:
        return string


class TeilMahlzeit(object):

    def __init__(self, title, tags=[], additives=[]):
        self.title = title
        self.tags = tags
        self.additives = additives

    def __str__(self):
        return self.title


class Mahlzeit(object):

    def __init__(self, parts=[]):
        self.parts = parts

    def __str__(self):
        return self.title

    @property
    def title(self):
        title_parts = []
        for p in self.parts:
            title_parts.append(p.title)
        return ' + '.join(title_parts)

    @property
    def tag_set(self):
        tags = set()
        for p in self.parts:
            tags.update(p.tags)
        return tags

    @property
    def additive_set(self):
        additives = set()
        for p in self.parts:
            additives.update(p.additives)
        return additives


class Speiseplan(object):

    URL = 'https://www.maxmanager.de/daten-extern/os-neu/html/inc/ajax-php_konnektor.inc.php'

    def __init__(self, date=datetime.date.today()):
        c = pycurl.Curl()
        buffer = BytesIO()

        c.setopt(c.URL, Speiseplan.URL)
        c.setopt(c.POSTFIELDS, 'func=make_spl&locId=7&lang=de&date='+str(date))
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        soup = BeautifulSoup(body.decode('utf-8'), 'html.parser')
        self.meals = []

        for cell in soup.find_all(class_='cell2'):
            divs = cell.find_all('div')
            parts = []
            contents = []

            # each div stands for a distinct part of a meal
            for div in divs:
                tags = []
                additives = []
                contents = div.contents
                title = div.contents[0].strip()

                # loop through unspecified children of the div tag
                for thing in contents:
                    # is it a tag?
                    try:
                        imgsrc = thing['src']
                    except:
                        pass
                    else:
                        tags.append(translate_pictogram(imgsrc))
                        continue

                    # is it additive list?
                    if thing.name == 'sup':
                        additives = list(thing.string.strip().split(','))

                parts.append(TeilMahlzeit(title=title, tags=tags, additives=additives))

            self.meals.append(Mahlzeit(parts))


#### tests #####
if __name__ == "__main__":
    s = Speiseplan()
    for m in s.meals:
        if not 'vegan' in m.tag_set:
            continue
        print('m')
        print(m.title, m.tag_set, m.additive_set)
        # for p in m.parts:
            # print(p.title, p.tag_set, p.additive_set)
