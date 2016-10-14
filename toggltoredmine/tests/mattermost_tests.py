import unittest
import requests
from unittest.mock import MagicMock, patch
from datetime import datetime

from toggltoredmine.mattermost import MattermostNotifier, RequestsRunner
from toggltoredmine.toggl import TogglEntry

class MattermostNotifierTests(unittest.TestCase):

    def setUp(self):
        self.today = datetime.strftime(datetime.today(), '%Y-%m-%d')

    def test_send(self):
        runner = MagicMock()

        mattermost = MattermostNotifier('http://dummy', runner)
        mattermost.append('test')
        mattermost.send()

        runner.send.assert_called_with('http://dummy', {'text': 'test', 'username': 'toggl2redmine'})

    def test_append_entries(self):
        runner = MagicMock()

        mattermost = MattermostNotifier('http://dummy', runner)
        mattermost.appendEntries([])
        mattermost.send()

        text = '''Found entries in toggl: **0** (with redmine id: **0**)
All together you did not work today at all :cry:. Hope you ok?
'''

        runner.send.assert_called_with('http://dummy', {'text': text, 'username': 'toggl2redmine'})

    def test_append_entries_one(self):
        runner = MagicMock()

        mattermost = MattermostNotifier('http://dummy', runner)
        mattermost.appendEntries([TogglEntry(None, 60, self.today, 777, '')])
        mattermost.send()

        text = '''Found entries in toggl: **1** (with redmine id: **0**)
You worked almost less than 4 hours today (exactly 1 m), not every day is a perfect day, right? :smirk:.
Huh, not many entries. It means, you did only a couple of tasks, but did it right .. right? :open_mouth:
Ugh. Less than 25% of your work had redmine id. Not so good :cry:.
'''

        runner.send.assert_called_with('http://dummy', {'text': text, 'username': 'toggl2redmine'})

    def test_append_entries_two_one_with_redmine(self):
        runner = MagicMock()

        mattermost = MattermostNotifier('http://dummy', runner)
        mattermost.appendEntries([
            TogglEntry(None, 60, self.today, 776, ''),
            TogglEntry(None, 60, self.today, 777, '#666 Hardwork')
        ])
        mattermost.send()

        text = '''Found entries in toggl: **2** (with redmine id: **1**)
You worked almost less than 4 hours today (exactly 2 m), not every day is a perfect day, right? :smirk:.
Huh, not many entries. It means, you did only a couple of tasks, but did it right .. right? :open_mouth:
It's gooood. A lot of today work had redmine id! Congrats :sunglasses:.
'''

        runner.send.assert_called_with('http://dummy', {'text': text, 'username': 'toggl2redmine'})

    def test_append_entries_two_one_with_redmine_4_hours(self):
        runner = MagicMock()

        mattermost = MattermostNotifier('http://dummy', runner)
        mattermost.appendEntries([
            TogglEntry(None, 4 * 3123, self.today, 777, '#666 Hardwork')
        ])
        mattermost.send()

        text = '''Found entries in toggl: **1** (with redmine id: **1**)
You worked almost less than 4 hours today (exactly 3.47 h), not every day is a perfect day, right? :smirk:.
Huh, not many entries. It means, you did only a couple of tasks, but did it right .. right? :open_mouth:
It seems that more than 75% of your today work had redmine id! So .. you rock :rocket:!
'''

        runner.send.assert_called_with('http://dummy', {'text': text, 'username': 'toggl2redmine'})

    def test_append_entries_10_entries(self):
        runner = MagicMock()

        mattermost = MattermostNotifier('http://dummy', runner)

        e = TogglEntry(None, 4 * 3600, self.today, 777, '#666 Hardwork')
        l = []

        for i in range(1, 10):
            l.append(e)

        mattermost.appendEntries(l)
        mattermost.send()

        text = '''Found entries in toggl: **9** (with redmine id: **9**)
Wow you did overtime today :rocket:! Doing overtime from time to time can be good, but life after work is also important. Remember this next time taking 36.00 h in work :sunglasses:!
Average day. Not too few, not too many entries :sunglasses:.
It seems that more than 75% of your today work had redmine id! So .. you rock :rocket:!
'''

        runner.send.assert_called_with('http://dummy', {'text': text, 'username': 'toggl2redmine'})

    def test_append_entries_50_entries(self):
        runner = MagicMock()

        mattermost = MattermostNotifier('http://dummy', runner)

        e = TogglEntry(None, 60, self.today, 777, '#666 Hardwork')
        l = []

        for i in range(50):
            l.append(e)

        mattermost.appendEntries(l)
        mattermost.send()

        text = '''Found entries in toggl: **50** (with redmine id: **50**)
You worked almost less than 4 hours today (exactly 50 m), not every day is a perfect day, right? :smirk:.
You did 50 entries like a boss :smirk: :boom:!
It seems that more than 75% of your today work had redmine id! So .. you rock :rocket:!
'''

        runner.send.assert_called_with('http://dummy', {'text': text, 'username': 'toggl2redmine'})

    def test_append_entries_3_entries_1_redmine(self):
        runner = MagicMock()

        mattermost = MattermostNotifier('http://dummy', runner)

        l = [
            TogglEntry(None, 60, self.today, 777, '#666 Hardwork'),
            TogglEntry(None, 60, self.today, 777, 'Hardwork'),
            TogglEntry(None, 60, self.today, 777, 'Hardwork')
        ]

        mattermost.appendEntries(l)
        mattermost.send()

        text = '''Found entries in toggl: **3** (with redmine id: **1**)
You worked almost less than 4 hours today (exactly 3 m), not every day is a perfect day, right? :smirk:.
Huh, not many entries. It means, you did only a couple of tasks, but did it right .. right? :open_mouth:
Almost 50% of your today work had redmine id :blush:.
'''

        runner.send.assert_called_with('http://dummy', {'text': text, 'username': 'toggl2redmine'})

    def test_formatSeconds_less_60(self):
        self.assertEquals('45 s', MattermostNotifier.formatSeconds(45))

    def test_formatSeconds_more_60_less_3600(self):
        self.assertEquals('5 m', MattermostNotifier.formatSeconds(5*60))

    def test_formatSeconds_hours(self):
        self.assertEquals('10.00 h', MattermostNotifier.formatSeconds(36000))

    def test_filterToday(self):
        actual = MattermostNotifier.filterToday([
            TogglEntry(None, 4 * 3600, self.today, 777, '#666 Hardwork'),
            TogglEntry(None, 4 * 3600, None, 778, '#666 Hardwork')
        ])

        self.assertEquals(1, len(actual))
        self.assertEquals(actual[0].id, 777)

    def test_filterToday_empty(self):
        actual = MattermostNotifier.filterToday([])
        self.assertEquals(0, len(actual))

    def test_filterToday_None(self):
        actual = MattermostNotifier.filterToday(None)
        self.assertEquals(0, len(actual))

    def test_filterWithRedmineId(self):
        entries = [
            TogglEntry(None, 1, self.today, 1, '#666 Hardwork'),
            TogglEntry(None, 1, self.today, 2, 'Hardwork'),
            TogglEntry(None, 1, self.today, 3, '#666 Hardwork'),
        ]

        filtered = MattermostNotifier.filterWithRedmineId(entries)

        self.assertEquals(2, len(filtered))
        self.assertEquals(1, filtered[0].id)
        self.assertEquals(3, filtered[1].id)

class RequestsRunnerTests(unittest.TestCase):
    class FakeResponse:
        def __init__(self, text, status_code, jsonObject):
            self.text = text
            self.status_code = status_code
            self.jsonObject = jsonObject

        def json(self):
            return self.jsonObject

    @patch('requests.post', side_effect=lambda url, data: RequestsRunnerTests.FakeResponse('', 200, None))
    def test_send_success(self, post_function):
        runner = RequestsRunner()
        runner.send('http://test.com', {'x':'y'})

        post_function.assert_called_with('http://test.com', data='{"x": "y"}')

    @patch('requests.post', side_effect=lambda url, data: RequestsRunnerTests.FakeResponse('Sth went wrong', 500, { 'message': 'Sth went wrong' }))
    def test_send_error(self, post_function):
        runner = RequestsRunner()

        try:
            runner.send('http://test.com', {'x':'y'})
            self.fail('expected exception')
        except Exception as exc:
            self.assertEquals('''Error sending to mattermost:
Sth went wrong''', str(exc))

        post_function.assert_called_with('http://test.com', data='{"x": "y"}')


    @patch('requests.post', side_effect=lambda url, data: RequestsRunnerTests.FakeResponse('Something went wrong...', 500, None))
    def test_send_error_no_json(self, post_function):
        runner = RequestsRunner()

        try:
            runner.send('http://test.com', {'x':'y'})
            self.fail('expected exception')
        except Exception as exc:
            self.assertEquals('''Error sending to mattermost:
Something went wrong...''', str(exc))

        post_function.assert_called_with('http://test.com', data='{"x": "y"}')
