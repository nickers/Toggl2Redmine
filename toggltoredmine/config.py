import os

from yaml import load, dump

class Entry:
	def __init__(self, label, redmine_api_key, toggl_api_key):
		self.label = label
		self.redmine = redmine_api_key
		self.toggl = toggl_api_key

	def __str__(self):
		return '{}: {}'.format(self.redmine, self.toggl)

class Config:
	def __init__(self, toggl, redmine, entries, mattermost):
		self.toggl = toggl
		self.redmine = redmine
		self.entries = entries
		self.mattermost = mattermost

	@classmethod
	def fromFile(cls, path='config.yml'):
		if not os.path.exists(path):
			raise Exception('File {} does not exist. Check out config.yml.example and create config.yml'.format(path))

		with open(path) as input:
			deserialized = load(input)

			if 'toggl' not in deserialized:
				raise Exception('"toggl" element not found in config')

			toggl = deserialized['toggl']

			if 'redmine' not in deserialized:
				raise Exception('"redmine" element not found in config')

			redmine = deserialized['redmine']

			if 'mattermost' in deserialized:
				mattermost = deserialized['mattermost']
			else:
				mattermost = None

			if 'entries' not in deserialized:
				raise Exception('"entries" element not found in config')

			entries = []

			for entry in deserialized['entries']:
				entries.append(Entry(**entry))

		return cls(toggl, redmine, entries, mattermost)

	def __str__(self):
		return '''config:
\ttoggl url:\t{}
\tredmine url:\t{}

\tentries:
\t\t{}'''.format(self.toggl, self.redmine, '\n\t\t'.join([str(e) for e in self.entries]))

if __name__ == '__main__':
	config = Config()
	print(config)
