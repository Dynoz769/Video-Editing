import json
p = {r["name"]: r for r in json.load(open("plan.json"))}; meta = json.load(open("audio_meta.json")); TOTAL = meta["total"]
AMB = "&H4FB6F2&"; WHITE = "&HFFFFFF&"; COOL = "&HE8C7A9&"; GREY = "&HB4B4B4&"
def tl(shot, T): return p[shot]["tl"] + T - p[shot]["master_T"][0]
def ts(t): t = max(t, 0); return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
EV = []
def ev(a, b, st, tx, layer=2): EV.append((a, b, st, tx, layer))
WARMK = {"perasaan", "pasangan", "merasakan", "keromantisan", "perbuatan", "perbuatan.", "dirinya.", "ucapkan…"}
COOLK = {"meniru,", "mencontoh.", "semu.", "media", "sosial,", "bunga,"}
ECHO = {"meniru,", "mencontoh.", "semu."}
def words(shot, rows, end_T, y0=1250, lh=92, st="Kin", out_ms=240):
    b = tl(shot, end_T)
    for r, row in enumerate(rows):
        ra = tl(shot, row[0][1]) - 0.06; parts = []; echo = []
        for w, T in row:
            dt = int(max(0, (tl(shot, T) - 0.06 - ra) * 1000)); lw = w.lower()
            col = AMB if lw in WARMK else (COOL if lw in COOLK else WHITE)
            glow = f"\\3c{AMB}\\bord2\\blur6" if lw in WARMK else "\\bord0\\blur0.4"
            parts.append(f"{{\\alpha&HFF&\\c{col}{glow}\\t({dt},{dt+300},\\alpha&H00&)}}{w}")
            # echo copies for imitation words: same row, offset ghosts that slide out and fade
            echo.append((w, dt, lw in ECHO))
        txt = " ".join(parts)
        ev(ra, b, st, f"{{\\an8\\move(540,{y0+r*lh+10},540,{y0+r*lh},0,380)\\fad(0,{out_ms})}}" + txt, 3)
        if any(e[2] for e in echo):
            for k, (dx, al) in enumerate(((14, "&HA0&"), (28, "&HD0&"))):
                ghost = " ".join(f"{{\\alpha&HFF&\\c{COOL}\\t({dt},{dt+300},\\alpha{al})\\t({dt+300},{dt+1400},\\alphaFF)}}{w}" if e else f"{{\\alphaFF}}{w}"
                                 for (w, dt, e) in echo)
                ghost = ghost.replace("\\alphaFF", "\\alpha&HFF&")
                ev(ra, b, st, f"{{\\an8\\move(540,{y0+r*lh},{540+dx},{y0+r*lh+dx//3},0,1400)\\fad(0,{out_ms})}}" + ghost, 2)
# --- lower gradient for contrast (picture part)
endpic = p["E_end"]["tl"] + p["E_end"]["frames"] / 30
ev(0, endpic, "Gfx", "{\\an7\\pos(0,0)\\fad(500,900)\\p1\\c&H000000&\\alpha&H5C&\\blur70\\bord0\\shad0}m 0 1160 l 1080 1160 l 1080 1560 l 0 1560", 1)
# --- hook
words("H_hook", [[("Kadang", 1253.40), ("luapan", 1253.72), ("itu", 1254.24)], [("tak", 1254.50), ("perlu", 1254.66), ("kita", 1254.84), ("ucapkan…", 1255.16)]], 1255.78, y0=1240, st="KinBig", lh=104)
# --- social media section (cool)
words("M1_wide", [[("Dia", 1180.34), ("tengok", 1180.54), ("di", 1181.34)], [("media", 1182.40), ("sosial,", 1182.72)]], 1183.58)
words("M1_cu", [[("orang", 1183.66), ("memberikan", 1183.90), ("bunga,", 1184.82)]], 1186.55)
words("M1_cu", [[("dia", 1186.60), ("akan", 1186.80), ("mengikuti", 1187.12)], [("orang", 1188.02), ("itu.", 1188.22)]], 1188.40)
words("M1_cu", [[("Padahal", 1188.42), ("itu", 1188.68)], [("bukan", 1188.88), ("romantis.", 1189.12)]], 1189.42)
words("M2_cu", [[("Banyak", 1209.50), ("orang", 1210.00)], [("yang", 1210.26), ("meniru,", 1210.42)]], 1210.84)
words("M2_cu", [[("padahal", 1210.86), ("itu", 1211.46), ("bukan", 1211.70)], [("luapan", 1212.00), ("emosional", 1212.42)]], 1214.50)
words("M2_main", [[("diri", 1214.54), ("dia", 1215.32), ("sendiri,", 1215.52)], [("tetapi", 1215.92), ("hanya", 1216.64), ("mencontoh.", 1217.11)]], 1217.54)
words("M2_main", [[("Itu", 1217.56), ("adalah", 1217.92), ("suatu", 1218.80)], [("nilai", 1219.12), ("yang", 1220.06), ("semu.", 1220.30)]], 1220.70, out_ms=500)
# phone motif (upper right negative space), from M1 start to the turn
a = p["M1_wide"]["tl"]; b = p["T1"]["tl"] + 0.8; x0, y0 = 700, 250
def rr(w, h, r):
    return f"m {r} 0 l {w-r} 0 b {w} 0 {w} 0 {w} {r} l {w} {h-r} b {w} {h} {w} {h} {w-r} {h} l {r} {h} b 0 {h} 0 {h} 0 {h-r} l 0 {r} b 0 0 0 0 {r} 0"
outline = rr(230, 430, 28) + " " + "m 4 32 l 4 398 b 4 422 8 426 32 426 l 198 426 b 222 426 226 422 226 398 l 226 32 b 226 8 222 4 198 4 l 32 4 b 8 4 4 8 4 32"
ev(a + 0.2, b, "Gfx", f"{{\\an7\\move({x0+30},{y0},{x0},{y0},0,700)\\fad(600,700)\\p1\\c&HFFFFFF&\\alpha&H70&\\bord0\\shad0}}{outline}", 2)
ev(a + 0.2, b, "Gfx", f"{{\\an7\\move({x0+30},{y0},{x0},{y0},0,700)\\fad(600,700)\\p1\\c{COOL}\\alpha&HC8&\\bord0\\shad0}}{rr(222,422,24)}", 1)
HEART = "m 24 46 b 12 36 0 28 0 16 b 0 6 8 0 15 0 b 20 0 23 4 24 6 b 25 4 28 0 33 0 b 40 0 48 6 48 16 b 48 28 36 36 24 46"
FLOWER = " ".join(f"m {24+14*c:.0f} {24+14*s:.0f} b {24+26*c-8*s:.0f} {24+26*s+8*c:.0f} {24+26*c+8*s:.0f} {24+26*s-8*c:.0f} {24+14*c:.0f} {24+14*s:.0f}"
                  for c, s in [(1, 0), (0.31, 0.95), (-0.81, 0.59), (-0.81, -0.59), (0.31, -0.95)]) + " m 24 18 b 32 18 32 30 24 30 b 16 30 16 18 24 18"
tb = tl("M1_cu", 1184.82)
ev(tb, b, "Gfx", f"{{\\an7\\pos({x0+90},{y0+150})\\fad(400,600)\\p1\\c{COOL}\\bord0\\shad0\\fscx120\\fscy120}}{FLOWER}", 3)
tm = tl("M2_cu", 1210.42)
for k, (dx, dy) in enumerate([(0, 0), (-60, 70), (60, 70), (-30, 150), (40, 160), (0, 230)]):
    ev(tm + 0.12 * k, b, "Gfx", f"{{\\an7\\move({x0+91},{y0+320},{x0+91+dx},{y0+300-dy},0,{900+100*k})\\fad(300,600)\\p1\\c{COOL}\\alpha&H40&\\bord0\\shad0\\fscx70\\fscy70}}{HEART}", 3)
tsemu = tl("M2_main", 1220.30)
ev(tsemu, b, "Gfx", f"{{\\an7\\pos({x0},{y0})\\fad(200,600)\\p1\\c&H000000&\\alpha&H60&\\bord0\\shad0}}{rr(230,430,28)}", 4)   # greys the screen out on "semu"
# --- the turn (warm)
words("T1", [[("Kadang", 1227.28), ("hal", 1228.04), ("tersebut", 1228.74)], [("mungkin", 1229.32), ("orang", 1229.70), ("melihat", 1229.94)]], 1230.18)
words("T1", [[("tidak", 1230.20), ("romantis,", 1231.08)]], 1231.98)
words("T2_alice", [[("tapi", 1232.00), ("pasangan", 1232.20), ("dia", 1233.04)], [("merasakan", 1233.26)]], 1233.86)
words("T3", [[("itulah", 1233.89 + 0.31), ("keromantisan", 1234.22)], [("pada", 1236.20), ("dirinya.", 1236.60)]], 1237.25, out_ms=450)
# --- peak: call and response
words("P1_ask", [[("Tapi", 1256.06), ("kita", 1256.22)], [("memberikan", 1257.40), ("sebuah…", 1258.34)]], 1260.20)
ta = tl("P1_ask", 1260.30)
ev(ta, tl("P1_ask", 1261.68), "Ask", "{\\an5\\pos(540,1330)\\fad(350,250)\\t(0,1200,\\fscx106\\fscy106)}…apa?", 4)
tr = tl("P2_alice", 1261.90)
ev(tr - 0.05, tl("P3_yes", 1264.2), "Answer", f"{{\\an8\\move(540,1258,540,1246,0,450)\\fad(350,350)\\c{AMB}\\3c{AMB}\\bord2\\blur7}}Sebuah perbuatan lah.", 4)
ev(tr + 0.4, tl("P3_yes", 1264.2), "Gfx", f"{{\\an7\\pos(300,1352)\\p1\\c{AMB}\\bord0\\shad0\\fad(0,350)\\clip(300,1348,300,1360)\\t(0,800,0.5,\\clip(300,1348,780,1360))}}m 0 0 l 480 0 l 480 3 l 0 3", 4)
words("P3_yes", [[("Memberikan", 1264.25), ("perbuatan.", 1264.90)]], 1266.60)
ev(tl("P3_yes", 1266.72), tl("P3_yes", 1267.27) + 0.05, "KinBig", "{\\an8\\pos(540,1252)\\fad(150,200)\\t(0,300,\\fscx108\\fscy108)}Betul.", 4)
# --- ending line (spoken) + end card on black
words("E_end", [[("Romantis", 1325.92), ("tidak", 1326.42), ("harus", 1326.68)], [("dengan", 1327.00), ("selalu", 1327.30), ("berpuisi,", 1327.72)]], 1328.38)
words("E_end", [[("tetapi", 1328.40), ("dengan", 1328.88), ("perbuatan", 1329.16)], [("dia", 1329.76), ("boleh", 1330.38), ("dilakukan…", 1330.94)]], 1332.15, out_ms=600)
t0 = endpic + 0.25
ev(t0, TOTAL, "EndL", "{\\an8\\pos(540,840)\\fad(700,0)}Romantis tidak harus", 3)
ev(t0 + 0.35, TOTAL, "EndL", "{\\an8\\pos(540,920)\\fad(700,0)}selalu berpuisi,", 3)
ev(t0 + 1.0, TOTAL, "EndL", f"{{\\an8\\pos(540,1030)\\fad(800,0)\\c{AMB}\\3c{AMB}\\bord2\\blur8\\t(0,1600,\\fscx104\\fscy104)}}tetapi dengan perbuatan.", 3)
ev(t0 + 1.7, TOTAL, "Small", "{\\an8\\pos(540,1160)\\fad(600,0)}Dr. Satria Abadi · Podcast Romantisisme", 3)
HDR = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kin,Inter SemiBold,64,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,0,2.5,8,0,0,0,1
Style: KinBig,Inter SemiBold,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,0,3,8,0,0,0,1
Style: Ask,Inter Light,150,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,2,0,1,0,3,5,0,0,0,1
Style: Answer,Inter SemiBold,76,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0,0,1,0,3,8,0,0,0,1
Style: EndL,Inter SemiBold,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,8,0,0,0,1
Style: Small,Inter Medium,30,&H00C8C8C8,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,8,0,0,0,1
Style: Gfx,Inter,20,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open("short2.ass", "w") as f:
    f.write(HDR)
    for a, b, st, tx, ly in sorted(EV, key=lambda e: e[0]): f.write(f"Dialogue: {ly},{ts(a)},{ts(b)},{st},,0,0,0,,{tx}\n")
SRT = [("H_hook", 1253.40, 1255.72, "Kadang luapan itu tak perlu kita ucapkan…"), ("M1_wide", 1180.34, 1183.58, "Dia tengok di media sosial,"),
       ("M1_cu", 1183.66, 1186.55, "orang memberikan bunga,"), ("M1_cu", 1186.60, 1188.40, "dia akan mengikuti orang itu."),
       ("M1_cu", 1188.42, 1189.42, "Padahal itu bukan romantis."), ("M2_cu", 1209.50, 1210.84, "Banyak orang yang meniru,"),
       ("M2_cu", 1210.86, 1214.50, "padahal itu bukan luapan emosional"), ("M2_main", 1214.54, 1217.54, "diri dia sendiri, tetapi hanya mencontoh."),
       ("M2_main", 1217.56, 1220.70, "Itu adalah suatu nilai yang semu."), ("T1", 1227.28, 1231.98, "Kadang hal tersebut mungkin orang melihat tidak romantis,"),
       ("T2_alice", 1232.00, 1233.86, "tapi pasangan dia merasakan"), ("T3", 1234.20, 1237.25, "itulah keromantisan pada dirinya."),
       ("P1_ask", 1256.06, 1261.68, "Tapi kita memberikan sebuah… apa?"), ("P2_alice", 1261.90, 1263.30, "Sebuah perbuatan lah."),
       ("P3_yes", 1264.25, 1267.27, "Memberikan perbuatan. Betul."), ("E_end", 1325.92, 1328.38, "Romantis tidak harus dengan selalu berpuisi,"),
       ("E_end", 1328.40, 1332.15, "tetapi dengan perbuatan dia boleh dilakukan…")]
def st_(t): ms = int(round(t * 1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
rows = sorted([(tl(s, a), tl(s, b), x) for s, a, b, x in SRT])
open("subtitles.srt", "w").write("".join(f"{i}\n{st_(a-0.05)} --> {st_(b+0.2)}\n{x}\n\n" for i, (a, b, x) in enumerate(rows, 1)))
print(len(EV), "events")
