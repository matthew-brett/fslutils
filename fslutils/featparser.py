""" Parser for FEAT designs
"""

import re

_DEF_RE = re.compile(
    r"""set \ (?P<top_name>[A-Za-z0-9_]+)
    \((?P<field>[A-Za-z0-9_]+)\)
    \ (?P<content>.*)""",
    re.VERBOSE)


def _to_bool(val):
    return bool(int(val))


_CONVERTERS = {
    'version': str,
    'inmelodic': _to_bool,
    'level': int,
    'npts': int,
    'ndelete': int,
    'analysis': int,
    'st': int,
    'smooth': float,
    'tr': float,
    'ncon_orig': int,
    'ncon_real': int,
    'nftests_orig': int,
    'nftests_real': int,
    'ncopeinputs': int,
    'paradigm_hp': int,
    'totalVoxels': int,
    'regstandard_nonlinear_warpres': int,
    'multiple': int,
}

_TOP_TYPES = {
    'fmri': dict,
    'feat_files': list,
    'initial_highres_files': list,
    'highres_files': list,
}


def _infer_converter(field_name):
    if field_name in _CONVERTERS:
        return _CONVERTERS[field_name]
    if field_name.endswith('_yn'):
        return _to_bool
    return str


def _process_line(line, out_dict):
    match = _DEF_RE.match(line)
    if match is None:
        return
    top_name, field_name, contents = match.groups()
    if (contents[0], contents[-1]) == ('"', '"'):
        contents = contents[1:-1]
    if top_name not in out_dict:
        out_dict[top_name] = _TOP_TYPES[top_name]()
    try:
        field_name = int(field_name) - 1
    except ValueError:
        contents = _infer_converter(field_name)(contents)
        out_dict[top_name][field_name] = contents
        return
    else:
        # List element
        assert len(out_dict[top_name]) == field_name
        out_dict[top_name].append(contents)


def fsf_to_dict(fsf):
    """ Parse FSF design file in string `fsf` to dictionary

    Parameters
    ----------
    fsf : str
        String containing contents of FSF design file.

    Returns
    -------
    fsf_dict : dict
        Dict containing contents of FSF file.
    """
    fsf_dict = {}
    for line in fsf.splitlines():
        _process_line(line, fsf_dict)
    return fsf_dict
