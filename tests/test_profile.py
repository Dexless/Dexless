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

class PortraitTests(unittest.TestCase):
    def test_square_subject_retains_square_proportions_and_is_clipped(self):
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from PIL import Image, ImageDraw
        import xml.etree.ElementTree as ET
        from scripts import profile_art
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root/'assets').mkdir()
            source = Image.new('RGB', (400, 400), 'black')
            ImageDraw.Draw(source).rectangle((100, 100, 299, 299), fill='white')
            source.save(root/'assets/avatar.jpg')
            with patch.object(profile_art, 'ROOT', root):
                tree = ET.fromstring(profile_art.portrait())
        ns = {'s': 'http://www.w3.org/2000/svg'}
        rows = [e for e in tree.findall('.//s:text', ns) if e.get('class') == 'row']
        occupied = [(i, e.text or '') for i, e in enumerate(rows) if (e.text or '').strip()]
        width = max((max(map(float, e.get('x').split())) - min(map(float, e.get('x').split())) + 800/180) / 800 for e in rows if e.text)
        height = (max(float(e.get('y')) for e in rows) - min(float(e.get('y')) for e in rows) + 800/96) / 800
        self.assertAlmostEqual(width, height, delta=.05)
        clip = tree.find('.//s:clipPath/s:rect', ns)
        self.assertIsNotNone(clip)
        self.assertEqual(clip.get('width'), clip.get('height'))
        self.assertIsNotNone(tree.find('.//s:g[@clip-path="url(#portrait-bounds)"]', ns))

    def test_glyphs_use_fixed_grid_positions_and_animation_repeats(self):
        import xml.etree.ElementTree as ET
        from scripts.profile_art import portrait
        tree = ET.fromstring(portrait())
        ns = {'s': 'http://www.w3.org/2000/svg'}
        rows = [e for e in tree.findall('.//s:text', ns) if e.get('class') == 'row']
        for row in rows:
            self.assertIsNone(row.get('textLength'))
            xs = [float(x) for x in row.get('x').split()]
            self.assertEqual(len(xs), len(row.text or ''))
            self.assertTrue(all(20 <= x < 820 for x in xs))
        animation = tree.find('.//s:clipPath/s:rect/s:animate', ns)
        self.assertIsNotNone(animation)
        self.assertEqual(animation.get('repeatCount'), 'indefinite')
