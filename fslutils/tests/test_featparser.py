""" Tests parsing of FEAT output files
"""

from os.path import join as pjoin, dirname
from glob import glob

import numpy as np

from fslutils.supporting import read_file
from fslutils.featparser import (fsf_to_dict, mat_to_dict, _infer_converter,
                                 _DEF_RE, _to_bool)


DATA_DIR = pjoin(dirname(__file__), 'data')


def test_def_re():
    assert (_DEF_RE.match('set fmri(sscleanup_yn) 0').groups()
            == ('fmri', 'sscleanup_yn', '0'))
    assert (_DEF_RE.match('set fmri(sscleanup_yn) 0').groups()
            == ('fmri', 'sscleanup_yn', '0'))
    assert (_DEF_RE.match(
        'set fmri(outputdir) '
        '"/home/people/brettmz/replication/feat/group/balloon"').groups()
        == ('fmri', 'outputdir',
            '"/home/people/brettmz/replication/feat/group/balloon"'))
    assert (_DEF_RE.match(
        'set feat_files(4) '
        '"/home/people/brettmz/replication/feat/1/balloon/sub-04_balloon.feat"'
    ).groups() == ('feat_files', '4',
        '"/home/people/brettmz/replication/feat/1/balloon/sub-04_balloon.feat"'))


def test__infer_converter():
    # Guessing from field names.
    assert _infer_converter('test_yn') == _to_bool
    # Default is string.
    assert _infer_converter('foo') == str
    # Known fields.
    assert _infer_converter('version') == str
    assert _infer_converter('inmelodic') == _to_bool
    assert _infer_converter('level') == int


def test_fsf_to_dict_all():
    for design_fname in glob(pjoin(DATA_DIR, '*.fsf')):
        design = fsf_to_dict(read_file(design_fname))
        assert set(design).issubset(['fmri', 'feat_files',
                                     'highres_files',
                                     'initial_highres_files'])
        assert design['fmri']['version'] == '6.00'


def test_fsf_to_dict_one_sess_group():
    # Specific tests.
    design = fsf_to_dict(read_file(pjoin(DATA_DIR, 'one_sess_group.fsf')))
    fmri, feat_files = design['fmri'], design['feat_files']
    assert fmri['inmelodic'] == False
    assert fmri['analysis'] == 2
    assert (fmri['outputdir'] ==
            "/home/people/brettmz/replication/feat/group/balloon")
    # Note conversion to 0-based indexing
    assert (feat_files[21] ==
            "/home/people/brettmz/replication/feat/1/balloon/sub-26_balloon.feat")
    # Group membership
    assert fmri['groupmem.4'] == 1
    # Contrasts
    assert fmri['con_real1.1'] == 1.0
    assert fmri['con_real1.2'] == 0.0
    assert fmri['evg18.2'] == -25.96


def test_mat_to_dict_all():
    for fname in glob(pjoin(DATA_DIR, '*.mat')):
        dmat = mat_to_dict(read_file(fname))
        assert set(dmat) == {'NumWaves', 'NumPoints', 'PPheights', 'Matrix'}
        assert dmat['Matrix'].shape == (dmat['NumPoints'], dmat['NumWaves'])
        assert len(dmat['PPheights']) == dmat['NumWaves']


def test_mat_to_dict_group():
    dmat = mat_to_dict(read_file(pjoin(DATA_DIR, 'one_sess_group.mat')))
    cov =[ -9.96,  27.04,  -6.96,   9.04,   7.04,  10.04,   3.04,   7.04,
          3.04,  12.04, -31.96,   0.04,  12.04,  16.04, -20.96,  19.04,
          10.04, -25.96,   5.04,  11.04, -35.96, -13.96, -17.96,  12.04]
    exp_x = np.ones((24, 2))
    exp_x[:, 1] = cov
    assert np.allclose(dmat['Matrix'], exp_x)
    assert np.allclose(dmat['PPheights'], [1, 63])


def test_mat_to_dict_level1():
    dmat = mat_to_dict(read_file(pjoin(DATA_DIR, 'one_sess_level1.mat')))
    assert dmat['Matrix'].shape == (222, 14)


def test_mat_to_dict_mid():
    dmat = mat_to_dict(read_file(pjoin(DATA_DIR, 'two_sess_mid.mat')))
    assert dmat['Matrix'].shape == (48, 24)
