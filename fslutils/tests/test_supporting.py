""" Test supporting module
"""

from fslutils.supporting import Bunch, read_file


def test_read_file():
    with open(__file__, 'rt') as fobj:
        contents = fobj.read()
    assert contents == read_file(__file__)


def test_bunch():
    foo = dict(foo=1, bar=2, baz=3)
    bfoo = Bunch(foo)
    assert bfoo.foo == 1
    assert bfoo.bar == 2
    assert bfoo.baz == 3
