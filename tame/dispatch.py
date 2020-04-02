import argparse
import sys
import pkg_resources
from . import validate, core

parser = argparse.ArgumentParser(description='A metadata system for humans')
parser.add_argument('--version', action='version',
        version='tame v' + pkg_resources.require('tame')[0].version)
subparsers = parser.add_subparsers(dest='subcommand', metavar='<command>')
validate_subparser = subparsers.add_parser('validate')
validate._init_argparse_(validate_subparser)

extended_help_message = '''

These are common Tame commands:

    validate    Check YAML metadata syntax and ensure
                that required files are present.
    describe
    collect
    freeze'''

no_root_message = """\
No root 'tame.yaml' file found. This is needed for metadata tracking!

If you did want to track metadata, add a (possibly empty) tame.yaml
file to the most top-level directory from which you want to track.
"""

def dispatch_console():
    args = parser.parse_args()
    
    try:
        if args.subcommand == 'validate':
            validate._dispatch_validate_(args)
        else:
            parser.print_help()
            print(extended_help_message)
            exit()
    except core.UntrackedRepositoryError:
        print(no_root_message)
        exit()

