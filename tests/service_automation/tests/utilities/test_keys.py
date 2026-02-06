"""Test key generation utilities for local testing.

Generates RSA keys dynamically at runtime to avoid storing secrets in the repo.
"""

import functools

import rsa


@functools.lru_cache(maxsize=1)
def get_test_rsa_keys() -> tuple[str, str]:
    """Generate RSA key pair for testing (cached).

    Returns:
        Tuple of (private_key_pem, public_key_pem) as strings.
    """
    public_key, private_key = rsa.newkeys(2048)
    private_key_pem = private_key.save_pkcs1().decode("utf-8")
    public_key_pem = public_key.save_pkcs1().decode("utf-8")
    return private_key_pem, public_key_pem


def get_test_private_key() -> str:
    """Get the test RSA private key (PEM format)."""
    private_key, _ = get_test_rsa_keys()
    return private_key


def get_test_public_key() -> str:
    """Get the test RSA public key (PEM format)."""
    _, public_key = get_test_rsa_keys()
    return public_key
