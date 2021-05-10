# Written by Tommy Zaft

import helper
# to get args
import sys
# to measure time
import time

# True - if you want to debug or get information about the program while it's running.
DEBUG = False

'''
    The output file formats. I used .pdf and .svg which are both very convenient.
    I prefer .svg because the library supports making nodes clickable.
    Graphviz documentation: https://graphviz.org/doc/info/output.html

    e.g:
    output_file_formats = ["svg", "jpg"]
    '''
output_file_formats = ["svg", "pdf"]


def main():
    """
    Gets in args the number of pages to draw.
    Then for each page, the programs asks you to choose a Wikipedia article name (by entering the index),
    and the program draws a graph of "Getting to Philosophy" with the Wikipedia articles chosen.

    for example:
    to draw 5 handpicked pages, we run in terminal:
    python draw_handpicked_pages.py 5

    :return: None
    """

    num_of_pages = int(sys.argv[1])

    u = helper.create_digraph()

    start_time = time.time()

    # if you want to choose each page manually in the drawing
    first_pages, total_num_drawn = helper.handpick_and_draw(num_of_pages, u, DEBUG)

    # we print details about the run: "run ended after: 0.34 minutes, ran on 2 names"
    time_in_minutes = helper.print_running_report(time.time(), start_time, len(first_pages))

    print()

    # adds a label with some details about the graph.
    u.attr(label=helper.create_label_for_output_file(first_pages, time_in_minutes, total_num_drawn),
           fontsize=helper.LABEL_FONT_SIZE)

    for output_format in output_file_formats:
        u.format = output_format
        u.view()
        # we create a copy of the graph we just generated, save it in ./output folder and give it a useful name.
        helper.create_corresponding_copy(helper.WORK_FILE_NAME, first_pages, output_format)


if __name__ == '__main__':
    main()
