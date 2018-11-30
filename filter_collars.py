#!/usr/bin/python3
"""Tool to parse and filter data sets acquired from wildlife tracking collars.

Author: John Sherohman
"""

import csv
import os
import re


class ChunkingCsvWriter:
    """A csv writer class that can automatically roll to a new file after a line limit.
    
    :param str name_prefix: The name to use for file(s) created by this class.
    :param list[str] headers: The headers which should be printed at the top of the file.
    :param bool with_dir: Whether output file(s) should be placed inside of a directory of the
        same name (True) or in a flat structure (False). Default True.
    :param int max_lines: The max number of lines to write in a single file before starting a new
        file. Default None is no limit.
    """
    SINGLE_FILE_FMT = "{prefix}.csv"
    MULTI_FILE_FMT = "{prefix}_{suffix}.csv"

    def __init__(self, name_prefix, headers, with_dir=True, max_lines=None):
        self.name_prefix = name_prefix
        self.headers = headers
        self.with_dir = with_dir
        self.max_lines = max_lines
        self.file_idx = 0
        self.line_idx = 0
        self.filename = ""

        # Make dir and initial file
        if with_dir:
            os.mkdir(self.name_prefix)
        self._make_file()

    def _make_file(self):
        if self.max_lines:
            self.filename = self.MULTI_FILE_FMT.format(prefix=self.name_prefix, suffix=self.file_idx)
            self.file_idx += 1
            self.line_idx = 0
        else:
            self.filename = self.SINGLE_FILE_FMT.format(prefix=self.name_prefix)
        path = (os.path.join(os.getcwd(), self.name_prefix, self.filename) if self.with_dir
                else os.path.join(os.getcwd(), self.filename))
        self.out_file_handle = open(path, 'w')
        self.write_line(self.headers)

    def write_line(self, values):
        """Write the provided list of values to the file, separated by commas.

        If we're at the line length limit, close the existing file and start another.

        :param list values: A list of the things that should be written to the file. Things must be
            castable to strings.
        """
        self.out_file_handle.write(",".join([str(item) for item in values]))
        # Python 3 docs say to write a single \n as line term for any platform
        self.out_file_handle.write("\n")
        self.line_idx += 1
        if self.max_lines and self.line_idx >= self.max_lines:
            self.out_file_handle.close()
            self._make_file()


def list_local_files(extension=None):
    """List files in the current working dir, optionally with a specific extensiom.

    :param str extension: The file extension (e.g. '.csv') that local files should end with to be
        listed here. Default None returns all files.
    """
    cwd = os.getcwd()
    all_files = [f for f in os.listdir(cwd) if os.path.isfile(os.path.join(cwd, f))]
    if extension:
        all_files = [f for f in all_files if f.endswith(extension)]
    return all_files


def get_user_selection(options, prompt=None, allow_empty=False):
    """Select an item out of a list based on user input.

    List items will be printed with numerical identifiers next to them to simplify input. Will retry
    on invalid inputs until a valid input is received.

    :param list options: The list of things that the user should select from. Options must all be
        representable as strings.
    :param str option_desc: Optional prompt to show to user; generic prompt will be shown if nothing is
        provided.
    :param bool allow_empty: Whether an empty response from the user is allowed, which will result in an
        empty string return from the function. Default False.
    :return: The item selected from the list.
    """
    prompt = "Please select from the following options:" if not prompt else prompt
    print(prompt)
    for idx, option in enumerate(options):
        print("{}) {}".format("{:>3}".format(idx + 1), option))
    valid_input = False
    while not valid_input:
        selection = input("-> ")
        if allow_empty and selection == "":
            return selection
        try:
            selection_int = int(selection)
        except (TypeError, ValueError):
            print("Didn't get a valid number, please try again")
            continue
        if selection_int <= 0 or selection_int > len(options):
            print("Selection out of range, please try again")
            continue
        selection_int -= 1  # User input is 1-indexed but list is 0-indexed
        return options[selection_int]


def get_user_int(min_n=None, max_n=None, prompt="", allow_empty=False):
    """Get an integer value from user input.

    """
    prompt = "Please enter a number" if not prompt else prompt
    if prompt:
        print(prompt)
    limit_str = ""
    if min_n is not None:
        limit_str += "min value is {}".format(min_n)
    if max_n is not None:
        if limit_str:
            limit_str += "; "
        limit_str +=  "max value is {}".format(max_n)
    if limit_str:
        print(limit_str)

    valid_input = False
    while not valid_input:
        selection = input("-> ")
        if allow_empty and selection == "":
            return selection
        try:
            selection_int = int(selection)
        except (TypeError, ValueError):
            print("Didn't get a valid number, please try again")
            continue
        if min_n is not None and selection_int < min_n:
            print("Selection out of range, please try again")
            continue
        if max_n is not None and selection_int > max_n:
            print("Selection out of range, please try again")
            continue
        return selection_int


def parse_valid_tag_ids(valid_tags_file):
    with open(valid_tags_file) as tags_handle:
        first_line = tags_handle.readline()
        tags = first_line.strip().split(',')
    if not tags:
        raise Exception("No tag IDs found in file {}".format(valid_tags_file))
    return [tag.upper() for tag in tags]


def main():
    # list local files that are options for parsing
    csv_files = list_local_files(".csv")

    # ask user to pick a tags file
    raw_tags_file = get_user_selection(csv_files,
                                       "Please select the csv file containing raw tags data")

    # Ask user to pick a valid tags file
    valid_tags_file = get_user_selection(csv_files,
                                         "Please select the csv file containing valid tag IDs")
    valid_tag_ids = parse_valid_tag_ids(valid_tags_file)

    # Ask user fox max output file size
    max_output_lines = get_user_int(min_n=0,
                                    prompt="Please enter max output file size in number of lines;"
                                           "entering 0 means no limit")
    max_output_lines = max_output_lines or None

    with open(raw_tags_file) as raw_tags_handle:
        tags_reader = csv.DictReader(raw_tags_handle)
        headers = tags_reader.fieldnames
        tag_field_name = get_user_selection(
            headers,
            prompt="Please select the column which contains tag IDs to filter on")
        output_writers = {
            valid_id: ChunkingCsvWriter(valid_id, headers, with_dir=True, max_lines=max_output_lines)
            for valid_id in valid_tag_ids}
        orphan_writer = ChunkingCsvWriter("orphan_ids", headers, with_dir=True,
                                          max_lines=max_output_lines)

        # Loop over the contents of the input file
        for line in tags_reader:
            if tag_field_name in line and line[tag_field_name].upper() in output_writers:
                output_writers[line[tag_field_name].upper()].write_line(line.values())
            else:
                orphan_writer.write_line(line.values())

        for writer in output_writers.values():
            writer.out_file_handle.close()
        orphan_writer.out_file_handle.close()


if __name__ == "__main__":
    main()
