import json, sys, subprocess, numpy as np, cv2
S = sys.argv[1]; p = sys.argv[2]; E = json.load(open(p))
cas = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
EXP = {"CU_D": (700, 0.38), "CU_H": (2300, 0.62), "CU_A": (3065, 0.62)}
BW, BH = 2112, 1188
cache = {}
def faces(f, t):
    t = round(t, 1)
    if (f, t) in cache: return cache[(f, t)]
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", f"{S}/dl/{f}", "-frames:v", "1", "-vf", "scale=1280:720,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
    g = np.frombuffer(raw, np.uint8).reshape(720, 1280)
    cache[(f, t)] = [(x * 3 + w * 1.5, y * 3 + h * 1.5, w * 3) for (x, y, w, h) in cas.detectMultiScale(g, 1.1, 5, minSize=(45, 45))]
    return cache[(f, t)]
for sh in E["shots"]:
    if sh["view"] not in EXP or not sh["src"].startswith("main"): continue
    ex, pos = EXP[sh["view"]]; cands = []
    for f in (0.25, 0.5, 0.75):
        for cx, cy, w in faces(sh["file"], sh["src_in"] + sh["dur"] * f):
            if abs(cx - ex) < 550 and 150 < w < 500 and 800 < cy < 1500: cands.append((cx, cy))
    if cands:
        cx, cy = np.median(cands, 0)
        x0 = int(min(max(cx - pos * BW, 0), 3840 - BW)) & ~1; y0 = int(min(max(cy - 0.36 * BH, 0), 2160 - BH)) & ~1
        sh["rect"] = [x0, y0, BW, BH]; sh["face"] = [int(cx), int(cy)]
    print(sh["id"], sh["view"], sh.get("face"), sh["rect"][:2])
json.dump(E, open(p, "w"), indent=1)
