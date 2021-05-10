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
    '''
    gets in args a list of numbers. e.g: 5 10
    For each number, we draw a graph of "Getting to Philosophy" with this number of pages,
     each page is chosen randomly.

    :return: None
    '''
    args_list = sys.argv
    num_of_pages = [int(n) for n in args_list[1:]]

    for i in num_of_pages:
        if i < 1:
            continue
        print("Drawing", i, "random pages ...")
        u = helper.create_digraph()

        start_time = time.time()

        # if you want to draw i random articles.
        first_pages, total_num_drawn = helper.draw_random_pages(u, i, DEBUG)

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
