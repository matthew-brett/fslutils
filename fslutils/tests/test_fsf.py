""" Test FSF object
"""

from os.path import join as pjoin, dirname
from glob import glob
from collections import OrderedDict

import numpy as np
from numpy.testing import assert_array_equal

from fslutils.supporting import read_file
from fslutils.fsf import (FSF, load, loads)


DATA_DIR = pjoin(dirname(__file__), 'data')
SUB_NOS = np.loadtxt(pjoin(DATA_DIR, 'subject_nos.txt'), int)


def test_fsf_all():
    for design_fname in glob(pjoin(DATA_DIR, '*.fsf')):
        contents = read_file(design_fname)
        for fsf in (FSF(contents),
                    FSF.from_string(contents),
                    loads(contents),
                    FSF.from_file(design_fname),
                    load(design_fname),
                   ):
            assert fsf.attrs.version == '6.00'
            assert fsf.n_contrasts > 0
            assert isinstance(fsf.contrasts, OrderedDict)
            assert isinstance(fsf.groupmem, np.ndarray)
            assert isinstance(fsf.evgs, np.ndarray)


def test_fsf_one_sess_group(bart_pumps):
    # Specific tests.
    fsf = load(pjoin(DATA_DIR, 'one_sess_group.fsf'))
    assert fsf.n_contrasts == 1
    assert list(fsf.contrasts) == ['Group mean']
    assert_array_equal(fsf.contrasts['Group mean'], [1, 0])
    assert_array_equal(fsf.groupmem, [1] * 24)
    exp_evgs = np.ones((24, 2))
    exp_evgs[:, 1] = bart_pumps
    assert_array_equal(fsf.evgs, exp_evgs)


def test_fsf_level1():
    fsf = load(pjoin(DATA_DIR, 'one_sess_level1.fsf'))
    assert fsf.n_contrasts == 1
    assert list(fsf.contrasts) == ['Cash-Inflate']
    assert_array_equal(fsf.contrasts['Cash-Inflate'], [-1, 0, 0, 0, 1, 0, 0, 0])
    assert_array_equal(fsf.groupmem, [])
    assert_array_equal(fsf.evgs, [])
    assert fsf.attrs.tr == 2


def test_fsf_mid(sub_nos):
    fsf = load(pjoin(DATA_DIR, 'two_sess_mid.fsf'))
    assert fsf.n_contrasts == 24
    assert list(fsf.contrasts) == ['sub-{:02d}'.format(s) for s in sub_nos]
    for contrast, exp_contrast in zip(fsf.contrasts.values(), np.eye(24)):
        assert_array_equal(contrast, exp_contrast)
    assert_array_equal(fsf.groupmem, [1] * 48)
    assert_array_equal(fsf.evgs, np.kron(np.eye(24), np.ones((2, 1))))
