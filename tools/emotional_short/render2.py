"""Vertical 1080x1920 emotional short: shot renderer."""
import json, sys, os, subprocess, numpy as np, cv2
S = sys.argv[1]; SH = f"{S}/short2/shots"; os.makedirs(SH, exist_ok=True)
TM = open(f"{S}/tm.txt").read()
W, H = 1080, 1920; BW, BH = 1188, 2112
OFF = {"IMG_3735.MOV": 1133.9582, "main2.mov": 611.777, "main3.mov": 1211.376}
LUT = {"IMG_3735.MOV": "3735", "main2.mov": "main2", "main3.mov": "main3"}
HDR = {"IMG_3735.MOV": False, "main2.mov": True, "main3.mov": True}
def rect(cx, cy, h, fy=0.38, fx=0.5):
    w = int(round(h * 9 / 16)); x0 = int(min(max(cx - fx * w, 0), 3840 - w)); y0 = int(min(max(cy - fy * h, 0), 2160 - h))
    return [x0 & ~1, y0 & ~1, w & ~1, h & ~1]
# (name, file, T0, T1, rect, zoom, drift, exposure, vignette, fade_in, fade_out, speed, tint(R,G,B), sat)
COOL = ((0.95, 0.99, 1.06), 0.72); NEU = ((1.0, 1.0, 1.0), 0.95); WARM = ((1.05, 1.0, 0.92), 1.0); WARM2 = ((1.08, 1.0, 0.88), 1.02)
SHOTS = [
 ("H_hook",  "IMG_3735.MOV", 1253.20, 1255.80, rect(1450, 1020, 1700, 0.40, 0.50), (1.00, 1.08), (0, -6), 0.95, 0.55, 0.45, 0.0, 1.0) + NEU,
 ("M1_wide", "main2.mov",    1180.00, 1183.60, rect(1200, 1100, 2160, 0.5, 0.5),    (1.00, 1.05), (10, 0), 0.95, 0.50, 0.0, 0.0, 1.0) + COOL,
 ("M1_cu",   "IMG_3735.MOV", 1183.60, 1189.42, rect(1350, 1050, 1900, 0.40, 0.50), (1.06, 1.00), (0, 0),  0.95, 0.50, 0.0, 0.0, 1.0) + COOL,
 ("M2_cu",   "IMG_3735.MOV", 1209.42, 1214.50, rect(1460, 860, 1700, 0.36, 0.50),  (1.00, 1.08), (0, 0),  0.93, 0.55, 0.0, 0.0, 1.0) + COOL,
 ("M2_main", "main3.mov",    1214.50, 1220.72, rect(810, 1140, 1500, 0.38, 0.45),  (1.00, 1.05), (6, 0),  0.94, 0.55, 0.0, 0.0, 1.0) + COOL,
 ("T1",      "IMG_3735.MOV", 1227.10, 1232.00, rect(1350, 950, 1900, 0.38, 0.50),  (1.06, 1.00), (0, 0),  0.98, 0.45, 0.0, 0.0, 1.0) + NEU,
 ("T2_alice","main3.mov",    1232.00, 1234.20, rect(3060, 1100, 1500, 0.38, 0.55), (1.00, 1.03), (0, 0),  1.00, 0.45, 0.0, 0.0, 1.0) + WARM,
 ("T3",      "IMG_3735.MOV", 1234.20, 1237.25, rect(1300, 900, 1700, 0.40, 0.50),  (1.00, 1.06), (0, 0),  1.00, 0.45, 0.0, 0.0, 1.0) + WARM,
 ("P1_ask",  "IMG_3735.MOV", 1255.95, 1261.70, rect(1480, 1060, 1650, 0.42, 0.50), (1.00, 1.10), (0, 0),  0.96, 0.60, 0.0, 0.0, 1.0) + WARM,
 ("P2_alice","main3.mov",    1261.70, 1263.30, rect(3060, 1100, 1450, 0.38, 0.55), (1.00, 1.04), (0, 0),  1.02, 0.45, 0.0, 0.0, 1.0) + WARM2,
 ("P3_yes",  "IMG_3735.MOV", 1263.30, 1267.27, rect(1500, 1060, 1800, 0.40, 0.50), (1.04, 1.00), (0, 0),  1.02, 0.45, 0.0, 0.0, 1.0) + WARM2,
 ("E_end",   "main3.mov",    1325.75, 1332.20, rect(810, 1140, 1500, 0.38, 0.45),  (1.00, 1.07), (0, -6), 1.00, 0.55, 0.0, 1.3, 1.0) + WARM2,
]
ENC = ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-r", "30"]
yy, xx = np.mgrid[0:H, 0:W]
R = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.42) / (H / 2)) ** 2)
VIG = np.clip((R - 0.55) / 0.9, 0, 1) ** 1.6
def render(i, sh, tl):
    name, f, T0, T1, (x, y, w, h), (z0, z1), (dx, dy), ex, vg, fi, fo, sp, tint, sat = sh
    TG = np.array(tint, np.float32)
    out_dur = (T1 - T0) / sp; N = round(out_dur * 30); src_n = round((T1 - T0) * 30) + 2
    vf = f"crop={w}:{h}:{x}:{y},scale={BW}:{BH}:flags=lanczos," + (TM if HDR[f] else "")
    vf += f"scale=in_color_matrix=bt709:in_range=tv,format=gbrp,lut3d={S}/lut/{LUT[f]}.cube:interp=tetrahedral,lut3d={S}/short2/perbuatan.cube:interp=tetrahedral,format=rgb24"
    dec = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-ss", str(T0 - OFF[f]), "-i", f"{S}/dl/{f}", "-an", "-frames:v", str(src_n), "-vf", vf,
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    buf = {}; nread = [0]; FS = BW * BH * 3
    def get(j):
        while nread[0] <= j:
            b = dec.stdout.read(FS)
            if len(b) < FS: break
            buf[nread[0]] = np.frombuffer(b, np.uint8).reshape(BH, BW, 3); nread[0] += 1
            for old in [q for q in buf if q < nread[0] - 3]: del buf[old]
        return buf[min(j, nread[0] - 1)]
    out = f"{SH}/{i:02d}_{name}.mp4"
    enc = subprocess.Popen(["ffmpeg", "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-"] + ENC + [out], stdin=subprocess.PIPE)
    vig = (1 - vg * VIG)[..., None]
    for k in range(N):
        sf = k * sp; a = int(np.floor(sf)); t = sf - a
        fa = get(a).astype(np.float32)
        fr = fa if t < 1e-3 else fa * (1 - t) + get(a + 1).astype(np.float32) * t  # frame blending for slow motion
        u = k / max(N - 1, 1); e = 0.5 - 0.5 * np.cos(np.pi * u); z = z0 + (z1 - z0) * e
        s = (W / BW) * z
        M = np.float32([[s, 0, W / 2 - s * BW / 2 + dx * e], [0, s, H / 2 - s * BH / 2 + dy * e]])
        img = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        g = ex
        if fi and k < fi * 30: g *= ((k + 1) / (fi * 30 + 1)) ** 1.5
        if fo and k >= N - fo * 30: g *= max(0.0, (N - k) / (fo * 30 + 1)) ** 1.5
        Yl = (img @ np.array([.2126, .7152, .0722], np.float32))[..., None]
        img = Yl + (img - Yl) * sat
        img = np.clip(img * TG * vig * g, 0, 255).astype(np.uint8)
        enc.stdin.write(img.tobytes())
    enc.stdin.close(); enc.wait(); dec.stdout.close(); dec.wait()
    return dict(tint=list(tint), sat=sat, id=i, name=name, file=f, master_T=[T0, T1], tl=round(tl, 3), frames=N, rect=[x, y, w, h], zoom=[z0, z1], speed=sp, exposure=ex, vignette=vg)
if __name__ == "__main__":
    plan = []; tl = 0.0
    for i, sh in enumerate(SHOTS):
        r = render(i, sh, tl); plan.append(r); tl += r["frames"] / 30; print(r["name"], r["frames"], flush=True)
    json.dump(plan, open(f"{S}/short2/plan.json", "w"), indent=1)
    with open(f"{SH}/concat.txt", "w") as f:
        for r in plan: f.write(f"file '{SH}/{r['id']:02d}_{r['name']}.mp4'\n")
    print("total", round(tl, 3))
