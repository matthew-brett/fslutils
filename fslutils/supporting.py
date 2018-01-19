""" Functions for code support (including tests)
"""


class Bunch(object):
    """ Class to represent dictionary as object
    """
    def __init__(self, vars):
        """ Initialize Bunch

        Parameters
        ----------
        vars : object
            Object implementing `items` method - for example, a ``dict``.
        """
        for key, name in vars.items():
            if key.startswith('__'):
                continue
            self.__dict__[key] = name


def read_file(fname):
    """ Read file at `fname` as text, return `contents`

    Parameters
    ----------
    fname : str
        Filename.

    Returns
    -------
    contents : str
        Contents read from `fname`.
    """
    with open(fname, 'rt') as fobj:
        contents = fobj.read()
    return contents
