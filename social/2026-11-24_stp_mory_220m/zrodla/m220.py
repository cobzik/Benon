import sys, os, subprocess, importlib.util
from PIL import Image, ImageDraw
D=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location("b",f"{D}/build.py"); b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
IMG="/root/.claude/uploads/5e4dd994-5aad-5aad-82f6-d818a0ee89cb/db64e807-image.jpg"
OUT="/home/user/Benon/social/2026-11-24_stp_mory_220m"; os.makedirs(OUT,exist_ok=True)
b.S=D; b.OUT=OUT; b.G_BOT=b.grad(980,1780,0,0.66)
W,H,FPS,X=1080,1920,30,0.45
# (dur, z0, z1, (cx0,cy0), (cx1,cy1))
SH=[(4.4,1.00,1.75,(0.50,0.50),(0.53,0.37)),
    (3.1,2.00,2.18,(0.80,0.60),(0.74,0.74)),
    (3.4,1.40,1.00,(0.50,0.42),(0.50,0.50))]
END=3.6
durs=[s[0] for s in SH]+[END]; starts=[];t=0
for d in durs: starts.append(t); t+=d-X
TOTAL=starts[-1]+durs[-1]; b.starts=starts; b.TOTAL=TOTAL
grade="eq=contrast=1.06:saturation=1.1,unsharp=5:5:0.7:5:5:0,vignette=PI/7,format=yuv420p,setsar=1"
def base():
    parts=[]
    for i,(d,z0,z1,c0,c1) in enumerate(SH):
        e=f"((1-cos(PI*t/{d}))/2)"
        Z=f"({z0}+({z1}-{z0})*{e})"; CX=f"({c0[0]}+({c1[0]}-{c0[0]})*{e})"; CY=f"({c0[1]}+({c1[1]}-{c0[1]})*{e})"
        vf=(f"fps={FPS},scale=w='2*trunc(1080.5*{Z}/2)':h=-2:eval=frame:flags=lanczos,"
            f"crop=1080:1920:'max(0\\,min(iw-1080\\,{CX}*iw-540))':'max(0\\,min(ih-1920\\,{CY}*ih-960))',{grade}")
        o=f"{D}/s{i}.mp4"
        subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-t",f"{d}","-i",IMG,"-vf",vf,"-c:v","libx264","-crf","14","-preset","fast",o],check=True); parts.append(o)
    o=f"{D}/endbg.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i",f"color=c=0x0f1114:s={W}x{H}:r={FPS}:d={END}","-c:v","libx264","-crf","14","-pix_fmt","yuv420p",o],check=True); parts.append(o)
    inp=[]
    for p in parts: inp+=["-i",p]
    fc="";last="[0:v]"
    for i in range(1,len(parts)):
        tr="fadeblack" if i==len(parts)-1 else "fade"
        fc+=f"{last}[{i}:v]xfade=transition={tr}:duration={X}:offset={starts[i]:.3f}[x{i}];"; last=f"[x{i}]"
    subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",fc[:-1],"-map",last,"-c:v","libx264","-crf","14","-preset","fast","-pix_fmt","yuv420p",f"{D}/base.mp4"],check=True)

def counter(L,t,t0,t1,kicker,val,unit,sub,y=1080):
    a=b.fade_ab(t,t0,t1)
    if a<=0: return
    d=ImageDraw.Draw(L); x=84; off=(1-b.ease((t-t0)/0.6))*40
    v=int(round(val*b.ease((t-t0-0.1)/1.8)))
    d.rectangle([x-34,y+4,x-24,y+4+300*b.ease((t-t0)/0.5)],fill=b.YEL+(int(255*a),))
    b.text(d,(x,y+off*0.5),kicker,b.F(b.FBo,30),b.YEL,a,spacing=4)
    w=b.text(d,(x-6,y+215+off),f"{v}",b.F(b.FB,190),b.WHITE,a,anchor="ls")
    b.text(d,(x+w+14,y+215+off),unit,b.F(b.FB,96),b.YEL,a,anchor="ls")
    b.text(d,(x,y+262+off*0.5),sub,b.F(b.FSB,46),(240,240,240),min(a,b.ease((t-t0-0.35)/0.5)))

s=[(starts[i],starts[i]+durs[i]) for i in range(len(SH))]
T=lambda i: s[i][0]+0.2; E=lambda i: s[i][1]-X-0.05
CFG={"end1":"Posadzki przemysłowe od 2000 roku","end2":"Duża inwestycja? Zapytaj o wycenę","items":[
 lambda L,t: counter(L,t,T(0),E(0),"STP MORY · PRZED BETONOWANIEM",220,"m","długości obiektu, ok. 1 000 m²"),
 lambda L,t: b.caption(L,t,T(1),E(1),"LOGISTYKA",["Pompa + rurociąg"],"z jednego ustawienia na całą długość",big=84),
 lambda L,t: b.caption(L,t,T(2),E(2),"BETONOWANIE",["12 h non-stop"],"ciągła praca, bez przerw",y=1190,big=96),
]}
if "base" in sys.argv: base()
if "test" in sys.argv:
    os.makedirs(f"{D}/test",exist_ok=True); ims=[]
    for i in range(len(SH)):
        for frac in (0.1,0.6,0.95):
            tt=s[i][0]+durs[i]*frac; fr=f"{D}/test/f.png"
            subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{tt}","-i",f"{D}/base.mp4","-frames:v","1",fr],check=True)
            im=Image.open(fr).convert("RGBA"); L=Image.new("RGBA",(W,H),(0,0,0,0)); L.alpha_composite(b.G_BOT); L.alpha_composite(b.G_TOP); L.alpha_composite(b.LOGO_S,((W-b.LOGO_S.width)//2,130))
            for fn in CFG["items"]: fn(L,tt)
            im.alpha_composite(L); ims.append(im.convert("RGB").resize((270,480)))
    sh=Image.new("RGB",(270*len(ims),480))
    for k,im in enumerate(ims): sh.paste(im,(270*k,0))
    sh.save(f"{D}/test/sheet.jpg")
if "final" in sys.argv: b.finish(CFG,"m220","benon_tiktok_stp_mory_220m")
print("TOTAL",round(TOTAL,2))
