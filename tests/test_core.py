"""Unittests for `gpsdio.core`"""


import itertools
import gzip
import tempfile
import unittest

import newlinejson as nlj
import six

from . import compare_msg
import gpsdio
import gpsdio.schema
import gpsdio.drivers
from .sample_files import TYPES_MSG_FILE
from .sample_files import TYPES_MSG_GZ_FILE
from .sample_files import TYPES_JSON_FILE
from .sample_files import TYPES_JSON_GZ_FILE


VALID_ROWS = [
    {'type': 5, 'shipname': 'fishy fishy', 'shiptype': 1},
    {'type': 5, 'shipname': 'fishy fishy', 'shiptype': 2},
    {'type': 5, 'shipname': 'fishy fishy', 'shiptype': 3},
    {'type': 5, 'shipname': 'fishy fishy', 'shiptype': 4}
]

INVALID_ROWS = [
    {'type': 1, 'timestamp': 'morning'},
    {'type': 1, 'timestamp': 'late'}
]


class TestOpen(unittest.TestCase):

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile(mode='r+')

    def tearDown(self):
        self.tempfile.close()

    def test_standard(self):

        with gpsdio.open(TYPES_MSG_FILE) as fp_msg, \
                gpsdio.open(TYPES_MSG_GZ_FILE) as fp_msg_gz, \
                gpsdio.open(TYPES_JSON_FILE) as fp_json, \
                gpsdio.open(TYPES_JSON_GZ_FILE) as fp_json_gz:

            for lines in zip(fp_msg, fp_msg_gz, fp_json, fp_json_gz):
                for pair in itertools.combinations(lines, 2):
                    self.assertTrue(compare_msg(*pair))

    def test_wrong_extension(self):

        with open(TYPES_MSG_FILE) as src:
            self.tempfile.write(src.read())
        self.tempfile.seek(0)

        with gpsdio.open(self.tempfile.name, driver='MsgPack') as actual, \
                gpsdio.open(TYPES_MSG_FILE) as expected:
            for e_line, a_line in zip(expected, actual):
                self.assertDictEqual(e_line, a_line)

        with tempfile.NamedTemporaryFile(mode='r+') as tfile:
            with open(TYPES_MSG_GZ_FILE) as src:
                tfile.write(src.read())
            tfile.seek(0)

            with gpsdio.open(tfile.name, driver='MsgPack', compression='GZIP') as actual, \
                    gpsdio.open(TYPES_MSG_GZ_FILE) as expected:
                for e_line, a_line in zip(expected, actual):
                    self.assertDictEqual(e_line, a_line)

    def test_no_detect_compression(self):

        with gpsdio.open(TYPES_MSG_FILE, compression=False) as actual, \
                gpsdio.open(TYPES_MSG_FILE) as expected:
            for e_line, a_line in zip(expected, actual):
                self.assertDictEqual(e_line, a_line)


class TestStream(unittest.TestCase):

    def setUp(self):
        self.tempfile = tempfile.NamedTemporaryFile(mode='r+')

    def tearDown(self):
        self.tempfile.close()

    def test_default_mode_is_read(self):
        with gpsdio.open(TYPES_MSG_FILE) as stream:
            self.assertEqual(stream.mode, 'r')

    def test_attrs(self):
        with gpsdio.open(TYPES_MSG_FILE) as stream:
            self.assertIsInstance(stream.__repr__(), six.string_types)
            self.assertTrue(hasattr(stream, '__next__'))

    def test_io_on_closed_stream(self):
        for mode in ('r', 'w', 'a'):
            with gpsdio.open(self.tempfile.name, mode=mode, driver='NewlineJSON') as stream:
                stream.close()
                self.assertTrue(stream.closed)
                with self.assertRaises(IOError):
                    next(stream)
                with self.assertRaises(IOError):
                    stream.write(None)

    def test_read_from_write_stream(self):
        with gpsdio.open(TYPES_MSG_GZ_FILE) as src, \
                gpsdio.open(self.tempfile.name, 'w', driver='NewlineJSON') as dst:
            for msg in src:
                dst.write(msg)
            with self.assertRaises(IOError):
                next(dst)


def test_get_driver():

    for d in [_d for _d in gpsdio.drivers._BaseDriver.by_name.values()]:
        rd = gpsdio.drivers.get_driver(d.driver_name)
        assert rd == d, "%r != %r" % (d, rd)
    try:
        gpsdio.drivers.get_driver('__---Invalid---__')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_get_compression():

    for c in [_d for _d in gpsdio.drivers._BaseDriver.by_name if getattr(_d, 'compresion', False)]:
        cd = gpsdio.drivers.get_compression(c.name)
        assert cd == c, "%r != %r" % (c, cd)
    try:
        gpsdio.drivers.get_compression('__---Invalid---__')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_detect_file_type():

    for d in [_d for _d in gpsdio.drivers._BaseDriver.by_name if getattr(_d, 'compresion', False)]:
        for ext in d.extensions:
            rd = gpsdio.drivers.detect_file_type('path.%s.ext' % ext)
            assert d == rd, "%r != %r" % (d, rd)
    try:
        gpsdio.drivers.detect_file_type('__---Invalid---__.ext.ext2')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_detect_compression_type():

    for c in [_d for _d in gpsdio.drivers._BaseDriver.by_name if getattr(_d, 'compresion', False)]:
        print(c)
        print(c.extensions)
        for ext in c.extensions:
            cd = gpsdio.drivers.detect_compression_type(('path.something.%s' % ext))
            assert c == cd, "%r != %r" % (c, cd)
    try:
        gpsdio.drivers.get_compression('__---Invalid---__.ext.ext2')
        raise TypeError("Above line should have raised a ValueError.")
    except ValueError:
        pass


def test_filter():

    # Pass all through unaltered
    with gpsdio.open(TYPES_MSG_GZ_FILE) as actual, gpsdio.open(TYPES_MSG_GZ_FILE) as expected:
        for a, e in zip(gpsdio.filter("isinstance(mmsi, int)", actual), expected):
            assert a == e

    # Extract only types 1, 2, and 3
    passed = []
    with gpsdio.open(TYPES_MSG_GZ_FILE) as stream:
        for msg in gpsdio.filter("type in (1,2,3)", stream):
            passed.append(msg)
            assert msg['type'] in (1, 2, 3)
    assert len(passed) >= 3

    # Filter out everything
    with gpsdio.open(TYPES_MSG_GZ_FILE) as stream:
        for msg in gpsdio.filter(("type is 5", "mmsi is -1000"), stream):
            assert False, "Above loop should not have executed because the filter should " \
                          "not have yielded anything."

    # Multiple expressions
    passed = []
    with gpsdio.open(TYPES_MSG_GZ_FILE) as stream:
        for msg in gpsdio.filter(
                ("status == 'Under way using engine'", "mmsi is 366268061"), stream):
            passed.append(msg)
            assert msg['mmsi'] is 366268061

    # Reference the entire message
    passed = []
    with gpsdio.open(TYPES_JSON_GZ_FILE) as stream:
        for msg in gpsdio.filter(("isinstance(msg, dict)", "'lat' in msg"), stream):
            passed.append(msg)
            assert 'lat' in msg
    assert len(passed) >= 9

    # Multiple complex filters
    criteria = ("turn is 0 and second is 0", "mmsi == 366268061", "'lat' in msg")
    with gpsdio.open(TYPES_JSON_GZ_FILE) as stream:
        passed = [m for m in gpsdio.filter(criteria, stream)]
        assert len(passed) >= 1


def test_mode_passed_to_driver(tmpdir):
    outfile = str(tmpdir.mkdir('out').join('outfile.msg.gz'))
    with gpsdio.open(outfile, 'w') as dst:
        assert dst._stream.mode == dst.mode == 'w'


def test_io_open_file_pointer():
    # msg gz
    with gzip.open(TYPES_MSG_GZ_FILE) as gz, \
            gpsdio.open(gz, driver='MsgPack', compression='GZIP') as actual, \
            gpsdio.open(TYPES_JSON_GZ_FILE) as expected:
        for e, a in zip(expected, actual):
            assert e == a
    # json gz
    with gzip.open(TYPES_JSON_GZ_FILE) as gz, \
            gpsdio.open(gz, driver='NewlineJSON', compression='GZIP') as actual, \
            gpsdio.open(TYPES_JSON_GZ_FILE) as expected:
        for e, a in zip(expected, actual):
            assert e == a
    # json fully opened
    with nlj.open(TYPES_JSON_FILE) as f, gpsdio.open(f, driver='NewlineJSON') as actual, \
            gpsdio.open(TYPES_JSON_FILE) as expected:
        for e, a in zip(expected, actual):
            assert e == a


# class TestBaseDriver(unittest.TestCase):
#
#     def test_attrs(self):
#         self.assertTrue(hasattr(gpsdio.drivers._BaseDriver, '__next__'))
#
#     def test_driver_context_manager(self):
#         with tempfile.NamedTemporaryFile(mode='r') as tfile:
#             with gpsdio.drivers.NewlineJSON(tfile, mode='r'):
#                 pass
#
#     def test_invalid_mode(self):
#         with self.assertRaises(ValueError):
#             gpsdio.drivers.FileDriver(None, mode='invalid')
#
#     def test_instantiated_properties(self):
#         modes = ('r', 'w', 'a')
#         name = 'drivername'
#         bd = gpsdio.drivers._BaseDriver(None, mode='r', modes=modes, name=name, reader=lambda x: x)
#         self.assertEqual(bd.modes, modes)
#         self.assertEqual(bd.name, name)
