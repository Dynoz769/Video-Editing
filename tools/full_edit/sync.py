import numpy as np, glob, os, json, sys
from scipy.io import wavfile
from scipy.signal import fftconvolve
S=sys.argv[1]; SR=8000
def load(p):
    x=wavfile.read(p)[1].astype(np.float32); x-=x.mean()
    # pre-emphasis to whiten
    x=np.append(x[0],x[1:]-0.97*x[:-1]); return x/(np.std(x)+1e-9)
masters={os.path.basename(p)[:-4]:load(p) for p in glob.glob(f"{S}/a8/*.wav") if not os.path.basename(p).startswith("c_")}
res={}
for p in sorted(glob.glob(f"{S}/a8/c_*.wav")):
    c=load(p); name=os.path.basename(p)[2:-4]; best=None
    for mn,m in masters.items():
        if len(c)>len(m): continue
        cc=fftconvolve(m,c[::-1],mode='valid')
        # local normalization
        e=np.sqrt(fftconvolve(m**2,np.ones(len(c)),mode='valid'))+1e-9
        ncc=cc/(e*np.sqrt((c**2).sum()))
        i=int(np.argmax(ncc)); sc=float(ncc[i]); s2=np.sort(ncc)[-50]
        if best is None or sc>best[2]: best=(mn,i/SR,sc,float(sc/(np.median(np.abs(ncc))+1e-9)))
    res[name]=dict(master=best[0],offset=round(best[1],4),ncc=round(best[2],3),snr=round(best[3],1),dur=len(c)/SR)
    print(name,res[name],flush=True)
json.dump(res,open(f"{S}/sync.json","w"),indent=1)
