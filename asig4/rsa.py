# https://www.laurentluce.com/posts/python-and-cryptography-with-pycrypto/

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random

# create Public/private key pair
random_generator = Random.new().read
key = RSA.generate(4096, random_generator)

# encrypt
public_key = key.publickey()
# enc_data = public_key.encrypt('abcdefgh', 32)

# decrypt
# key.decrypt(enc_data)

########
"""
Create a pair key to on every program

"""
########
blah = key.publickey()

# Write to file
with open('key.pem','w') as file:
	file.write(key.exportKey().decode('utf-8'))

with open('key.pem','r') as file:
	# key2 = file.read()
	# key2 = key2.encode('utf-8')
	key2 = RSA.importKey(file.read().encode('utf-8'))

if key == key2:
	print("yas")

blah2 = key2.publickey()
if blah == blah2:
	print("yes")
print(key2.publickey())