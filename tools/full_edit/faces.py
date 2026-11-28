import numpy as np, subprocess, json, sys, cv2
S=sys.argv[1]; D=f"{S}/dl"
TM="zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:desat=0:param=0.3,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,"
cas=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
src={"main":("IMG_2836.mov",[40,120,220,330,450,560])}
for c in "3709 3710 3717 3718 3719 3720 3721 3722 3724 3725 3726 3727 3728 3730".split():
    dur=float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{D}/IMG_{c}.MOV"]))
    src[c]=(f"IMG_{c}.MOV",list(np.linspace(0.5,dur-0.5,5)))
res=json.load(open(f"{S}/colan.json"))
for k,(f,ts) in src.items():
    fp=[];boxes=[]
    for t in ts:
        vf=(TM if k=="main" else "")+"scale=1280:720,format=rgb24"
        raw=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i",f"{D}/{f}","-frames:v","1","-vf",vf,"-f","rawvideo","-"],capture_output=True).stdout
        im=np.frombuffer(raw,np.uint8).reshape(720,1280,3)
        g=cv2.cvtColor(im,cv2.COLOR_RGB2GRAY)
        for (x,y,w,h) in cas.detectMultiScale(g,1.1,6,minSize=(40,40)):
            boxes.append([round(t,1),int(x*3),int(y*3),int(w*3)])
            fp.append(im[y+h//4:y+3*h//4, x+w//4:x+3*w//4].reshape(-1,3)/255.)
    if fp:
        p=np.concatenate(fp); Y=(0.2126*p[:,0]+0.7152*p[:,1]+0.0722*p[:,2])
        res[k]["faceY"]=float(np.median(Y)); res[k]["faceRGB"]=np.median(p,0).round(3).tolist()
    res[k]["faces4k"]=boxes
    print(k,res[k].get("faceY"),res[k].get("faceRGB"),boxes[:6],flush=True)
json.dump(res,open(f"{S}/colan.json","w"),default=float)
