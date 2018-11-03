#!/usr/bin/env python
"""
Created on May 20, 2016

@author:    Mark Sawyer
@date:      29-June-2016

@package:   StateEngineCrank
@brief:     Main entry module
@details:   Main module for the modules utility

@todo:    Need to handle the case where there is a [guard] / Transition
          but no Event to trigger the transition. This case will occur
          if there is a state where it is desirable to always transition
          if the [guard] condition is met. Not sure if this is actually
          valid UML but it came up during debugging of the Philosophers.

@copyright: Mark B Sawyer, All Rights Reserved 2016
"""
print('Loading modules: ', __file__, 'as', __name__)

import modules.CodeGeneration               # noqa e408
import modules.CodeScan                     # noqa e408
import modules.CommandLineParsing           # noqa e408
import modules.ConfigurationFileParsing     # noqa e408
import modules.DebugSupport                 # noqa e408
import modules.ErrorHandling                # noqa e408
import modules.FileSupport                  # noqa e408
import modules.Options                      # noqa e408
import modules.Signature                    # noqa e408
import modules.UMLParse                     # noqa e408

# =========================================================
#  DEBUG *** DEBUG *** DEBUG *** DEBUG *** DEBUG *** DEBUG
#
#  Create a file for debugging
# =========================================================
# filenames = ['../StateEngine.UML', '../StateMachine.c']
# with open('./StateEngine.c', 'w') as outfile:
#    for fname in filenames:
#        with open(fname) as infile:
#            for line in infile:
#                outfile.write(line)
#    outfile.close()
# =========================================================
# main entry point - start of execution
# =========================================================
print('Start execution as: ', __name__)
if __name__ == '__main__':

    CMDLINE = modules.CommandLineParsing.CommandLine()
    CODEGEN = modules.CodeGeneration.CodeGen()
    CODESCAN = modules.CodeScan.CodeScan()
    DEBUG = modules.DebugSupport.Debug()
    FILE = modules.FileSupport.File()
    OPTIONS = modules.Options.Options()
    SIG = modules.Signature.Signature()
    UML = modules.UMLParse.UML()

    # =========================================================================
    # the big try for all of our processing
    try:
        # parse command line
        CMDLINE.parse()
        DEBUG.dprint(('Command Line: ', CMDLINE.args))

        # parse configuration file if one was specified
        CONFIG_FILE = CMDLINE.config()
        if CONFIG_FILE is not None:
            DEBUG.dprint(('Configuration File:', CONFIG_FILE))
            CONFIG = modules.ConfigurationFileParsing.ConfigFile()
            CONFIG.read_config_file(CONFIG_FILE)

        # check for input files to process
        INPUT_FILES = OPTIONS.files()
        NUM_INPUT_FILES = len(INPUT_FILES)
        if NUM_INPUT_FILES == 0:
            DEBUG.vprint(('Nothing to do.', ''))
            exit()

        # display invocation information
        DEBUG.dprint(('Begin execution:', __name__))
        DEBUG.dprint(('Processing', NUM_INPUT_FILES, 'input files.'))

        # =====================================================================
        # process all input files
        for input_file in INPUT_FILES:
            DEBUG.vprint(('Input file:', input_file))

            # read source file into memory
            FILE.open(input_file)
            FILE.read()
            FILE.close()

            # scan for UML and parse
            # initialize UML module before parsing
            UML.init()
            if UML.find_start_plant_uml() is False:
                DEBUG.dvprint(('UML Start NOT FOUND', 'Ignoring'))
                continue
            if UML.find_end_plant_uml() is False:
                DEBUG.dvprint(('UML End NOT FOUND', 'Ignoring'))
                continue
            if UML.parse_plant_uml() is False:
                exit()

            # scan for StateEngineCrank signatures
            # Note:
            #    We either find ALL of the signatures or we find NONE of the signatures.
            #    If we only find SOME of the signatures then something is BROKEN.
            #    If the signatures are NOT found then we create them
            if SIG.find_signatures() is False:
                SIG.create_signatures()

            # Scan and create list of current user state functions
            CODESCAN.scan_code()

            # Signatures (now) exist so update code based on current UML
            CODEGEN.update_code()

            # Process files if any state machine changes were detected
            #    If the file changed then backup (rename) the original/
            #    And write the updated contents.
            if FILE.compare_files() is False:
                FILE.backup(input_file)
                FILE.update(input_file)

    # =========================================================================
    except modules.ErrorHandling.UnimplementedCodeError as error:
        print('Unimplemented code encountered -->', error)
    except modules.ErrorHandling.SourceFileError as error:
        print('Error processing source file -->', error)
    except modules.ErrorHandling.UMLParseError as error:
        print('Error parsing UML -->', error)
    except modules.ErrorHandling.SignatureError as error:
        print('Error processing signatures -->', error)
    except modules.ErrorHandling.ScanCodeError as error:
        print('Error scanning user state functions -->', error)
    except modules.ErrorHandling.UpdateCodeError as error:
        print('Error updating code -->', error)
    except modules.ErrorHandling.FileBackupError as error:
        print('Error processing file updates -->', error)
    except modules.ErrorHandling.FileWriteError as error:
        print('Error writing file -->', error)
    except modules.ErrorHandling.ConfigFileError as error:
        print('Error processing configuration file --->', error)
    except Exception as e:
        print('Uncategorized error encountered')
        raise e     # re-raise to dump the specifics of this error
    else:
        print('Success')

    # =========================================================
    # exit processing and cleanup
    # =========================================================
        print('Execution complete ... exiting ...')
        exit(1)
