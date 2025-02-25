"""Unit tests for mbedtls.cipher."""

# Disable checks for violations that are acceptable in tests.
# pylint: disable=missing-docstring
# pylint: disable=attribute-defined-outside-init
# pylint: disable=invalid-name, redefined-outer-name

from functools import partial

import pytest

# pylint: disable=import-error
from mbedtls.cipher._cipher import CIPHER_NAME, get_supported_ciphers
from mbedtls.cipher._cipher import Cipher
from mbedtls.exceptions import *

import mbedtls.cipher as mb

# pylint: enable=import-error


def test_cipher_list():
    assert len(CIPHER_NAME) == 74


def test_get_supported_ciphers():
    cl = get_supported_ciphers()
    assert cl and set(cl).issubset(set(CIPHER_NAME))


def test_wrong_size_raises_exception():
    with pytest.raises(TLSError):
        Cipher(b"AES-512-ECB", b"", mb.Mode.ECB, b"")


def test_random_name_raises_exception():
    with pytest.raises(TLSError):
        Cipher(b"RANDOM TEXT IS NOT A CIPHER", b"", mb.Mode.ECB, b"")


def test_zero_length_raises_exception():
    with pytest.raises(TLSError):
        Cipher(b"", b"", mb.Mode.ECB, b"")


@pytest.mark.parametrize("mode", [mb.MODE_CBC, mb.Mode.CBC])
def test_cbc_raises_value_error_without_iv(mode):
    with pytest.raises(ValueError):
        Cipher(b"AES-512-CBC", b"", mode, b"")


@pytest.mark.parametrize("mode", [mb.MODE_CFB, mb.Mode.CFB])
def test_cfb_raises_value_error_without_iv(mode):
    with pytest.raises(ValueError):
        Cipher(b"AES-512-CFB", b"", mode, b"")


class _TestCipher:
    @pytest.fixture(
        params=[
            mb.Mode.ECB,
            mb.Mode.CBC,
            mb.Mode.CFB,
            mb.Mode.CTR,
            mb.Mode.GCM,
            mb.Mode.CCM,
        ]
    )
    def mode(self, request):
        return request.param

    @pytest.fixture
    def iv(self, mode, randbytes):
        return randbytes(16)

    @pytest.fixture
    def key_size(self):
        raise NotImplementedError

    @pytest.fixture
    def module(self):
        raise NotImplementedError

    @pytest.fixture
    def cipher(self):
        raise NotImplementedError

    @pytest.fixture
    def key(self, key_size, randbytes):
        return randbytes(key_size)

    @pytest.fixture
    def cipher(self, module, key, mode, iv):
        return module.new(key, mode, iv)

    @pytest.fixture
    def data(self, cipher, mode, randbytes):
        # `block_size` is limited for ECB because it is a block cipher.
        return randbytes(cipher.block_size if mode is mb.Mode.ECB else 20000)

    def test_encrypt_decrypt(self, cipher, data):
        assert cipher.decrypt(cipher.encrypt(data)) == data

    def test_module_level_block_size(self, module, cipher):
        assert module.block_size == cipher.block_size

    def test_module_level_key_size(self, module, cipher):
        assert module.key_size in {module.key_size, None}


class _TestAEADCipher(_TestCipher):
    @pytest.fixture
    def cipher(self, module, key, mode, iv, ad):
        return module.new(key, mode, iv, ad)

    @pytest.fixture(params=[0, 1, 16, 256])
    def ad(self, mode, randbytes, request):
        return randbytes(request.param)

    def test_encrypt_decrypt(self, cipher, data):
        msg, tag = cipher.encrypt(data)
        assert cipher.decrypt(msg, tag) == data


class TestAES(_TestCipher):
    @pytest.fixture(
        params=[
            mb.Mode.ECB,
            mb.Mode.CBC,
            mb.Mode.CFB,
            mb.Mode.CTR,
            mb.Mode.OFB,
        ]
    )
    def mode(self, request):
        return request.param

    @pytest.fixture(params=[16, 24, 32])
    def key_size(self, request):
        return request.param

    @pytest.fixture
    def module(self):
        return mb.AES


class TestAES_XTS(TestAES):
    @pytest.fixture(params=[mb.Mode.XTS])
    def mode(self, request):
        return request.param

    @pytest.fixture(params=[32, 64])
    def key_size(self, request):
        return request.param


class TestAES_AEAD(_TestAEADCipher):
    @pytest.fixture(params=[mb.Mode.GCM, mb.Mode.CCM])
    def mode(self, request):
        return request.param

    @pytest.fixture(params=[16, 24, 32])
    def key_size(self, request):
        return request.param

    @pytest.fixture(params=range(7, 14))
    def iv(self, mode, randbytes, request):
        return randbytes(request.param)

    @pytest.fixture
    def module(self):
        return mb.AES


class TestARC4(_TestCipher):
    @pytest.fixture(params=[16])
    def key_size(self, request):
        return request.param

    @pytest.fixture
    def module(self):
        return mb.ARC4


class TestARIA(_TestCipher):
    @pytest.fixture(
        params=[mb.Mode.ECB, mb.Mode.CBC, mb.Mode.CTR, mb.Mode.GCM]
    )
    def mode(self, request):
        return request.param

    @pytest.fixture(params=[16, 24, 32])
    def key_size(self, request):
        return request.param

    @pytest.fixture
    def module(self):
        return mb.ARIA


class TestBlowfish(_TestCipher):
    @pytest.fixture(
        params=[mb.Mode.ECB, mb.Mode.CBC, mb.Mode.CFB, mb.Mode.CTR]
    )
    def mode(self, request):
        return request.param

    @pytest.fixture(params=range(4, 57))
    def key_size(self, request):
        return request.param

    @pytest.fixture
    def module(self):
        return mb.Blowfish


class TestCamellia(_TestCipher):
    @pytest.fixture(
        params=[
            # CCM is not available.
            mb.Mode.ECB,
            mb.Mode.CBC,
            mb.Mode.CFB,
            mb.Mode.CTR,
            mb.Mode.GCM,
        ]
    )
    def mode(self, request):
        return request.param

    @pytest.fixture(params=[16, 24, 32])
    def key_size(self, request):
        return request.param

    @pytest.fixture
    def module(self):
        return mb.Camellia


class TestDES(_TestCipher):
    @pytest.fixture(params=[mb.Mode.ECB, mb.Mode.CBC])
    def mode(self, request):
        return request.param

    @pytest.fixture(params=[8])
    def key_size(self, request):
        return request.param

    @pytest.fixture
    def module(self):
        return mb.DES


class TestDES3(_TestCipher):
    @pytest.fixture(params=[mb.Mode.ECB, mb.Mode.CBC])
    def mode(self, request):
        return request.param

    @pytest.fixture(params=[24])
    def key_size(self, request):
        return request.param

    @pytest.fixture
    def module(self):
        return mb.DES3


class TestDES3dbl(_TestCipher):
    @pytest.fixture(params=[mb.Mode.ECB, mb.Mode.CBC])
    def mode(self, request):
        return request.param

    @pytest.fixture(params=[16])
    def key_size(self, request):
        return request.param

    @pytest.fixture
    def module(self):
        return mb.DES3dbl


class TestCHACHA20(_TestCipher):
    @pytest.fixture(params=[mb.Mode.STREAM])
    def mode(self, request):
        return request.param

    @pytest.fixture(params=[32])
    def key_size(self, request):
        return request.param

    @pytest.fixture
    def module(self):
        return mb.CHACHA20


class TestCHACHA20AEAD(_TestAEADCipher):
    @pytest.fixture
    def iv(self, mode, randbytes):
        return randbytes(12)

    @pytest.fixture(params=[mb.Mode.CHACHAPOLY])
    def mode(self, request):
        return request.param

    @pytest.fixture(params=[32])
    def key_size(self, request):
        return request.param

    @pytest.fixture
    def module(self):
        return mb.CHACHA20
