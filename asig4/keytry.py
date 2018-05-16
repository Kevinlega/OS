from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto import Random

random_generator = Random.new().read

key = RSA.generate(4096, random_generator)
key.publickey()

with open("/Users/Kevinlega/Desktop/key.pem","w") as file:
	file.write(str(key.exportKey('PEM')))

pr = ''
with open("/Users/Kevinlega/Desktop/key.pem","r") as file:
	read = file.read()
	read = read.replace('b\'',"")
	read = read.replace('\'',"")
	pr = RSA.importKey(read)

if pr.exportKey() == key.exportKey():
	print("yas")


