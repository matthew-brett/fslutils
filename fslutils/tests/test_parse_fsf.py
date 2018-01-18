""" Tests parsing of fsf files
"""

from os.path import join as pjoin, dirname
from glob import glob

from fslutils.featparser import (fsf_to_dict, _infer_converter, _DEF_RE,
                                 _to_bool)


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


def read_file(fname):
    with open(fname, 'rt') as fobj:
        contents = fobj.read()
    return contents


def test_fsf_to_dict():
    for design_fname in glob(pjoin(DATA_DIR, '*.fsf')):
        design = fsf_to_dict(read_file(design_fname))
        assert set(design).issubset(['fmri', 'feat_files',
                                     'highres_files',
                                     'initial_highres_files'])
        assert design['fmri']['version'] == '6.00'
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
