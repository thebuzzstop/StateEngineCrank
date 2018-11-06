"""
Created on May 19, 2016

@author:    Mark Sawyer
@date:      20-May-2016

@package:   StateEngineCrank
@brief:     File support
@details:   File support for StateEngineCrank (open, read, write, close, etc...)

@copyright: Mark B Sawyer, All Rights Reserved 2016
"""
print('Loading modules: ', __file__, 'as', __name__)

import os       # noqa 408
import re       # noqa 408
import shutil   # noqa 408

import modules.ErrorHandling    # noqa 408
import modules.Singleton        # noqa 408


class File(modules.Singleton.Singleton):
    """ File support for StateEngineCrank
        (open, read, write, close, etc...)
    """

    EOF = -1    # end of file reached

    # =========================================================================
    def __init__(self):
        self.error = modules.ErrorHandling.Error()
        self.file_object = None
        self.file_name = None
        self.file_original = []     # input file - original version
        self.file_content = []      # input file - updated content
        self.file_line = None
        self.file_index = 0
        self.file_lines = 0
        self.file_temp = 0          # used for comparing before and after
        self.debug.dprint(('FileSupport ID:', id(self)))

    # =========================================================================
    def open(self, filename):
        """ Open requested file for reading. """
        self.file_name = filename
        self.debug.dprint(('[File_Open]', self.file_name))
        try:
            self.file_name = filename
            self.file_object = open(self.file_name, 'r')
        except IOError:
            self.error.input_file_open_error(self.file_name)

    # =========================================================================
    def read(self):
        """ Read file contents into array. """
        self.debug.dprint(('[File_Read]', self.file_name))
        try:
            # read input file
            self.file_original = self.file_object.read().splitlines()
            # clear out input file updated content
            self.file_content = []
            self.file_index = 0
            self.file_lines = len(self.file_original)
            self.debug.dprint(('Lines read:', self.file_lines))
            # create a working copy
            for i in range(len(self.file_original)):
                self.file_content.append(self.file_original[i])
        except IOError:
            self.error.input_file_read_error(self.file_name)

    # =========================================================================
    def get_line(self, index):
        """ Get requested line from file array. """
        self.file_index = index
        if self.file_index >= self.file_lines:
            print(self.file_index, self.file_lines, self.file_line)
            return [self.EOF, self.file_line.strip()]
        self.file_line = self.file_content[self.file_index]

        # strip leading/trailing whitespace
        self.file_line = self.file_line.strip()

        # replace multiple whitespace with single space
        self.file_line = re.sub(r'\s+', ' ', self.file_line)

        self.debug.dprint(('Line: [', self.file_index, '] ', self.file_line))
        return [self.file_index, self.file_line]

    # =========================================================================
    def append_line(self, text):
        """ Append text to end of file in memory. """
        self.debug.dprint(('Append: ', text))
        self.file_content.append(text)
        self.file_lines = self.file_lines + 1

    # =========================================================================
    def delete_line(self, index):
        """ Delete line of text specified by 'index' from file in memory. """
        if (index < 1) or (index > self.file_lines):
            self.error.bad_file_index(index)

        # index passed to us is 1-relative, make it 0-relative
        index = index-1

        # delete line and adjust the number of lines
        self.debug.dprint(('Delete Line #', index, self.get_line_text(index)))
        del self.file_content[index]
        self.file_lines = len(self.file_content)

    # =========================================================================
    def get_line_text(self, index):
        """ Get specified line of text from file in memory. """
        return self.get_line(index)[1]

    # =========================================================================
    def insert_line_text(self, index, text):
        """ Insert a line of text into file in memory. """
        self.file_content.insert(index, text)
        self.file_lines = self.file_lines + 1

    # =========================================================================
    def number_of_lines(self):
        """ Return number of lines in file in memory. """
        return self.file_lines

    # =========================================================================
    def close(self):
        """ Close file. """
        self.debug.dprint(('[File_Close]', self.file_name))
        self.file_object.close()

    # =========================================================================
    def compare_files(self):
        """ Compare original file to most recent file after all processing. """
        self.debug.dprint(('[File_CompareFiles]', self.file_name))
        # files must be of the same length
        if len(self.file_content) != len(self.file_original):
            return False
        # compare all lines in file
        for i in range(len(self.file_original)):
            if self.file_original[i] != self.file_content[i]:
                return False
        return True

    # =========================================================================
    @staticmethod
    def mk_suffix_string(suffix):
        """ Create a suffix string to add as a sequence number to a filename. """
        i = str(suffix)
        while len(i) < 3:
            i = '0' + i
        return '.'+i

    # =========================================================================
    def backup(self, filename):
        """ Make a backup copy of the requested file. """
        looking = True
        suffix_number = 0
        backup_filename = filename
        # find first available backup filename
        while looking:
            suffix_string = self.mk_suffix_string(suffix_number)
            backup_filename = filename+suffix_string
            self.debug.dprint(('[Backup File]', backup_filename))
            if os.path.isfile(backup_filename) is False:
                looking = False
            else:
                suffix_number = suffix_number + 1
        # create backup file
        shutil.copyfile(filename, backup_filename)

    # =========================================================================
    def update(self, filename):
        """ Update the requested file with the latest contents. """
        self.debug.dprint(('[Writing File', filename))
        filehandle = open(self.file_name, 'w')
        for line in self.file_content:
            filehandle.write(line + '\n')
        filehandle.close()

    # =========================================================================
    def dump_file(self):
        """ Dump the file currently in memory for debug purposes. """
        for line in range(0, self.file_lines):
            self.debug.dprint(('Line [', line, '] ', self.file_content[line]))
