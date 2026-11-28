import json, sys, os, subprocess, numpy as np, cv2, hashlib
from multiprocessing import Pool
S = sys.argv[1]; E = json.load(open(sys.argv[2])); D = f"{S}/dl"; SH = f"{S}/shots2"; os.makedirs(SH, exist_ok=True)
TM = open(f"{S}/tm.txt").read()
W, H = 1920, 1080; BW, BH = 2112, 1188
ENC = ["-vf", "scale=out_color_matrix=bt709:out_range=tv,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "15",
       "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-r", "30"]

def key(sh):
    lut = open(f"{S}/lut/{sh['lut']}.cube", "rb").read() if sh.get("lut") else b""
    return hashlib.md5((json.dumps(sh, sort_keys=True, default=str) + TM).encode() + lut).hexdigest()[:10]

def render(sh):
    out = f"{SH}/{sh['id']:03d}.mp4"; kf = out + ".key"; k = key(sh)
    if os.path.exists(out) and os.path.exists(kf) and open(kf).read() == k: return sh["id"], "cached"
    N = sh["frames"]
    if sh["view"] == "BLACK":
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=black:s={W}x{H}:r=30", "-frames:v", str(N)] + ENC + [out], check=True)
    else:
        x, y, w, h = sh["rect"]
        vf = f"crop={w}:{h}:{x}:{y},scale={BW}:{BH}:flags=lanczos,"
        vf += TM if sh["hdr"] else ""
        vf += f"scale=in_color_matrix=bt709:in_range=tv,format=gbrp,lut3d={S}/lut/{sh['lut']}.cube:interp=tetrahedral,format=rgb24"
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(sh["src_in"]), "-i", f"{D}/{sh['file']}", "-an", "-frames:v", str(N),
                                "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-"] + ENC + [out],
                               stdin=subprocess.PIPE)
        z0, z1 = sh["zoom"]; fi = int(sh["fade_in"] * 30); fo = int(sh["fade_out"] * 30); last = None
        for i in range(N):
            buf = dec.stdout.read(BW * BH * 3)
            if len(buf) == BW * BH * 3: last = np.frombuffer(buf, np.uint8).reshape(BH, BW, 3)
            fr = last
            u = i / max(N - 1, 1); z = z0 + (z1 - z0) * (0.5 - 0.5 * np.cos(np.pi * u))
            if z0 == 1 and z1 == 1:
                img = cv2.resize(fr, (W, H), interpolation=cv2.INTER_AREA)
            else:
                s = (W / BW) * z
                M = np.float32([[s, 0, W / 2 - s * BW / 2], [0, s, H / 2 - s * BH / 2]])
                img = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
            g = 1.0
            if fi and i < fi: g = (i + 1) / (fi + 1)
            if fo and i >= N - fo: g = min(g, (N - i) / (fo + 1))
            if g < 1: img = (img.astype(np.float32) * (g * g * (3 - 2 * g))).astype(np.uint8)
            enc.stdin.write(img.tobytes())
        enc.stdin.close(); enc.wait(); dec.stdout.close(); dec.wait()
    n = int(subprocess.check_output(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries", "stream=nb_read_frames", "-of", "csv=p=0", out]))
    if n != N: return sh["id"], f"FRAME MISMATCH {n}!={N}"
    open(kf, "w").write(k)
    return sh["id"], "ok"

if __name__ == "__main__":
    ids = None if len(sys.argv) < 4 else set(map(int, sys.argv[3].split(",")))
    todo = [s for s in E["shots"] if ids is None or s["id"] in ids]
    with Pool(int(os.environ.get("NP", "3"))) as p:
        for r in p.imap_unordered(render, todo): print(*r, flush=True)
    with open(f"{SH}/concat.txt", "w") as f:
        for s in E["shots"]: f.write(f"file '{SH}/{s['id']:03d}.mp4'\n")
