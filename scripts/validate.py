"""Validate generated SVG safety, data consistency, and README asset paths."""
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

root = Path(__file__).resolve().parent.parent
data = json.loads((root/'data/contributions.json').read_text())
assert data['username'] == 'Dexless'
assert data['stats']['total'] == sum(d['count'] for d in data['days'])
for name in ('portrait.svg', 'stats.svg', 'contrib-heatmap.svg'):
    tree = ET.parse(root/name)
    assert tree.getroot().tag == '{http://www.w3.org/2000/svg}svg'
    assert tree.getroot().get('viewBox')
    for node in tree.iter():
        assert node.tag.rsplit('}',1)[-1] not in ('script','foreignObject')
        assert not any(k.lower().startswith('on') for k in node.attrib)
        assert not any('href' in k for k in node.attrib)
for path in re.findall(r'src="\./([^"]+)"', (root/'README.md').read_text()):
    assert (root/path).is_file(), path
print('SVG safety, real-data totals, and README asset paths validated')
