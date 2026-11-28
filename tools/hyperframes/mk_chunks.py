"""Split the full composition into time chunks: shift clip timing, drive the master timeline with tweenFromTo."""
import re, sys, os
src = open("full/index.html").read()
TOTAL = float(re.search(r'data-composition-id="main" data-start="0" data-duration="([0-9.]+)"', src).group(1))
CH = 300.0
n = int(-(-TOTAL // CH))
for k in range(n):
    off = k * CH; dur = min(CH, TOTAL - off); d = f"chunks/c{k:02d}"; os.makedirs(f"{d}/assets", exist_ok=True)
    if not os.path.exists(f"{d}/assets/gsap.min.js"): os.link("full/assets/gsap.min.js", f"{d}/assets/gsap.min.js")
    def fix(m):
        a = float(m.group(2)); du = float(m.group(3)); b = a + du
        if b <= off or a >= off + dur: return m.group(1) + ' data-hidden="true" data-start="0" data-duration="0.05"'
        na = max(a, off) - off; nb = min(b, off + dur) - off
        return f'{m.group(1)} data-start="{na:.3f}" data-duration="{max(nb - na, 0.04):.3f}"'
    body = re.sub(r'(<div id="[^"]+" class="clip[^"]*") data-start="([0-9.]+)" data-duration="([0-9.]+)"', fix, src)
    body = body.replace(f'data-composition-id="main" data-start="0" data-duration="{TOTAL:.3f}"', f'data-composition-id="main" data-start="0" data-duration="{dur:.3f}"')
    body = body.replace('window.__timelines["main"] = tl;',
        f'const drv = gsap.timeline({{ paused: true }}); drv.add(tl.tweenFromTo({off:.3f}, {off+dur:.3f}, {{ ease: "none", duration: {dur:.3f} }}), 0);\nwindow.__timelines["main"] = drv;')
    body = body.replace('const tl = gsap.timeline({ paused: true });', 'const tl = gsap.timeline({ paused: true }); tl.to({}, {duration: %.3f}, 0);' % TOTAL)
    open(f"{d}/index.html", "w").write(body)
    print(d, off, dur)
