"""Full-video timeline, subtitles and motion graphics builder."""
import json, sys, re, os, numpy as np
from PIL import ImageFont
S = sys.argv[1]; OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
FPS = 30
sync = json.load(open(f"{S}/sync.json"))

# ------------------------------------------------------------------ sources
MAINS = {  # name: file, offset, valid master range
    "main":  dict(file="IMG_2836.mov", offset=11.818, lo=11.9, hi=616.9),
    "main2": dict(file="main2.mov", offset=611.777, lo=611.9, hi=1215.0),
    "main3a": dict(file="main3.mov", offset=1211.376, lo=1215.0, hi=1377.45),
    "main3b": dict(file="main3.mov", offset=1211.428, lo=1375.5, hi=1626.6),
}
LUTOF = {"main": "main", "main2": "main2", "main3a": "main3", "main3b": "main3"}
SRC = {}
for k, v in MAINS.items():
    SRC[k] = dict(file=v["file"], offset=v["offset"], hdr=True, lut=LUTOF[k], lo=v["lo"], hi=v["hi"])
ANG = "3709 3710 3717 3718 3720 3721 3722 3724 3725 3726 3727 3728 3730 3731 3733 3734 3735 3737".split()
for c in ANG:
    v = sync[f"IMG_{c}"]
    SRC[c] = dict(file=f"IMG_{c}.MOV", offset=v["offset"], hdr=False, lut=c, lo=v["offset"] + 0.05, hi=v["offset"] + v["dur"] - 0.1, master=v["master"])
FULL = (0, 0, 3840, 2160); BW, BH = 2112, 1188
def face_rect(cx, cy, pos):
    x0 = int(min(max(cx - pos * BW, 0), 3840 - BW)); y0 = int(min(max(cy - 0.33 * BH, 0), 2160 - BH))
    return [x0 & ~1, y0 & ~1, BW, BH]
GEN = {"WIDE": (FULL, "wide"), "CU_D": (face_rect(700, 1140, .38), "cu"), "CU_H": (face_rect(2300, 1135, .62), "cu"), "CU_A": (face_rect(3065, 1135, .62), "cu")}
EXTRA = {"3710": ("3710", FULL, "angle"), "3710_H": ("3710", face_rect(1165, 935, .40), "cu"), "3710_A": ("3710", face_rect(2776, 976, .60), "cu"),
         "3709": ("3709", FULL, "angle"), "3709_A": ("3709", face_rect(2736, 993, .60), "cu")}
def resolve(view, T, L):
    """return (src, rect, kind, available seconds) for a view at master time T"""
    if view in GEN:
        best = None
        for m in MAINS:
            s = SRC[m]
            if s["lo"] <= T < s["hi"]:
                av = s["hi"] - T
                if best is None or av > best[3]: best = (m, GEN[view][0], GEN[view][1], av)
        return best
    if view in EXTRA:
        src, rect, kind = EXTRA[view]; s = SRC[src]
    else:
        src, rect, kind = view, FULL, "angle"; s = SRC[view]
        if s.get("master") != "sesi_podcast": return None
    return (src, rect, kind, s["hi"] - T) if s["lo"] <= T < s["hi"] else None

# ------------------------------------------------------------------ edit decisions (session master time)
KEEP = [(11.95, 604.45), (661.95, 766.3), (805.2, 1125.3), (1155.2, 1333.3), (1369.45, 1531.7), (1542.3, 1626.3)]
CUTS_WHY = {(604.45, 661.95): "Alice's fumbled first attempt at the question / restart",
            (766.3, 805.2): "off-script chatter between questions",
            (1125.3, 1155.2): "host restarting the last question twice",
            (1333.3, 1369.45): "false ending + off-mic crew chatter before the empathy topic",
            (1531.7, 1542.3): "off-topic chatter"}
# speaker regions: default male speaker, female (Alice) by pitch
REGIONS = [(11.95, 26.0, 'H'), (26.0, 28.6, 'D'), (28.6, 41.3, 'H'), (41.3, 65.5, 'D'), (65.5, 68.0, 'H'), (68.0, 95.5, 'D'),
           (95.5, 100.2, 'H'), (100.2, 106.5, 'D'), (106.5, 111.6, 'H'), (111.6, 165.0, 'D'), (165.0, 173.5, 'H'), (173.5, 229.9, 'D'),
           (229.9, 238.7, 'H'), (238.7, 251.8, 'A'), (251.8, 264.8, 'H'), (264.8, 302.7, 'D'), (302.7, 323.0, 'H'), (323.0, 355.0, 'A'),
           (355.0, 377.0, 'H'), (377.0, 599.6, 'D'), (599.6, 604.45, 'A'),
           (661.95, 672.6, 'H'), (672.6, 742.6, 'D'), (742.6, 749.0, 'H'), (749.0, 766.4, 'D'),
           (805.2, 835.6, 'H'), (835.6, 926.8, 'D'), (926.8, 928.3, 'H'), (928.3, 938.5, 'D'), (938.5, 940.2, 'H'), (940.2, 948.8, 'D'),
           (948.8, 978.8, 'H'), (978.8, 1112.2, 'D'), (1112.2, 1125.3, 'H'), (1155.2, 1166.8, 'H'), (1166.8, 1272.0, 'D'),
           (1272.0, 1315.6, 'H'), (1315.6, 1333.3, 'D'), (1369.45, 1531.7, 'D'), (1542.3, 1551.5, 'H'), (1551.5, 1580.0, 'D'),
           (1580.0, 1626.3, 'H')]
FEMALE_ONLY = [(238.7, 251.8), (323.0, 355.0), (599.6, 604.45)]

# ------------------------------------------------------------------ transcript words (large-v3)
import difflib
def _norm(w): return re.sub(r"[^a-z0-9]", "", w.lower())
def _raw(dirn, name):
    d = json.load(open(f"{S}/{dirn}/{name}.json")); return [[a, b, w.strip(), p] for sg in d["segments"] for a, b, w, p in sg["words"] if w.strip()]
def load_words(name):
    big = _raw(os.environ.get("TRL", "trl"), name); med = _raw("trm", name)
    sm = difflib.SequenceMatcher(None, [_norm(w[2]) for w in big], [_norm(w[2]) for w in med], autojunk=False)
    anchor = {}
    for blk in sm.get_matching_blocks():
        for k in range(blk.size): anchor[blk.a + k] = med[blk.b + k]
    idx = sorted(anchor)
    for i, w in enumerate(big):
        if i in anchor: w[0], w[1] = anchor[i][0], anchor[i][1]; continue
        lo = max([j for j in idx if j < i], default=None); hi = min([j for j in idx if j > i], default=None)
        if lo is not None and hi is not None:
            ob0, ob1 = big[lo][2+0] if False else None, None
            # interpolate inside the gap between anchored neighbours (by original large-v3 spacing)
            A0, A1 = anchor[lo][1], anchor[hi][0]; n = hi - lo
            w[0] = A0 + (A1 - A0) * (i - lo - 0.5) / n; w[1] = A0 + (A1 - A0) * (i - lo + 0.4) / n
        elif lo is not None: d_ = anchor[lo][1] - _ORIG[name][lo][1] if False else 0; w[0] += 0; w[1] += 0
    W = []
    for a, b, w, p in big:
        if w.startswith("-") and W: W[-1][1] = b; W[-1][2] += w; continue
        W.append([a, b, w, p])
    return W
def _unused(name):
    d = json.load(open(f"{S}/{os.environ.get("TRL","trl")}/{name}.json")); W = []
    for sg in d["segments"]:
        for a, b, w, p in sg["words"]:
            w = w.strip()
            if not w: continue
            if w.startswith("-") and W: W[-1][1] = b; W[-1][2] += w; continue
            W.append([a, b, w, p])
    return W
WS = load_words("sesi_podcast")
# pitch per word-run to detect Alice
import librosa
y16, _ = librosa.load(f"{S}/a16/sesi_podcast.wav", sr=16000)
def f0_of(a, b, y=y16):
    x = y[int(a * 16000):int(b * 16000)]
    if len(x) < 1600: return 0
    f = librosa.yin(x, fmin=70, fmax=400, sr=16000); return float(np.median(f))
def region_spk(T):
    for a, b, s in REGIONS:
        if a <= T < b: return s
    return 'D'

# pause tightening inside keep ranges: gaps > 1.4 s shrink to 0.5 s
KEEP2 = []
for a, b in KEEP:
    ws = [w for w in WS if a <= w[0] < b]; segs = []; cur = a
    for i in range(1, len(ws)):
        g0, g1 = ws[i - 1][1], ws[i][0]
        if g1 - g0 > 1.4 and g0 - cur > 2.5 and b - g1 > 2.5:
            segs.append((cur, g0 + 0.25)); cur = g1 - 0.25
    segs.append((cur, b)); KEEP2 += segs
# timeline
SECT = [("intro", "intro", 9.0, 33.6), ("pengenalan", "pengenalan_diri", 0.06, 17.9)]
GAP = 0.35; TAIL = 4.5
segs = []  # (section, audio, a0, a1, tl0)
t = 0.0
for n, f, a0, a1 in SECT:
    segs.append((n, f, a0, a1, t)); t += (a1 - a0) + GAP
for a0, a1 in KEEP2:
    segs.append(("sesi", "sesi_podcast", a0, a1, t)); t += (a1 - a0)
TOTAL = round((t + TAIL) * FPS) / FPS
SESI = [s for s in segs if s[0] == "sesi"]
def tl_of(T):
    for n, f, a0, a1, t0 in SESI:
        if T < a0: return t0
        if a0 <= T <= a1: return t0 + T - a0
    return SESI[-1][4] + SESI[-1][3] - SESI[-1][2]
def tl_sec(name, T):
    for n, f, a0, a1, t0 in segs:
        if n == name: return t0 + T - a0

# ------------------------------------------------------------------ chapters / diagrams (master T)
CHAPTERS = [(11.95, "01", "Mengenali Tetamu"), (314.0, "02", "Apa Itu Romantisisme?"), (661.95, "03", "Akal & Perasaan"),
            (805.2, "04", "Manusia & Alam"), (958.0, "05", "Berani Menjadi Diri Sendiri"), (1116.5, "06", "Romantisisme Masa Kini"),
            (1369.45, "07", "Empati"), (1542.3, "08", "Penutup")]
DIAG_WIN = [(49.0, 58.0), (116.5, 165.0), (190.5, 200.0), (273.5, 285.0), (387.5, 397.0), (455.5, 500.0), (518.5, 582.0),
            (675.0, 742.0), (866.0, 892.0), (907.0, 926.0), (984.0, 1001.0), (1019.0, 1090.0), (1167.0, 1216.0), (1238.0, 1271.0),
            (1325.0, 1333.3), (1440.0, 1530.0), (1546.0, 1578.0)]
def in_diag(T0, T1):
    return any(a < T1 and T0 < b for a, b in DIAG_WIN)
DLEFT = {"CU_D", "3718", "3721", "3722", "3725", "3727", "3728", "3731", "3733", "3734", "3735", "3737"}

# ------------------------------------------------------------------ shot plan
shots = []
def add_shot(view, sec, T0, T1, src, rect, kind, zoom, fin=0, fout=0):
    tl0 = tl_sec(sec, T0) if sec != "sesi" else tl_of(T0)
    if view == "BLACK":
        shots.append(dict(view="BLACK", tl=round(tl0, 4), dur=round(T1 - T0, 4))); return
    s = SRC[src]
    shots.append(dict(view=view, src=src, file=s["file"], hdr=s["hdr"], lut=s["lut"], src_in=round(T0 - s["offset"], 4),
                      dur=round(T1 - T0, 4), tl=round(tl0, 4), rect=list(rect), kind=kind, zoom=list(zoom), fade_in=fin,
                      fade_out=fout, master_T=round(T0, 3)))
def xv(view):  # helper for intro sections
    src, rect, kind = EXTRA[view]; return view, src, rect, kind
for v, a, b, z, fi, fo in [("3710", 9.45, 16.5, (1, 1.07), .8, 0), ("3710_H", 16.5, 25.3, (1.1, 1.0), 0, 0), ("3710", 25.3, 30.3, (1, 1), 0, 0),
                           ("3710_A", 30.3, 33.6, (1, 1.06), 0, .3)]:
    vv, src, rect, kind = xv(v); add_shot(vv, "intro", a, b, src, rect, kind, z, fi, fo)
add_shot("BLACK", "intro", 9.0, 9.45, None, None, None, None)
for v, a, b, z, fi, fo in [("3709", 0.06, 7.8, (1, 1.07), .3, 0), ("3709_A", 7.8, 13.15, (1.08, 1.0), 0, 0), ("3709", 13.15, 17.9, (1, 1.05), 0, .3)]:
    vv, src, rect, kind = xv(v); add_shot(vv, "pengenalan", a, b, src, rect, kind, z, fi, fo)

# turns: merge regions into turns; sub-2s turns absorbed
TURNS = []
for a, b, s in REGIONS:
    if TURNS and TURNS[-1][2] == s: TURNS[-1][1] = b
    else: TURNS.append([a, b, s])
T2 = []
for tr in TURNS:  # absorb turns shorter than 2 s into the previous turn
    if T2 and tr[1] - tr[0] < 2.0: T2[-1][1] = tr[1]
    elif T2 and T2[-1][2] == tr[2]: T2[-1][1] = tr[1]
    else: T2.append(list(tr))
TURNS = T2
def turn_spk(T):
    for a, b, s in TURNS:
        if a <= T < b: return s
    return 'D'
CAND = {'D': ["3718", "3721", "3722", "3725", "3727", "3728", "3730", "3731", "3733", "3734", "3735", "3737", "CU_D", "WIDE"],
        'H': ["3717", "3720", "3725", "3726", "CU_H", "WIDE"], 'A': ["3724", "3726", "CU_A", "WIDE"]}
LENS = {'D': [6.5, 8.0, 5.5, 7.0, 9.0], 'H': [5.0, 6.5, 4.5], 'A': [5.0, 6.0]}
ZPAT = {"wide": [(1, 1.12), (1, 1), (1.12, 1), (1.15, 1.15)], "cu": [(1, 1.1), (1, 1), (1.1, 1), (1, 1)],
        "angle": [(1, 1.08), (1, 1), (1.1, 1), (1.18, 1.18)]}
chap_T = [c[0] for c in CHAPTERS]
hist = []; zi = 0; li = 0; react_i = 0
plan = []  # (T0, T1, view)
for ka, kb in KEEP2:
    t = ka; first = True
    while kb - t > 0.05:
        # speaker at t and end of their turn (cut 3 frames early on speaker change)
        sp = turn_spk(t + 0.15)
        nxt = kb
        for a, b, s in TURNS:
            if a > t + 0.2 and s != sp: nxt = min(nxt, a - 0.1); break
        nxt = max(nxt, t + 0.1)
        rem = nxt - t
        if rem < 2.0 and kb - t > rem + 0.05 and plan and not first:  # tiny turn: extend previous decision
            pass
        L = LENS[sp][li % len(LENS[sp])]; li += 1
        forced = None
        if any(abs(t - c) < 0.3 for c in chap_T) and t > 20: forced = "WIDE"; L = min(rem, 4.5)
        # reaction shot inside long Dr turns
        turn_len = next((b - a for a, b, s in TURNS if a <= t + 0.15 < b), 0)
        if forced is None and sp == 'D' and turn_len > 25 and not in_diag(t, t + 3) and len(hist) and hist[-1] not in ("CU_H", "CU_A") \
                and plan and (t - plan[-1][0]) > 0 and react_i % 4 == 3 and rem > 9:
            forced = "CU_A" if (react_i // 4) % 2 else "CU_H"; L = 2.6
        react_i += 1
        if rem - L < 2.5: L = rem
        cands = [forced] if forced else CAND[sp]
        diag = in_diag(t, t + L)
        best = None
        for i, v in enumerate(cands):
            if diag and not forced and sp == 'D' and v not in DLEFT: continue
            r = resolve(v, t, L)
            if r is None or r[3] < min(L, 2.2): continue
            if hist and hist[-1] == v and not forced: continue
            score = i + 3.0 * hist[-4:].count(v)
            if v == "WIDE" and "WIDE" not in hist[-5:] and len(hist) >= 4: score -= 4
            if r[2] == "angle": score -= 0.8
            if best is None or score < best[0]: best = (score, v, r)
        if best is None:  # fallback: any main view
            for v in ("WIDE", "CU_D", "CU_H"):
                r = resolve(v, t, L)
                if r: best = (0, v, r); break
        if best is None: raise SystemExit(f"no view at T={t:.2f} sp={sp} L={L} forced={forced}")
        v, r = best[1], best[2]
        Ls = min(L, r[3])
        if rem - Ls < 2.0 and r[3] >= rem: Ls = rem
        if kb - (t + Ls) < 2.0 and r[3] >= kb - t: Ls = kb - t
        plan.append((t, t + Ls, v, r)); hist.append(v); t += Ls; first = False
# merge sub-1.8 s shots into neighbours when possible
i = 0
while i < len(plan):
    a, b, v, r = plan[i]
    if b - a < 2.0:
        if i > 0:
            pa, pb, pv, pr = plan[i - 1]
            same_keep = any(ka <= pa and b <= kb + 1e-6 for ka, kb in KEEP2)
            if same_keep and abs(pb - a) < 1e-6 and pr[3] >= b - pa: plan[i - 1] = (pa, b, pv, pr); plan.pop(i); continue
        if i + 1 < len(plan):
            na, nb, nv, nr = plan[i + 1]
            same_keep = any(ka <= a and nb <= kb + 1e-6 for ka, kb in KEEP2)
            rr = resolve(nv, a, nb - a)
            if same_keep and abs(na - b) < 1e-6 and rr and rr[3] >= nb - a and rr[0] == nr[0]:
                plan[i + 1] = (a, nb, nv, rr); plan.pop(i); continue
    i += 1
for i, (a, b, v, r) in enumerate(plan):
    src, rect, kind, av = r
    z = ZPAT[kind][zi % 4]; zi += 1
    if b - a < 3.5: z = (z[0], z[0])
    if v in ("CU_H", "CU_A") and b - a < 3: z = (1, 1)
    last = i == len(plan) - 1
    add_shot(v, "sesi", a, b, src, rect, kind, z, fin=0.35 if i == 0 else 0, fout=1.5 if last else 0)
# black: intro lead, section gaps, tail
for n, f, a0, a1, t0 in segs[:2]:
    shots.append(dict(view="BLACK", tl=round(t0 + a1 - a0, 4), dur=GAP))
shots.append(dict(view="BLACK", tl=round(tl_of(1626.3), 4), dur=TAIL))
shots.sort(key=lambda x: x["tl"])
for i, sh in enumerate(shots):
    nxt = shots[i + 1]["tl"] if i + 1 < len(shots) else TOTAL
    sh["frames"] = round(nxt * FPS) - round(sh["tl"] * FPS); sh["id"] = i

# ------------------------------------------------------------------ subtitle lines
ALLW = []
for n, f, a0, a1, t0 in segs:
    W = load_words(f) if f != "sesi_podcast" else WS
    for a, b, w, p in W:
        if a >= a0 - 0.12 and b <= a1 + 0.15:
            T = a
            spk = region_spk(T) if n == "sesi" else (('H' if a < 30.2 else 'A') if n == "intro" else ('H' if a < 7.85 or 13.1 <= a < 14.3 else 'A'))
            ALLW.append(dict(t0=max(t0, t0 + a - a0), t1=t0 + b - a0, w=w, n=n, T=a, spk=spk))
# group to lines (speaker-aware; <= 42 chars; break on pause/punctuation)
lines = []; cur = []
for w in ALLW:
    if cur:
        gap = w["t0"] - cur[-1]["t1"]; txt = " ".join(x["w"] for x in cur + [w])
        if gap > 0.5 or len(txt) > 42 or w["spk"] != cur[-1]["spk"] or w["n"] != cur[-1]["n"] or \
                re.search(r'[.?!]$', cur[-1]["w"]) or (re.search(r',$', cur[-1]["w"]) and len(cur) >= 3):
            lines.append(cur); cur = []
    cur.append(w)
if cur: lines.append(cur)
# Alice override by pitch on session lines (outside fixed regions)
for ln in lines:
    if ln[0]["n"] == "sesi":
        T0, T1 = ln[0]["T"], ln[-1]["T"] + 0.3
        if any(a <= T0 < b for a, b in FEMALE_ONLY): spk = 'A'
        else:
            f = f0_of(T0, max(T1, T0 + 0.3)); spk = 'A' if f > 170 else region_spk(T0)
        for w in ln: w["spk"] = spk
L = [dict(id=i, t0=round(ln[0]["t0"], 3), t1=round(ln[-1]["t1"], 3), spk=ln[0]["spk"], T=round(ln[0]["T"], 2), sec=ln[0]["n"],
          text=" ".join(w["w"] for w in ln)) for i, ln in enumerate(lines)]
json.dump(L, open(f"{OUT}/lines_raw.json", "w"), ensure_ascii=False, indent=0)
FIXF = f"{S}/fixes.json"
FIXES = json.load(open(FIXF)) if os.path.exists(FIXF) else {}
for l in L:
    k = str(l["id"])
    if k in FIXES: l["text"] = FIXES[k]
L = [l for l in L if l["text"].strip() and l["text"] != "DEL"]

# ------------------------------------------------------------------ ASS authoring
ACC = "&H4FB6F2&"; ACC_HEX = "F2B64F"; WHITE = "&HFFFFFF&"; INK = "&H1A1410&"
FB = "/usr/share/fonts/opentype/inter/"
F_SB = {sz: ImageFont.truetype(FB + "Inter-SemiBold.otf", sz) for sz in (22, 24, 26, 30, 34, 40, 52, 64)}
F_M = {sz: ImageFont.truetype(FB + "Inter-Medium.otf", sz) for sz in (20, 22, 24, 28)}
def tw(txt, sz=40, bold=True, sp=0): return (F_SB[sz] if bold else F_M[sz]).getlength(txt) + sp * len(txt)
def ts(t):
    t = max(t, 0); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"
EV = []
def ev(a, b, style, txt, layer=None):
    if b - a > 0.02: EV.append((a, b, style, txt, layer))
def rrect(w, h, r=14):
    return (f"m {r} 0 l {w-r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h-r} b {w} {h} {w} {h} {w-r} {h} "
            f"l {r} {h} b 0 {h} 0 {h} 0 {h-r} l 0 {r} b 0 0 0 0 {r} 0")
def shape(a, b, x, y, path, col, alpha="&H00&", extra="", an=7):
    ev(a, b, "Gfx", f"{{\\an{an}\\pos({x},{y})\\p1\\c{col}\\alpha{alpha}\\bord0\\shad0{extra}}}{path}")
def panel(a, b, x, y, w, h, dx=30, fade=(350, 300), alpha="&H40&"):
    ev(a, b, "Gfx", f"{{\\an7\\move({x+dx},{y},{x},{y},0,380)\\fad({fade[0]},{fade[1]})\\p1\\c{INK}\\alpha{alpha}\\bord0\\shad0}}{rrect(w,h)}")
    ev(a, b, "Gfx", f"{{\\an7\\move({x+dx},{y},{x},{y},0,380)\\fad({fade[0]},{fade[1]})\\p1\\c{ACC}\\bord0\\shad0}}m 0 14 l 5 14 l 5 {h-14} l 0 {h-14}")
def text(a, b, x, y, txt, style="Card", dx=30, delay=0.1, extra="", an=7, fade=(400, 300)):
    ev(a + delay, b, style, f"{{\\an{an}\\move({x+dx},{y},{x},{y},0,{int(420)})\\fad({fade[0]},{fade[1]}){extra}}}{txt}")
def line_draw(a, b, x, y, w, col=ACC, dur=600, th=2):
    ev(a, b, "Gfx", f"{{\\an7\\pos({x},{y})\\p1\\c{col}\\bord0\\shad0\\fad(0,300)\\clip({x},{y-2},{x},{y+th+2})\\t(0,{dur},0.5,\\clip({x},{y-2},{x+w},{y+th+2}))}}m 0 0 l {w} 0 l {w} {th} l 0 {th}")
def particles(a, b, x, y, w, h, n=7, seed=0):
    rng = np.random.default_rng(seed)
    for i in range(n):
        px, py = x + rng.uniform(0, w), y + rng.uniform(0, h); dy = rng.uniform(-60, -25); r = rng.uniform(2, 4)
        ev(a, b, "Gfx", f"{{\\an7\\move({px:.0f},{py:.0f},{px+rng.uniform(-15,15):.0f},{py+dy:.0f})\\fad(900,900)\\p1\\c{ACC}\\alpha&HB0&\\blur2\\bord0\\shad0}}"
                        f"m 0 0 b {r} 0 {r} {r} 0 {r} b {-r} {r} {-r} 0 0 0")
# --- icons (drawn at 1x, ~48 px box)
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
def icon(a, b, x, y, name, scale=100, col=ACC, delay=0.0):
    ev(a + delay, b, "Gfx", f"{{\\an7\\pos({x},{y})\\fscx{scale}\\fscy{scale}\\fad(400,300)\\p1\\c{col}\\bord0\\shad0\\t(0,400,\\fscx{scale}\\fscy{scale})}}{ICON[name]}")
# --- composite graphics
RX = 1840  # right edge of right panel
def card(a, b, label, body, ic=None, x_right=RX, y=130):
    lines_ = body.split("\\N"); w = int(max(max(tw(l, 40) for l in lines_), tw(label, 24, False, 2)) + 70 + (66 if ic else 0))
    h = 74 + 50 * len(lines_); x = x_right - w; ox = x + (66 if ic else 0)
    panel(a, b, x, y, w, h)
    if ic: icon(a + 0.15, b, x + 26, y + h / 2 - 26, ic, 90)
    text(a, b, ox + 32, y + 20, label, "Label"); text(a, b, ox + 32, y + 52, body, "Card", delay=0.18)
    particles(a, b, x - 60, y + h, w, 220, 6, int(a * 10))
def quote_card(a, b, body, who, y=150):
    lines_ = body.split("\\N"); w = int(max(tw(l, 40) for l in lines_) + 120); h = 120 + 50 * len(lines_); x = RX - w
    panel(a, b, x, y, w, h)
    icon(a + 0.1, b, x + 34, y + 26, "quote", 70)
    text(a, b, x + 40, y + 76, body, "Card", delay=0.2)
    text(a, b, x + 40, y + 86 + 50 * len(lines_), "— " + who, "Label", delay=0.35)
def steps(a, b, title, items, y=130, ic=None):
    """vertical list that builds item by item: items=[(T_appear_timeline, label, text)]"""
    w = int(max([tw(t_, 34) for _, _, t_ in items] + [tw(title, 24, False, 2)]) + 120); x = RX - w
    h = 80 + 86 * len(items)
    panel(a, b, x, y, w, h)
    text(a, b, x + 32, y + 22, title, "Label")
    line_draw(a + 0.2, b, x + 32, y + 56, w - 64, dur=700, th=1)
    for i, (ta, lab, t_) in enumerate(items):
        yy = y + 74 + 86 * i
        shape(max(ta, a + 0.3), b, x + 40, yy + 10, "m 6 0 b 9 0 12 3 12 6 b 12 9 9 12 6 12 b 3 12 0 9 0 6 b 0 3 3 0 6 0", ACC, extra="\\fad(300,300)")
        if i: shape(max(ta, a + 0.3), b, x + 45, yy - 64, f"m 0 0 l 2 0 l 2 70 l 0 70", ACC, "&H90&", extra="\\fad(300,300)")
        text(max(ta, a + 0.3), b, x + 70, yy - 2, lab, "Label", dx=20, delay=0)
        text(max(ta, a + 0.3), b, x + 70, yy + 26, t_, "Card34", dx=20, delay=0.1)
def compare(a, b, title, left, right, t_right, y=140, ic=(None, None)):
    """two concept boxes with a divider; right side appears at t_right"""
    colw = int(max(tw(l, 34) for l in left[1].split("\\N") + right[1].split("\\N")) + 60)
    colw = max(colw, 260); w = colw * 2 + 70; x = RX - w; nl = max(left[1].count("\\N"), right[1].count("\\N")) + 1; h = 150 + 44 * nl
    panel(a, b, x, y, w, h)
    text(a, b, x + 32, y + 20, title, "Label")
    line_draw(a + 0.2, b, x + 32, y + 54, w - 64, dur=700, th=1)
    for k, (lab, body), ta in ((0, left, a + 0.3), (1, right, t_right)):
        xx = x + 32 + k * (colw + 30)
        if ic[k]: icon(ta, b, xx, y + 70, ic[k], 60)
        text(ta, b, xx + (46 if ic[k] else 0), y + 72, lab, "Label", dx=20, delay=0)
        text(ta, b, xx, y + 108, body, "Card34", dx=20, delay=0.12)
    shape(t_right, b, x + 32 + colw + 10, y + 76, f"m 0 0 l 2 0 l 2 {h-100} l 0 {h-100}", ACC, "&H80&", extra="\\fad(300,300)")
def lower3(a, b, name, role, x=90, y=780):
    w = int(max(tw(name, 40), tw(role, 24, False, 2)) + 72); h = 108
    panel(a, b, x, y, w, h, dx=-30)
    text(a, b, x + 34, y + 14, name, "Card", dx=-30); text(a, b, x + 34, y + 66, role, "Label", dx=-30, delay=0.2)
def chapter(a, num, title, dur=3.6):
    b = a + dur; cx = 960; y = 150
    ev(a, b, "Gfx", "{\\an7\\pos(0,0)\\fad(400,500)\\p1\\c&H000000&\\alpha&H78&\\blur40\\bord0\\shad0}m 360 60 l 1560 60 l 1560 330 l 360 330", 0)
    ev(a, b, "Chap", f"{{\\an8\\pos({cx},{y})\\fad(300,400)\\fsp8}}BAB {num}")
    line_draw(a + 0.15, b, cx - 60, y + 46, 120, dur=500, th=3)
    ev(a + 0.25, b, "ChapT", f"{{\\an8\\move({cx},{y+78},{cx},{y+64},0,500)\\fad(450,400)\\blur0.6}}{title}")
    particles(a, b, cx - 300, y + 40, 600, 140, 8, int(a))

# --- persistent elements: chapter bug + progress bar (top-left), hidden during title & tail
t_start = 5.0; t_end = tl_of(1626.3) - 0.5
chap_tl = [(tl_of(T), n, ttl) for T, n, ttl in CHAPTERS]
for i, (a, n, ttl) in enumerate(chap_tl):
    b = chap_tl[i + 1][0] if i + 1 < len(chap_tl) else t_end
    a2 = max(a, t_start)
    w_ = max(int(tw(n + "  " + ttl.upper(), 22, True, 3) + 40), 282)
    ev(a2 + 3.8, b, "Gfx", f"{{\\an7\\pos(44,38)\\fad(500,300)\\p1\\c{INK}\\alpha&H60&\\bord0\\shad0}}{rrect(w_, 70, 12)}", 0)
    ev(a2 + 3.8, b, "Bug", f"{{\\an7\\pos(64,52)\\fad(500,300)}}{{\\c{ACC}}}{n}  {{\\c{WHITE}\\alpha&H30&}}{ttl.upper()}")
ev(t_start, t_end, "Gfx", f"{{\\an7\\pos(64,92)\\p1\\c{WHITE}\\alpha&HC8&\\bord0\\shad0\\fad(600,600)}}m 0 0 l 240 0 l 240 2 l 0 2")
ev(t_start, t_end, "Gfx", f"{{\\an7\\pos(64,92)\\p1\\c{ACC}\\bord0\\shad0\\fad(600,600)\\clip(64,88,{64+240*t_start/t_end:.0f},96)"
                     f"\\t(0,{int((t_end-t_start)*1000)},\\clip(64,88,304,96))}}m 0 0 l 240 0 l 240 2 l 0 2")
ev(4.9, 4.6 + 4.0, "Bug", f"{{\\an7\\pos(64,52)\\fad(600,300)}}{{\\c{ACC}}}00  {{\\c{WHITE}\\alpha&H30&}}PEMBUKAAN")

# --- title sequence
ev(0.0, 4.9, "Gfx", "{\\an7\\pos(0,0)\\fad(0,700)\\p1\\c&H000000&\\alpha&H70&\\bord0\\shad0}m 0 0 l 1920 0 l 1920 1080 l 0 1080")
ev(0.0, 4.7, "Kicker", "{\\an5\\pos(960,452)\\fad(500,600)\\fsp6}PODCAST")
ev(0.15, 4.7, "Title", "{\\an5\\pos(960,530)\\fad(600,600)\\t(0,4500,\\fscx104\\fscy104)}Romantisisme")
line_draw(0.4, 4.7, 900, 598, 120, dur=700, th=3)
ev(0.5, 4.7, "Kicker", "{\\an5\\pos(960,640)\\fad(600,600)\\fs30\\fsp2}Antara akal dan perasaan")
particles(0.2, 4.8, 560, 380, 800, 320, 14, 3)
# --- names
lower3(tl_sec("pengenalan", 11.95), tl_sec("pengenalan", 16.6), "Alice Catherine", "PENGACARA", y=690)
lower3(tl_sec("pengenalan", 13.35), tl_sec("pengenalan", 17.6), "Muhammad Hasid", "PENGACARA", y=815)
lower3(tl_of(41.6), tl_of(48.0), "Dr. Satria Abadi", "TETAMU UNDANGAN", y=780)
# --- chapters (skip 01: its first seconds overlap section start / name card; show at 11.95+1.2)
for T, n, ttl in CHAPTERS:
    a = tl_of(T) + (0.6 if n != "01" else 0.4)
    chapter(a, n, ttl)
# --- content graphics (all in right negative space; shots forced to Dr-left framing)
G = tl_of
card(G(49.5), G(57.5), "ASAL", "Bogor, Indonesia", "pin")
steps(G(117.0), G(164.5), "PERJALANAN KERJAYA", [(G(117.5), "2004", "Pensyarah di Indonesia"), (G(129.5), "PENGAJIAN", "PhD"),
      (G(134.5), "PASCADOKTORAL", "Finland · Brunei · Malaysia"), (G(158.5), "KINI", "Pensyarah di Malaysia")])
card(G(191.2), G(199.5), "CITA-CITA SEJAK KECIL", "Menjadi pendidik", "book")
quote_card(G(273.9), G(284.5), "Tiada batasan untuk\\Nmengejar cita-cita.", "Dr. Satria Abadi")
card(G(388.0), G(396.8), "ROMANTISISME", "Luapan perasaan\\Ndari dalam diri", "heart")
compare(G(456.0), G(499.5), "DUA CARA MELIHAT ALAM", ("SAINTIS", "Alam bergerak\\Nseperti mesin"), ("SUFI / ROMANTIS", "Alam dirasai\\Ndengan jiwa"), G(484.0), ic=("spark", "heart"))
steps(G(519.0), G(581.5), "PENYAIR & PEMIKIR DISEBUT", [(G(519.2), "PENYAIR SUFI", "Jalaluddin Ar-Rumi"), (G(535.0), "PENYAIR SUFI", "Rabiatul Adawiyah"),
      (G(572.0), "SASTERAWAN", "Hamka")])
compare(G(675.0), G(741.5), "KESEIMBANGAN", ("AKAL", "Menimbang\\Ndengan rasional"), ("PERASAAN", "Tanpa akal,\\Nmenjadi egois"), G(712.0), ic=("scale", "heart"))
compare(G(866.0), G(891.5), "MELIHAT DAUN YANG GUGUR", ("SAINTIS", "Fotosintesis"), ("ROMANTIS", "Daun berterbangan,\\Nmenggugurkan rasa"), G(875.0), ic=("spark", "leaf"))
card(G(908.0), G(925.5), "PEPATAH", "Seperti air di daun keladi", "leaf")
compare(G(984.5), G(1000.5), "BERANI MENJADI DIRI SENDIRI", ("DIRI", "Pendirian sendiri"), ("MASYARAKAT", "Aturan & regulasi"), G(992.0), ic=("people", "people"))
steps(G(1019.5), G(1062.0), "MELUAHKAN RASA MELALUI KARYA", [(G(1020.0), "PUISI", "Jalaluddin Ar-Rumi"), (G(1024.0), "DARI PENJARA", "Hamka"),
      (G(1048.0), "SYAIR", "Rabiatul Adawiyah")])
quote_card(G(1065.0), G(1089.5), "Jika syurga itu untukku,\\Nberikan saja kepada\\Norang yang Kau cintai.", "Rabiatul Adawiyah (diceritakan Dr. Satria)")
compare(G(1167.0), G(1215.5), "ROMANTIS DI ERA TEKNOLOGI", ("MEDIA SOSIAL", "Meniru orang lain"), ("ROMANTIS SEBENAR", "Luapan emosi\\Ndiri sendiri"), G(1188.0), ic=("phone", "heart"))
card(G(1238.5), G(1270.5), "INTI PANDANGAN", "Romantis ditunjukkan\\Nmelalui perbuatan", "heart")
card(G(1325.5), G(1333.2), "ROMANTIS", "Tak perlu selalu berpuisi", "spark")
steps(G(1440.0), G(1530.5), "TIGA RASA YANG BERBEZA", [(G(1440.5), "EMPATI", "Merasakan situasi orang lain"),
      (G(1459.0), "BELAS KASIHAN", "Muncul pada orang yang dekat"), (G(1495.0), "SIMPATI", "Sekadar rasa suka")])
card(G(1546.5), G(1577.5), "BUAH TANGAN", "Kenang-kenangan untuk tetamu", "gift")
# --- end card
te = TOTAL
ev(te - TAIL + 0.6, te, "ChapT", f"{{\\an5\\pos(960,430)\\fad(600,0)}}Terima kasih")
line_draw(te - TAIL + 0.9, te, 900, 478, 120, dur=600, th=3)
ev(te - TAIL + 1.1, te, "Kicker", "{\\an5\\pos(960,530)\\fad(500,0)\\fs26\\fsp3}TETAMU  ·  DR. SATRIA ABADI")
ev(te - TAIL + 1.3, te, "Kicker", "{\\an5\\pos(960,575)\\fad(500,0)\\fs26\\fsp3}PENGACARA  ·  ALICE CATHERINE  &  MUHAMMAD HASID")
ev(te - TAIL + 1.5, te, "Kicker", "{\\an5\\pos(960,650)\\fad(500,0)\\fs24\\fsp6\\c&HDDDDDD&}PODCAST  ·  ROMANTISISME")
particles(te - TAIL + 0.5, te, 560, 380, 800, 320, 12, 9)

# --- subtitles: phrase reveal, selective keyword highlight
KEYW = ["romantisisme", "romantisme", "romantis", "akal", "perasaan", "empati", "simpati", "belas kasihan", "falsafah", "filosofi", "alam",
        "cinta", "mencintai", "jiwa", "puisi", "syair", "penyair", "keseimbangan", "teknologi", "media sosial", "perbuatan", "egois",
        "Jalaluddin Ar-Rumi", "Rabiatul Adawiyah", "Hamka", "Satria Abadi", "Bogor", "Indonesia", "Malaysia", "pendidik", "cita-cita",
        "sufi", "saintis", "daun keladi", "buah tangan", "luapan", "kebahagiaan"]
KRE = re.compile(r"(?<![\w-])(" + "|".join(sorted(map(re.escape, KEYW), key=len, reverse=True)) + r")(?![\w-])", re.I)
def esc(s): return s.replace("{", "(").replace("}", ")")
for i, l in enumerate(L):
    a = l["t0"] - 0.06; b = l["t1"] + 0.35
    if i + 1 < len(L): b = min(b, L[i + 1]["t0"] - 0.08)
    b = max(b, l["t1"] + 0.05, a + 0.6)
    body = KRE.sub(lambda m: "{\\c" + ACC + "}" + m.group(0) + "{\\c" + WHITE + "}", esc(l["text"]))
    ev(a, b, "Sub", "{\\blur2.5\\fad(140,120)\\move(960,1006,960,1000,0,180)}" + body)
    l["show"] = [round(a, 3), round(b, 3)]

HDR = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Inter SemiBold,50,&H00FFFFFF,&H00FFFFFF,&H90000000,&H80000000,0,0,0,0,100,100,0.5,0,1,2.6,1.5,2,160,160,78,1
Style: Gfx,Inter,20,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Card,Inter SemiBold,40,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,0,0,0,0,100,100,0,0,1,0,1,7,0,0,0,1
Style: Card34,Inter SemiBold,34,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,0,0,0,0,100,100,0,0,1,0,1,7,0,0,0,1
Style: Label,Inter Medium,22,&H00{ACC_HEX[4:]}{ACC_HEX[2:4]}{ACC_HEX[:2]},&H00FFFFFF,&H00000000,&HA0000000,0,0,0,0,100,100,2,0,1,0,0,7,0,0,0,1
Style: Title,Inter SemiBold,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,0,2,5,0,0,0,1
Style: Kicker,Inter SemiBold,30,&H00{ACC_HEX[4:]}{ACC_HEX[2:4]}{ACC_HEX[:2]},&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,4,0,1,0,1,5,0,0,0,1
Style: Chap,Inter SemiBold,24,&H00{ACC_HEX[4:]}{ACC_HEX[2:4]}{ACC_HEX[:2]},&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,6,0,1,0,1.5,8,0,0,0,1
Style: ChapT,Inter SemiBold,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,1,0,1,0,2,8,0,0,0,1
Style: Bug,Inter SemiBold,22,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,0,0,0,0,100,100,3,0,1,0,1.2,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
LAYER = {"Gfx": 1, "Card": 2, "Card34": 2, "Label": 2, "Bug": 2, "Title": 3, "Kicker": 3, "Chap": 3, "ChapT": 3, "Sub": 6}
with open(f"{OUT}/subtitles.ass", "w") as f:
    f.write(HDR)
    for a, b, st, tx, lay in sorted(EV, key=lambda e: e[0]):
        f.write(f"Dialogue: {LAYER[st] if lay is None else lay},{ts(a)},{ts(b)},{st},,0,0,0,,{tx}\n")
def srt_ts(t):
    ms = int(round(max(t, 0) * 1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
with open(f"{OUT}/subtitles.srt", "w") as f:
    for i, l in enumerate(L, 1):
        f.write(f"{i}\n{srt_ts(l['show'][0])} --> {srt_ts(l['show'][1])}\n{l['text']}\n\n")
SPK = {'H': "Muhammad Hasid", 'D': "Dr. Satria Abadi", 'A': "Alice Catherine"}
with open(f"{OUT}/transcript.txt", "w") as f:
    f.write("Transkrip disemak - Podcast Romantisisme (video penuh)\n\n"); cur = None; buf = []
    for l in L:
        if l["spk"] != cur:
            if buf: f.write(" ".join(buf) + "\n\n")
            cur = l["spk"]; buf = [f"[{int(l['t0']//60):02d}:{int(l['t0']%60):02d}] {SPK[cur]}:"]
        buf.append(l["text"])
    f.write(" ".join(buf) + "\n")
json.dump(L, open(f"{OUT}/lines_final.json", "w"), ensure_ascii=False, indent=0)
json.dump(dict(fps=FPS, total=TOTAL, keep_ranges_session=KEEP, keep_ranges_after_pause_trim=KEEP2, cuts=[dict(master_from=a, master_to=b, why=w) for (a, b), w in CUTS_WHY.items()],
               segments=[dict(section=n, audio=f, a0=a0, a1=a1, tl=t0) for n, f, a0, a1, t0 in segs], chapters=[dict(master_T=T, tl=round(tl_of(T), 2), num=n, title=t_) for T, n, t_ in CHAPTERS],
               regions=REGIONS, shots=shots), open(f"{OUT}/editing_timeline.json", "w"), indent=1)
from collections import Counter
print("total", TOTAL, "shots", len(shots), "lines", len(L), "keep2", len(KEEP2))
print(Counter(s["view"] for s in shots))
print("short", [(s["id"], s["view"], s["frames"]) for s in shots if s["frames"] < 54 and s["view"] != "BLACK"])
