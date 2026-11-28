import json, subprocess, numpy as np
meta=json.load(open('audio_meta.json')); p={r['name']:r['tl'] for r in json.load(open('plan.json'))}
T=meta['total']; N=int(round(T*30)); w,h=270,480
yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
def blob(cx,cy,r): return np.exp(-(((xx-cx)/r)**2+((yy-cy)/(r*1.4))**2))
AMBER=np.array([1.0,0.62,0.28],np.float32); GOLD=np.array([1.0,0.80,0.45],np.float32); SCREEN=np.array([0.45,0.65,1.0],np.float32)
def env(t,a,b,ri=0.8,fo=0.8):
    if t<a or t>b: return 0.0
    return min(1,(t-a)/ri,(b-t)/fo)
rng=np.random.default_rng(5); P=55
px=rng.uniform(0,w,P); py=rng.uniform(0,h,P); vx=rng.uniform(-2,2,P); vy=rng.uniform(-5,-1.5,P); pb=rng.uniform(0.25,0.9,P); ph=rng.uniform(0,6.28,P)
endpic=p['E_end']+6.45
enc=subprocess.Popen(["ffmpeg","-nostdin","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{w}x{h}","-r","30","-i","-",
    "-vf","scale=1080:1920:flags=bicubic","-c:v","libx264","-preset","veryfast","-crf","12","-pix_fmt","yuv420p","leak2.mp4"],stdin=subprocess.PIPE)
for i in range(N):
    t=i/30; img=np.zeros((h,w,3),np.float32)
    img+=env(t,0,p['M1_wide'],0.8,0.6)*0.18*blob(w*0.2,h*0.1,150)[...,None]*AMBER                                   # hook: faint warmth
    k=env(t,p['M1_wide']-0.2,p['T1']+0.6,0.6,1.2); fl=0.85+0.15*np.sin(t*7.3)*np.sin(t*2.1)
    img+=k*0.16*fl*blob(w*0.85,h*0.30,120)[...,None]*SCREEN                                                        # cool screen glow
    warm=env(t,p['T1']-0.3,endpic,2.5,1.2)
    img+=warm*0.16*blob(w*0.15+8*np.sin(t*0.3),h*0.12,170)[...,None]*AMBER                                         # warmth arrives
    img+=env(t,p['P2_alice']-0.1,p['P3_yes']+3.0,0.4,1.5)*0.30*blob(w*0.5,h*0.05,200)[...,None]*GOLD                 # bloom on the answer
    img+=env(t,p['E_end'],T-1.0,1.0,1.5)*0.22*blob(w*0.75,h*0.15,170)[...,None]*AMBER                               # ending warmth
    if warm>0 or t<p['M1_wide']:
        dk=max(warm, env(t,0,p['M1_wide'],0.5,0.5))
        x=(px+vx*t)%w; y=(py+vy*t)%h; tw=0.6+0.4*np.sin(ph+t*1.3)
        for j in range(P):
            xi,yi=int(x[j]),int(y[j]); img[yi,xi]+=dk*0.20*pb[j]*tw[j]*GOLD
    enc.stdin.write((np.clip(img,0,1)*255).astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait(); print('frames',N)
