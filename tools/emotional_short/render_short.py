"""Vertical 1080x1920 emotional short: shot renderer."""
import json, sys, os, subprocess, numpy as np, cv2
S = sys.argv[1]; SH = f"{S}/short/shots"; os.makedirs(SH, exist_ok=True)
TM = open(f"{S}/tm.txt").read()
W, H = 1080, 1920; BW, BH = 1188, 2112
OFF = {"IMG_3734.MOV": 979.4025, "main2.mov": 611.777}
LUT = {"IMG_3734.MOV": "3734", "main2.mov": "main2"}
HDR = {"IMG_3734.MOV": False, "main2.mov": True}
def rect(cx, cy, h, fy=0.38, fx=0.5):
    w = int(round(h * 9 / 16)); x0 = int(min(max(cx - fx * w, 0), 3840 - w)); y0 = int(min(max(cy - fy * h, 0), 2160 - h))
    return [x0 & ~1, y0 & ~1, w & ~1, h & ~1]
D34 = (1160, 1150); DM2 = (800, 1140); AM2 = (3000, 1170)
# (name, file, master_T_start, master_T_end, rect, zoom(z0,z1), drift_px(x,y), exposure, vignette, fade_in, fade_out, speed)
SHOTS = [
 ("A_hook",     "IMG_3734.MOV", 1066.20, 1070.40, rect(1080, 1150, 1700, 0.42, 0.50), (1.00, 1.08), (6, 0), 0.92, 0.55, 0.55, 0.0, 1.0),
 ("B1_ctx",     "main2.mov",    1047.50, 1049.95, rect(*DM2, 1500, 0.38, 0.45), (1.00, 1.05), (12, 0),  1.00, 0.45, 0.0, 0.0, 1.0),
 ("B2_ctx",     "IMG_3734.MOV", 1051.70, 1056.33, rect(*D34, 1900, 0.36, 0.48), (1.06, 1.00), (-14, 0), 1.00, 0.45, 0.0, 0.0, 1.0),
 ("B3_env",     "main2.mov",    1056.33, 1059.85, rect(1150, 1080, 2160, 0.5, 0.5), (1.00, 1.06), (0, 0),  0.97, 0.50, 0.0, 0.0, 1.0),
 ("C1_verse",   "IMG_3734.MOV", 1070.40, 1074.30, rect(1090, 1120, 1850, 0.40, 0.50), (1.08, 1.00), (0, 8),   0.98, 0.50, 0.0, 0.0, 1.0),
 ("C2_verse",   "main2.mov",    1074.30, 1076.95, rect(*DM2, 1500, 0.38, 0.45), (1.00, 1.04), (8, 0),  0.97, 0.50, 0.0, 0.0, 1.0),
 ("D_peak",     "IMG_3734.MOV", 1080.85, 1088.60, rect(1190, 1110, 1650, 0.46, 0.50), (1.00, 1.11), (0, 10), 0.88, 0.70, 0.35, 0.0, 1.0),
 ("E_react",    "main2.mov",    1088.12, 1089.58, rect(*AM2, 1500, 0.38, 0.55), (1.00, 1.03), (0, 0),  0.95, 0.55, 0.0, 0.0, 1.0),
 ("F_end",      "IMG_3734.MOV", 1088.15, 1089.75, rect(1080, 1130, 1900, 0.42, 0.52), (1.00, 1.07), (0, 0),  0.92, 0.65, 0.0, 1.6, 0.5),
]
ENC = ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-r", "30"]
yy, xx = np.mgrid[0:H, 0:W]
R = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.42) / (H / 2)) ** 2)
VIG = np.clip((R - 0.55) / 0.9, 0, 1) ** 1.6
def render(i, sh, tl):
    name, f, T0, T1, (x, y, w, h), (z0, z1), (dx, dy), ex, vg, fi, fo, sp = sh
    out_dur = (T1 - T0) / sp; N = round(out_dur * 30); src_n = round((T1 - T0) * 30) + 2
    vf = f"crop={w}:{h}:{x}:{y},scale={BW}:{BH}:flags=lanczos," + (TM if HDR[f] else "")
    vf += f"scale=in_color_matrix=bt709:in_range=tv,format=gbrp,lut3d={S}/lut/{LUT[f]}.cube:interp=tetrahedral,lut3d={S}/short/rindu.cube:interp=tetrahedral,format=rgb24"
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
        img = np.clip(img * vig * g, 0, 255).astype(np.uint8)
        enc.stdin.write(img.tobytes())
    enc.stdin.close(); enc.wait(); dec.stdout.close(); dec.wait()
    return dict(id=i, name=name, file=f, master_T=[T0, T1], tl=round(tl, 3), frames=N, rect=[x, y, w, h], zoom=[z0, z1], speed=sp, exposure=ex, vignette=vg)
if __name__ == "__main__":
    plan = []; tl = 0.0
    for i, sh in enumerate(SHOTS):
        r = render(i, sh, tl); plan.append(r); tl += r["frames"] / 30; print(r["name"], r["frames"], flush=True)
    json.dump(plan, open(f"{S}/short/plan.json", "w"), indent=1)
    with open(f"{SH}/concat.txt", "w") as f:
        for r in plan: f.write(f"file '{SH}/{r['id']:02d}_{r['name']}.mp4'\n")
    print("total", round(tl, 3))
