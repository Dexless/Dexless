import unittest
from scripts.profile_art import summarize

class ContributionTests(unittest.TestCase):
    def test_today_does_not_end_yesterdays_streak(self):
        days = [{'date': f'2026-10-{d:02}', 'count': n, 'level': 0}
                for d, n in [(18, 0), (19, 2), (20, 3), (21, 0)]]
        stats = summarize(days)
        self.assertEqual(stats['current'], 2)
        self.assertEqual(stats['longest'], 2)
        self.assertEqual(stats['total'], 5)
        self.assertEqual(stats['active'], 2)

    def test_no_activity_has_no_streak_or_average(self):
        stats = summarize([{'date': '2026-10-21', 'count': 0, 'level': 0}])
        self.assertEqual((stats['current'], stats['longest'], stats['average']), (0, 0, 0))

    def test_gap_breaks_streak(self):
        days = [{'date': f'2026-10-{d:02}', 'count': n, 'level': 0}
                for d, n in [(18, 1), (19, 1), (20, 0), (21, 2)]]
        self.assertEqual(summarize(days)['current'], 1)
        self.assertEqual(summarize(days)['longest'], 2)
