import hashlib


class Consistent_Hashing:
	def get_hash(value):
		return hashlib.sha1(value.encode()).hexdigest()

	def get_modulo_hash(value, m = 10):
		hash_string = Consistent_Hashing.get_hash(value)
		return int(hash_string, 16) % (2**m)