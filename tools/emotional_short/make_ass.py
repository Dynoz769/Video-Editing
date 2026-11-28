import json
from PIL import ImageFont
p = {r["name"]: r for r in json.load(open("plan.json"))}; meta = json.load(open("audio_meta.json")); TOTAL = meta["total"]
F = "/tmp/claude-0/-home-user-Video-Editing/076371bc-bd5a-53cb-b805-1e4df1af2938/scratchpad/fonts/CG_500italic.ttf"
FS = 80; font = ImageFont.truetype(F, FS)
AMB = "&H4FB6F2&"; WHITE = "&HFFFFFF&"
def tl(shot, T): return p[shot]["tl"] + T - p[shot]["master_T"][0]
def ts(t):
    t = max(t, 0); return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
EV = []
def ev(a, b, st, tx, layer=2): EV.append((a, b, st, tx, layer))
KEY = {"syurga", "neraka", "cintai", "jiwa", "rindu", "rinduku", "tuhan"}
def verse(shot, rows, end_T, y0=1268, lh=108, out_ms=260):
    """rows of (word, T): one event per row (renderer spacing); each word fades in at its spoken time."""
    b = tl(shot, end_T)
    a0 = tl(shot, rows[0][0][1]) - 0.06
    for r, row in enumerate(rows):
        ra = tl(shot, row[0][1]) - 0.06; parts = []
        for w, T in row:
            k = w.strip('“”",.?!').lower() in KEY
            dt = int(max(0, (tl(shot, T) - 0.06 - ra) * 1000))
            col = AMB if k else WHITE
            glow = f"\\3c{AMB}\\bord2.2\\blur6" if k else "\\bord0\\blur0.5"
            pop = f"\\t({dt},{dt+1400},\\fscx107\\fscy107)" if w.lower().startswith("rindu") else ""
            parts.append(f"{{\\alpha&HFF&\\c{col}{glow}\\t({dt},{dt+320},\\alpha&H00&){pop}}}{w}")
        ev(ra, b, "Verse", f"{{\\an8\\move(540,{y0+r*lh+10},540,{y0+r*lh},0,400)\\fad(0,{out_ms})}}" + " ".join(parts), 3)
def sub(shot, T0, T1, text, hl=()):
    a = tl(shot, T0) - 0.06; b = tl(shot, T1) + 0.25
    for h in hl: text = text.replace(h, f"{{\\c{AMB}}}{h}{{\\c{WHITE}}}")
    ev(a, b, "Sub", f"{{\\an2\\pos(540,1452)\\fad(160,140)\\blur2.2}}{text}", 4)
# --- soft lower gradient for text contrast (whole picture part)
ev(0.0, p["F_end"]["tl"] + 3.2, "Gfx", "{\\an7\\pos(0,0)\\fad(600,900)\\p1\\c&H000000&\\alpha&H58&\\blur70\\bord0\\shad0}m 0 1180 l 1080 1180 l 1080 1600 l 0 1600", 1)
# --- hook (A)
verse("A_hook", [[("“Seandainya", 1066.51), ("syurga", 1067.10)], [("itu", 1067.58), ("untukku,", 1067.82)]], 1068.33)
verse("A_hook", [[("saya", 1068.36), ("tidak", 1068.58), ("perlukan", 1068.88)], [("syurga", 1069.22), ("itu.”", 1069.68)]], 1070.38, out_ms=400)
# --- context (B) : name card + regular subtitles
a = p["B1_ctx"]["tl"] + 0.15; b = p["B2_ctx"]["tl"] + 2.9
ev(a, b, "Gfx", "{\\an7\\pos(0,0)\\fad(500,700)\\p1\\c&H000000&\\alpha&H60&\\blur30\\bord0\\shad0}m 0 0 l 1080 0 l 1080 470 l 0 470", 1)
ev(a, b, "Label", "{\\an8\\move(540,236,540,222,0,600)\\fad(600,700)\\fsp10}RABIATUL ADAWIYAH", 3)
ev(a + 0.3, b, "Gfx", f"{{\\an7\\pos(480,284)\\p1\\c{AMB}\\bord0\\shad0\\fad(0,700)\\clip(480,280,480,290)\\t(0,700,0.5,\\clip(480,280,600,290))}}m 0 0 l 120 0 l 120 2 l 0 2", 3)
ev(a + 0.45, b, "VerseS", "{\\an8\\move(540,318,540,306,0,650)\\fad(650,700)}penyair sufi · Basrah, abad ke-8", 3)
sub("B1_ctx", 1047.58, 1049.95, "Rabiatul Adawiyah yang saya ceritakan itu,")
sub("B2_ctx", 1051.82, 1053.82, "orang menganggap dia seperti orang")
sub("B2_ctx", 1053.85, 1056.30, "yang tidak punya, tidak punya apa,")
sub("B3_env", 1056.38, 1057.96, "yang bertentangan dengan agama,")
sub("B3_env", 1058.04, 1059.80, "tapi luapan perasaan itu...", hl=("luapan perasaan",))
# --- verse continued (C)
verse("C1_verse", [[("“Berikan", 1070.78), ("saja", 1070.98)], [("syurga", 1071.26), ("itu", 1071.66)]], 1071.97)
verse("C1_verse", [[("kepada", 1072.00), ("orang", 1072.68)], [("yang", 1073.10), ("Kau", 1073.24), ("cintai.", 1073.38)]], 1074.28)
verse("C2_verse", [[("Kalau", 1074.34), ("neraka", 1074.50)], [("itu", 1075.00), ("untukku,", 1075.24)]], 1075.63)
verse("C2_verse", [[("saya", 1075.66), ("tak", 1075.76), ("perlu", 1075.96)], [("neraka", 1076.12), ("itu.”", 1076.60)]], 1076.94, out_ms=380)
# --- peak (D)
verse("D_peak", [[("“Tetapi", 1081.30), ("kalau", 1081.70)], [("jiwa", 1082.22), ("ini", 1082.64)]], 1082.86)
verse("D_peak", [[("ada", 1082.88), ("rindu", 1083.10)], [("kepada-Mu,", 1083.60)]], 1084.10)
verse("D_peak", [[("ya", 1084.13), ("Tuhan,”", 1084.34)]], 1085.58, y0=1320)
sub("D_peak", 1085.63, 1085.96, "kata dia,")
verse("D_peak", [[("“maka", 1086.06), ("jangan", 1086.60), ("Kau", 1086.92)], [("tolak", 1087.16), ("rinduku", 1087.53), ("ini.”", 1087.96)]], 1088.58, out_ms=500)
# --- reaction (E)
sub("E_react", 1088.15, 1089.55, "Itu dahsyat sekali.")
# --- ending card on black
t0 = p["F_end"]["tl"] + 2.2
for r, row in enumerate(([("“…maka", 0.0), ("jangan", 0.25), ("Kau", 0.45)], [("tolak", 0.75), ("rinduku", 1.0), ("ini.”", 1.3)])):
    parts = []
    for w, d in row:
        k = w.strip('“”",.…').lower() in KEY; dt = int((d - row[0][1]) * 1000)
        g = f"\\c{AMB}\\3c{AMB}\\bord2\\blur8" if k else f"\\c{WHITE}\\bord0\\blur0.4"
        parts.append(f"{{\\alpha&HFF&{g}\\t({dt},{dt+600},\\alpha&H00&)}}{w}")
    ev(t0 + row[0][1], TOTAL, "VerseL", f"{{\\an8\\move(540,{830 + r * 104 + 12},540,{830 + r * 104},0,600)}}" + " ".join(parts), 3)
ev(t0 + 1.7, TOTAL, "Label", "{\\an8\\pos(540,1080)\\fad(600,0)\\fsp8\\fs28}RABIATUL ADAWIYAH", 3)
ev(t0 + 1.9, TOTAL, "Small", "{\\an8\\pos(540,1132)\\fad(600,0)\\fs30}diceritakan oleh Dr. Satria Abadi · Podcast Romantisisme", 3)
HDR = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Verse,Cormorant Garamond Light Medium,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,0,1,0,0,100,100,0.5,0,1,0,3,8,0,0,0,1
Style: VerseS,Cormorant Garamond Light Medium,46,&H00F2F2F2,&H00FFFFFF,&H00000000,&H90000000,0,1,0,0,100,100,0.5,0,1,0,1.5,8,0,0,0,1
Style: VerseL,Cormorant Garamond Light Medium,86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,1,0,0,100,100,0.5,0,1,0,0,7,0,0,0,1
Style: Sub,Inter SemiBold,48,&H00FFFFFF,&H00FFFFFF,&H90000000,&H80000000,0,0,0,0,100,100,0.3,0,1,2.4,1.5,2,90,90,0,1
Style: Label,Inter SemiBold,30,&H004FB6F2,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,8,0,1,0,1,8,0,0,0,1
Style: Small,Inter Medium,26,&H00C8C8C8,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,1,0,1,0,0,8,0,0,0,1
Style: Gfx,Inter,20,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open("short.ass", "w") as f:
    f.write(HDR)
    for a, b, st, tx, ly in sorted(EV, key=lambda e: e[0]): f.write(f"Dialogue: {ly},{ts(a)},{ts(b)},{st},,0,0,0,,{tx}\n")
# SRT (spoken words only)
SRT = [("A_hook", 1066.51, 1068.33, "“Seandainya syurga itu untukku,"), ("A_hook", 1068.36, 1070.12, "saya tidak perlukan syurga itu.”"),
       ("B1_ctx", 1047.58, 1049.95, "Rabiatul Adawiyah yang saya ceritakan itu,"), ("B2_ctx", 1051.82, 1053.82, "orang menganggap dia seperti orang"),
       ("B2_ctx", 1053.85, 1056.30, "yang tidak punya, tidak punya apa,"), ("B3_env", 1056.38, 1057.96, "yang bertentangan dengan agama,"),
       ("B3_env", 1058.04, 1059.80, "tapi luapan perasaan itu..."), ("C1_verse", 1070.78, 1071.97, "“Berikan saja syurga itu"),
       ("C1_verse", 1072.00, 1074.28, "kepada orang yang Kau cintai."), ("C2_verse", 1074.34, 1075.63, "Kalau neraka itu untukku,"),
       ("C2_verse", 1075.66, 1076.94, "saya tak perlu neraka itu.”"), ("D_peak", 1081.30, 1082.86, "“Tetapi kalau jiwa ini"),
       ("D_peak", 1082.88, 1084.10, "ada rindu kepada-Mu,"), ("D_peak", 1084.13, 1085.58, "ya Tuhan,” kata dia,"),
       ("D_peak", 1086.06, 1088.58, "“maka jangan Kau tolak rinduku ini.”"), ("E_react", 1088.15, 1089.55, "Itu dahsyat sekali.")]
def st_(t): ms = int(round(t * 1000)); return f"{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}"
rows = sorted([(tl(s, a), tl(s, b), x) for s, a, b, x in SRT])
open("subtitles.srt", "w").write("".join(f"{i}\n{st_(a-0.05)} --> {st_(b+0.2)}\n{x}\n\n" for i, (a, b, x) in enumerate(rows, 1)))
print(len(EV), "events")
