"""Generate the HyperFrames composition (index.html) for the full podcast edit."""
import json, re, html, sys
S = sys.argv[1]; OUT = f"{S}/hf/full/index.html"
E = json.load(open("/home/user/Video-Editing/hasil/editing_timeline.json"))
L = json.load(open(f"{S}/out3/lines_final.json"))
TOTAL = E["total"]; SEGS = E["segments"]; SESI = [s for s in SEGS if s["section"] == "sesi"]
def tl_of(T):
    for s in SESI:
        if T < s["a0"]: return s["tl"]
        if s["a0"] <= T <= s["a1"]: return s["tl"] + T - s["a0"]
    return SESI[-1]["tl"] + SESI[-1]["a1"] - SESI[-1]["a0"]
def tl_sec(name, T):
    s = [x for x in SEGS if x["section"] == name][0]; return s["tl"] + T - s["a0"]
G = tl_of
ACC = "#F2B64F"
# ---------- icons: ASS drawing paths -> SVG
ICON = {
 "pin": "m 24 0 b 37 0 46 9 46 21 b 46 34 30 46 24 56 b 18 46 2 34 2 21 b 2 9 11 0 24 0 m 24 12 b 19 12 15 16 15 21 b 15 26 19 30 24 30 b 29 30 33 26 33 21 b 33 16 29 12 24 12",
 "book": "m 2 8 l 22 4 l 24 6 l 26 4 l 46 8 l 46 46 l 26 42 l 24 44 l 22 42 l 2 46 m 6 12 l 6 41 l 21 38 l 21 9 m 27 9 l 27 38 l 42 41 l 42 12",
 "heart": "m 24 46 b 12 36 0 28 0 16 b 0 6 8 0 15 0 b 20 0 23 4 24 6 b 25 4 28 0 33 0 b 40 0 48 6 48 16 b 48 28 36 36 24 46",
 "leaf": "m 4 44 b 4 20 20 4 46 2 b 44 28 30 44 6 44 m 8 42 b 18 30 28 20 38 10 l 36 8 b 26 18 16 28 6 40",
 "phone": "m 12 0 l 36 0 b 40 0 42 2 42 6 l 42 50 b 42 54 40 56 36 56 l 12 56 b 8 56 6 54 6 50 l 6 6 b 6 2 8 0 12 0 m 10 8 l 10 46 l 38 46 l 38 8 m 21 50 l 27 50 l 27 52 l 21 52",
 "scale": "m 23 4 l 25 4 l 25 44 l 34 44 l 34 48 l 14 48 l 14 44 l 23 44 m 4 12 l 44 12 l 44 15 l 4 15 m 4 15 l 0 30 b 2 34 10 34 12 30 l 8 15 m 40 15 l 36 30 b 38 34 46 34 48 30 l 44 15",
 "quote": "m 2 24 b 2 10 8 2 20 0 l 21 4 b 13 7 10 12 10 18 l 20 18 l 20 38 l 2 38 m 28 24 b 28 10 34 2 46 0 l 47 4 b 39 7 36 12 36 18 l 46 18 l 46 38 l 28 38",
 "gift": "m 4 18 l 44 18 l 44 28 l 4 28 m 7 30 l 41 30 l 41 50 l 7 50 m 22 18 l 26 18 l 26 50 l 22 50 m 24 18 b 14 18 8 8 16 6 b 20 5 24 12 24 18 b 24 12 28 5 32 6 b 40 8 34 18 24 18",
 "people": "m 14 10 b 19 10 22 14 22 18 b 22 23 19 26 14 26 b 9 26 6 23 6 18 b 6 14 9 10 14 10 m 0 46 b 0 34 6 29 14 29 b 22 29 28 34 28 46 m 34 12 b 38 12 41 15 41 19 b 41 23 38 26 34 26 b 30 26 27 23 27 19 b 27 15 30 12 34 12 m 30 46 b 30 38 32 30 36 30 b 44 30 48 36 48 46",
 "spark": "m 24 0 l 28 20 l 48 24 l 28 28 l 24 48 l 20 28 l 0 24 l 20 20",
}
def svgpath(a):
    out = []; toks = a.split(); i = 0; cmd = None
    while i < len(toks):
        t = toks[i]
        if t in "mlb": cmd = t; i += 1; continue
        if cmd == "m": out.append(f"M{toks[i]} {toks[i+1]}"); i += 2; cmd = "l"
        elif cmd == "l": out.append(f"L{toks[i]} {toks[i+1]}"); i += 2
        elif cmd == "b": out.append(f"C{' '.join(toks[i:i+6])}"); i += 6
    return " ".join(out) + " Z"
def icon(name, size=44): return f'<svg class="ic" width="{size}" height="{size}" viewBox="-2 -2 52 60"><path d="{svgpath(ICON[name])}" fill="{ACC}" fill-rule="evenodd"/></svg>'
# ---------- collect clips + tweens
HTMLC = []; TW = []; uid = [0]
def nid(p): uid[0] += 1; return f"{p}{uid[0]}"
def clip(a, b, inner, cls="", style="", z=10):
    i = nid("c"); HTMLC.append(f'<div id="{i}" class="clip {cls}" data-start="{a:.3f}" data-duration="{max(b-a,0.05):.3f}" data-track-index="1" style="z-index:{z};{style}">{inner}</div>'); return i
def tw(js): TW.append(js)
def card_in(sel, a, b, dx=40):
    tw(f'tl.fromTo("{sel}",{{opacity:0,x:{dx}}},{{opacity:1,x:0,duration:0.55,ease:"power3.out"}},{a+0.02:.3f});')
    tw(f'tl.to("{sel}",{{opacity:0,x:{dx//2},duration:0.4,ease:"power2.in"}},{b-0.45:.3f});')
def particles(a, b, x, y, w, h, n, seed):
    i = nid("pt"); dots = "".join(f'<i class="pd" id="{i}d{k}"></i>' for k in range(n))
    clip(a, b, dots, "pt", f"left:{x}px;top:{y}px;width:{w}px;height:{h}px;", z=5)
    tw(f'particles("{i}",{n},{w},{h},{a:.3f},{b:.3f},{seed});')
# --- title sequence
i = clip(0.0, 4.9, '<div class="dim"></div><div class="kick" id="tk">PODCAST</div><div class="title" id="tt">Romantisisme</div><div class="tline" id="tln"></div><div class="tsub" id="ts">Antara akal dan perasaan</div>', "full", z=30)
tw('tl.fromTo("#tk",{opacity:0,y:-10,filter:"blur(6px)"},{opacity:1,y:0,filter:"blur(0px)",duration:1.0,ease:"power3.out"},0.1);')
tw('tl.fromTo("#tt",{opacity:0,y:20,filter:"blur(12px)"},{opacity:1,y:0,filter:"blur(0px)",duration:1.1,ease:"power3.out"},0.25);')
tw('tl.fromTo("#tt",{scale:1},{scale:1.04,duration:4.4,ease:"none"},0.25);')
tw('tl.fromTo("#tln",{scaleX:0},{scaleX:1,duration:0.8,ease:"power2.inOut"},0.6);')
tw('tl.fromTo("#ts",{opacity:0,y:12},{opacity:1,y:0,duration:0.8,ease:"power2.out"},0.8);')
tw(f'tl.to("#{i} .dim, #tk, #tt, #tln, #ts",{{opacity:0,duration:0.7,ease:"power2.in"}},4.1);')
particles(0.2, 4.8, 560, 380, 800, 320, 14, 3)
# --- chapter tag + progress (top-left) across the session
CH = [(c["tl"], c["num"], c["title"]) for c in E["chapters"]]
t_end = tl_of(1626.3) - 0.5
for k, (a, n, ttl) in enumerate(CH):
    b = CH[k + 1][0] if k + 1 < len(CH) else t_end
    a2 = max(a, 5.0) + 3.8
    i = clip(a2, b, f'<div class="bug"><span class="bn">{n}</span><span class="bt">{html.escape(ttl.upper())}</span></div>', z=20)
    tw(f'tl.fromTo("#{i} .bug",{{opacity:0,x:-20}},{{opacity:1,x:0,duration:0.5,ease:"power3.out"}},{a2:.3f});')
i = clip(5.0, t_end, '<div class="prog"><div class="pfill" id="pf"></div></div>', z=20)
tw(f'tl.fromTo("#{i} .prog",{{opacity:0}},{{opacity:1,duration:0.6}},5.0);')
tw(f'tl.fromTo("#pf",{{scaleX:{5.0/t_end:.4f}}},{{scaleX:1,duration:{t_end-5.0:.3f},ease:"none"}},5.0);')
# --- chapter cards (over the establishing wide shot)
for (a, n, ttl) in CH:
    a = a + (0.6 if n != "01" else 0.4); b = a + 3.6
    i = clip(a, b, f'<div class="chband"></div><div class="chn">BAB {n}</div><div class="chl"></div><div class="cht">{html.escape(ttl)}</div>', "full", z=25)
    tw(f'tl.fromTo("#{i} .chband",{{opacity:0}},{{opacity:1,duration:0.4}},{a:.3f});')
    tw(f'tl.fromTo("#{i} .chn",{{opacity:0,y:-8,filter:"blur(6px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.7,ease:"power3.out"}},{a:.3f});')
    tw(f'tl.fromTo("#{i} .chl",{{scaleX:0}},{{scaleX:1,duration:0.6,ease:"power2.inOut"}},{a+0.15:.3f});')
    tw(f'tl.fromTo("#{i} .cht",{{opacity:0,y:16,filter:"blur(8px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.7,ease:"power3.out"}},{a+0.25:.3f});')
    tw(f'tl.to("#{i} .chband, #{i} .chn, #{i} .chl, #{i} .cht",{{opacity:0,duration:0.45}},{b-0.5:.3f});')
    particles(a, b, 660, 190, 600, 140, 8, int(a))
# --- lower thirds
def lower3(a, b, name, role, y):
    i = clip(a, b, f'<div class="l3" style="top:{y}px"><div class="acc"></div><div class="l3n">{html.escape(name)}</div><div class="l3r">{role}</div></div>', z=22)
    tw(f'tl.fromTo("#{i} .l3",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:0.55,ease:"power3.out"}},{a:.3f});')
    tw(f'tl.fromTo("#{i} .acc",{{scaleY:0}},{{scaleY:1,duration:0.5,ease:"power2.out"}},{a+0.1:.3f});')
    tw(f'tl.to("#{i} .l3",{{opacity:0,x:-20,duration:0.4}},{b-0.45:.3f});')
lower3(tl_sec("pengenalan", 11.95), tl_sec("pengenalan", 16.6), "Alice Catherine", "PENGACARA", 690)
lower3(tl_sec("pengenalan", 13.35), tl_sec("pengenalan", 17.6), "Muhammad Hasid", "PENGACARA", 815)
lower3(G(41.6), G(48.0), "Dr. Satria Abadi", "TETAMU UNDANGAN", 780)
# --- context graphics (right negative space)
def card(a, b, label, body, ic=None):
    i = clip(a, b, f'<div class="card">{icon(ic) if ic else ""}<div><div class="lab">{label}</div><div class="body">{body}</div></div></div>', z=22)
    card_in(f"#{i} .card", a, b)
    if ic: tw(f'tl.fromTo("#{i} .ic",{{scale:0.6,opacity:0}},{{scale:1,opacity:1,duration:0.5,ease:"back.out(2)"}},{a+0.15:.3f});')
    particles(a, b, 1240, 330, 600, 220, 6, int(a * 10))
def quote(a, b, body, who):
    i = clip(a, b, f'<div class="card quote">{icon("quote", 40)}<div class="qb">{body}</div><div class="qw">— {who}</div></div>', z=22)
    card_in(f"#{i} .card", a, b)
    tw(f'tl.fromTo("#{i} .qb",{{opacity:0,y:10}},{{opacity:1,y:0,duration:0.6,ease:"power2.out"}},{a+0.25:.3f});')
    tw(f'tl.fromTo("#{i} .qw",{{opacity:0}},{{opacity:1,duration:0.5}},{a+0.6:.3f});')
def steps(a, b, title, items):
    rows = "".join(f'<div class="st" id="SID{k}"><div class="dot"></div><div><div class="lab">{l}</div><div class="body s">{t}</div></div></div>' for k, (ta, l, t) in enumerate(items))
    i = clip(a, b, f'<div class="card steps"><div class="lab">{title}</div><div class="rule"></div><div class="stl"><div class="vline"></div>{rows}</div></div>', z=22)
    HTMLC[-1] = HTMLC[-1].replace('id="SID', f'id="{i}s')
    card_in(f"#{i} .card", a, b)
    tw(f'tl.fromTo("#{i} .rule",{{scaleX:0}},{{scaleX:1,duration:0.7,ease:"power2.inOut"}},{a+0.2:.3f});')
    for k, (ta, l, t) in enumerate(items):
        ta = max(ta, a + 0.3)
        tw(f'tl.fromTo("#{i}s{k}",{{opacity:0,x:20}},{{opacity:1,x:0,duration:0.5,ease:"power3.out"}},{ta:.3f});')
    tw(f'tl.fromTo("#{i} .vline",{{scaleY:0}},{{scaleY:1,duration:{max(items[-1][0]-a,0.6):.3f},ease:"power1.inOut"}},{a+0.3:.3f});')
def compare(a, b, title, left, right, t_right, ic=(None, None)):
    col = lambda lab, body, ic_: f'<div class="col">{icon(ic_, 34) if ic_ else ""}<div class="lab">{lab}</div><div class="body s">{body}</div></div>'
    i = clip(a, b, f'<div class="card cmp"><div class="lab">{title}</div><div class="rule"></div><div class="cols">{col(*left, ic[0])}<div class="div"></div>{col(*right, ic[1])}</div></div>', z=22)
    card_in(f"#{i} .card", a, b)
    tw(f'tl.fromTo("#{i} .rule",{{scaleX:0}},{{scaleX:1,duration:0.7,ease:"power2.inOut"}},{a+0.2:.3f});')
    tw(f'tl.fromTo("#{i} .col:first-child",{{opacity:0,y:10}},{{opacity:1,y:0,duration:0.5}},{a+0.35:.3f});')
    tw(f'tl.fromTo("#{i} .div",{{scaleY:0}},{{scaleY:1,duration:0.5}},{t_right:.3f});')
    tw(f'tl.fromTo("#{i} .col:last-child",{{opacity:0,y:10}},{{opacity:1,y:0,duration:0.5}},{t_right+0.1:.3f});')
card(G(49.5), G(57.5), "ASAL", "Bogor, Indonesia", "pin")
steps(G(117.0), G(164.5), "PERJALANAN KERJAYA", [(G(117.5), "2004", "Pensyarah di Indonesia"), (G(129.5), "PENGAJIAN", "PhD"),
      (G(134.5), "PASCADOKTORAL", "Finland · Brunei · Malaysia"), (G(158.5), "KINI", "Pensyarah di Malaysia")])
card(G(191.2), G(199.5), "CITA-CITA SEJAK KECIL", "Menjadi pendidik", "book")
quote(G(273.9), G(284.5), "Tiada batasan untuk<br>mengejar cita-cita.", "Dr. Satria Abadi")
card(G(388.0), G(396.8), "ROMANTISISME", "Luapan perasaan<br>dari dalam diri", "heart")
compare(G(456.0), G(499.5), "DUA CARA MELIHAT ALAM", ("SAINTIS", "Alam bergerak<br>seperti mesin"), ("SUFI / ROMANTIS", "Alam dirasai<br>dengan jiwa"), G(484.0), ("spark", "heart"))
steps(G(519.0), G(581.5), "PENYAIR &amp; PEMIKIR DISEBUT", [(G(519.2), "PENYAIR SUFI", "Jalaluddin Ar-Rumi"), (G(535.0), "PENYAIR SUFI", "Rabiatul Adawiyah"), (G(572.0), "SASTERAWAN", "Hamka")])
compare(G(675.0), G(741.5), "KESEIMBANGAN", ("AKAL", "Menimbang<br>dengan rasional"), ("PERASAAN", "Tanpa akal,<br>menjadi egois"), G(712.0), ("scale", "heart"))
compare(G(866.0), G(891.5), "MELIHAT DAUN YANG GUGUR", ("SAINTIS", "Fotosintesis"), ("ROMANTIS", "Daun berterbangan,<br>menggugurkan rasa"), G(875.0), ("spark", "leaf"))
card(G(908.0), G(925.5), "PEPATAH", "Seperti air di daun keladi", "leaf")
compare(G(984.5), G(1000.5), "BERANI MENJADI DIRI SENDIRI", ("DIRI", "Pendirian sendiri"), ("MASYARAKAT", "Aturan &amp; regulasi"), G(992.0), ("people", "people"))
steps(G(1019.5), G(1062.0), "MELUAHKAN RASA MELALUI KARYA", [(G(1020.0), "PUISI", "Jalaluddin Ar-Rumi"), (G(1024.0), "DARI PENJARA", "Hamka"), (G(1048.0), "SYAIR", "Rabiatul Adawiyah")])
quote(G(1065.0), G(1089.5), "Jika syurga itu untukku,<br>berikan saja kepada<br>orang yang Kau cintai.", "Rabiatul Adawiyah (diceritakan Dr. Satria)")
compare(G(1167.0), G(1215.5), "ROMANTIS DI ERA TEKNOLOGI", ("MEDIA SOSIAL", "Meniru orang lain"), ("ROMANTIS SEBENAR", "Luapan emosi<br>diri sendiri"), G(1188.0), ("phone", "heart"))
card(G(1238.5), G(1270.5), "INTI PANDANGAN", "Romantis ditunjukkan<br>melalui perbuatan", "heart")
card(G(1325.5), G(1333.2), "ROMANTIS", "Tak perlu selalu berpuisi", "spark")
steps(G(1440.0), G(1530.5), "TIGA RASA YANG BERBEZA", [(G(1440.5), "EMPATI", "Merasakan situasi orang lain"), (G(1459.0), "BELAS KASIHAN", "Muncul pada orang yang dekat"), (G(1495.0), "SIMPATI", "Sekadar rasa suka")])
card(G(1546.5), G(1577.5), "BUAH TANGAN", "Kenang-kenangan untuk tetamu", "gift")
# --- end card
te = TOTAL; a = te - 4.5 + 0.6
i = clip(a, te, '<div class="end"><div class="et">Terima kasih</div><div class="tline e"></div><div class="ec">TETAMU · DR. SATRIA ABADI</div><div class="ec">PENGACARA · ALICE CATHERINE &amp; MUHAMMAD HASID</div><div class="ek">PODCAST · ROMANTISISME</div></div>', "full", z=30)
tw(f'tl.fromTo("#{i} .et",{{opacity:0,y:16,filter:"blur(10px)"}},{{opacity:1,y:0,filter:"blur(0px)",duration:0.9,ease:"power3.out"}},{a:.3f});')
tw(f'tl.fromTo("#{i} .tline",{{scaleX:0}},{{scaleX:1,duration:0.7,ease:"power2.inOut"}},{a+0.3:.3f});')
tw(f'tl.fromTo("#{i} .ec, #{i} .ek",{{opacity:0,y:8}},{{opacity:1,y:0,duration:0.6,stagger:0.2}},{a+0.5:.3f});')
particles(a, te, 560, 380, 800, 320, 12, 9)
# --- subtitles: phrase reveal + selective keyword highlight
KEYW = ["romantisisme", "romantisme", "romantis", "akal", "perasaan", "empati", "simpati", "belas kasihan", "falsafah", "filosofi", "alam",
        "cinta", "mencintai", "jiwa", "puisi", "syair", "penyair", "keseimbangan", "teknologi", "media sosial", "perbuatan", "egois",
        "Jalaluddin Ar-Rumi", "Rabiatul Adawiyah", "Hamka", "Satria Abadi", "Bogor", "Indonesia", "Malaysia", "pendidik", "cita-cita",
        "sufi", "saintis", "daun keladi", "buah tangan", "luapan", "kebahagiaan"]
KRE = re.compile(r"(?<![\w-])(" + "|".join(sorted(map(re.escape, KEYW), key=len, reverse=True)) + r")(?![\w-])", re.I)
subs = []
for l in L:
    a, b = l["show"]; t = html.escape(l["text"])
    t = KRE.sub(lambda m: f'<b>{m.group(0)}</b>', t)
    sid = nid("s"); subs.append(f'<div id="{sid}" class="clip sub" data-start="{a:.3f}" data-duration="{max(b-a,0.1):.3f}" data-track-index="2"><span>{t}</span></div>')
    tw(f'tl.fromTo("#{sid} span",{{opacity:0,y:8}},{{opacity:1,y:0,duration:0.16,ease:"power2.out"}},{a:.3f});')
    tw(f'tl.to("#{sid} span",{{opacity:0,duration:0.12}},{max(b-0.13,a+0.17):.3f});')
CSS = f"""
html,body{{margin:0;background:transparent}}
#main{{position:relative;width:1920px;height:1080px;overflow:hidden;font-family:Inter,sans-serif;color:#fff}}
.clip{{position:absolute;left:0;top:0;width:1920px;height:1080px}}
.full{{inset:0}}
.dim{{position:absolute;inset:0;background:rgba(0,0,0,.45)}}
.kick{{position:absolute;left:0;right:0;top:420px;text-align:center;color:{ACC};font-weight:700;font-size:28px;letter-spacing:10px}}
.title{{position:absolute;left:0;right:0;top:468px;text-align:center;font-weight:700;font-size:104px;letter-spacing:1px;text-shadow:0 6px 40px rgba(0,0,0,.5)}}
.tline{{position:absolute;left:900px;top:600px;width:120px;height:3px;background:{ACC};transform-origin:center}}
.tline.e{{top:478px}}
.tsub{{position:absolute;left:0;right:0;top:626px;text-align:center;color:{ACC};font-weight:400;font-size:30px;letter-spacing:3px}}
.bug{{position:absolute;left:44px;top:38px;padding:14px 22px 22px;border-radius:12px;background:rgba(16,20,26,.55);backdrop-filter:blur(10px);font-weight:700;font-size:20px;letter-spacing:3px;min-width:240px}}
.bn{{color:{ACC};margin-right:14px}} .bt{{color:rgba(255,255,255,.85)}}
.prog{{position:absolute;left:66px;top:92px;width:240px;height:3px;background:rgba(255,255,255,.22);border-radius:2px;overflow:hidden}}
.pfill{{width:100%;height:100%;background:{ACC};transform-origin:left center}}
.chband{{position:absolute;left:360px;top:70px;width:1200px;height:280px;background:radial-gradient(ellipse at center,rgba(0,0,0,.5),rgba(0,0,0,0) 70%)}}
.chn{{position:absolute;left:0;right:0;top:150px;text-align:center;color:{ACC};font-weight:700;font-size:24px;letter-spacing:8px}}
.chl{{position:absolute;left:900px;top:196px;width:120px;height:3px;background:{ACC}}}
.cht{{position:absolute;left:0;right:0;top:214px;text-align:center;font-weight:700;font-size:64px;text-shadow:0 4px 30px rgba(0,0,0,.6)}}
.l3{{position:absolute;left:90px;padding:16px 36px 18px 34px;border-radius:14px;background:rgba(16,20,26,.62);backdrop-filter:blur(12px)}}
.acc{{position:absolute;left:0;top:14px;bottom:14px;width:5px;background:{ACC};border-radius:3px;transform-origin:center top}}
.l3n{{font-weight:700;font-size:40px}} .l3r{{color:{ACC};font-weight:700;font-size:22px;letter-spacing:3px;margin-top:6px}}
.card{{position:absolute;right:80px;top:130px;display:flex;gap:22px;align-items:center;padding:22px 34px 24px 30px;border-radius:16px;background:rgba(16,20,26,.60);backdrop-filter:blur(14px);border-left:5px solid {ACC};box-shadow:0 18px 50px rgba(0,0,0,.35)}}
.lab{{color:{ACC};font-weight:700;font-size:20px;letter-spacing:3px}}
.body{{font-weight:700;font-size:38px;line-height:1.22;margin-top:8px}} .body.s{{font-size:31px}}
.quote{{flex-direction:column;align-items:flex-start;gap:10px}} .qb{{font-weight:700;font-size:38px;line-height:1.25}} .qw{{color:{ACC};font-size:20px;letter-spacing:2px}}
.steps,.cmp{{flex-direction:column;align-items:stretch;gap:0}}
.rule{{height:1px;background:rgba(255,255,255,.45);margin:12px 0 14px;transform-origin:left center}}
.stl{{position:relative;padding-left:4px}} .vline{{position:absolute;left:9px;top:12px;bottom:30px;width:2px;background:rgba(242,182,79,.5);transform-origin:center top}}
.st{{display:flex;gap:20px;align-items:flex-start;margin:6px 0 14px}} .dot{{width:12px;height:12px;border-radius:6px;background:{ACC};margin-top:8px;flex:none;position:relative;left:4px}}
.cols{{display:flex;gap:30px}} .col{{min-width:250px}} .col .ic{{display:block;margin-bottom:6px}} .div{{width:2px;background:rgba(242,182,79,.55);transform-origin:center top}}
.end{{position:absolute;inset:0;text-align:center}} .et{{position:absolute;left:0;right:0;top:380px;font-weight:700;font-size:64px}}
.ec{{position:relative;top:520px;color:{ACC};font-weight:700;font-size:24px;letter-spacing:3px;margin-bottom:18px}} .ek{{position:relative;top:560px;color:#ddd;font-size:22px;letter-spacing:6px}}
.pt{{position:absolute}} .pd{{position:absolute;width:6px;height:6px;border-radius:3px;background:{ACC};opacity:0;filter:blur(1px)}}
.band{{position:absolute;left:0;right:0;bottom:0;height:260px;background:linear-gradient(to top,rgba(0,0,0,.45),rgba(0,0,0,0))}}
.sub{{display:flex;align-items:flex-end;justify-content:center;z-index:40}}
.sub span{{display:inline-block;margin-bottom:64px;max-width:1500px;text-align:center;font-weight:700;font-size:48px;letter-spacing:.3px;
  text-shadow:0 0 6px rgba(0,0,0,.85),0 2px 14px rgba(0,0,0,.75)}}
.sub b{{color:{ACC};font-weight:700}}
"""
JS_PART = """
function mulberry(a){return function(){a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;}}
function particles(id,n,w,h,a,b,seed){const r=mulberry(seed+1);for(let k=0;k<n;k++){const el='#'+id+'d'+k;const x=r()*w,y=r()*h,dy=-(25+r()*35),dx=(r()-.5)*30,s=.6+r()*.9;
 tl.fromTo(el,{x:x,y:y,opacity:0,scale:s},{x:x+dx,y:y+dy,opacity:.55,duration:Math.min(.9,(b-a)/2),ease:'sine.out'},a);
 tl.to(el,{x:x+dx*2,y:y+dy*2,opacity:0,duration:Math.max(.4,(b-a)/2-.05),ease:'sine.in'},a+Math.min(.9,(b-a)/2));}}
"""
doc = f"""<!doctype html>
<html><head><meta charset="utf-8"><script src="assets/gsap.min.js"></script><style>{CSS}</style></head>
<body>
<div id="main" data-composition-id="main" data-start="0" data-duration="{TOTAL:.3f}" data-width="1920" data-height="1080">
<div id="bandc" class="clip" data-start="0" data-duration="{TOTAL:.3f}" data-track-index="1" style="z-index:3"><div class="band"></div></div>
{chr(10).join(HTMLC)}
{chr(10).join(subs)}
</div>
<script>
const tl = gsap.timeline({{ paused: true }});
{JS_PART}
{chr(10).join(TW)}
window.__timelines["main"] = tl;
</script>
</body></html>"""
open(OUT, "w").write(doc)
print("clips", len(HTMLC), "subs", len(subs), "tweens", len(TW), "bytes", len(doc))
