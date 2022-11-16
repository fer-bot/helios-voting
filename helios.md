# ☼ HELIOS ☼

---

## What is Helios

Helios is an online cryptographic mini-voting (yes/no voting) platform. This is a variant of Helios Voting Scheme referencing from [Cryptographic Voting – A Gentle Introduction](https://eprint.iacr.org/2016/765.pdf).

A voting event will have 3 types of user:

- (one) voting event creator
- (one or more) authority(s)
- (one or more) voter(s)

The voting event creator is not crucial for determining the result of our voting. He/she will only be useful for managing the event details, eligible voters and trusted authorities, and opening/closing the event.

The authority(s) is the important key for a safe and secure voting event. Here, more than one authority is required to prevent malicious act. With more than one authority, we can be sure this voting is safe if at least one of the authorities is honest.

Our goal is trying to recreate offline voting system where:

1. There will be a public lists of voters and authorities.
1. Each voter can vote yes/no during the given period of time.
1. Everyone can see who have voted but only the voter him/her self know his/her choice.
1. After the voting ends, all authority will use the key to open the voting box which can only be opened if all the keys are present.
1. The voter can make sure his vote is calculated for the end result and the end result is not rigged.

Let's see how we could do this using cryptography!

## Technical Details

To achieve our goal for an anonymous voting, we are using `Exponential ElGamal` encryption scheme and two zero-knowledge protocol: `Chaum-Pedersen` and `DCP (Disjunctive Chaum-Pedersen)`.

We will also have a public bulletin board that can be seen by everyone (voters and authority).

### Voting Event Creation Phase

As we are using ElGamal for our encryption scheme, we will need a large prime number `p` and its primitive root (generator) `g`. Both `p` and `g` will be public constant and be shown at the buletin board. For this system, we will have `p` with length of 1024-bit.

It takes a lot of time to produce 1024-bit prime number and its primitive root. Hence, we are using a pre-generated random safe prime `p`. `p` is a safe prime if `p = 2q + 1` and `q` is also a prime. This prime is used such that generation of `g` is much faster. Using the lagrange theorem, we would just need to check if `g^2 != 1` and `g^q != 1`

The code used to generate such primes and the generator in Python:

```python
from Crypto.Util import number

# For generating safe prime p
def generate_large_prime():
    n_length = 1024
    p = number.getPrime(n_length)
    while not number.isPrime((p-1)//2):
        p = number.getPrime(n_length)
    return p

# For generating generator g
def find_primitive_root(p):
    f2 = (p-1)//2
    while True:
        g = random.randint(3, p-1)
        if not pow(g, 2, p) == 1 and not pow(g, f2, p) == 1:
            return g
```

### Authority Setup Phase

During this phase, we will get the consolidated public key `pk` for the ElGamal encryption. As we have multiple authorities, we will define the secret key (`sk`) and public key (`pk`) as:

```
sk = sk_1 + sk_2 + ... + sk_n
pk = g^(sk) mod p
   = g^(sk_1 + sk_2 + ... + sk_n) mod p
   = (g^sk_1 * g^sk_2 * ... * g^sk_n) mod p
   = pk_1 * pk_2 * ... * pk_n mod p
```

where `sk_i` and `pk_i` is the secret key and public key of n-th authority. For this, each authority must then create their random `sk_i`, store it somewhere safe, generate `pk_i = g^sk_i mod p`, and send only the `pk_i` to this voting system and will be posted to the bulletin board.

After receiving all the authorities' public key, we then generate the final public key and post it to the buletin board.

To help authorities in generating their public key and secret key while making sure it does not leak to the server, we give this function in JavaScript as their secret key should never reach the our voting system:

```javascript
var bits = 1024;

// For generating new SK. Do take note this is not the best practice to generate a random number. We will need to improve this part.
function getRandom() {
  var result = "";
  for (var i = 0; i < 80; i++) {
    result += String(Math.floor(Math.random() * 10000));
  }
  return result;
}

// For generating new PK
function powMod(g, sk, modulus) {
  g = BigInt(g);
  sk = BigInt(sk);
  modulus = BigInt(modulus);

  if (modulus === BigInt(1)) return 0;

  var result = BigInt(1);
  g = g % modulus;
  while (sk > 0) {
    if (sk % BigInt(2) === BigInt(1))
      //odd number
      result = (result * g) % modulus;
    sk = sk / BigInt(2); //divide by 2
    g = (g * g) % modulus;
  }
  return result;
}
```

The code to generate the final public key `pk` in Python:

```python
def get_room_pk(authority_pks, p):
    pk = 1

    for authority_pk in authority_pks:
        pk = (pk * authority_pk) % p

    return pk
```

### Voting Phase

During the voting period, each user will use exponential ElGamal to encrypt their voting result as exponential ElGamal is great for tallying up the votes. Each user will pick a random number `r_i` and generate ciphertext `(a_i, b_i)` with `a_i = g^r_i mod p` and `b_i = g^m * pk^r_i mod p` where `m = 0` for yes and `m = 1` for no.

We also need a way to verify that a voter does not send any invalid vote (for example, `b_i = g^100 * pk^r_i mod p`) that could give him an unfair advantage. Here is where we use DCP (Disjunctive Chaum-Pedersen's) zero-knowledge proof protocol. DCP requires the voter to generate proofs that his/her vote is valid without giving any information about whether they choose yes or no. The main idea is that the voter will need to submit 2 proofs and the voter can only cheat on one of the two proofs. This is needed such that no one can predict the vote from the proof.

DCP relies on a hash function. Because the hash function is unpredictable and depends on `(pk, a, b, a0, bo, a1, b1) `, trying to adjust one of these values will result in changing the challenge `c = H(pk, a, b, a0, bo, a1, b1)`. This makes generating fake proof very hard. For this application, our hash function will be:

`c = sha256(sum(pk, a, b, a0, bo, a1, b1))`

As a result, each voter will send ciphertext that would later be posted on the bulletin board:

```
(a_i, b_i, a0_i, a1_i, b0_i, b1_i, c0_i, c1_i, r0_i, r1_i)
```

As we don't want to leak any secrets to the server, to help voters generate the ciphertexts, we give these functions in JavaScript:

```javascript
// Like pow function in Python
function powMod(a, b, modulus) {
  a = BigInt(a);
  b = BigInt(b);
  modulus = BigInt(modulus);

  if (modulus === BigInt(1)) return 0;

  var result = BigInt(1);
  a = a % modulus;
  while (b > 0) {
    if (b % BigInt(2) === BigInt(1))
      //odd number
      result = (result * a) % modulus;
    b = b / BigInt(2); //divide by 2
    a = (a * a) % modulus;
  }
  return result;
}

// Encrypt function
function encrypt_vote(choice){
    var g = BigInt("{{room.generator}}")
    var p = BigInt("{{room.prime}}")
    var pk = BigInt("{{room.public_key}}")
    var q = p - BigInt(1)

    // generate encryption a
    var r = getRandomInput() // from user
    var a = powMod(g, r, p)
    var b = powMod(pk, r, p)
    var r0 = BigInt(getRandom())
    var r1 = BigInt(getRandom())
    var a0, a1, b0, b1, c0, c1;

    if (choice === 0){
        a0 = powMod(g, r0, p);
        b0 = powMod(pk, r0, p);

        c1 = BigInt(getRandom())

        a1 = powMod(g, r1, p) * powMod(a, c1 * (p - BigInt(2)), p) % p;
        b1 = powMod(pk, r1, p) * powMod(b * powMod(g, p - BigInt(2), p) % p, c1 * (p - BigInt(2)), p) % p;

        var hash_input = ((pk + a + b + a0 + b0 + a1 + b1) % q).toString()
        // URL to hash to SHA256 input";
        var url_mask = "/user/hash/" + hash_input" ;

        fetch(url_mask).then(function(response){
            return response.json()
        }).then(function(data){
            var c = BigInt(data.hash_response) // hash result
            c0 = (q + (c - c1)) % q;
            r0 = (r0 + (c0 * r) % q) % q;

            return [a, b, a0, a1, b0, b1, c0, c1, r0, r1];
        })
    }

    else if (choice === 1) {
        b = (b * BigInt("{{room.generator}}")) % BigInt("{{room.prime}}")

        c0 = BigInt(getRandom());

        a0 = powMod(g, r0, p) * powMod(a, c0 * (p - BigInt(2)), p) % p;
        b0 = powMod(pk, r0, p) * powMod(b, c0 * (p - BigInt(2)), p) % p;

        a1 = powMod(g, r1, p);
        b1 = powMod(pk, r1, p);

        var hash_input = ((pk + a + b + a0 + b0 + a1 + b1) % q).toString()
        // URL to hash to SHA256 input";
        var url_mask = "/user/hash/" + hash_input" ;

        fetch(url_mask).then(function(response){
            return response.json()
        }).then(function(data){
            var c = BigInt(data.hash_response) // hash result
            c1 = (q + (c - c0)) % q;
            r1 = (r1 + (c1 * r) % q) % q;

            return [a, b, a0, a1, b0, b1, c0, c1, r0, r1];
        })
    }
}
```

After receiving voter's ciphertext, the system will then check the validity of the vote using its DCP proof. The Python code for it:

```python
def hash_sha(hash_input):
    return int(sha256(str(hash_input).encode('utf-8')).hexdigest(), 16)

def DCP_check(proof, pk, g, p):
    a, b, a0, a1, b0, b1, c0, c1, r0, r1 = proof

    s1 = pow(g, r0, p) == a0 * pow(a, c0, p) % p
    s2 = pow(g, r1, p) == a1 * pow(a, c1, p) % p
    s3 = pow(pk, r0, p) == b0 * pow(b, c0, p) % p
    s4 = pow(pk, r1, p) == b1 * \
        pow(b * pow(g, p - 2, p) % p, c1, p) % p
    c = hash_sha(sum([pk, a, b, a0, b0, a1, b1]) % (p - 1))
    s5 = (c0 + c1) % (p - 1) == c

    return (s1 and s2 and s3 and s4 and s5)
```

The verified votes will then be posted on the buletin board so that each voter can view their own ciphertext: `(a_i, b_i, a0_i, a1_i, b0_i, b1_i, c0_i, c1_i, r0_i, r1_i)` and also can verify the correctness of anyone's ciphertext.

### Tallying phase

At the end of the voting period, we will now tally the vote. We will do this by getting the final (`a`, `b`) ciphertext by calculating

```
a = (a_1 * a_2 * ... * a_n) mod p
b = (b_1 * b_2 * ... * b_n) mod p
```

The code to sum all the ciphertext in Python:

```python
def add_ciphers(ciphers, p):
    a = 1
    b = 1
    for ai, bi in ciphers:
        a = (a * ai) % p
        b = (b * bi) % p
    return a, b
```

Do notice that:

```
a = g^r_1 * g^r_2 * ... *  g^r_n mod p
  = g^(r_1 + r_2 + ... + r_n) mod p
b = (g^m_1 * g^(sk*r_1)) * ... * (g^m_n * g^(sk*r_n)) mod p
  = (g^m_1 * ... * g^m_n) * (g^(sk*r_1) * ... * g^(sk*r_n)) mod p
  = g^(m_1 + ... + m_n) * g^(sk*(r_1 + ... + r_n)) mod p
  = g^m * a^sk mod p
```

Hence, we could later get the tallying result by computing `ai = a^(sk*(p-2)) mod p` and then getting the value of `g^m mod p` by computing `ai * b mod p`. By using Fermat little theorem:

```
ai * b mod p = a^(sk*(p-2)) * g^m * a^sk mod p
             = g^m * a^(sk(p-1)) mod p
             = g^m mod p
```

As our secret key is created by using the sum of more than one authorities, we would need each authority to calculate their own `d` where `d_i = a^(sk_i) mod p` so we can calculate the final ai:

```
ai = (d_1 * d_2 * ... * d_n)^(p-2) mod p
   = (a^sk_1 * ... * a^sk_n)^(p-2) mod p
   = (a^(sk_1 + ... + sk_n))^(p-2) mod p
   = a^(sk * (p-2)) mod p
```

We also want to prevent the authority from doing malicious acts by decrypting incorrectly or announcing a fake result. Here is where Chaum-Pedersen zero-knowledge Protocol comes to help. This protocol will request proof from the authority without actually leaking his/her secret key to anyone.

Here we also need an unpredictable hash function. Like DCP, the hash function `c = H(pk, a, b, u, v)` will also change along when trying to fake the proof.

As a result, each authority will send ciphertext `(u_i, v_i, s_i ,d_i)` that would later be posted on the bulletin board with `d_i = a^sk_i mod p`. As we don't want to leak the secret key `sk_i`, to help authority without leaking their secret key to the server, we use this function in JavaScript:

```javascript
// Work as Python's pow(a, b, c)
function powMod(a, b, modulus) {
  a = BigInt(a);
  b = BigInt(b);
  modulus = BigInt(modulus);

  if (modulus === BigInt(1)) return 0;

  var result = BigInt(1);
  a = a % modulus;
  while (b > 0) {
    if (b % BigInt(2) === BigInt(1))
      //odd number
      result = (result * a) % modulus;
    b = b / BigInt(2); //divide by 2
    a = (a * a) % modulus;
  }
  return result;
}

// Main encryption function.
function encrypt_vote() {
  var g = BigInt("{{room.generator}}");
  var p = BigInt("{{room.prime}}");
  var pk = BigInt("{{details.public_key}}");
  var total_a = BigInt("{{room.total_a}}");
  var total_b = BigInt("{{room.total_b}}");
  var q = p - BigInt(1);

  var r = BigInt(document.getElementById("user_r").value);
  var sk = BigInt(document.getElementById("user_sk").value);
  var u = powMod(total_a, r, p);
  var v = powMod(g, r, p);
  var d = powMod(total_a, sk, p);

  var hash_input = ((pk + total_a + total_b + u + v) % p).toString();
  var url_mask = "/user/hash/" + hash_input; // URL to hash to SHA265

  fetch(url_mask)
    .then(function (response) {
      return response.json();
    })
    .then(function (data) {
      var c = BigInt(data.hash_response);
      var s = (r + ((c * sk) % q)) % q;
    });

  return [u, v, s, d];
}
```

After getting the ciphertext, the system can then verify the cipher decryption of each authority. This Chaum-Pedersen's protocol will validate if the generated `d_i` is indeed `a^sk_i` and whether the secret key `sk_i` used is the same one used to generate the public key `pk_i`. After ensuring that it is correct, we could also generate the `ai_i` where `ai_i = d^(p-2) mod p`.

Here is the code for the validation:

```python
def CP_check(pk, cipher, proof, g, p):
    a, b = cipher
    u, v, s, d = proof
    c = hash_sha(sum([pk, a, b, u, v]) % p)
    return pow(a, s, p) == u * pow(d, c, p) % p and pow(g, s, p) == v * pow(pk, c, p) % p


def get_ai(d, p):
    return pow(d, p-2, p)
```

### Result release

Lastly, after all the authorities has done submitting their decryption and proof, we would now get the result of the voting event. As mentioned before, we will get the voting result by calculating `g^m` where m is the number total number of people who voted for yes:

```
ai = ai_1 * ai_2 * ... *ai_n mod p
   = a^(sk*(p-2)) mod p
ai * b mod p = a^(sk*(p-2)) * g^m * a^sk mod p
             = g^m * a^(sk(p-1)) mod p
             = g^m mod p
```

The code for this in Python:

```python
// Combine all result from authorities
def add_decrypted_ciphers(all_decrypted_a, b, p):
    ai = 1
    for a in all_decrypted_a:
        ai = (ai * a) % p
    return ai * b % p
```

We could then find number of voters `m` by checking one by one from `i = 0` to `i = number_of_voters` and find one that satisfy `g^i mod p = g^m mod p`.

The code for this in Python:

```python
# get the number of people voting for yes(1)
def decrypt_ciphers(gm, g, p):
    m = 0
    while pow(g, m, p) != gm:
        m += 1
    return m
```

Everyone can then validate the authority's proof and the voting result from the bulletin board to make sure the voting result is not rigged using this knowledge.

#### Thank you for reading until the end :-)
