# -*- coding: utf-8 -*-
#
#  SelfTest/Hash/HMAC.py: Self-test for the HMAC module
#
# Written in 2008 by Dwayne C. Litzenberger <dlitz@dlitz.net>
#
# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# No rights are reserved.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ===================================================================

"""Self-test suite for Crypto.Hash.HMAC"""


import sys
import unittest
from binascii import hexlify
from Crypto.Util.py3compat import _memoryview, tostr, tobytes

from Crypto.Hash import HMAC, MD5, SHA1, SHA256
hash_modules = dict(MD5=MD5, SHA1=SHA1, SHA256=SHA256)

try:
    from Crypto.Hash import SHA224, SHA384, SHA512, RIPEMD160
    hash_modules |= dict(
        SHA224=SHA224, SHA384=SHA384, SHA512=SHA512, RIPEMD160=RIPEMD160
    )

except ImportError:
    sys.stderr.write("SelfTest: warning: not testing HMAC-SHA224/384/512"
                     " (not available)\n")

default_hash = None

def xl(text):
    return tostr(hexlify(tobytes(text)))

# This is a list of (key, data, results, description) tuples.
test_data = [
    ## Test vectors from RFC 2202 ##
    # Test that the default hashmod is MD5
    ('0b' * 16,
        '4869205468657265',
        dict(default_hash='9294727a3638bb1c13f48ef8158bfc9d'),
        'default-is-MD5'),

    # Test case 1 (MD5)
    ('0b' * 16,
        '4869205468657265',
        dict(MD5='9294727a3638bb1c13f48ef8158bfc9d'),
        'RFC 2202 #1-MD5 (HMAC-MD5)'),

    # Test case 1 (SHA1)
    ('0b' * 20,
        '4869205468657265',
        dict(SHA1='b617318655057264e28bc0b6fb378c8ef146be00'),
        'RFC 2202 #1-SHA1 (HMAC-SHA1)'),

    # Test case 2
    ('4a656665',
        '7768617420646f2079612077616e7420666f72206e6f7468696e673f',
        dict(MD5='750c783e6ab0b503eaa86e310a5db738',
            SHA1='effcdf6ae5eb2fa2d27416d5f184df9c259a7c79'),
        'RFC 2202 #2 (HMAC-MD5/SHA1)'),

    # Test case 3 (MD5)
    ('aa' * 16,
        'dd' * 50,
        dict(MD5='56be34521d144c88dbb8c733f0e8b3f6'),
        'RFC 2202 #3-MD5 (HMAC-MD5)'),

    # Test case 3 (SHA1)
    ('aa' * 20,
        'dd' * 50,
        dict(SHA1='125d7342b9ac11cd91a39af48aa17b4f63f175d3'),
        'RFC 2202 #3-SHA1 (HMAC-SHA1)'),

    # Test case 4
    ('0102030405060708090a0b0c0d0e0f10111213141516171819',
        'cd' * 50,
        dict(MD5='697eaf0aca3a3aea3a75164746ffaa79',
            SHA1='4c9007f4026250c6bc8414f9bf50c86c2d7235da'),
        'RFC 2202 #4 (HMAC-MD5/SHA1)'),

    # Test case 5 (MD5)
    ('0c' * 16,
        '546573742057697468205472756e636174696f6e',
        dict(MD5='56461ef2342edc00f9bab995690efd4c'),
        'RFC 2202 #5-MD5 (HMAC-MD5)'),

    # Test case 5 (SHA1)
    # NB: We do not implement hash truncation, so we only test the full hash here.
    ('0c' * 20,
        '546573742057697468205472756e636174696f6e',
        dict(SHA1='4c1a03424b55e07fe7f27be1d58bb9324a9a5a04'),
        'RFC 2202 #5-SHA1 (HMAC-SHA1)'),

    # Test case 6
    ('aa' * 80,
        '54657374205573696e67204c6172676572205468616e20426c6f636b2d53697a'
        + '65204b6579202d2048617368204b6579204669727374',
        dict(MD5='6b1ab7fe4bd7bf8f0b62e6ce61b9d0cd',
            SHA1='aa4ae5e15272d00e95705637ce8a3b55ed402112'),
        'RFC 2202 #6 (HMAC-MD5/SHA1)'),

    # Test case 7
    ('aa' * 80,
        '54657374205573696e67204c6172676572205468616e20426c6f636b2d53697a'
        + '65204b657920616e64204c6172676572205468616e204f6e6520426c6f636b2d'
        + '53697a652044617461',
        dict(MD5='6f630fad67cda0ee1fb1f562db3aa53e',
            SHA1='e8e99d0f45237d786d6bbaa7965c7808bbff1a91'),
        'RFC 2202 #7 (HMAC-MD5/SHA1)'),

    ## Test vectors from RFC 4231 ##
    # 4.2. Test Case 1
    ('0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b',
        '4869205468657265',
        dict(SHA256='''
            b0344c61d8db38535ca8afceaf0bf12b
            881dc200c9833da726e9376c2e32cff7
        '''),
        'RFC 4231 #1 (HMAC-SHA256)'),

    # 4.3. Test Case 2 - Test with a key shorter than the length of the HMAC
    # output.
    ('4a656665',
        '7768617420646f2079612077616e7420666f72206e6f7468696e673f',
        dict(SHA256='''
            5bdcc146bf60754e6a042426089575c7
            5a003f089d2739839dec58b964ec3843
        '''),
        'RFC 4231 #2 (HMAC-SHA256)'),

    # 4.4. Test Case 3 - Test with a combined length of key and data that is
    # larger than 64 bytes (= block-size of SHA-224 and SHA-256).
    ('aa' * 20,
        'dd' * 50,
        dict(SHA256='''
            773ea91e36800e46854db8ebd09181a7
            2959098b3ef8c122d9635514ced565fe
        '''),
        'RFC 4231 #3 (HMAC-SHA256)'),

    # 4.5. Test Case 4 - Test with a combined length of key and data that is
    # larger than 64 bytes (= block-size of SHA-224 and SHA-256).
    ('0102030405060708090a0b0c0d0e0f10111213141516171819',
        'cd' * 50,
        dict(SHA256='''
            82558a389a443c0ea4cc819899f2083a
            85f0faa3e578f8077a2e3ff46729665b
        '''),
        'RFC 4231 #4 (HMAC-SHA256)'),

    # 4.6. Test Case 5 - Test with a truncation of output to 128 bits.
    #
    # Not included because we do not implement hash truncation.
    #

    # 4.7. Test Case 6 - Test with a key larger than 128 bytes (= block-size of
    # SHA-384 and SHA-512).
    ('aa' * 131,
        '54657374205573696e67204c6172676572205468616e20426c6f636b2d53697a'
        + '65204b6579202d2048617368204b6579204669727374',
        dict(SHA256='''
            60e431591ee0b67f0d8a26aacbf5b77f
            8e0bc6213728c5140546040f0ee37f54
        '''),
        'RFC 4231 #6 (HMAC-SHA256)'),

    # 4.8. Test Case 7 - Test with a key and data that is larger than 128 bytes
    # (= block-size of SHA-384 and SHA-512).
    ('aa' * 131,
        '5468697320697320612074657374207573696e672061206c6172676572207468'
        + '616e20626c6f636b2d73697a65206b657920616e642061206c61726765722074'
        + '68616e20626c6f636b2d73697a6520646174612e20546865206b6579206e6565'
        + '647320746f20626520686173686564206265666f7265206265696e6720757365'
        + '642062792074686520484d414320616c676f726974686d2e',
        dict(SHA256='''
            9b09ffa71b942fcb27635fbcd5b0e944
            bfdc63644f0713938a7f51535c3a35e2
        '''),
        'RFC 4231 #7 (HMAC-SHA256)'),

    # Test case 8 (SHA224)
    ('4a656665',
        '7768617420646f2079612077616e74'
        + '20666f72206e6f7468696e673f',
        dict(SHA224='a30e01098bc6dbbf45690f3a7e9e6d0f8bbea2a39e6148008fd05e44'),
        'RFC 4634 8.4 SHA224 (HMAC-SHA224)'),

    # Test case 9 (SHA384)
    ('4a656665',
        '7768617420646f2079612077616e74'
        + '20666f72206e6f7468696e673f',
        dict(SHA384='af45d2e376484031617f78d2b58a6b1b9c7ef464f5a01b47e42ec3736322445e8e2240ca5e69e2c78b3239ecfab21649'),
        'RFC 4634 8.4 SHA384 (HMAC-SHA384)'),

   # Test case 10 (SHA512)
    ('4a656665',
        '7768617420646f2079612077616e74'
        + '20666f72206e6f7468696e673f',
        dict(SHA512='164b7a7bfcf819e2e395fbe73b56e0a387bd64222e831fd610270cd7ea2505549758bf75c05a994a6d034f65f8f0e6fdcaeab1a34d4a6b4b636e070a38bce737'),
        'RFC 4634 8.4 SHA512 (HMAC-SHA512)'),

    # Test case 11 (RIPEMD)
    ('0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b',
     xl("Hi There"),
     dict(RIPEMD160='24cb4bd67d20fc1a5d2ed7732dcc39377f0a5668'),
     'RFC 2286 #1 (HMAC-RIPEMD)'),

    # Test case 12 (RIPEMD)
    (xl("Jefe"),
     xl("what do ya want for nothing?"),
     dict(RIPEMD160='dda6c0213a485a9e24f4742064a7f033b43c4069'),
     'RFC 2286 #2 (HMAC-RIPEMD)'),

    # Test case 13 (RIPEMD)
    ('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
     'dd' * 50,
     dict(RIPEMD160='b0b105360de759960ab4f35298e116e295d8e7c1'),
     'RFC 2286 #3 (HMAC-RIPEMD)'),

    # Test case 14 (RIPEMD)
    ('0102030405060708090a0b0c0d0e0f10111213141516171819',
     'cd' * 50,
     dict(RIPEMD160='d5ca862f4d21d5e610e18b4cf1beb97a4365ecf4'),
     'RFC 2286 #4 (HMAC-RIPEMD)'),

    # Test case 15 (RIPEMD)
    ('0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c0c',
     xl("Test With Truncation"),
     dict(RIPEMD160='7619693978f91d90539ae786500ff3d8e0518e39'),
     'RFC 2286 #5 (HMAC-RIPEMD)'),

    # Test case 16 (RIPEMD)
    ('aa' * 80,
     xl("Test Using Larger Than Block-Size Key - Hash Key First"),
     dict(RIPEMD160='6466ca07ac5eac29e1bd523e5ada7605b791fd8b'),
     'RFC 2286 #6 (HMAC-RIPEMD)'),

    # Test case 17 (RIPEMD)
    ('aa' * 80,
     xl("Test Using Larger Than Block-Size Key and Larger Than One Block-Size Data"),
     dict(RIPEMD160='69ea60798d71616cce5fd0871e23754cd75d5a0a'),
     'RFC 2286 #7 (HMAC-RIPEMD)'),

]


class HMAC_Module_and_Instance_Test(unittest.TestCase):
    """Test the HMAC construction and verify that it does not
    matter if you initialize it with a hash module or
    with an hash instance.

    See https://bugs.launchpad.net/pycrypto/+bug/1209399
    """

    def __init__(self, hashmods):
        """Initialize the test with a dictionary of hash modules
        indexed by their names"""

        unittest.TestCase.__init__(self)
        self.hashmods = hashmods
        self.description = ""

    def shortDescription(self):
        return self.description

    def runTest(self):
        key = b"\x90\x91\x92\x93" * 4
        payload = b"\x00" * 100

        for hashname, hashmod in self.hashmods.items():
            if hashmod is None:
                continue
            self.description = f"Test HMAC in combination with {hashname}"
            one = HMAC.new(key, payload, hashmod).digest()
            two = HMAC.new(key, payload, hashmod.new()).digest()
            self.assertEqual(one, two)


class HMAC_None(unittest.TestCase):

    def runTest(self):

        key = b"\x04" * 20
        one = HMAC.new(key, b"", SHA1).digest()
        two = HMAC.new(key, None, SHA1).digest()
        self.assertEqual(one, two)


class ByteArrayTests(unittest.TestCase):

    def runTest(self):

        key = b"0" * 16
        data = b"\x00\x01\x02"

        # Data and key can be a bytearray (during initialization)
        key_ba = bytearray(key)
        data_ba = bytearray(data)

        h1 = HMAC.new(key, data)
        h2 = HMAC.new(key_ba, data_ba)
        key_ba[:1] = b'\xFF'
        data_ba[:1] = b'\xFF'
        self.assertEqual(h1.digest(), h2.digest())

        # Data can be a bytearray (during operation)
        key_ba = bytearray(key)
        data_ba = bytearray(data)

        h1 = HMAC.new(key)
        h2 = HMAC.new(key)
        h1.update(data)
        h2.update(data_ba)
        data_ba[:1] = b'\xFF'
        self.assertEqual(h1.digest(), h2.digest())


class MemoryViewTests(unittest.TestCase):

    def runTest(self):

        key = b"0" * 16
        data = b"\x00\x01\x02"

        def get_mv_ro(data):
            return memoryview(data)

        def get_mv_rw(data):
            return memoryview(bytearray(data))

        for get_mv in (get_mv_ro, get_mv_rw):

            # Data and key can be a memoryview (during initialization)
            key_mv = get_mv(key)
            data_mv = get_mv(data)

            h1 = HMAC.new(key, data)
            h2 = HMAC.new(key_mv, data_mv)
            if not data_mv.readonly:
                key_mv[:1] = b'\xFF'
                data_mv[:1] = b'\xFF'
            self.assertEqual(h1.digest(), h2.digest())

            # Data can be a memoryview (during operation)
            data_mv = get_mv(data)

            h1 = HMAC.new(key)
            h2 = HMAC.new(key)
            h1.update(data)
            h2.update(data_mv)
            if not data_mv.readonly:
                data_mv[:1] = b'\xFF'
            self.assertEqual(h1.digest(), h2.digest())


def get_tests(config={}):
    global test_data
    import types
    from .common import make_mac_tests

    # A test vector contains multiple results, each one for a
    # different hash algorithm.
    # Here we expand each test vector into multiple ones,
    # and add the relevant parameters that will be passed to new()
    exp_test_data = []
    for row in test_data:
        for modname in row[2].keys():
            t = list(row)
            t[2] = row[2][modname]
            try:
                t.append(dict(digestmod=globals()[modname]))
                exp_test_data.append(t)
            except AttributeError:
                sys.stderr.write("SelfTest: warning: not testing HMAC-%s"
                                 " (not available)\n" % modname)
    tests = make_mac_tests(HMAC, "HMAC", exp_test_data)
    tests.append(HMAC_Module_and_Instance_Test(hash_modules))
    tests.append(HMAC_None())

    tests.append(ByteArrayTests())
    import sys
    if sys.version[:3] != "2.6":
        tests.append(MemoryViewTests())

    return tests


if __name__ == '__main__':
    suite = lambda: unittest.TestSuite(get_tests())
    unittest.main(defaultTest='suite')
