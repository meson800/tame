"""
Formats exceptions with additional information, such as
Clang-style formatting that shows the specific characters
that cause problems.

Available under the MIT license.
Copyright (c) 2020 Christopher Johnstone
"""
from pathlib import Path
import re
from colorama import Fore, Style

def simplify_filename(filename=None):
    """
    Given a filename, normalizes it relative
    to the current working directory.

    Args:
    -----
    filename: (optional) A string describing the source filename.

    Returns:
    --------
    If filename is unspecified, returns 'INLINE_YAML'.
    If the filename is specified, it is resolved and transformed
    into a relative path relative to the current working directory.
    """
    if filename is None:
        return 'INLINE_YAML'
    try:
        return str(Path(filename).resolve().relative_to(Path.cwd()))
    except ValueError:
        pass
    return str(Path(filename).resolve())


def format_yaml_error(yaml_source, error_str, filename=None):
    """
    Given the YAML source document and a
    YAML scanner error, highlights the error
    location.

    Args:
    -----
    yaml_source: A string encoding the entire YAML document.
    error_str: A ScannerError reported by the YAML parser.
    filename: (optional) A string listing the filename of the
        loaded YAML source.

    Returns:
    --------
    A string encoding the pretty-printed error.
    """
    accum_error = ''
    accum_context = ''
    building_context = False
    location = ''

    rel_filename = simplify_filename(filename)

    for line in error_str.split('\n'):
        match = re.search('line (\\d+), column (\\d+)', line)
        if match is not None:
            location = match.group(0)
            building_context = True
            continue
        if building_context:
            accum_context += '\n'
            accum_context += line
        else:
            accum_error += ' '
            accum_error += line
    return (Style.BRIGHT + Fore.RED + 'YAML parse error:' + Style.RESET_ALL
            + accum_error + '\n in file {}, {}:'.format(rel_filename, location)
            + accum_context.replace('^', Style.BRIGHT +
                                    Fore.RED + '^' + Style.RESET_ALL))

def format_parent_error(parent_locator, error_str, filename=None):
    """
    Given a parent locator and the error message, gives a pretty-
    printed version of the error message, identifying the problem
    region.

    Args:
    -----
    parent_locator: A parent identifier for the unidentified metadata file.
    error_str: The string describing the exception.
    filename: (optional) A string listing the filename of the loaded YAML.
    """
    rel_filename = simplify_filename(filename)

    return (Style.BRIGHT + Fore.RED
            + 'Parent lookup error:' + Style.RESET_ALL
            + '\n in file {}, parent locator {}\n'.format(rel_filename,
                                                          parent_locator)
            + error_str)
