import pycurl
from io import BytesIO
from bs4 import BeautifulSoup


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

    def __init__(self, title, tags=[]):
        self.title = title
        self.tags = tags

    def __str__(self):
        return self.title


class Speiseplan(object):

    PROVIDER_URL = 'https://www.maxmanager.de/daten-extern/os-neu/html/inc/ajax-php_konnektor.inc.php'

    def __init__(self):
        c = pycurl.Curl()
        buffer = BytesIO()

        c.setopt(c.URL, Speiseplan.PROVIDER_URL)
        c.setopt(c.POSTFIELDS, 'func=make_spl&locId=7&lang=de&date=2016-01-29')
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()

        body = buffer.getvalue()
        self.soup = BeautifulSoup(body.decode('utf-8'), 'html.parser')
        self.meals = []

        for cell in self.soup.find_all(class_='cell2'):
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

            self.meals.append(parts)


#### tests #####
if __name__ == "__main__":
    s = Speiseplan()
    for m in s.meals:
        print('m')
        for p in m:
            print(p.title, p.tags, p.additives)
