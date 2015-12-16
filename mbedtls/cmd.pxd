"""Declarations from `mbedtls/md.h`."""

__author__ = "Mathias Laurin"
__copyright__ = "Copyright 2015, Elaborated Networks GmbH"
__license__ = "Apache License 2.0"


cdef extern from "mbedtls/md.h":
    ctypedef enum mbedtls_md_type_t:
        pass

    ctypedef enum mbedtls_md_info_t:
        pass
    
    ctypedef enum mbedtls_md_context_t:
        pass

    const int *mbedtls_md_list()
    const mbedtls_md_info_t *mbedtls_md_info_from_string(
        const char *md_name)
    # mbedtls_md_info_from_type

    void mbedtls_md_init(mbedtls_md_context_t *ctx)
    void mbedtls_md_free(mbedtls_md_context_t *ctx)

    # mbedtls_md_setup
    # mbedtls_md_clone
    unsigned char mbedtls_md_get_size(const mbedtls_md_info_t *md_info)
    mbedtls_md_type_t mbedtls_md_get_type(const mbedtls_md_info_t *md_info)
    const char *mbedtls_md_get_name(const mbedtls_md_info_t *md_info)

    # mbedtls_md_starts
    # mbedtls_md_update
    # mbedtls_md_finish

    int mbedtls_md(
        const mbedtls_md_info_t *md_info,
        const unsigned char *input,
        size_t ilen,
        unsigned char *output)
    int mbedtls_md_file(
        const mbedtls_md_info_t *md_info,
        const char *path,
        unsigned char *output)

    # mbedtls_md_hmac_starts
    # mbedtls_md_hmac_update
    # mbedtls_md_hmac_finish
    # mbedtls_md_hmac_reset
    int mbedtls_md_hmac(
        const mbedtls_md_info_t *md_info,
        const unsigned char *key,
        size_t keylen,
        const unsigned char *input,
        size_t ilen,
        unsigned char *output)
