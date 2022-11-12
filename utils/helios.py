import os
import random
import math
import secrets
from Crypto.Util import number
from .safeprimes import safeprimes
import random


def generate_large_prime():
    # using safe prime because it is easier to find the generator
    # g where order(g) = p-1
    return safeprimes[random.randint(0, len(safeprimes)-1)]


def find_primitive_root(p):
    if p == 2:
        return 1

    # because p is safe prime, factor of p-1 = [2, (p-1)/2]
    f2 = (p-1)//2

    # test random g's until one is found that is a primitive root mod p
    # g is a primitive root if for all prime factors of p-1, primes[i]
    # g^((p-1)/p[i]) (mod p) is not congruent to 1
    # since p is safe prime, prime factors of p-1 = [2, (p-1)/2]
    while True:
        g = random.randint(3, p-1)
        if not pow(g, 2, p) == 1 and not pow(g, f2, p) == 1:
            return g


def generate_room_id():
    n_length = int(os.getenv('ROOM_ID_LENGTH', 8))
    return secrets.token_urlsafe(n_length)


def get_room_pk(authority_pks, p):
    pk = 1

    for authority_pk in authority_pks:
        pk = (pk * authority_pk) % p

    return pk


def add_ciphers(ciphers, p):
    a = 1
    b = 1
    for ai, bi in ciphers:
        a = (a * ai) % p
        b = (b * bi) % p
    return a, b


def add_decrypted_ciphers(all_decrypted_a, b, p):
    ai = 1
    for a in all_decrypted_a:
        ai = (ai * a) % p
    return ai * b % p


def decrypt_ciphers(gm, g, p):
    m = 0
    while pow(g, m, p) != gm:
        m += 1
    return m


def CP_check(pk, cipher, proof, g, p):
    a, b = cipher
    u, v, s, d = proof
    c = sum([pk, a, b, u, v]) % g
    return pow(a, s, p) == u * pow(d, c, p) % p and pow(g, s, p) == v * pow(pk, c, p) % p


def get_ai(d, p):
    return pow(d, p-2, p)


def DCP_check(proof, pk, g, p):
    a, b, a0, a1, b0, b1, c0, c1, r0, r1 = proof

    s1 = pow(g, r0, p) == a0 * pow(a, c0, p) % p
    s2 = pow(g, r1, p) == a1 * pow(a, c1, p) % p
    s3 = pow(pk, r0, p) == b0 * pow(b, c0, p) % p
    s4 = pow(pk, r1, p) == b1 * \
        pow(b * pow(g, p - 2, p) % p, c1, p) % p

    return (s1 and s2 and s3 and s4)
