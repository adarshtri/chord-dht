class InterClassMessaging:
	def send_message(nodeId, function, **kwargs):
		return eval('nodeId.' + function + '(**kwargs)')