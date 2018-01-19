""" Class and functions to encapsulate FSF information
"""

from collections import OrderedDict

import numpy as np

from .supporting import Bunch, read_file
from .featparser import fsf_to_dict


def _after_dot(k):
    # Key sorter using number after last dot in string
    return int(k.split('.')[-1])


class FSF(object):
    """ Encapsulate FSF contents
    """

    def __init__(self, contents):
        self.contents = contents
        self._fsf_dict = fsf_to_dict(contents)
        self.attrs = Bunch(self._fsf_dict['fmri'])
        self.feat_files = self._fsf_dict['feat_files']

    @classmethod
    def from_string(cls, in_str):
        """ Initialize from string `in_str`, return as FSF object
        """
        return cls(in_str)

    @classmethod
    def from_file(cls, file_ish):
        """ Initialize from contents of `file_ish`, return as FSF object
        """
        return cls.from_string(read_file(file_ish))

    @property
    def n_contrasts(self):
        return len(self._dotted_vals('conname_real'))

    def _dotted_vals(self, prefix):
        fsfd = self._fsf_dict['fmri']
        keys = [k for k in fsfd if k.startswith(prefix + '.')]
        keys = sorted(keys, key=_after_dot)
        return [fsfd[k] for k in sorted(keys, key=_after_dot)]

    def _get_contrasts(self, suffix='real'):
        contrasts = OrderedDict()
        fsfd = self._fsf_dict['fmri']
        # May be no contrasts of this type (given by suffix)
        if not 'conname_{}.1'.format(suffix) in fsfd:
            return contrasts
        # 1-based indexing in FSF file
        for con_no in range(1, self.n_contrasts + 1):
            name = fsfd['conname_{}.{}'.format(suffix, con_no)]
            contrasts[name] = np.array(
                self._dotted_vals('con_{}{}'.format(suffix, con_no)))
        return contrasts

    @property
    def contrasts_real(self):
        return self._get_contrasts('real')

    @property
    def contrasts_orig(self):
        return self._get_contrasts('orig')

    @property
    def evgs(self):
        evgs = []
        # 1-based indexing in FSF file
        evg_no = 1
        while True:
            evg_vals = self._dotted_vals('evg{}'.format(evg_no))
            if len(evg_vals) == 0:
                break
            evgs.append(evg_vals)
            evg_no += 1
        return np.array(evgs)

    @property
    def groupmem(self):
        return np.array(self._dotted_vals('groupmem'))


load = FSF.from_file

loads = FSF.from_string
