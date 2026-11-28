import numpy as np
def ss(a,b,x): t=np.clip((x-a)/(b-a),0,1); return t*t*(3-2*t)
N=33; g=np.linspace(0,1,N); B_,G_,R_=np.meshgrid(g,g,g,indexing='ij'); x=np.stack([R_,G_,B_],-1).reshape(-1,3)
W=np.array([.2126,.7152,.0722]); Y=x@W
# saturation: 0.80, skin hues keep 0.92
mx=x.max(1); mn=x.min(1); c=mx-mn+1e-6; r,gg,b=x.T
h=np.where(mx==r,((gg-b)/c)%6,np.where(mx==gg,(b-r)/c+2,(r-gg)/c+4))*60
skin=ss(5,18,h)*(1-ss(45,60,h))
sat=0.80+0.12*skin
x=Y[:,None]+(x-Y[:,None])*sat[:,None]
# tone: slightly deeper shadows, soft highlight roll-off (max 0.95)
Y=x@W; Yt=np.clip(Y,0,1)**1.07
Yt=np.where(Yt>0.72,0.72+0.23*np.tanh((Yt-0.72)/0.23),Yt)
x=x*((Yt+1e-5)/(Y+1e-5))[:,None]
# warm amber highlights, gentle warm mids
hl=ss(0.42,0.95,Yt)[:,None]; mid=(4*Yt*(1-Yt))[:,None]
x=x+hl*np.array([0.035,0.012,-0.030])+mid*np.array([0.008,0.0,-0.006])
x=np.clip(x,0,1)
open('rindu.cube','w').write("LUT_3D_SIZE 33\n"+"\n".join(" ".join(f"{v:.5f}" for v in p) for p in x))
print('ok')
