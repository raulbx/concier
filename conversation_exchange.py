import core_engine

class Exchange(object):

	def __init__(self, member_identifier, source):
		self.member_identifier = member_identifier
		self.source = source

	def get_action(self):
		print("Member Identifier is {}".format(member_identifier))