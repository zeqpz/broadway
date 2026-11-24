"""Engine review fixes (2026-11-20) - the page's side, applied by reskin_outage.py after pass 5:
  - "scrolling in both horizontal and vertical directions is not allowed": on a narrow phone (300 px wide) the
    rules panel's Game Modes table ran 47 px past the panel, so the panel scrolled sideways as well as down. The
    panels that share .infopanel (rules, replay, error) now scroll up and down only, and their tables wrap to fit.
  - the paytable's pay chips no longer clip their text on phones (they drop to one per row when two don't fit).
The other half of the review (the lobby tiles' separate background / foreground, brighter) is tools/broadway/gen_tiles.py."""

CSS = '''  /* ---- engine review, 2026-11-20: one scroll direction only ---- */
  /* the rules, replay and error panels scroll up and down, never sideways: nothing in them may be wider than the
     panel (Engine saw a sideways scrollbar on a 300 px phone - the Game Modes table ran past the panel). The tables'
     cells wrap instead, and the panels cannot scroll sideways at all. */
  html .infopanel { overflow-x: hidden; overflow-y: auto; overscroll-behavior: contain; }
  html .infopanel .tbl { overflow-x: visible; }
  html .infopanel table { width: 100%; max-width: 100%; }
  html .infopanel table td, html .infopanel table th { overflow-wrap: anywhere; min-width: 0; }
  html .infopanel table.guide td:first-child { white-space: normal; }
  html .infopanel img, html .infopanel svg, html .infopanel canvas { max-width: 100%; }
  /* the paytable's pay chips ("16-25 x400 $400.00") were cut inside their fixed half-width cells on phones (a 75 px
     cell for 136 px of text at 300 px wide, 113 px at 375): two to a row while both fit, one to a row when not, and
     only past the whole row does a chip's text wrap - never clipped */
  html .infopanel .pvals { display: flex; flex-wrap: wrap; }
  html .infopanel .pvals > div { flex: 1 1 calc(50% - 3px); min-width: fit-content; max-width: 100%; box-sizing: border-box;
    white-space: normal; overflow: visible; }
  @media (max-width: 420px) {
    html .infopanel table.modes td, html .infopanel table.modes th, html .infopanel table.guide td,
    html .infopanel table.hist td, html .infopanel table.hist th { padding-left: 7px; padding-right: 7px; }
    html .infopanel table.modes th, html .infopanel table.hist th { letter-spacing: .06em; }
    html .infopanel table.hist td, html .infopanel table.hist th { white-space: normal; }
  }
'''
