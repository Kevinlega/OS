# https://www.laurentluce.com/posts/python-and-cryptography-with-pycrypto/

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random

# create Public/private key pair
random_generator = Random.new().read
key = RSA.generate(4096, random_generator)

# encrypt
public_key = key.publickey()
enc_data = public_key.encrypt('abcdefgh', 32)

# decrypt
key.decrypt(enc_data)

# Sign

key = RSA.generate(4096, random_generator)
text = 'abcdefgh'
hash = SHA256.new(text).digest()
signature = key.sign(hash, '')

# Verify

text = 'abcdefgh'
hash = SHA256.new(text).digest()
public_key.verify(hash, signature)


########
"""
Create a pair key to on every program


"""
########














# Those algorithms work on a byte-by-byte basis. The block size is always one byte. Two algorithms are supported by pycrypto: ARC4 and XOR. Only one mode is available: ECB.

# Let’s look at an example with the algorithm ARC4 using the key ‘01234567’.
# 1
# 	>>> from Crypto.Cipher import ARC4
# 2
# 	>>> obj1 = ARC4.new('01234567')
# 3
# 	>>> obj2 = ARC4.new('01234567')
# 4
# 	>>> text = 'abcdefghijklmnop'
# 5
# 	>>> cipher_text = obj1.encrypt(text)
# 6
# 	>>> cipher_text
# 7
# 	'\xf0\xb7\x90{#ABXY9\xd06\x9f\xc0\x8c '
# 8
# 	>>> obj2.decrypt(cipher_text)
# 9
# 	'abcdefghijklmnop'