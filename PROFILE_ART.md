# Profile art

Original Python/SVG implementation, visually inspired by
[AVIVASHISHTA29's profile](https://github.com/AVIVASHISHTA29/AVIVASHISHTA29).
That repository has no explicit license; its implementation and assets have not
been copied. The supplied avatar belongs to Dexless. Profile text and links
come from this repository's previous README.

## Regenerate

Use Python 3.12, install `scripts/requirements.txt`, then run:

```sh
python -m unittest discover -s tests
python scripts/profile_art.py
python scripts/validate.py
```

The public GitHub contribution calendar supplies exact daily counts and color
levels. No personal token or third-party statistics service is needed. Statistics
cover the displayed trailing-year calendar (including partial weeks), not lifetime
activity. A zero-count final day does not end yesterday's current streak. Longest
streak refers only to this calendar. Monthly bars include partial boundary months.
Counts reflect whatever GitHub publicly exposes, which can include anonymized
private contribution counts if enabled in account settings.

The avatar is stored at `assets/avatar.jpg`; replace it to change the portrait.
The generated SVGs contain CSS animations and no scripts or external resources.
Reduced-motion users see the completed artwork immediately. At narrow widths the
paired panels scale with the README table; fine ASCII details will be smaller.

The refresh workflow runs daily and manually. It generates all outputs before
replacing files and fails without committing if GitHub returns invalid data.
Previous successful graphics remain available. There are no push triggers or
recursive update loops. Scheduled updates use Jason's existing GitHub-associated
identity as both author and committer, with no agent or bot co-author trailers.
These commits represent automated refreshes, not manual edits.

GitHub proxies/caches README images; a new commit may take time to appear. CSS
animation is evaluated by the viewer's browser; GitHub does not execute JavaScript.
