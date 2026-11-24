# ---- rules.js: review fixes (2026-11-22)
r.rep("""    if (sym === "M") return `<div class="ptile multi"><span>x5</span><small>MULTI</small></div>`;""",
      """    if (sym === "M") return `<img class="ptile" src="${art("assets/flat/M3.webp")}" alt="${esc(T("Gold Record", social))}" draggable="false">`;""")
r.rep("Gold Records land more often than in the base game and Hit Parades far more often",
      "Hit Parades land far more often than in the base game")
r.rep("Gold Records land more often still, every Gold Record is worth x2 or more", "every Gold Record is worth x2 or more")
r.rep("and every copy of one regular symbol (Horseshoe, Guitar Pick or Harmonica) on the board turns into it.",
      "and every copy of one regular symbol (Horseshoe, Guitar Pick or Harmonica) that has at least 3 copies on the board turns into it.")
r.rep('''<div class="pname">${t("Hit Parade and Sold-Out Show")}''', '''<div class="pname">${t("Record colours")}</div>
    <div class="ptext">${t("A Gold Record's disc shows how much it is worth: bronze up to x2, silver up to x5, gold up to x20, platinum up to x100, and diamond (pink) above x100.")}</div></div>
  <div class="prow">${tile("M")}<div class="pname">${t("Hit Parade and Sold-Out Show")}''')
