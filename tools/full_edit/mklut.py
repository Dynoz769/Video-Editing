import numpy as np, json, sys, colorsys
S=sys.argv[1]; C=json.load(open(f"{S}/colan.json"))
TR,TB,TY=1.36,0.82,0.56
def smooth(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
def look(rgb):
    # luminance-based contrast curve with soft shoulder, black lift
    Y=rgb@np.array([.2126,.7152,.0722])
    p=0.45; k=0.10
    Yc=Y+k*np.sin(np.pi*np.clip(Y,0,1))*(np.clip(Y,0,1)-p)*2*(Y>0)  # gentle S around pivot
    sh=0.82; Yc=np.where(Yc>sh, sh+(1-sh)*np.tanh((Yc-sh)/(1-sh)), Yc)  # roll-off
    Yc=0.03+Yc*(0.975-0.03)
    out=rgb*((Yc+1e-5)/(Y+1e-5))[...,None]
    # split warmth: warm mids, very slight cool shadows
    mid=4*Y*(1-Y); shd=np.clip(1-Y/0.3,0,1)
    out[...,0]+=0.012*mid; out[...,2]-=0.010*mid
    pass
    return out
def satskin(rgb,sat):
    Y=(rgb@np.array([.2126,.7152,.0722]))[...,None]
    r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]
    mx=rgb.max(-1); mn=rgb.min(-1); c=mx-mn+1e-6
    h=np.where(mx==r,((g-b)/c)%6,np.where(mx==g,(b-r)/c+2,(r-g)/c+4))*60
    skin=smooth(5,18,h)*(1-smooth(45,60,h))  # skin hue band
    s=sat+(1.0-sat)*skin   # skin keeps native saturation
    out=Y+(rgb-Y)*s[...,None]
    # cap skin chroma (avoid orange/red)
    ch=(out.max(-1)-out.min(-1))/(out.max(-1)+1e-6)
    cap=np.where((skin>0.5)&(ch>0.5), 0.5/ch, 1.0)
    out=Y+(out-Y)*cap[...,None]
    return out
N=33; g=np.linspace(0,1,N)
B_,G_,R_=np.meshgrid(g,g,g,indexing='ij'); base=np.stack([R_,G_,B_],-1).reshape(-1,3)
params={}
for k,v in C.items():
    fr=np.array(v["faceRGB"]); rg=fr[0]/fr[1]; bg=fr[2]/fr[1]
    gr=np.clip((TR/rg)**0.75,0.9,1.1); gb=np.clip((TB/bg)**0.75,0.9,1.12)
    gains=np.array([gr,1,gb]); gains/= (gains@[.2126,.7152,.0722])
    fy=v["faceY"]; gam=np.clip(np.log(TY)/np.log(fy),0.75,1.4)
    x=np.clip(base*gains,0,1)**gam
    if k.startswith('main'):
        hl=np.clip((x@np.array([.2126,.7152,.0722])-0.55)/0.4,0,1)[:,None]
        x=x*(1-hl*np.array([0.015,0,0.005]))
    if k.startswith('main'):
        sd=np.clip(1-(x@np.array([.2126,.7152,.0722]))/0.35,0,1)
        x[:,2]-=0.03*sd*x[:,2]/np.maximum(x.max(1),1e-3); x[:,0]+=0.008*sd
    x=look(x); x=satskin(x,0.96); x=np.clip(x,0,1)
    params[k]=dict(gainR=round(float(gains[0]),3),gainB=round(float(gains[2]),3),gamma=round(float(gam),3))
    with open(f"{S}/lut/{k}.cube","w") as f:
        f.write(f"LUT_3D_SIZE {N}\n"); np.savetxt(f,x,fmt="%.5f")
print(json.dumps(params))
json.dump(params,open(f"{S}/lut/params.json","w"))
