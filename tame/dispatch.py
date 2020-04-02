from yaml import Loader
import argparse
import sys
import pkg_resources

parser = argparse.ArgumentParser(description='A metadata system for humans')
parser.add_argument('--version', action='version',
        version='tame v' + pkg_resources.require('tame')[0].version)
subparsers = parser.add_subparsers(dest='subcommand', metavar='<command>')
subparsers.add_parser('validate')

extended_help_message = '''

These are common Tame commands:

    validate    Check YAML metadata syntax and ensure
                that required files are present.
    describe
    collect
    freeze'''

def dispatch_console():
    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
        print(extended_help_message)
        exit()
