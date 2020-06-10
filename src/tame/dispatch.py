"""
Handles parsing command line arguments in order
to call internal API functions.

Available under the MIT license.
Copyright (c) 2020 Christopher Johnstone
"""
import argparse
import sys
import colorama
import pkg_resources
from . import validate, core


EXTENDED_HELP_MESSAGE = '''

These are common Tame commands:

    validate    Check YAML metadata syntax and ensure
                that required files are present.
    describe
    collect
    freeze'''

NO_ROOT_MESSAGE = """\
No root 'tame.yaml' file found. This is needed for metadata tracking!

If you did want to track metadata, add a (possibly empty) tame.yaml
file to the most top-level directory from which you want to track.
"""


def dispatch_console():
    """
    Entry point called when 'tame' is run.
    Reads the command line args and decides what submodule
    that should be called.
    """
    colorama.init()
    parser = argparse.ArgumentParser(description='A metadata system for humans')
    parser.add_argument('--version', action='version', version='tame v'
                        + pkg_resources.require('tame')[0].version)
    subparsers = parser.add_subparsers(dest='subcommand', metavar='<command>')
    validate_subparser = subparsers.add_parser('validate')
    validate._init_argparse_(validate_subparser)  # pylint: disable=protected-access

    args = parser.parse_args()

    try:
        if args.subcommand == 'validate':
            validate._dispatch_validate_(args)  # pylint: disable=protected-access
        else:
            parser.print_help()
            print(EXTENDED_HELP_MESSAGE)
            sys.exit()
    except core.UntrackedRepositoryError:
        print(NO_ROOT_MESSAGE)
        sys.exit()
