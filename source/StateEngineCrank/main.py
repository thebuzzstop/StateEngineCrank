""" StateEngineCrank.main

Main module for StateEngineCrank

This is the main processing for The State Engine Crank aka *The Crank*

Processing consists of the following steps:

    #. Configuration file processing
    #. Instantiate some support classes (File, Uml, Error)
    #. Process input source files.
    #. Based on input source file type (Python or Ansi-C):

        * Instantiate signature scanner
        * Instantiate code scanner
        * Instantiate code generator

    #. Read source file into memory for processing
    #. Scan for PlantUML
    #. Parse PlantUML
    #. Scan for State Engine Crank :term:`signatures`
    #. Create :term:`signatures` if not found
    #. Scan for existing user state functions
    #. Update code based on current PlantUML
    #. Backup source file if changed

.. todo::
    Need to handle the case where there is a [guard] / Transition
    but no Event to trigger the transition. This case will occur
    if there is a state where it is desirable to always transition
    if the [guard] condition is met. Not sure if this is actually
    valid UML but it came up during debugging of the Philosophers.
"""

# System imports
import logging
# logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(message)s')
logging.basicConfig(level=logging.DEBUG, format='%(message)s')
logging.debug('Loading modules: %s as %s' % (__file__, __name__))

# Project imports
import modules.Config as Config                     # noqa e408

import modules.ansi_c.Signature as c_Sig            # noqa e408
import modules.ansi_c.CodeGeneration as c_CodeGen   # noqa e408
import modules.ansi_c.CodeScan as c_CodeScan        # noqa e408

import modules.python.Signature as py_Sig           # noqa e408
import modules.python.CodeGeneration as py_CodeGen  # noqa e408
import modules.python.CodeScan as py_CodeScan       # noqa e408

import modules.ErrorHandling as Error           # noqa e408
import modules.FileSupport as File              # noqa e408
import modules.UMLParse as Uml                  # noqa e408

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
logging.info('Start execution as: %s' % __name__)
if __name__ == '__main__':

    # instantiate configuration first to parse command line and configuration file
    config = Config.TheConfig()
    files = File.File()
    uml = Uml.UML()
    err = Error.Error()

    # =========================================================================
    # the big try for all of our processing
    try:
        # check for input files to process
        input_files = config.files
        num_files = len(input_files)
        if num_files == 0:
            logging.info('Nothing to do: no input files')
            exit()

        # display invocation information
        logging.debug('Begin execution: %s' % __name__)
        logging.debug('Processing %s input files' % num_files)

        # =====================================================================
        # process all input files
        for input_file in input_files:
            logging.debug('Input file: %s' % input_file)

            if files.file_type(input_file) is files.FileType.c:
                sig = c_Sig.Signature()
                scan = c_CodeScan.CodeScan()
                gen = c_CodeGen.CodeGen()
            elif files.file_type(input_file) is files.FileType.py:
                sig = py_Sig.Signature()
                scan = py_CodeScan.CodeScan()
                gen = py_CodeGen.CodeGen()
            else:
                err.file_type_error(input_file)

            # read source file into memory
            files.open(input_file)
            files.read()
            files.close()

            # scan for UML and parse
            # initialize UML module before parsing
            uml.init()
            if uml.find_start_plant_uml() is False:
                logging.debug('UML Start NOT FOUND: Ignoring')
                continue
            if uml.find_end_plant_uml() is False:
                logging.debug('UML End NOT FOUND: Ignoring')
                continue
            if uml.parse_plant_uml() is False:
                exit()

            # scan for StateEngineCrank signatures
            # Note:
            #    We either find ALL of the signatures or we find NONE of the signatures.
            #    If we only find SOME of the signatures then something is BROKEN.
            #    If the signatures are NOT found then we create them
            if sig.find_signatures() is False:
                sig.create_signatures()

            # Scan and create list of current user state functions
            scan.scan_code()

            # Signatures (now) exist so update code based on current UML
            gen.update_code()

            # Process files if any state machine changes were detected
            #    If the file changed then backup (rename) the original/
            #    And write the updated contents.
            if files.compare_files() is False:
                files.backup(input_file)
                files.update(input_file)

            uml.dump_uml()

    # =========================================================================
    except Error.UnimplementedCodeError as e:
        logging.critical('Unimplemented code encountered --> %s' % e)
    except Error.SourceFileError as e:
        logging.critical('Error processing source file --> %s' % e)
    except Error.UMLParseError as e:
        logging.critical('Error parsing UML --> %s' % e)
    except Error.SignatureError as e:
        logging.critical('Error processing signatures --> %s' % e)
    except Error.ScanCodeError as e:
        logging.critical('Error scanning user state functions --> %s' % e)
    except Error.UpdateCodeError as e:
        logging.critical('Error updating code --> %s' % e)
    except Error.FileBackupError as e:
        logging.critical('Error processing file updates --> %s' % e)
    except Error.FileWriteError as e:
        logging.critical('Error writing file --> %s' % e)
    except Error.ConfigFileError as e:
        logging.critical('Error processing configuration file ---> %s' % e)
    except Exception as e:
        logging.critical('Uncategorized error encountered')
        raise e     # re-raise to dump the specifics of this error
    finally:
        # =========================================================
        # exit processing and cleanup
        # =========================================================
        logging.info('Execution complete ... exiting ...')
        exit(0)
