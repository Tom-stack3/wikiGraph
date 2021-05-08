# Written by Tommy Zaft

from bs4 import BeautifulSoup
import re
import wikipedia
import requests


class WikiPage:
    base_wiki_url = "https://en.wikipedia.org/"

    def __init__(self, page_url, debug=False):
        self.url = None
        self.set_url(page_url)
        self.name = WikiPage.__url_to_name(page_url)
        # the name shown on the graph.
        # we replace the ':' with a '˸' because a colon is used as a separator in Graphviz.
        self.name_to_show = self.name.replace(":\t", ": ").replace(":", "˸")
        self.html = None
        self.next_url = None
        self.debug = debug

    def get_first_link(self):
        self.html = self.get_page_html()
        # print(html)
        soup = BeautifulSoup(self.html, "html.parser")

        first_link = None

        for link in soup.find_all('a', href=True):
            if self.is_href_valid(link):
                if first_link is None:
                    first_link = link['href']
                    break
        if self.debug:
            print("chose:", WikiPage.__url_to_full_url(first_link))
        return first_link

    @staticmethod
    def get_random_page(debug=False):
        """
        Get a random wikipedia page.

        :param debug: True - if you want to debug or get information about the program while it's running.
                False - default
        :type debug: bool
        :return: a random (WikiPage) wikipedia page.
        """
        url = requests.get("https://en.wikipedia.org/wiki/Special:Random")
        random_page_url = WikiPage.__full_url_to_url(url.url)
        return WikiPage(random_page_url, debug)

    @staticmethod
    def is_substring_enclosed_in_brackets(sub, string):
        """
        to check if substring is enclosed in brackets.

        :param sub: the substring
        :param string: the string
        :return: True - if substring is enclosed in brackets.
        False - otherwise.
        """
        # to get (...)
        pattern = re.compile("\([^\)]*\)")
        # to get:  (...(...)...)
        pattern2 = re.compile("\([^\)]*\([^\)]*\)[^\)]*\)")
        # to get:  (...(...(...)...)...)
        pattern3 = re.compile("\([^\)]*\([^\)]*\([^\)]*\)[^\)]*\)[^\)]*\)")

        string = str(string)
        search = re.findall(pattern, string)
        search2 = re.findall(pattern2, string)
        search3 = re.findall(pattern3, string)

        search3 = set(search + search2 + search3)
        if any(str(sub) in s for s in search3):  # or any(str(sub) in s for s in search2):
            return True
        return False

    def is_href_valid(self, link):
        """
        Checks if the href is a valid Wikipedia link to click on as the first link in an article.

        :param link: the BeautifulSoup link.
        :type link bs4.element.Tag
        :return:  True - if the link is ok to click on as a first link in an article
        False - not a valid link to click on.
        """
        url = str(link['href'])
        # if it doesn't lead to a wiki page
        if not url.startswith("/wiki/"):
            return False

        wikipedia_classes = ["external_text", "mw-disambig", "infobox-data"]
        # if the href has a class
        if link.get("class") is not None:
            link_class = "_".join(link.get("class"))
            # if the class is an external text class, or a disambiguation link
            if any(wiki_class in link_class for wiki_class in wikipedia_classes):
                return False

        if 'wikimedia' in url or 'wiktionary' in url:
            return False
        wikipedia_keywords = ["Help", "Category", "Wikipedia", "Template", "File", "Talk", "Special", "Portal"]
        if any(keyword + ':' in url for keyword in wikipedia_keywords):
            return False
        if '#' in url:
            return False
        # if the page is a file
        if re.search("\.[a-zA-Z][a-zA-Z][a-zA-Z]$", url) or re.search("\.[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]$", url):
            return False

        # if the href is enclosed in brackets
        if WikiPage.is_substring_enclosed_in_brackets(link, link.parent.parent):
            return False

        wikipedia_not_needed_tags = ['small', 'sup', 'i']
        if link.parent.name in wikipedia_not_needed_tags:
            return False

        # if the href shows two different spellings. like in: https://en.wikipedia.org/wiki/Carbon_fibers
        # Carbon fibers ~or~ carbon fibres - here or is the href.

        if link.contents == ["or"]:
            return False

        parents_classes = [p.get("class") for p in link.parents if p.get("class") is not None]
        parents_classes = [str("_".join(p)) for p in parents_classes]
        parents_ids = [p.get("id") for p in link.parents if p.get("id") is not None]

        # 'toc' - the Contents menu class
        # 'mw-editsection' - the Edit section
        # 'thumbcaption' - a Photo Caption
        # 'hlist' - a list like in: https://en.wikipedia.org/wiki/January
        wikipedia_classes_to_ignore = ["thumbcaption", "infobox", "navigation-not-searchable", "sidebar", "box-text",
                                       "toc", "mw-editsection", "thumb", "hlist"]

        for p_class in parents_classes:

            if any(class_to_ignore in p_class for class_to_ignore in wikipedia_classes_to_ignore):
                return False

        # if it is a coordinates href
        if "coordinates" in parents_ids:
            return False

        '''
        Update 13.04.2021:
        ------------------
        Someone edited the "Epistemology" page. and changed the first link <a>branches<a/>.
        Instead of pointing to the page "Branches of science", it was changed to point to "Outline of philosophy".
        Which creates a loop. I chose to ignore it manually, and instead click on the next link.
        ( which happens to be Philosophy :) )
        This changed also caused some of the "paths" in the PDF files,
        generated before that date to be slightly outdated. But the concept stays the same :)
        
        Update 08.05.2021:
        ------------------
        they fixed it since :)
        "Epistemology" -> branches of philosophy : "https://en.wikipedia.org/wiki/Outline_of_philosophy" ->
        -> Philosophy.
        
        #if "Outline_of_philosophy" in url:
        #   return False
        '''

        return True

    # if we want to init a first page in the chain
    @staticmethod
    def choose_first_page_manually(debug=False):
        name = input("Please enter wiki page name: ")
        search = wikipedia.search(name)

        while True:
            if not search:
                print("no such page found :(\nenter a valid wiki page name")
            elif len(search) > 1:
                print("Please choose one from the following list,")
                print("Enter the index of the page wanted (0 - for first page):\n")
                print(search, "\n")
                num_chosen = int(input("choice:"))
                if num_chosen >= len(search) or num_chosen < 0:
                    print("out of the boundary..")
                else:
                    page = WikiPage.first_page_init(search[num_chosen], debug)
                    if page is None:
                        print("the page is not valid, please choose another one.")
                    else:
                        print('Chose "' + page.url + '"')
                        return page
            else:
                page = WikiPage.first_page_init(search[0], debug)
                if page is None:
                    print("the page is not valid, please choose another one.")
                else:
                    print('Chose "' + page.url + '"')
                    return page

            # if we got here, we need to search again
            name = input("\nPlease enter wiki page name: ")
            search = wikipedia.search(name)

    @staticmethod
    def first_page_init(name, debug=False):
        page_url = WikiPage.__name_to_url(name)
        # if the page is not a valid wiki page (can be a disambiguation page for example)
        if not WikiPage.__is_page_ok(name):
            return None
        else:
            return WikiPage(page_url, debug)

    @staticmethod
    def __name_to_url(name):
        return "/wiki/" + name.replace(' ', '_')

    @staticmethod
    def __url_to_name(url):
        url = WikiPage.__full_url_to_url(url)
        name = url.replace("/wiki/", '').replace('_', ' ')
        from urllib.parse import unquote
        name = unquote(name)
        return name

    @staticmethod
    def __full_url_to_url(url):
        url = url.replace(WikiPage.base_wiki_url[:-1], '')
        return url

    @staticmethod
    def __url_to_full_url(url):
        url = WikiPage.base_wiki_url[:-1] + url
        return url

    # checks if the page is not a valid wiki page:
    # - if it's not a disambiguation page, or it doesn't exist
    @staticmethod
    def __is_page_ok(name):
        url = WikiPage.base_wiki_url + "w/api.php?action=parse&page=TITLE_HERE&prop=text&format=json"
        GET_request = requests.get(url.replace("TITLE_HERE", name))
        bad_messages_to_see = ["The page you specified doesn't exist", "Disambiguation page", " may refer to:"]
        if any(bad_msg in GET_request.text for bad_msg in bad_messages_to_see):
            return False
        return True

    def fix_redirect(self, GET_request):
        html = GET_request.json()["parse"]["text"]["*"]
        soup = BeautifulSoup(html, "html.parser")
        div = soup.find('div', attrs={"class": "redirectMsg"})
        ul_with_url = None
        for p_element in div.find_all('p'):
            if p_element.text == "Redirect to:":
                ul_with_url = p_element.next_sibling
        li = ul_with_url.contents[0]
        url = WikiPage.clean_url(li.contents[0]["href"])

        self.name = WikiPage.__url_to_name(url)
        self.set_url(url)
        return self.get_page_html()

    def set_url(self, url_without_base):
        self.url = WikiPage.base_wiki_url[:-1] + WikiPage.clean_url(url_without_base)

    @staticmethod
    def clean_url(url):
        return re.sub(r'#.*', '', url)

    def get_page_html(self):
        url = WikiPage.base_wiki_url + "w/api.php?action=parse&page=TITLE_HERE&prop=text&format=json"
        url = url.replace("TITLE_HERE", self.name)
        if self.debug:
            print(url)
        GET_request = requests.get(url)
        # if the page is a redirect page
        if "Redirect to:" in GET_request.text:
            return self.fix_redirect(GET_request)

        if "missingtitle" in GET_request.text:
            print("didn't find", self.name)
            return None

        return GET_request.json()["parse"]["text"]["*"]
