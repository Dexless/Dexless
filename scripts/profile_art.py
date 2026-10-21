"""Generate GitHub-safe animated art from the public contribution calendar.

No token required. Failed fetches abort before touching existing assets.
"""
from collections import defaultdict
from datetime import date, timedelta
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import json
import urllib.request
from PIL import Image, ImageOps, ImageEnhance

ROOT = Path(__file__).resolve().parent.parent
USER = 'Dexless'
PALETTE = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells, self.tips = {}, {}
        self.tip = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'td' and a.get('data-date'):
            self.cells[a['id']] = {'date': a['data-date'], 'level': int(a['data-level'])}
        if tag == 'tool-tip':
            self.tip = a.get('for')
            self.tips[self.tip] = ''
    def handle_data(self, text):
        if self.tip:
            self.tips[self.tip] += text
    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.tip = None
    def days(self):
        result = []
        for key, cell in self.cells.items():
            words = self.tips.get(key, '').strip().split()
            if not words:
                raise ValueError('Missing contribution count; refusing to invent data')
            n = 0 if words[0].lower() == 'no' else int(words[0].replace(',', ''))
            result.append(dict(cell, count=n))
        result.sort(key=lambda d: d['date'])
        if len(result) < 350:
            raise ValueError('Incomplete GitHub calendar')
        return result

def summarize(days):
    current = longest = run = 0
    monthly = defaultdict(int)
    for day in days:
        run = run + 1 if day['count'] else 0
        longest = max(longest, run)
        monthly[day['date'][:7]] += day['count']
    tail = days[:-1] if not days[-1]['count'] else days
    for day in reversed(tail):
        if not day['count']:
            break
        current += 1
    total = sum(d['count'] for d in days)
    active = sum(d['count'] > 0 for d in days)
    return dict(total=total, active=active, current=current, longest=longest,
                average=round(total / active, 1) if active else 0,
                best=max(days, key=lambda d: d['count']), monthly=dict(monthly))

def text(x, y, value, size=20, color='#7d8590', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(str(value))}</text>'

def svg(w, h, content, title):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}" font-family="ui-monospace,Menlo,Consolas,monospace">
<title>{escape(title)}</title><style>
@keyframes appear{{0%,3%{{opacity:0;transform:translateY(10px)}}15%,100%{{opacity:1;transform:translateY(0)}}}}
@keyframes grow{{0%,8%{{transform:scaleY(0)}}25%,100%{{transform:scaleY(1)}}}}
@keyframes type{{from{{clip-path:inset(0 100% 0 0)}}to{{clip-path:inset(0 0 0 0)}}}}
.reveal{{animation:appear 12s ease-out infinite both}}.bar{{transform-box:fill-box;transform-origin:bottom;animation:grow 12s ease-out infinite both}}
.row{{font-variant-ligatures:none}}
@media(prefers-reduced-motion:reduce){{.reveal,.bar,.row{{animation:none!important}}#portrait-bounds rect{{height:800px!important}}}}
</style>{content}</svg>'''

def window(command):
    s = '<rect width="840" height="880" rx="12" fill="#0d1117" stroke="#30363d"/><path d="M0 30H840" stroke="#30363d"/>'
    for i, c in enumerate(['#ff5f56', '#ffbd2e', '#27c93f']):
        s += f'<circle cx="{20+i*16}" cy="15" r="5" fill="{c}"/>'
    return s + text(420, 20, f'Dexless@github: ~$ {command}', 12, extra='text-anchor="middle"')

def heatmap(days, stats):
    start = date.fromisoformat(days[0]['date'])
    start -= timedelta(days=(start.weekday()+1) % 7)
    columns = (date.fromisoformat(days[-1]['date'])-start).days // 7 + 1
    width = 40 + columns*16
    s = ''
    last_month = None
    for week in range(columns):
        dt = start + timedelta(weeks=week)
        if dt.month != last_month:
            s += text(34+week*16, 16, dt.strftime('%b'), 12)
            last_month = dt.month
    for row, label in [(1,'Mon'),(3,'Wed'),(5,'Fri')]:
        s += text(0, 35+row*16, label, 11)
    for day in days:
        offset = (date.fromisoformat(day['date'])-start).days
        col, row = divmod(offset, 7)
        s += f'<rect class="reveal" x="{34+col*16}" y="{24+row*16}" width="13" height="13" rx="2.5" fill="{PALETTE[day["level"]]}" style="animation-delay:{(col+row*.5)*.065:.3f}s"><title>{day["date"]}: {day["count"]} contributions</title></rect>'
    s += text(34, 152, f'{stats["total"]:,} contributions in the last year', 15, '#e6edf3')
    return svg(width, 160, s, 'Dexless contribution calendar')

def portrait():
    # Sample the complete square image; non-square character cells correct
    # the grid's aspect ratio when rendered in the 800 x 800 art area.
    square = ImageOps.pad(Image.open(ROOT/'assets/avatar.jpg').convert('RGB'), (800, 800))
    color = square.resize((180, 96), Image.Resampling.LANCZOS)
    im = color.convert('L')
    im = ImageEnhance.Contrast(ImageOps.autocontrast(im)).enhance(1.3)
    ramp = ' .,:;irsXA253hMHGS#9B&@'
    s = window('whoami')
    s += '<defs><clipPath id="portrait-bounds"><rect x="20" y="40" width="800" height="800"><animate attributeName="height" values="0;0;800;800" keyTimes="0;0.08;0.58;1" dur="12s" repeatCount="indefinite"/></rect></clipPath></defs><g clip-path="url(#portrait-bounds)">'
    for y in range(96):
        line = ''
        for x in range(180):
            r, g, b = color.getpixel((x, y))
            background = g > r * 1.08 and g > b * 1.04
            line += ' ' if background else ramp[im.getpixel((x,y))*(len(ramp)-1)//255]
        # Explicit glyph coordinates avoid SVG textLength redistributing spaces.
        # Browser whitespace handling must never change the source pixel grid.
        visible = [(x, ch) for x, ch in enumerate(line) if ch != ' ']
        if visible:
            positions = ' '.join(f'{20+x*800/180:.3f}' for x, _ in visible)
            s += text(positions, 47.4+y*(800/96), ''.join(ch for _, ch in visible),
                      7.4, '#c9d1d9', 'class="row"')
    s += '</g>'
    s += text(20, 860, 'Jason Avalos · Dexless', 14)
    return svg(840, 880, s, 'Jason Avalos — animated ASCII GitHub avatar')

def stats_card(stats, days):
    s = window('./stats.sh')
    items = [('current streak', stats['current'], 'days · current streak'),
             ('longest streak', stats['longest'], 'days in this calendar'),
             ('contributions', stats['total'], 'in the last year'),
             ('active days', stats['active'], f'of {len(days)} calendar days'),
             ('best day', stats['best']['count'], stats['best']['date']),
             ('avg / active day', stats['average'], 'contributions')]
    for i, (label, value, caption) in enumerate(items):
        x, y = 20+(i%2)*408, 54+(i//2)*166
        s += f'<g class="reveal" style="animation-delay:{i*.15}s"><rect x="{x}" y="{y}" width="392" height="150" rx="10" fill="#161b22" stroke="#30363d"/>'
        s += text(x+22,y+39,'$ '+label,22)
        s += text(x+22,y+99,f'{value:,}',54,'#39d353' if i == 0 else '#e6edf3')
        s += text(x+22,y+132,caption,17)+'</g>'
    s += '<rect x="20" y="552" width="800" height="308" rx="10" fill="#161b22" stroke="#30363d"/>'
    s += text(44,592,'$ contributions / month',22)
    months = list(stats['monthly'].items())
    peak = max(v for _, v in months) or 1
    for i, (month, count) in enumerate(months):
        step = 752/len(months)
        x = 44+i*step+step*.19
        height = max(2,count/peak*190)
        s += f'<rect class="bar" x="{x:.1f}" y="{816-height:.1f}" width="{step*.62:.1f}" height="{height:.1f}" rx="3" fill="#26a641" style="animation-delay:{1.3+i*.06}s"><title>{month}: {count}</title></rect>'
        s += text(round(x+step*.31,1),844,date.fromisoformat(month+'-01').strftime('%b')[0],18,extra='text-anchor="middle"')
    return svg(840,880,s,'Dexless contribution statistics — trailing year')

def main():
    request = urllib.request.Request(f'https://github.com/users/{USER}/contributions',headers={'User-Agent':'Dexless-profile-art'})
    with urllib.request.urlopen(request,timeout=30) as response:
        raw = response.read().decode()
    parser = Calendar()
    parser.feed(raw)
    days = parser.days()
    stats = summarize(days)
    outputs = {'contrib-heatmap.svg': heatmap(days,stats), 'portrait.svg': portrait(), 'stats.svg': stats_card(stats,days),
               'data/contributions.json':json.dumps(dict(username=USER,days=days,stats=stats),indent=2)+'\n'}
    # Generate everything before replacing any previous successful output.
    for name, content in outputs.items():
        (ROOT/name).write_text(content)
    print(f'Generated {len(days)} real calendar days; {stats["total"]} contributions; {stats["current"]}-day current streak')

if __name__ == '__main__':
    main()
