# Written by Tommy Zaft

from WikiPage import WikiPage
import wikipedia
# to draw the graph
from graphviz import Digraph
# for saving the file the right way
import os
import shutil

import time

# for the output label
from datetime import datetime

# for getting random words
from random_word import RandomWords

# separator for printing
SEP = "---------------------------"

# we color the first pages a bit differently from the other pages.
# Nodes Color documentation: https://graphviz.org/doc/info/colors.html
FIRST_PAGES_COLOR = "lightskyblue1"
REGULAR_PAGES_COLOR = "lightskyblue"

# True - if you want to debug or get information about the program while it's running.
DEBUG = False


def autocomplete_search(name_searched):
    """
    Autocompletes a search to a Wikipedia page name using the wikipedia library.

    e.g:
    'lebron' -> 'LeBron James',
    'ferari' -> 'Ferrari'

    :param name_searched: the name searched
    :return: the autocompletion
    """
    search_results = wikipedia.search(name_searched)
    if len(search_results) < 1:
        return None
    return search_results[0]


def init_first_page_automatically(name_searched, debug=False):
    """
    inits and returns a WikiPage first page using the autocomplete_search() and WikiPage.
    :param name_searched: the name searched

    :param debug: True - if you want to debug or get information about the program while it's running.
                False - default
    :type debug: bool
    :return: return a WikiPage page
    """
    name = autocomplete_search(name_searched)
    page = None
    if name is not None:
        page = WikiPage.first_page_init(name, debug)
    return page


def draw_page_path(page, u, pages_drawn, debug=False):
    """
    draws the path of the WikiPage page until reaching "Philosophy" or a loop onto the graph.

    :param page: the WikiPage page to draw path of.
    :type page: WikiPage page
    :param u: the graph to draw on.
    :type u: Digraph
    :param pages_drawn: the list of the pages drawn so far in the graph.
    :param debug: True - if you want to debug or get information about the program while it's running.
                False - default
    :type debug: bool
    :return: returns the 'road' of the page got by clicking the first link in each page. The 'road' is a list containing
     all the pages names drawn.
    """
    road_of_page = [page.name]
    count_pages = 0
    # we add the first page node
    u.node(page.name_to_show, URL=page.url, color=FIRST_PAGES_COLOR)
    while page.name != "Philosophy":
        next_url = page.get_first_link()
        # if we got to the limit, reached a dead end or have duplicates in our road.
        if next_url is None or count_pages > 100 or len(road_of_page) != len(set(road_of_page)):
            break
        else:
            next_page = WikiPage(next_url, debug)
            road_of_page.append(next_page.name)
            u.edge(page.name_to_show, next_page.name_to_show)

            count_pages += 1
            if page.name in pages_drawn:
                if debug:
                    print("already drawn", page.name)
                break

            # we add the next page node
            u.node(next_page.name_to_show, URL=next_page.url)

            page = next_page
    pages_drawn += road_of_page
    return road_of_page


def create_corresponding_copy(const_filename, first_pages, file_format):
    """
    copies the output file generated to the /output folder and and gives it a corresponding name.
    writes the number of first pages drawn in the beginning and three of them in the name.

    e.g:
    "15 Academy Award for Best Live Action Short Film+Kiddo+There are known knowns+Tim Buckley.svg"

    :param const_filename: the file name to copy
    :param first_pages: the list of the first pages drawn
    :param file_format: the file format of the output.
        e.g:
        "svg" or "pdf"
    :return: None
    """
    new_file_name = str(len(first_pages)) + " " + "+".join(first_pages[:3]) + "." + file_format

    # get the current working dir
    src_dir = os.getcwd()

    if not os.path.exists("output"):
        os.mkdir('output')
    dst_file = os.path.join(src_dir, "output", new_file_name)
    src_file = os.path.join(src_dir, const_filename + "." + file_format)
    # copy the file to destination dir
    shutil.copy(src_file, dst_file)


def draw_list_of_pages(pages, u, debug=False):
    """
    Draws a list of pages onto the graph.
    for each page we draw its path using draw_page_path().
    The function also prints it's progress in percentage.
    It prints when finished going over 25%,50%,75% and 100% of the page names.

    :param pages: the of the pages to draw.
    :type pages: WikiPage page
    :param u: the graph to draw on.
    :type u: Digraph
    :param debug: True - if you want to debug or get information about the program while it's running.
                False - default
    :type debug: bool
    :return: the list of the first pages drawn (the names of the first pages) and the total number of pages drawn.
    """
    pages_drawn = []
    first_pages_drawn = []

    percentage_to_alert = [25, 50, 75, 100]
    indexes_to_alert_on = [int(len(pages) * (p / 100)) - 1 for p in percentage_to_alert]
    index_in_names = 0

    for page in pages:
        print("Working on", page.name, "...")
        draw_page_path(page, u, pages_drawn, debug)
        first_pages_drawn.append(page.name)

        if index_in_names in indexes_to_alert_on:
            i = indexes_to_alert_on.index(index_in_names)
            print(SEP)
            print("Finished going thorough", str(percentage_to_alert[i]) + "%")
            print(SEP)

        index_in_names += 1

    return first_pages_drawn, len(pages_drawn)


def draw_list_of_page_names(names, u, debug=False):
    """
    Draws a list of page names onto the graph.
    for each page name  we generate a WikiPage using init_first_page_automatically().
    then we call draw_list_of_pages() to draw the pages.

    :param names: the names of the pages to draw.
    :param u: the graph to draw on.
    :type u: Digraph
    :param debug: True - if you want to debug or get information about the program while it's running.
                False - default
    :type debug: bool
    :return: the list of the first pages drawn (the names of the first pages) and the total number of pages drawn.
    """
    not_found_names = []

    pages_to_draw = []

    for name in names:
        first_page = init_first_page_automatically(name, debug)
        if first_page is None:
            print("Didn't find", name)
            not_found_names.append(name)
        else:
            pages_to_draw.append(first_page)

    return draw_list_of_pages(pages_to_draw, u, debug)


def create_label_for_output_file(first_pages_drawn, time_in_minutes, total_num_drawn):
    """
    creates a label for a graph drawn, for example:
            Graph generated on 08/05/2021 13:15:56. Checked 40 pages.
    :param first_pages_drawn: the list of the first pages drawn
    :param time_in_minutes: time took to run in minutes
    :param total_num_drawn: the total number of pages drawn
    :return: the label generated for the graph.
    """
    now = datetime.now()
    # \l is for new line
    label = "\lGraph generated on " + now.strftime("%d/%m/%Y %H:%M:%S") + ".\lChecked " + str(
        len(first_pages_drawn)) + " pages. Time took: " + time_in_minutes + \
            " minutes.\lNumber of pages drawn: " + str(total_num_drawn)
    return label


def draw_random_pages(u, num_of_pages, debug=False):
    """
    draws random pages using draw_list_of_pages()

    :param u: the graph to draw on.
    :type u: Digraph
    :param num_of_pages: the number of random pages to draw on
    :param debug: True - if you want to debug or get information about the program while it's running.
                False - default
    :type debug: bool
    :return: the list of the first pages drawn (the names of the first pages) and the total number of pages drawn.
    """
    pages_to_draw = []
    for _ in range(num_of_pages):
        pages_to_draw.append(WikiPage.get_random_page(debug))

    first_pages, num_drawn = draw_list_of_pages(pages_to_draw, u, debug)
    return first_pages, num_drawn


def main():
    const_workfile_filename = "graph_drawn"

    '''
    The output file formats. I used .pdf and .svg which are both very convenient.
    I prefer .svg because the library supports making nodes clickable.
    Graphviz documentation: https://graphviz.org/doc/info/output.html
    
    e.g:
    output_file_formats = ["svg", "pdf", "jpg"]
    '''
    output_file_formats = ["svg", "pdf"]

    num_of_pages = [5, 5, 5, 5, 5, 5, 7, 10, 8, 5, 5, 8, 10, 8, 15, 15]
    num_of_pages = [1]
    for i in num_of_pages:
        if i < 1:
            continue

        u = Digraph('unix', filename=const_workfile_filename, strict=True,
                    node_attr={'color': REGULAR_PAGES_COLOR, 'style': 'filled'}, )
        u.attr(size='50,50')
        start_time = time.time()
        '''
        r = RandomWords()
        names = r.get_random_words(hasDictionaryDef="true", minLength=4, maxLength=13, sortBy="alpha",
                                   sortOrder="asc", limit=i)
        print(len(names), names)
        first_pages, total_num_drawn = draw_list_of_page_names(names, u, False)
        '''
        # first_pages, total_num_drawn = draw_random_pages(u, i, DEBUG)
        names = ["russia", "Space", "coronavirus", "real madrid", "Art", "lebron james", "formula 1"]
        names = ["United States"]
        first_pages, total_num_drawn = draw_list_of_page_names(names, u, False)
        '''num_of_pages_to_connect = int(input("how many pages? "))
        first_pages = []
        for _ in range(num_of_pages_to_connect):
            first_page = WikiPage.choose_first_page_manually()
            draw_page_path(first_page, u)
            first_pages.append(first_page.name)'''

        time_in_minutes = "{:.2f}".format((time.time() - start_time) / 60)
        print("run ended after:", time_in_minutes, "minutes")
        print("ran on ", len(first_pages), "names")
        #u.attr(label=create_label_for_output_file(first_pages, time_in_minutes, total_num_drawn), fontsize="20")

        for output_format in output_file_formats:
            u.format = output_format
            u.view()
            # we create a copy of the graph we just generated, save it in ./output folder and give it a useful name.
            create_corresponding_copy(const_workfile_filename, first_pages, output_format)


if __name__ == '__main__':
    main()
