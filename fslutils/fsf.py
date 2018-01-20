""" Class and functions to encapsulate FSF information
"""

from collections import OrderedDict
import re

import numpy as np

from .supporting import Bunch, read_file
from .featparser import fsf_to_dict


END_NO = re.compile(r'(\d+)$')

def _end_number(k):
    # Key sorter using number at end of string
    return int(END_NO.search(k).groups()[0])


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

    def _numbered_vals(self, prefix):
        fsfd = self._fsf_dict['fmri']
        keys = [k for k in fsfd if k.startswith(prefix)]
        return [fsfd[k] for k in sorted(keys, key=_end_number)]

    def _get_contrasts(self, suffix='real'):
        contrasts = OrderedDict()
        fsfd = self._fsf_dict['fmri']
        # May be no contrasts of this type (given by suffix)
        names = self._numbered_vals('conname_{}.'.format(suffix))
        if not 'conname_{}.1'.format(suffix) in fsfd:
            return contrasts
        for i, name in enumerate(names):
            contrasts[name] = np.array(
                # 1-based indexing in FSF file
                self._numbered_vals('con_{}{}.'.format(suffix, i + 1)))
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
            evg_vals = self._numbered_vals('evg{}.'.format(evg_no))
            if len(evg_vals) == 0:
                break
            evgs.append(evg_vals)
            evg_no += 1
        return np.array(evgs)

    @property
    def n_events(self):
        return len(self._numbered_vals('conname_real.'))

    @property
    def events(self):
        events = OrderedDict()
        fsfd = self._fsf_dict['fmri']
        names = self._numbered_vals('evtitle')
        for i, name in enumerate(names):
            ev_no = str(i + 1)
            event = {}
            for key_root in ('shape',
                             'convolve',
                             'convolve_phase',
                             'tempfilt_yn',
                             'deriv_yn',
                             'custom'):
                event[key_root] = fsfd.get(key_root + ev_no)
            events[name] = event
        return events

    @property
    def groupmem(self):
        return np.array(self._numbered_vals('groupmem.'))


load = FSF.from_file

loads = FSF.from_string
