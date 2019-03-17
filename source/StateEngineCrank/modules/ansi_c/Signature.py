""" StateEngineCrank.ansi_c.Signature

Signature Processing (Ansi-C State Engine)

Signature Processing - creation and identification
"""
# System imports
import logging
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

import modules.ErrorHandling  # noqa 408
import modules.FileSupport  # noqa 408
import modules.Singleton  # noqa 408


# =========================================================================
class Signature(modules.Singleton.Singleton):
    """
    Class for processing StateEngineCrank signatures in user source code.
    """

    ####
    # 00000000011111111112222222222333333333344444444445555555555666666666677777777778
    # 12345678901234567890123456789012345678901234567890123456789012345678901234567890
    # // =============================================================================
    # // ========== SIGNATURE_DELIMITER_STRING =======================================
    # // =============================================================================
    ####
    SIGNATURE_LINE_LENGTH = 80          # length of a signature in characters
    SIGNATURE_LINE_PRELIM = 10          # length of the start of the signature
    SIGNATURE_LINE_CHAR = '='           # primary signature character
    SIGNATURE_LINE_DELIM = '// '        # signature line delimiter (it's a comment)
    SIGNATURE_LINE_START = 3            # index of line start (past line delimiter)

    SIGNATURE_LINE_LENGTH_0 = SIGNATURE_LINE_LENGTH - SIGNATURE_LINE_PRELIM - len(SIGNATURE_LINE_DELIM)
    SIGNATURE_LINE_NUM_CHARS = SIGNATURE_LINE_LENGTH - SIGNATURE_LINE_START

    MAIN_CODE_START = ' MAIN STATE CODE START - DO NOT MODIFY '
    MAIN_CODE_END = ' MAIN STATE CODE END - DO NOT MODIFY '
    MAIN_CODE_DEFINES_START = ' MAIN STATE CODE DEFINES START - DO NOT MODIFY '
    MAIN_CODE_DEFINES_END = ' MAIN STATE CODE DEFINES END - DO NOT MODIFY '
    MAIN_CODE_ENUMS_START = ' MAIN STATE CODE STATE DEFINES START - DO NOT MODIFY '
    MAIN_CODE_ENUMS_END = ' MAIN STATE CODE STATE DEFINES END - DO NOT MODIFY '
    MAIN_CODE_PROTOTYPES_START = ' MAIN STATE CODE PROTOTYPES START - DO NOT MODIFY '
    MAIN_CODE_PROTOTYPES_END = ' MAIN STATE CODE PROTOTYPES END - DO NOT MODIFY '
    MAIN_CODE_VARIABLES_START = ' MAIN STATE CODE VARIABLES START - DO NOT MODIFY '
    MAIN_CODE_VARIABLES_END = ' MAIN STATE CODE VARIABLES END - DO NOT MODIFY '

    USER_CODE_START = ' USER STATE CODE START '
    USER_CODE_END = ' USER STATE CODE END '
    USER_CODE_PROTOTYPES_START = ' USER STATE CODE PROTOTYPES START '
    USER_CODE_PROTOTYPES_END = ' USER STATE CODE PROTOTYPES END '

    # =========================================================================
    def __init__(self):
        # instantiate local instances of global support
        self.signatures = {}            # a dictionary of all signatures
        self.lines = []                 # each signature has '3' lines
        self.lines.append(None)
        self.lines.append(None)
        self.lines.append(None)

        self.err = modules.ErrorHandling.Error()
        self.file = modules.FileSupport.File()

        self.lines[0] = self.SIGNATURE_LINE_DELIM + \
                        "".join(self.SIGNATURE_LINE_CHAR for _ in range(self.SIGNATURE_LINE_NUM_CHARS))     # noqa e127
        self.lines[2] = self.lines[0]

        self.signature_line1 = self.SIGNATURE_LINE_DELIM + \
                               "".join(self.SIGNATURE_LINE_CHAR for _ in range(self.SIGNATURE_LINE_PRELIM))  # noqa e127

        self.create_signature(self.MAIN_CODE_DEFINES_START)
        self.create_signature(self.MAIN_CODE_DEFINES_END)
        self.create_signature(self.MAIN_CODE_ENUMS_START)
        self.create_signature(self.MAIN_CODE_ENUMS_END)
        self.create_signature(self.MAIN_CODE_PROTOTYPES_START)
        self.create_signature(self.MAIN_CODE_PROTOTYPES_END)
        self.create_signature(self.MAIN_CODE_VARIABLES_START)
        self.create_signature(self.MAIN_CODE_VARIABLES_END)
        self.create_signature(self.MAIN_CODE_START)
        self.create_signature(self.MAIN_CODE_END)

        self.create_signature(self.USER_CODE_PROTOTYPES_START)
        self.create_signature(self.USER_CODE_PROTOTYPES_END)
        self.create_signature(self.USER_CODE_START)
        self.create_signature(self.USER_CODE_END)

    # =========================================================================
    def create_signature_user_proto_start(self):
        """ Create user prototype signature start. """
        self.file.append_line(self.signatures[self.USER_CODE_PROTOTYPES_START][1][0])
        self.file.append_line(self.signatures[self.USER_CODE_PROTOTYPES_START][1][1])
        self.file.append_line(self.signatures[self.USER_CODE_PROTOTYPES_START][1][2])

    # =========================================================================
    def create_signature_user_proto_end(self):
        """ Create user prototype signature end. """
        self.file.append_line(self.signatures[self.USER_CODE_PROTOTYPES_END][1][0])
        self.file.append_line(self.signatures[self.USER_CODE_PROTOTYPES_END][1][1])
        self.file.append_line(self.signatures[self.USER_CODE_PROTOTYPES_END][1][2])

    # =========================================================================
    def create_signature_user_code_start(self):
        """ Create user code signature start. """
        self.file.append_line(self.signatures[self.USER_CODE_START][1][0])
        self.file.append_line(self.signatures[self.USER_CODE_START][1][1])
        self.file.append_line(self.signatures[self.USER_CODE_START][1][2])

    # =========================================================================
    def create_signature_user_code_end(self):
        """ Create user code signature start. """
        self.file.append_line(self.signatures[self.USER_CODE_END][1][0])
        self.file.append_line(self.signatures[self.USER_CODE_END][1][1])
        self.file.append_line(self.signatures[self.USER_CODE_END][1][2])

    # =========================================================================
    def create_signature_main_code_defines_start(self):
        """ Create state engine declarations signature start. """
        self.file.append_line(self.signatures[self.MAIN_CODE_DEFINES_START][1][0])
        self.file.append_line(self.signatures[self.MAIN_CODE_DEFINES_START][1][1])
        self.file.append_line(self.signatures[self.MAIN_CODE_DEFINES_START][1][2])

    # =========================================================================
    def create_signature_main_code_defines_end(self):
        """ Create state engine declarations signature end. """
        self.file.append_line(self.signatures[self.MAIN_CODE_DEFINES_END][1][0])
        self.file.append_line(self.signatures[self.MAIN_CODE_DEFINES_END][1][1])
        self.file.append_line(self.signatures[self.MAIN_CODE_DEFINES_END][1][2])

    # =========================================================================
    def create_signature_main_code_enums_start(self):
        """ Create state engine enumerations signature start. """
        self.file.append_line(self.signatures[self.MAIN_CODE_ENUMS_START][1][0])
        self.file.append_line(self.signatures[self.MAIN_CODE_ENUMS_START][1][1])
        self.file.append_line(self.signatures[self.MAIN_CODE_ENUMS_START][1][2])

    # =========================================================================
    def create_signature_main_code_enums_end(self):
        """ Create state engine enumerations signature end. """
        self.file.append_line(self.signatures[self.MAIN_CODE_ENUMS_END][1][0])
        self.file.append_line(self.signatures[self.MAIN_CODE_ENUMS_END][1][1])
        self.file.append_line(self.signatures[self.MAIN_CODE_ENUMS_END][1][2])

    # =========================================================================
    def create_signature_main_code_start(self):
        """ Create state engine code signature start. """
        self.file.append_line(self.signatures[self.MAIN_CODE_START][1][0])
        self.file.append_line(self.signatures[self.MAIN_CODE_START][1][1])
        self.file.append_line(self.signatures[self.MAIN_CODE_START][1][2])

    # =========================================================================
    def create_signature_main_code_end(self):
        """ Create state engine code signature end. """
        self.file.append_line(self.signatures[self.MAIN_CODE_END][1][0])
        self.file.append_line(self.signatures[self.MAIN_CODE_END][1][1])
        self.file.append_line(self.signatures[self.MAIN_CODE_END][1][2])

    # =========================================================================
    def create_signature_main_code_proto_start(self):
        """ Create state engine prototype signature start. """
        self.file.append_line(self.signatures[self.MAIN_CODE_PROTOTYPES_START][1][0])
        self.file.append_line(self.signatures[self.MAIN_CODE_PROTOTYPES_START][1][1])
        self.file.append_line(self.signatures[self.MAIN_CODE_PROTOTYPES_START][1][2])

    # =========================================================================
    def create_signature_main_code_proto_end(self):
        """ Create state engine prototype signature end. """
        self.file.append_line(self.signatures[self.MAIN_CODE_PROTOTYPES_END][1][0])
        self.file.append_line(self.signatures[self.MAIN_CODE_PROTOTYPES_END][1][1])
        self.file.append_line(self.signatures[self.MAIN_CODE_PROTOTYPES_END][1][2])

    # =========================================================================
    def create_signature_main_code_vars_start(self):
        """ Create state engine variables signature start. """
        self.file.append_line(self.signatures[self.MAIN_CODE_VARIABLES_START][1][0])
        self.file.append_line(self.signatures[self.MAIN_CODE_VARIABLES_START][1][1])
        self.file.append_line(self.signatures[self.MAIN_CODE_VARIABLES_START][1][2])

    # =========================================================================
    def create_signature_main_code_vars_end(self):
        """ Create state engine variables signature end. """
        self.file.append_line(self.signatures[self.MAIN_CODE_VARIABLES_END][1][0])
        self.file.append_line(self.signatures[self.MAIN_CODE_VARIABLES_END][1][1])
        self.file.append_line(self.signatures[self.MAIN_CODE_VARIABLES_END][1][2])

    # =========================================================================
    def create_signatures(self):
        """ Create all signatures (user and main). """
        self.file.append_line('')    # add a blank line
        self.create_signature_user_proto_start()
        self.file.append_line('')    # add a blank line
        self.create_signature_user_proto_end()
        self.file.append_line('')    # add a blank line
        self.create_signature_user_code_start()
        self.file.append_line('')    # add a blank line
        self.create_signature_user_code_end()
        self.file.append_line('')    # add a blank line
        self.create_signature_main_code_enums_start()
        self.file.append_line('')    # add a blank line
        self.create_signature_main_code_enums_end()
        self.file.append_line('')    # add a blank line
        self.create_signature_main_code_defines_start()
        self.file.append_line('')    # add a blank line
        self.create_signature_main_code_defines_end()
        self.file.append_line('')    # add a blank line
        self.create_signature_main_code_proto_start()
        self.file.append_line('')    # add a blank line
        self.create_signature_main_code_proto_end()
        self.file.append_line('')    # add a blank line
        self.create_signature_main_code_vars_start()
        self.file.append_line('')    # add a blank line
        self.create_signature_main_code_vars_end()
        self.file.append_line('')    # add a blank line
        self.create_signature_main_code_start()
        self.file.append_line('')    # add a blank line
        self.create_signature_main_code_end()

    # =========================================================================
    def find_signature(self, signature):
        """ Find requested signature. """
        logging.debug('signature: %s' % signature)

        sig = self.signatures[signature]
        logging.debug('signature: %s' % sig)

        logging.debug('sigID: %s' % signature)
        logging.debug('sigLines: %s' % sig[1])
        logging.debug('sigLocation: %s' % sig[0])

        # break out the signature lines
        sig_line1_text = sig[1][0]
        sig_line2_text = sig[1][1]
        sig_line3_text = sig[1][2]

        logging.debug('sig_line1_text: %s' % sig_line1_text)
        logging.debug('sig_line2_text: %s' % sig_line2_text)
        logging.debug('sig_line3_text: %s' % sig_line3_text)

        # total number of lines in the file
        num_lines = self.file.number_of_lines()

        # scan all lines in the file
        for line in range(0, num_lines-2):
            line1_text = self.file.get_line_text(line)
            if line1_text == sig_line1_text:
                line2_text = self.file.get_line_text(line+1)
                if line2_text == sig_line2_text:
                    line3_text = self.file.get_line_text(line+2)
                    if line3_text == sig_line3_text:
                        ####
                        # we don't know what the caller was searching for so
                        # we return "line+2" which is line #2 of the signature
                        # based on a 1-relative index
                        #
                        # the caller must know whether or not to add or subtract
                        # from our return
                        ####
                        return [True, line+2]

        return [False, -1]

    # =========================================================================
    def find_signatures(self):
        """ Find all signatures (user and main). """
        sig_found = False    # set True when a signature is found
        all_found = True     # set False when a signature is NOT found

        # loop through all signatures
        for sig in enumerate(self.signatures):
            # try to find signature in current file
            # we only want the result, not the line number
            logging.debug('FINDSIG: %s' % sig[1])
            if self.find_signature(sig[1])[0]:
                logging.debug('FINDSIG: FOUND %s' % sig[1])
                sig_found = True
            else:
                logging.debug('FINDSIG: NOT FOUND % s' % sig[1])
                all_found = False

        # verify we either found ALL or NONE
        if all_found:
            logging.debug('FINDSIG: All signatures found')
            return True
        if sig_found is False:
            return False

        # we found SOME but not ALL
        self.err.signature_scan_error(self.file.file_name)
        return False

    # =========================================================================
    def find_state_engine_code_start(self):
        """ Find state engine code start. """
        return self.findsignature(self.MAIN_CODE_START)

    # =========================================================================
    def find_state_engine_code_end(self):
        """ Find state engine code end. """
        return self.findsignature(self.MAIN_CODE_END)

    # =========================================================================
    def find_state_engine_code_defines_start(self):
        """ Find state engine code defines start. """
        return self.findsignature(self.MAIN_CODE_DEFINES_START)

    # =========================================================================
    def find_state_engine_code_defines_end(self):
        """ Find state engine code defines end. """
        return self.findsignature(self.MAIN_CODE_DEFINES_END)

    # =========================================================================
    def find_state_engine_code_enums_start(self):
        """ Find state engine code enumerations start. """
        return self.findsignature(self.MAIN_CODE_ENUMS_START)

    # =========================================================================
    def find_state_engine_code_enums_end(self):
        """ Find state engine code enumerations end. """
        return self.findsignature(self.MAIN_CODE_ENUMS_END)

    # =========================================================================
    def find_state_engine_code_proto_start(self):
        """ Find state engine code prototypes start. """
        return self.findsignature(self.MAIN_CODE_PROTOTYPES_START)

    # =========================================================================
    def find_state_engine_code_proto_end(self):
        """ Find state engine code prototypes end. """
        return self.findsignature(self.MAIN_CODE_PROTOTYPES_END)

    # =========================================================================
    def find_state_engine_code_variables_start(self):
        """ Find state engine code variables start. """
        return self.findsignature(self.MAIN_CODE_VARIABLES_START)

    # =========================================================================
    def find_state_engine_code_variables_end(self):
        """ Find state engine code variables end. """
        return self.findsignature(self.MAIN_CODE_VARIABLES_END)

    # =========================================================================
    def find_user_code_start(self):
        """ Find user code start. """
        return self.findsignature(self.USER_CODE_START)

    # =========================================================================
    def find_user_code_end(self):
        """ Find user code end. """
        return self.findsignature(self.USER_CODE_END)

    # =========================================================================
    def find_user_code_proto_start(self):
        """ Find user prototypes start. """
        return self.findsignature(self.USER_CODE_PROTOTYPES_START)

    # =========================================================================
    def find_user_code_proto_end(self):
        """ Find user prototypes end. """
        return self.findsignature(self.USER_CODE_PROTOTYPES_END)

    # =========================================================================
    def create_signature(self, signature_string):
        """ Worker function called during initialization to create signatures """
        line = -1           # signature does not yet have a line number
        sig = [None] * 3    # signature is 3 lines long
        sig_len = self.SIGNATURE_LINE_LENGTH_0 - len(signature_string)
        sig[0] = self.lines[0]
        sig[1] = self.signature_line1 + signature_string + "".join(self.SIGNATURE_LINE_CHAR for _ in range(sig_len))
        sig[2] = self.lines[2]

        # add it to the dictionary of signatures
        self.signatures[signature_string] = [line, sig]

    # =========================================================================
    def findsignature(self, signature):
        """ Find requested signature (state or user, start or end). """
        result, line = self.find_signature(signature)
        if result is False:
            self.err.signature_not_found(signature)
        return line
