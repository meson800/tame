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

    if filename is None:
        rel_filename = 'INLINE_YAML'
    else:
        rel_filename = Path(filename).resolve().relative_to(Path.cwd())

    for line in error_str.split('\n'):
        match = re.search('line (\\d+), column (\\d+)', line)
        print(line)
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
    return ('YAML parse ' + Fore.RED + 'error:' + Style.RESET_ALL
            + accum_error + '\n in file {}, {}:'.format(rel_filename, location)
            + accum_context)
