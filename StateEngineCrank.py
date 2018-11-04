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

import modules.CodeGeneration as CodeGen    # noqa e408
import modules.CodeScan as CodeScan         # noqa e408
import modules.Config as Config             # noqa e408
import modules.DebugSupport as Debug        # noqa e408
import modules.ErrorHandling as Error       # noqa e408
import modules.FileSupport as File          # noqa e408
import modules.Signature as Sig             # noqa e408
import modules.UMLParse as Uml              # noqa e408

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

    codegen = CodeGen.CodeGen()
    codescan = CodeScan.CodeScan()
    debug = Debug.Debug()
    files = File.File()
    config = Config.TheConfig()
    sig = Sig.Signature()
    uml = Uml.UML()

    # =========================================================================
    # the big try for all of our processing
    try:
        # check for input files to process
        input_files = config.files
        num_files = len(input_files)
        if num_files == 0:
            print('Nothing to do: no input files')
            exit()

        # display invocation information
        debug.dprint(('Begin execution:', __name__))
        debug.dprint(('Processing', num_files, 'input files.'))

        # =====================================================================
        # process all input files
        for input_file in input_files:
            debug.vprint(('Input file:', input_file))

            # read source file into memory
            files.open(input_file)
            files.read()
            files.close()

            # scan for UML and parse
            # initialize UML module before parsing
            uml.init()
            if uml.find_start_plant_uml() is False:
                debug.dvprint(('UML Start NOT FOUND', 'Ignoring'))
                continue
            if uml.find_end_plant_uml() is False:
                debug.dvprint(('UML End NOT FOUND', 'Ignoring'))
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
            codescan.scan_code()

            # Signatures (now) exist so update code based on current UML
            codegen.update_code()

            # Process files if any state machine changes were detected
            #    If the file changed then backup (rename) the original/
            #    And write the updated contents.
            if files.compare_files() is False:
                files.backup(input_file)
                files.update(input_file)

    # =========================================================================
    except Error.UnimplementedCodeError as e:
        print('Unimplemented code encountered -->', e)
    except Error.SourceFileError as e:
        print('Error processing source file -->', e)
    except Error.UMLParseError as e:
        print('Error parsing UML -->', e)
    except Error.SignatureError as e:
        print('Error processing signatures -->', e)
    except Error.ScanCodeError as e:
        print('Error scanning user state functions -->', e)
    except Error.UpdateCodeError as e:
        print('Error updating code -->', e)
    except Error.FileBackupError as e:
        print('Error processing file updates -->', e)
    except Error.FileWriteError as e:
        print('Error writing file -->', e)
    except Error.ConfigFileError as e:
        print('Error processing configuration file --->', e)
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
