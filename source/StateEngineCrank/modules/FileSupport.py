""" StateEngineCrank File Support """

# System imports
import logging
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

from enum import Enum   # noqa 408
import os               # noqa 408
import re               # noqa 408
import shutil           # noqa 408

import modules.ErrorHandling    # noqa 408
import modules.Singleton        # noqa 408


class File(modules.Singleton.Singleton):
    """ File support for StateEngineCrank
        (open, read, write, close, etc...)
    """

    EOF = -1    #: end of file reached

    class FileType(Enum):
        c = 1           #: Ansi-C files
        py = 2          #: Python files
        unknown = 3     #: Unknown file type

    # =========================================================================
    def __init__(self):
        self.error = modules.ErrorHandling.Error()
        self.file_object = None
        self.file_name = None
        self.file_original = []     #: input file - original version
        self.file_content = []      #: input file - updated content
        self.file_line = None
        self.file_index = 0
        self.file_lines = 0
        self.file_temp = 0          #: used for comparing before and after
        logging.debug('FileSupport ID: %s' % id(self))

    # =========================================================================
    @staticmethod
    def file_type(filename):
        """ Return filetype enum for file (based on extension)

            :param filename: name of file to test
            :returns: File.FileType.c : filename ends with '.c'
            :returns: File.FileType.py : filename ends with '.py'
            :returns: File.FileType.unknown : file type is unknown
        """
        if filename.endswith('.c'):
            return File.FileType.c
        elif filename.endswith('.py'):
            return File.FileType.py
        else:
            return File.FileType.unknown

    # =========================================================================
    def open(self, filename):
        """ Open requested file for reading

            :param filename: name of file to open
            :raises: IOError(filename)
        """
        self.file_name = filename
        logging.debug('[File_Open] %s' % self.file_name)
        try:
            self.file_name = filename
            self.file_object = open(self.file_name, 'r')
        except IOError:
            self.error.input_file_open_error(self.file_name)

    # =========================================================================
    def read(self):
        """ Read file contents into array

            :raises: IOError(filename)
        """
        logging.debug('[File_Read] %s' % self.file_name)
        try:
            # read input file
            self.file_original = self.file_object.read().splitlines()
            # clear out input file updated content
            self.file_content = []
            self.file_index = 0
            self.file_lines = len(self.file_original)
            logging.debug('Lines read: %s' % self.file_lines)
            # create a working copy
            for i in range(len(self.file_original)):
                self.file_content.append(self.file_original[i])
        except IOError:
            self.error.input_file_read_error(self.file_name)

    # =========================================================================
    def get_line(self, index):
        """ Get requested line from file array

            Returns line number and text as a list[]

            :param index: index of line to return from file
            :returns: [file_index, file_line_text]
        """
        self.file_index = index
        if self.file_index >= self.file_lines:
            logging.info(self.file_index, self.file_lines, self.file_line)
            return [self.EOF, self.file_line.strip()]
        self.file_line = self.file_content[self.file_index]

        # strip leading/trailing whitespace
        self.file_line = self.file_line.strip()

        # replace multiple whitespace with single space
        self.file_line = re.sub(r'\s+', ' ', self.file_line)

        logging.debug('Line: [%s] %s' % (self.file_index, self.file_line))
        return [self.file_index, self.file_line]

    # =========================================================================
    def append_line(self, text):
        """ Append text to end of file in memory

            :param text: text to append to end of file in memory
        """
        logging.debug('Append:  %s' % text)
        self.file_content.append(text)
        self.file_lines = self.file_lines + 1

    # =========================================================================
    def delete_line(self, index):
        """ Delete line of text specified by 'index' from file in memory

            :param index: index of line to be deleted from memory
            :raises: Exception
        """
        if (index < 1) or (index > self.file_lines):
            self.error.bad_file_index(index)

        # index passed to us is 1-relative, make it 0-relative
        index = index-1

        # delete line and adjust the number of lines
        logging.debug('Delete Line # %s : %s' % (index, self.get_line_text(index)))
        del self.file_content[index]
        self.file_lines = len(self.file_content)

    # =========================================================================
    def get_line_text(self, index):
        """ Get specified line of text from file in memory

            :param index: index of line to be retrieved from memory
            :returns: text for requested line
        """
        return self.get_line(index)[1]

    # =========================================================================
    def insert_line_text(self, index, text):
        """ Insert a line of text into file in memory

            :param index: index of line to be inserted into memory
            :param text: text of line to insert
        """
        self.file_content.insert(index, text)
        self.file_lines = self.file_lines + 1

    # =========================================================================
    def number_of_lines(self):
        """ Return number of lines in file in memory

            :returns: Number of lines in file
        """
        return self.file_lines

    # =========================================================================
    def close(self):
        """ Close file """
        logging.debug('[File_Close] %s' % self.file_name)
        self.file_object.close()

    # =========================================================================
    def compare_files(self):
        """ Compare original file to most recent file after all processing

            :returns: True : files are identical
            :returns: False : files are different
        """
        logging.debug('[File_CompareFiles] %s' % self.file_name)
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
        """ Create a suffix string to add as a sequence number to a filename

            :param suffix: string to use as a basis for the sequence number
            :returns: Completed suffix string
        """
        i = str(suffix)
        while len(i) < 3:
            i = '0' + i
        return '.'+i

    # =========================================================================
    def backup(self, filename):
        """ Make a backup copy of the requested file

            :param filename: name of file to backup
        """
        looking = True
        suffix_number = 0
        backup_filename = filename
        # find first available backup filename
        while looking:
            suffix_string = self.mk_suffix_string(suffix_number)
            backup_filename = filename+suffix_string
            logging.debug('[Backup File] %s' % backup_filename)
            if os.path.isfile(backup_filename) is False:
                looking = False
            else:
                suffix_number = suffix_number + 1
        # create backup file
        shutil.copyfile(filename, backup_filename)

    # =========================================================================
    def update(self, filename):
        """ Update the requested file with the latest contents

            :param filename: name of file to update
        """
        logging.debug('[Write File] %s' % filename)
        filehandle = open(self.file_name, 'w')
        for line in self.file_content:
            filehandle.write(line + '\n')
        filehandle.close()

    # =========================================================================
    def dump_file(self):
        """ Dump the file currently in memory for debug purposes. """
        for line in range(0, self.file_lines):
            logging.debug('Line [%s] %s' % (line, self.file_content[line]))
