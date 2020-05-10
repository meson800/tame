def touch(filename):
    """Creates the desired file by writing a newline"""
    with open(filename, 'w') as f:
        f.write('\n')
