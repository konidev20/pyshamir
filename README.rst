========
pyshamir
========
Python port of HashiCorp Vault's Shamir key Split and Combine methods.

Installation
============
.. code-block::

    pip install pyshamir 

Usage
=====
Split & Combine
---------------
.. code-block::

    from pyshamir import split, combine
    import secrets

    # generate a random secret, here secret is a 32 bytes
    secret = secrets.token_bytes(32)

    # set the number of shares; i.e. the number of parts to split the secret into
    num_of_shares = 5

    # threshold is minimum number of keys required to get back the secret
    threshold = 3

    # split to get a list of bytearrays which can be combined later to get back the secret
    parts = split(secret, num_of_shares, threshold)

    # Now, the parts be combined to get back the secret
    recomb_secret = combine(parts)

References
==========
#. `Shamir Secret Sharing | Wikipedia <https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing>`
#. `Go Implementation | HashiCorp Vault <https://github.com/hashicorp/vault/tree/main/shamir>`