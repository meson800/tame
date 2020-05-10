def touch(filename):
    """Creates the desired file by writing a newline"""
    with open(str(filename), 'w') as f:
        f.write('\n')
