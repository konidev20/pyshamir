# pyshamir

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=konidev20_pyshamir&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=konidev20_pyshamir)
[![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=konidev20_pyshamir&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=konidev20_pyshamir)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=konidev20_pyshamir&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=konidev20_pyshamir)
[![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=konidev20_pyshamir&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=konidev20_pyshamir)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=konidev20_pyshamir&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=konidev20_pyshamir)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=konidev20_pyshamir&metric=coverage)](https://sonarcloud.io/summary/new_code?id=konidev20_pyshamir)

Python port of Shamir key Split and Combine methods from Hashicorp Vault.

## Installation

```sh
pip install pyshamir 
```

## Usage

### Split & Combine

```py
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
```

## References

1. [Shamir Secret Sharing | Wikipedia](https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing)
2. [Go Implementation | HashiCorp Vault](https://github.com/hashicorp/vault/tree/main/shamir)
