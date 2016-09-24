import requests
import json
from argparse import ArgumentParser

from toggltoredmine.config import Config

class RequestsRunner:
    def send(url, data):
        requests.post(url, data=json.dumps(data))

class MattermostNotifier:
    def __init__(self, url, runner, simulation=False):
        self.url = url
        self.lines = []
        self.runner = runner
        self.simulation = simulation

    def append(self, message):
        self.lines.append(message)

    def send(self):
        text = '\n'.join(self.lines)
        data = { 'text': text, 'username': 'toggl2redmine' }

        if self.simulation:
            print('Message to mattermost:')
            print('-----------------------------------')
            print(text)
            print('-----------------------------------')
        else:
            self.runner.send(self.url, data)

        self.lines = []

if __name__ == '__main__':
    parser = ArgumentParser(description='Sends notification to mattermost')

    parser.add_argument('-m', '--message', help='Message to send', required=True)
    parser.add_argument('-s', '--simulation', help='Simulation mode', action='store_true', default=False)

    config = Config.fromFile()

    if config.mattermost == None:
        raise Exception('No mattermost in config defined')

    args = parser.parse_args()

    notifier = MattermostNotifier(config.mattermost, RequestsRunner(), args.simulation)
    notifier.append(args.message)
    notifier.send()

    print('Sent')
