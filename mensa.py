import pycurl
from io import BytesIO
from bs4 import BeautifulSoup
import datetime


def translate_pictogram(string):
    """Translates parsed icon names to verbose tag names."""
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
    """Meal part objects which make up a meal (Mahlzeit)

    These objects are strings with corresponding tags and additives.

    Keyword arguments:
    title -- a string describing the name of the meal part
    tags -- a list of tags describing the contents of the meal part
            (default: empty list)
    additives -- a list of additives in the meal part (default: empty list)
    """

    def __init__(self, title, tags=[], additives=[]):
        self.title = title
        self.tags = tags
        self.additives = additives

    def __str__(self):
        return self.title


class Mahlzeit(object):
    """Meal objects which make up a meal plan (Speiseplan)

    These objects are more or less a list of meal parts (TeilMahlzeit) and
    should contain at least one of them.

    Keyword arguments:
    parts -- takes a list of TeilMahlzeit objects (default: empty list)
    """

    def __init__(self, parts=[]):
        self.parts = parts

    def __str__(self):
        return self.title

    @property
    def title(self):
        """Complete name of the meal."""
        title_parts = []
        for p in self.parts:
            title_parts.append(p.title)
        return ' + '.join(title_parts)

    @property
    def tag_set(self):
        """List of all tags of the meal."""
        tags = set()
        for p in self.parts:
            tags.update(p.tags)
        return tags

    @property
    def additive_set(self):
        """List of all additives of the meal."""
        additives = set()
        for p in self.parts:
            additives.update(p.additives)
        return additives


class Speiseplan(object):
    """Meal plan object.

    This object is a list of meals (Mahlzeit) which gets created by parsing
    the official site of the Osnabrück Mensa.

    Keyword arguments:
    date -- a datetime.date object describing the date you want the meal plan
            for (default: current date)
    """

    def __init__(self, date=datetime.date.today()):
        """Gets the official meal plan site of Mensa Osnabrück and translates
        the html to python objects which can be handled more nicely.
        """

        c = pycurl.Curl()
        buffer = BytesIO()

        URL = 'https://www.maxmanager.de/daten-extern/os-neu/html/inc/ajax-php_konnektor.inc.php'
        c.setopt(c.URL, URL)
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
