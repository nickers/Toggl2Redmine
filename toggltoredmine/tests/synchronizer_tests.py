import unittest

from unittest.mock import Mock, MagicMock, NonCallableMagicMock
from mock import patch

from toggltoredmine.synchronizer import Synchronizer
from toggltoredmine.config import Config
from toggltoredmine.config import Entry
from toggltoredmine.redmine import RedmineTimeEntry
from toggltoredmine.toggl import TogglEntry

class SynchronizerTests(unittest.TestCase):
    def test_start_one_day_empty(self):
        redmine = Mock()
        toggl = Mock()
        toggl.get = MagicMock()

        s = Synchronizer(Mock(), redmine, toggl, None)
        s.start(1)

        toggl.get.assert_called_once_with(1)

    def test_start_one_day_single(self):
        redmine = Mock()
        toggl = Mock()

        toggl.get.return_value = [ TogglEntry(None, 3600, '2016-01-01T01:01:01', 777, 'test #333') ]

        redmine.get.return_value = [ RedmineTimeEntry(
            777,
            '2016-01-01T01:02:03',
            'john doe',
            1.25,
            '2016-03-02',
            333,
            'test #333 [toggl#777]'
        )]

        s = Synchronizer(Mock(), redmine, toggl, None)
        s.start(1)

        toggl.get.assert_called_once_with(1)

    def test_groupTogglByIssueId(self):
        entries = [
            TogglEntry(None, 3600, None, 1, '#15'),
            TogglEntry(None, 3600, None, 2, '#16'),
            TogglEntry(None, 3600, None, 3, '#16'),
            TogglEntry(None, 3600, None, 4, '#16'),
            TogglEntry(None, 3600, None, 5, '#17'),
        ]

        groups = Synchronizer.groupTogglByIssueId(entries)

        self.assertIsNotNone(groups)

        self.assertEqual(3, len(groups))

        self.assertTrue(15 in groups)
        self.assertTrue(16 in groups)
        self.assertTrue(17 in groups)

        self.assertEquals(1, len(groups[15]))
        self.assertEquals(3, len(groups[16]))
        self.assertEquals(1, len(groups[17]))

        self.assertEquals(1, groups[15][0].id)
        self.assertEquals(2, groups[16][0].id)
        self.assertEquals(3, groups[16][1].id)
        self.assertEquals(4, groups[16][2].id)
        self.assertEquals(5, groups[17][0].id)

    def test_groupRedmineByIssueId(self):
        entries = [
            RedmineTimeEntry(66, None, None, None, None, 1, '[toggl#21]'),
            RedmineTimeEntry(67, None, None, None, None, 2, '[toggl#22]'),
            RedmineTimeEntry(68, None, None, None, None, 2, '[toggl#23]'),
            RedmineTimeEntry(69, None, None, None, None, 2, '[toggl#24]')
        ]

        groups = Synchronizer.groupRedmineByIssueId(entries)

        self.assertEquals(2, len(groups))

        self.assertTrue(1 in groups)
        self.assertTrue(2 in groups)

        self.assertEquals(1, len(groups[1]))
        self.assertEquals(3, len(groups[2]))

        self.assertEquals(22, groups[2][0].toggl_id)
        self.assertEquals(23, groups[2][1].toggl_id)
        self.assertEquals(24, groups[2][2].toggl_id)

    def test_sync_single_toggl_no_redmine(self):
        class RedmineSpec:
            def get(self): pass
            def put(self, id, spentOn, hours, comment): pass

        class TogllSpec:
            def get(self, days): pass

        config = MagicMock()
        redmine = MagicMock(spec_set=RedmineSpec)
        toggl = MagicMock(spec_set=TogllSpec)

        toggl.get.return_value = [
            TogglEntry(None, 3600, '2016-01-01T01:01:01', 17, '#987 hard work')
        ]

        redmine.get.return_value = []

        s = Synchronizer(config, redmine, toggl, None)
        s.start(1)

        toggl.get.assert_called_once_with(1)

        redmine.put.assert_called_once_with(
            issueId=987,
            spentOn='2016-01-01',
            hours=1.0,
            comment='#987 hard work [toggl#17]'
        )

    def test_sync_single_toggl_already_inserted_in_redmine(self):
        class RedmineSpec:
            def get(self): pass

        class TogllSpec:
            def get(self, days): pass

        redmine = MagicMock(spec_set=RedmineSpec)
        toggl = MagicMock(spec_set=TogllSpec)

        toggl.get.return_value = [
            TogglEntry(None, 3600, '2016-01-01T01:01:01', 17, '#987 hard work')
        ]

        redmine.get.return_value = [
            RedmineTimeEntry(
                222,
                '2016-05-01T04:02:22',
                'john doe',
                1,
                '2016-01-01',
                987,
                '#987 hard work [toggl#17]'
            )
        ]

        s = Synchronizer(MagicMock(), redmine, toggl, None)
        s.start(1)

    def test_sync_single_toggl_modified_entry(self):
        class RedmineSpec:
            def get(self): pass
            def update(self): pass

        class TogllSpec:
            def get(self, days): pass

        redmine = MagicMock(spec_set=RedmineSpec)
        toggl = MagicMock(spec_set=TogllSpec)

        toggl.get.return_value = [
            TogglEntry(None, 2*3600, '2016-01-01T01:01:01', 17, '#987 hard work')
        ]

        redmine.get.return_value = [
            RedmineTimeEntry(
                222,
                '2016-05-01T04:02:22',
                'john doe',
                1,
                '2016-01-01',
                987,
                '#987 hard work [toggl#17]'
            )
        ]

        s = Synchronizer(MagicMock(), redmine, toggl, None)
        s.start(1)

        redmine.update.assert_called_once_with(
            id=222,
            issueId=987,
            spentOn='2016-01-01',
            hours=2.0,
            comment='#987 hard work [toggl#17]'
        )

    def test_ignore_negative_duration(self):
        """
        Synchronizer should ignore entries with negative durations (pending entries).

		From toggl docs:
           duration: time entry duration in seconds. If the time entry is currently running, the duration attribute contains a negative value, denoting the start
           of the time entry in seconds since epoch (Jan 1 1970). The correct duration can be calculated as current_time + duration, where current_time is the current
           time in seconds since epoch. (integer, required)
        """

        redmine = Mock()
        toggl = Mock()

        toggl.get.return_value = [
            TogglEntry(None, 3600, '2016-01-01T01:01:01', 777, 'test #333'),
            TogglEntry(None, -3600, '2016-01-01T01:01:01', 778, 'test #334')
        ]

        redmine.get.return_value = []

        s = Synchronizer(Mock(), redmine, toggl, None)
        s.start(1)

        toggl.get.assert_called_once_with(1)
        redmine.get.assert_called_once_with(333)

        redmine.put.assert_called_once_with(issueId=333,
            spentOn='2016-01-01',
            hours=1.0,
            comment='test #333 [toggl#777]')

if __name__ == '__main__':
    unittest.main()
