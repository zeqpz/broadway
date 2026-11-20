"""iOS crash at load (Engine live test, 2026-11-20: "repeatedly crashes and fails to load on mobile Safari ... 'A problem
repeatedly occurred' ... iPhone 12, iOS 18.6.2") - the page's side, applied by reskin_outage.py after pass 6.

That message is Safari giving up after its WebContent process was killed several times running, on an iPhone 12 for
memory (the game shares the process with the casino page round its iframe). The sister games met it and were fixed
(zeqpz/fallslotsga de81ebf / 9694dd3 / 9c3ac82, zeqpz/slotsgame 53a4fb5, zeqpz/orleans 2ef6d35 .. ff43083): a phone
tier (window.MOBILE, html.mob) with no live canvases beside the board, no particle effects, no 3D transforms, no
filters or blend modes, nothing animating at idle, and only the phone's own art fetched. On iOS every 2D canvas and
every animating or 3D-transformed element is a GPU layer at its LAYOUT size x DPR^2, and whatever is drawn over one is
pushed onto layers of its own.

Power Outage was forked from orleans after those fixes, but the owner passes since then (2 - 5) were built and checked
on desktop and put some of it back on phones. Measured against orleans' phone tier (tools/review/memprobe/iosprobe3.py,
iPhone 390x844 @3):
  - frontend/cable.js: a 1120 x 1558 px canvas (7 MB) redrawn every frame, under the whole frame        -> a still <img>
  - frontend/spark.js: a 1121 x 1208 px canvas (5.4 MB) over the frame's corner                         -> not run
  - the breaker's handle: a 3D transform (perspective + rotateX)                                         -> a 2D flip
  - the bonus emblem's bob: a second always-running animation                                            -> off
  - the Surge's value: a five-step drop-shadow chain marked !important, so it beat the phone tier's
    "no filters" rule (software-painted on a tile), plus two always-running animations                   -> off
  - the preloader fetched and held desktop-only art: the 4K Xtreme room (33 MB once painted), and the
    title sign's four pictures were built (and fetched) though a phone never shows the sign              -> never fetched
  - the win line's bolt: sparks and a redraw every 55 ms                                                 -> no sparks, 110 ms
Everything here is behind html.mob / window.MOBILE: desktop is unchanged."""

CSS = '''  /* ---- iOS crash at load (Engine live test, 2026-11-20): the phone tier back to the sister games' rules ---- */
  /* no spark canvas, no cord handle (frontend/spark.js and cable.js do not make them on a phone; belt and braces) */
  html.mob #sparkbox { display: none !important; }
  html.mob #cablebox .cablegrab { display: none !important; }
  /* the breaker: a flat flip about its pivot instead of a 3D rock - the same two poses, no 3D layer, no transition */
  html.mob #leverbox img { transform: none !important; transition: none !important; }
  html.mob body.poweron #leverbox img { transform: scaleY(-1) !important; }
  /* nothing bobbing at idle beside what orleans' phone tier already had */
  html.mob .bonusbtn::after { animation: none !important; }
  /* the Surge's own value: no filter chain on a tile, no always-running animations (the rules above it are
     !important, so the phone tier's blanket "filter: none" lost to them) */
  html.mob .cell.booster .multface .mv { filter: none !important; animation: none !important; }
  html.mob .cell.booster .multface .mv .vg { animation: none !important; }
  /* the win line throws no sparks on a phone (drawWinLine makes none there) */
  html.mob .lineLayer b { display: none !important; }
  /* (bonus crashes, Engine 2026-11-20 second test) the board itself never animates on a phone. WebKit does not zoom
     viewport units, so the phone's zoom fit falls back to transform: scale(~.33) there and any animating element is a
     GPU layer at its LAYOUT size x DPR^2 - the board is 980 x 810 layout px = 29 MB, and everything drawn over it
     (the frame's bars, the values, the bar) is pushed onto layers of its own. The board leaned in (scale) as a bonus
     was about to trigger and was knocked on every landing: no lean-in and no transition here; the knock is off in
     script (Knock.kick) */
  html.mob #board, html.mob .board, html.mob .board.zoomin { scale: 1 !important; transition: none !important; animation: none !important; }
  /* the other screen-sized fades a bonus brings: the bonus intro's own fade (9 MB as a layer), the win line's sheet
     fading out (10 MB), the emblem's drift - cut, not faded, on a phone */
  html.mob .bonusintro { transition: none !important; }
  html.mob .lineLayer .lsheet.out { transition: none !important; }
  html.mob .bonusbtn { animation: none !important; }
'''


def apply(d):
    """The page edits (index.html), after every earlier pass."""
    # no knock on a phone: the board (and the wall) hold still - see the CSS note above
    d.rep("""    const B = BODY[name], el = $(B.id);
    if (!el || REDUCED_MOTION) return;""", """    const B = BODY[name], el = $(B.id);
    if (!el || REDUCED_MOTION || window.MOBILE) return;   // (phones: nothing as big as the board animates - bonus crashes, 2026-11-20)""")
    # a phone never fetches the desktop's Xtreme room or the title sign (the preloader reads every url() in the
    # stylesheets and holds what it fetched; the rule that kept other tiers' art out named only the base room)
    d.rep(r'''  const OTHER_TIER = window.MOBILE ? /assets\/(bonus_wall\.webp|bg\/|chars\/)/ : /assets\/mobile\//;''',
          r'''  const OTHER_TIER = window.MOBILE ? /assets\/(bonus_wall(_xtreme)?\.webp|logo_sign|bg\/|chars\/)/ : /assets\/mobile\//;   // (2026-11-20: + the Xtreme room, the sign)''')
