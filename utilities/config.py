class Config:
	def __init__(self, config_set = 'default'):
		exec('self.' + config_set + '()')

	def default(self):
		self.m_bits = 20
