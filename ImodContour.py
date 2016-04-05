from __future__ import absolute_import
from __future__ import print_function
import struct
import six

class ImodContour(object):

    def __init__(self,
        fid = None,
        nPoints = 0,
        flags = 0,
        type = 0,
        iSurface = 0,
        points = [],
        pointSizes = [],
        **kwargs):
            self.__dict__.update(kwargs)
            self.__dict__.update(locals())
            if self.fid:
                self.read_file()    

    def read_file(self):
        fid = self.fid
        self.nPoints = struct.unpack('>l', fid.read(4))[0]
        self.flags = struct.unpack('>l', fid.read(4))[0]
        self.type = struct.unpack('>l', fid.read(4))[0]
        self.iSurface = struct.unpack('>l', fid.read(4))[0]
        self.points = struct.unpack('>{0}f'.format(3 * self.nPoints),
            fid.read(12 * self.nPoints))
        return self

    def dump(self):
        from collections import OrderedDict as od
        for key, value in six.iteritems(od(sorted(self.__dict__.items()))):
            print(key, value)
        print("\n")

