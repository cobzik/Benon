import sys, os, subprocess, importlib.util, math
from PIL import Image, ImageDraw
D=os.path.dirname(os.path.abspath(__file__))
spec=importlib.util.spec_from_file_location("b",f"{D}/build.py"); b=importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
U="/root/.claude/uploads/5e4dd994-5aad-5aad-82f6-d818a0ee89cb"
OUT="/home/user/Benon/social/2026-11-24_stp_mory_metro"; os.makedirs(OUT,exist_ok=True)
b.S=D; b.OUT=OUT
b.G_BOT=b.grad(980,1780,0,0.6)
W,H,FPS,X=1080,1920,30,0.45
# (file, kind, duration, param): V -> zoom from/to ; H -> vanishing point x in source px
SH=[("ed9bd308","V",2.9,(1.00,1.07)),
    ("eb06219f","H",2.3,940),
    ("1e01814d","V",2.2,(1.07,1.00)),
    ("8a615399","H",2.3,790),
    ("0cd49275","H",2.3,1060),
    ("6c624136","V",2.2,(1.00,1.06)),
    ("8b6bca28","V",2.4,(1.06,1.00))]
END=3.6
durs=[s[2] for s in SH]+[END]; starts=[];t=0
for d in durs: starts.append(t); t+=d-X
TOTAL=starts[-1]+durs[-1]; b.starts=starts; b.TOTAL=TOTAL
grade="eq=contrast=1.05:saturation=1.08,unsharp=5:5:0.6:5:5:0,vignette=PI/7,format=yuv420p,setsar=1"
def base():
    parts=[]
    for i,(f,k,d,p) in enumerate(SH):
        src=f"{U}/{f}-image.jpg"; o=f"{D}/s{i}.mp4"
        if k=="V":
            z0,z1=p; z=f"({z0}+({z1}-{z0})*t/{d})"
            vf=f"fps={FPS},scale=w='2*trunc(1080*{z}/2)':h=-2:eval=frame:flags=lanczos,crop=1080:1920:'(iw-1080)/2':'(ih-1920)/2',{grade}"
        else:
            sc=1920/924; vp=p*sc; x0=vp-540-260; x1=vp-540+260
            vf=f"fps={FPS},scale=-2:1920:flags=lanczos,crop=1080:1920:'max(0,min(iw-1080,{x0:.0f}+({x1-x0:.0f})*t/{d}))':0,{grade}"
        subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-t",f"{d}","-i",src,"-vf",vf,"-c:v","libx264","-crf","14","-preset","fast",o],check=True)
        parts.append(o)
    o=f"{D}/endbg.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i",f"color=c=0x0f1114:s={W}x{H}:r={FPS}:d={END}","-c:v","libx264","-crf","14","-pix_fmt","yuv420p",o],check=True); parts.append(o)
    inp=[]
    for p in parts: inp+=["-i",p]
    fc="";last="[0:v]"
    for i in range(1,len(parts)):
        tr="fadeblack" if i==len(parts)-1 else ("slideleft" if SH[i][1]=="H" and SH[i-1][1]=="V" else "fade")
        tr="fadeblack" if i==len(parts)-1 else "fade"
        fc+=f"{last}[{i}:v]xfade=transition={tr}:duration={X}:offset={starts[i]:.3f}[x{i}];"; last=f"[x{i}]"
    subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",fc[:-1],"-map",last,"-c:v","libx264","-crf","14","-preset","fast","-pix_fmt","yuv420p",f"{D}/base.mp4"],check=True)

def big_counter(L,t,t0,t1,kicker,sub1,sub2,y=1060):
    a=b.fade_ab(t,t0,t1)
    if a<=0: return
    d=ImageDraw.Draw(L); x=84; off=(1-b.ease((t-t0)/0.6))*40
    v=int(round(45000*b.ease((t-t0-0.1)/1.4)/100))*100
    s=f"{v:,}".replace(","," ")
    d.rectangle([x-34,y+4,x-24,y+4+330*b.ease((t-t0)/0.5)],fill=b.YEL+(int(255*a),))
    b.text(d,(x,y+off*0.5),kicker,b.F(b.FBo,30),b.YEL,a,spacing=4)
    w=b.text(d,(x-4,y+200+off),s,b.F(b.FB,160),b.WHITE,a,anchor="ls")
    b.text(d,(x+w+12,y+200+off),"m²",b.F(b.FB,80),b.YEL,a,anchor="ls")
    a2=min(a,b.ease((t-t0-0.35)/0.5))
    b.text(d,(x,y+238+off*0.5),sub1,b.F(b.FSB,46),(240,240,240),a2)
    b.text(d,(x,y+296+off*0.5),sub2,b.F(b.FSB,46),(240,240,240),a2)

s=[(starts[i],starts[i]+durs[i]) for i in range(len(SH))]
T=lambda i: s[i][0]+0.2; E=lambda i: s[i][1]-X-0.05
CFG={"end1":"Posadzki przemysłowe od 2000 roku","end2":"Duża inwestycja? Zapytaj o wycenę","items":[
 lambda L,t: big_counter(L,t,T(0),E(0),"METRO WARSZAWSKIE · STP MORY","posadzek w halach","obsługi taboru metra"),
 lambda L,t: b.caption(L,t,T(1),E(2),"TECHNOLOGIA",["Posadzki DST"],"utwardzane powierzchniowo"),
 lambda L,t: b.caption(L,t,T(3),E(3),"BETON",["C25/30","+ włókna"],"kopolimerowe Bautech"),
 lambda L,t: b.caption(L,t,T(4),E(5),"KOMPLEKSOWO",["Wykonanie","z projektem"],"system utwardzenia Bautech"),
 lambda L,t: b.caption(L,t,T(6),E(6),"REALIZACJA",["2024–2026"],None,y=1200),
 lambda L,t: b.pin_chip(L,t,T(6)+0.25,E(6),[("pin","Warszawa · STP Mory")],y=1400),
]}
if "base" in sys.argv: base()
if "test" in sys.argv:
    os.makedirs(f"{D}/test",exist_ok=True)
    for i in range(len(SH)):
        tt=s[i][0]+min(1.6,durs[i]*0.7); fr=f"{D}/test/f{i}.png"
        subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{tt}","-i",f"{D}/base.mp4","-frames:v","1",fr],check=True)
        im=Image.open(fr).convert("RGBA"); L=Image.new("RGBA",(W,H),(0,0,0,0)); L.alpha_composite(b.G_BOT); L.alpha_composite(b.G_TOP); L.alpha_composite(b.LOGO_S,((W-b.LOGO_S.width)//2,130))
        for fn in CFG["items"]: fn(L,tt)
        im.alpha_composite(L); im.convert("RGB").resize((360,640)).save(f"{D}/test/c{i}.png")
if "final" in sys.argv: b.finish(CFG,"mory","benon_tiktok_stp_mory")
print("TOTAL",round(TOTAL,2))
