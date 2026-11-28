import json, subprocess, numpy as np
D='.'; meta=json.load(open('audio_meta.json')); p={r['name']:r['tl'] for r in json.load(open('plan.json'))}
T=meta['total']; N=int(round(T*30)); w,h=270,480
yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
def blob(cx,cy,r): return np.exp(-(((xx-cx)/r)**2+((yy-cy)/(r*1.4))**2))
AMBER=np.array([1.0,0.62,0.28],np.float32); GOLD=np.array([1.0,0.80,0.45],np.float32)
def env(t,a,b,ri=0.8,fo=0.8):
    if t<a or t>b: return 0.0
    return min(1,(t-a)/ri,(b-t)/fo)
rng=np.random.default_rng(3); P=60
px=rng.uniform(0,w,P); py=rng.uniform(0,h,P); vx=rng.uniform(-2,2,P); vy=rng.uniform(-5,-1.5,P); pb=rng.uniform(0.25,0.9,P); ph=rng.uniform(0,6.28,P)
rindu=p['D_peak']+(1083.10-1080.85)
enc=subprocess.Popen(["ffmpeg","-nostdin","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{w}x{h}","-r","30","-i","-",
    "-vf","scale=1080:1920:flags=bicubic","-c:v","libx264","-preset","veryfast","-crf","12","-pix_fmt","yuv420p","leak.mp4"],stdin=subprocess.PIPE)
for i in range(N):
    t=i/30; img=np.zeros((h,w,3),np.float32)
    k=env(t,0.0,4.6,1.2,1.6); img+=k*0.32*blob(-20+40*t,60+10*t,150)[...,None]*AMBER                     # hook sweep
    k=env(t,p['B1_ctx']-0.15,p['B1_ctx']+0.9,0.15,0.75); img+=k*0.55*blob(w*0.8,h*0.15,170)[...,None]*GOLD    # memory flare
    k=env(t,p['B1_ctx'],p['C1_verse'],1.0,1.5); img+=k*0.10*np.clip(1-yy/(h*0.55),0,1)[...,None]*AMBER        # haze from top
    k=env(t,p['C1_verse'],p['D_peak'],1.2,1.0); img+=k*0.22*blob(w+30-10*(t-p['C1_verse']),h*0.35,140)[...,None]*AMBER  # side glow verse
    k=env(t,rindu-0.3,p['E_react']-0.2,2.2,0.9); img+=k*0.30*blob(w*0.55,-40+6*(t-rindu),210)[...,None]*GOLD   # light rising on "rindu"
    k=env(t,p['F_end']-0.2,T-1.2,0.8,1.6); img+=k*0.28*blob(w*0.25,h*0.2,180)[...,None]*AMBER                # ending warmth
    # dust
    x=(px+vx*t)%w; y=(py+vy*t)%h; tw=0.6+0.4*np.sin(ph+t*1.3)
    for j in range(P):
        xi,yi=int(x[j]),int(y[j])
        if 0<=xi<w and 0<=yi<h: img[yi,xi]+=0.20*pb[j]*tw[j]*GOLD
    enc.stdin.write((np.clip(img,0,1)*255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print('frames',N)
