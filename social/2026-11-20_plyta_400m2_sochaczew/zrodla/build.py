import subprocess, os, sys, math, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
S=os.path.dirname(os.path.abspath(__file__)); STAB=f"{S}/stab.mp4"
OUT="/home/user/Benon/social/2026-11-20_plyta_400m2_sochaczew"
W,H,FPS=1080,1920,30; X=0.45
YEL=(223,255,26); WHITE=(255,255,255); DARK=(15,17,20)
FB="/usr/share/fonts/opentype/inter/Inter-Black.otf"; FXB="/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FBo="/usr/share/fonts/opentype/inter/Inter-Bold.otf"; FSB="/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
_fc={}
def F(p,s):
    k=(p,s)
    if k not in _fc: _fc[k]=ImageFont.truetype(p,s)
    return _fc[k]
# shots: (src_a, src_b, speed, zoom_from, zoom_to)
SHOTS=[(1.6,4.9,1.0,1.00,1.07),   # row of trowels on slab edge
       (6.6,12.2,1.45,1.04,1.00), # slab wide pan
       (16.2,20.2,1.1,1.00,1.06), # trowels close w/ TOI TOI
       (28.5,30.3,0.9,1.06,1.00), # trowels row close
       (24.0,28.0,1.0,1.00,1.05), # BENON crew
       (12.4,14.8,1.0,1.00,1.06), # wet surface
       (32.4,35.9,1.0,1.00,1.05)] # wide panorama
END=3.6
durs=[(b-a)/sp for a,b,sp,_,_ in SHOTS]+[END]
starts=[];t=0
for d in durs: starts.append(t); t+=d-X
TOTAL=starts[-1]+durs[-1]
def seg(i): return starts[i], starts[i]+durs[i]

def build_base():
    parts=[]
    for i,(a,b,sp,z0,z1) in enumerate(SHOTS):
        d=durs[i]; p=f"{S}/shot{i}.mp4"
        zexpr=f"({z0}+({z1}-{z0})*min(t/{d:.3f}\\,1))"
        vf=(f"trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},fps={FPS},"
            f"scale=w='2*trunc(1080*{zexpr}*1.03/2)':h=-2:eval=frame:flags=lanczos,"
            f"crop=1080:1920:'(iw-1080)/2':'(ih-1920)*0.42',"
            "eq=contrast=1.07:saturation=1.12:gamma=0.98,"
            "colorbalance=rs=-0.03:bs=0.04:rh=0.04:bh=-0.03,"
            "unsharp=5:5:0.9:5:5:0,noise=alls=5:allf=t,vignette=PI/7,format=yuv420p,setsar=1")
        subprocess.run(["ffmpeg","-v","error","-y","-i",STAB,"-vf",vf,"-an","-c:v","libx264","-crf","14","-preset","fast",p],check=True)
        parts.append(p)
    p=f"{S}/endbg.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i",f"color=c=0x0f1114:s={W}x{H}:r={FPS}:d={END}","-c:v","libx264","-crf","14","-pix_fmt","yuv420p",p],check=True)
    parts.append(p)
    inp=[];
    for p in parts: inp+=["-i",p]
    fc="";last="[0:v]"
    for i in range(1,len(parts)):
        off=starts[i]
        tr="fade" if i<len(parts)-1 else "fadeblack"
        fc+=f"{last}[{i}:v]xfade=transition={tr}:duration={X}:offset={off:.3f}[x{i}];"; last=f"[x{i}]"
    subprocess.run(["ffmpeg","-v","error","-y",*inp,"-filter_complex",fc[:-1],"-map",last,"-c:v","libx264","-crf","14","-preset","fast","-pix_fmt","yuv420p",f"{S}/base.mp4"],check=True)

# ---------- graphics helpers ----------
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def fade_ab(t,t0,t1,fi=0.5,fo=0.35):
    return min(ease((t-t0)/fi), ease((t1-t)/fo)) if t0<=t<=t1 else 0
def text(d,xy,s,font,fill,alpha=1.0,spacing=0,anchor="la"):
    col=fill+(int(255*alpha),)
    if spacing==0: d.text(xy,s,font=font,fill=col,anchor=anchor); return d.textlength(s,font=font)
    x,y=xy
    for ch in s: d.text((x,y),ch,font=font,fill=col,anchor=anchor); x+=d.textlength(ch,font=font)+spacing
    return x-xy[0]
def white_logo(w):
    lg=Image.open("/home/user/Benon/logo.jpg").convert("L"); lg=lg.resize((w,int(lg.height*w/lg.width)),Image.LANCZOS)
    a=np.clip((235-np.asarray(lg,dtype=float))/(235-100),0,1)*255
    im=Image.new("RGBA",lg.size,(255,255,255,0)); im.putalpha(Image.fromarray(a.astype(np.uint8))); return im
LOGO_S=white_logo(250); LOGO_L=white_logo(780)
def grad(h0,h1,a0,a1):
    g=np.zeros((H,W,4),np.uint8); ys=np.arange(H)
    a=np.clip((ys-h0)/(h1-h0),0,1); a=a0+(a1-a0)*a**1.4
    g[...,3]=(a*255).astype(np.uint8)[:,None]; g[...,:3]=8; return Image.fromarray(g,"RGBA")
G_BOT=grad(950,1700,0,0.78); G_TOP=Image.fromarray(np.asarray(grad(-1,360,0.55,0))*np.array([1,1,1,1])*(np.arange(H)<360)[:,None,None],"RGBA") if False else Image.fromarray((np.asarray(grad(-1,360,0.55,0)).astype(float)*(np.arange(H)<360)[:,None,None]).astype(np.uint8),"RGBA")

def caption(L,t,t0,t1,kicker,title,sub,y=1170,big=None):
    a=fade_ab(t,t0,t1)
    if a<=0: return
    d=ImageDraw.Draw(L); p=ease((t-t0)/0.6); off=(1-p)*40
    x=84
    lines=title if isinstance(title,list) else [title]
    tf=F(FB,big or 86); lh=(big or 86)*1.08
    hblock=46+len(lines)*lh+(64 if sub else 0)
    d.rectangle([x-34,y+4,x-24,y+4+hblock*ease((t-t0)/0.5)],fill=YEL+(int(255*a),))
    text(d,(x,y+off*0.5),kicker,F(FBo,30),YEL,a,spacing=4)
    yy=y+48+off
    for ln in lines: text(d,(x,yy),ln,tf,WHITE,a); yy+=lh
    if sub:
        a2=min(a,ease((t-t0-0.2)/0.5)); text(d,(x,yy+10+off*0.5),sub,F(FSB,42),(235,237,240),a2*0.95)

def counter(L,t,t0,t1,kicker,sub,y=1110):
    a=fade_ab(t,t0,t1)
    if a<=0: return
    d=ImageDraw.Draw(L); x=84; off=(1-ease((t-t0)/0.6))*40
    v=int(round(400*ease((t-t0-0.15)/1.3)))
    d.rectangle([x-34,y+4,x-24,y+4+300*ease((t-t0)/0.5)],fill=YEL+(int(255*a),))
    text(d,(x,y+off*0.5),kicker,F(FBo,30),YEL,a,spacing=4)
    w=text(d,(x-6,y+215+off),f"{v}",F(FB,190),WHITE,a,anchor="ls")
    text(d,(x+w+14,y+215+off),"m²",F(FB,96),YEL,a,anchor="ls")
    text(d,(x,y+262+off*0.5),sub,F(FSB,46),(240,240,240),min(a,ease((t-t0-0.35)/0.5)))

def tracker(L,t,t0,t1,active,y=1010):
    a=fade_ab(t,t0,t1)
    if a<=0: return
    d=ImageDraw.Draw(L); names=["Betonowanie","Wiązanie","Zacieranie"]; xs=[84+18,84+18+300,84+18+580]
    f=F(FSB,30)
    for i in range(2):
        c=YEL if i<active else (255,255,255)
        d.line([xs[i]+26,y,xs[i+1]-26,y],fill=c+(int(255*a*(1 if i<active else .45)),),width=4)
    for i,(nx,nm) in enumerate(zip(xs,names)):
        if i<active:
            d.ellipse([nx-18,y-18,nx+18,y+18],fill=YEL+(int(255*a),))
            d.line([(nx-8,y+1),(nx-2,y+8),(nx+9,y-7)],fill=DARK+(int(255*a),),width=5)
        elif i==active:
            pr=0.5+0.5*math.sin((t-t0)*5); r=18+5*pr
            d.ellipse([nx-r-6,y-r-6,nx+r+6,y+r+6],outline=YEL+(int(110*a*(1-pr)),),width=3)
            d.ellipse([nx-18,y-18,nx+18,y+18],outline=YEL+(int(255*a),),width=5)
            d.ellipse([nx-7,y-7,nx+7,y+7],fill=YEL+(int(255*a),))
        else:
            d.ellipse([nx-18,y-18,nx+18,y+18],outline=(255,255,255,int(140*a)),width=4)
        col=YEL if i==active else WHITE
        text(d,(nx-18,y+32),nm,f,col,a*(1 if i<=active else .6))

def pin_chip(L,t,t0,t1,lines,y=1500):
    a=fade_ab(t,t0,t1)
    if a<=0: return
    d=ImageDraw.Draw(L); x=84
    for k,(ic,s) in enumerate(lines):
        ak=min(a,ease((t-t0-0.15*k)/0.5)); yy=y+k*92+(1-ak)*20
        f=F(FBo,40); w=d.textlength(s,font=f)
        d.rounded_rectangle([x-24,yy-10,x+w+86,yy+62],radius=36,fill=(15,17,20,int(170*ak)))
        cx,cy=x+18,yy+26
        if ic=="pin":
            d.ellipse([cx-14,cy-20,cx+14,cy+8],fill=YEL+(int(255*ak),)); d.polygon([(cx-11,cy+1),(cx+11,cy+1),(cx,cy+22)],fill=YEL+(int(255*ak),))
            d.ellipse([cx-5,cy-11,cx+5,cy-1],fill=DARK+(int(255*ak),))
        else:
            d.rounded_rectangle([cx-17,cy-10,cx+13,cy+12],radius=3,fill=YEL+(int(255*ak),)); d.rectangle([cx+13,cy-3,cx+22,cy+12],fill=YEL+(int(255*ak),))
            for wx in (cx-9,cx+14): d.ellipse([wx-6,cy+8,wx+6,cy+20],fill=DARK+(int(255*ak),),outline=YEL+(int(255*ak),),width=3)
        text(d,(x+50,yy+4),s,f,WHITE,ak)

def endcard(L,t,t0,cfg):
    lt=t-t0
    if lt<0: return
    d=ImageDraw.Draw(L)
    a=ease(lt/0.7); sc=0.94+0.06*ease(lt/0.9)
    lg=LOGO_L.resize((int(LOGO_L.width*sc),int(LOGO_L.height*sc)),Image.LANCZOS)
    la=np.asarray(lg).copy(); la[...,3]=(la[...,3]*a).astype(np.uint8); lg=Image.fromarray(la,"RGBA")
    L.alpha_composite(lg,((W-lg.width)//2,600-lg.height//2))
    lw=int(520*ease((lt-0.3)/0.6)); d.rectangle([(W-lw)//2,760,(W+lw)//2,766],fill=YEL+(255,))
    def c(s,f,y,col,al,box=None):
        w=d.textlength(s,font=f); x=(W-w)/2
        if box: d.rounded_rectangle([x-36,y-20,x+w+36,y+f.size+18],radius=40,fill=box+(int(255*al),))
        text(d,(x,y),s,f,col,al)
    c(cfg["end1"],F(FSB,44),820,(190,195,205),ease((lt-0.45)/0.5))
    al=ease((lt-0.7)/0.5); c("www.benon.com.pl",F(FB,64),980+(1-al)*20,DARK,al,YEL)
    al=ease((lt-0.9)/0.5); c("tel. 781 555 519",F(FXB,56),1120+(1-al)*20,WHITE,al)
    al=ease((lt-1.1)/0.5); c(cfg["end2"],F(FSB,38),1225+(1-al)*20,(190,195,205),al)

def render(cfg,tag):
    fd=f"{S}/ov_{tag}"; shutil.rmtree(fd,ignore_errors=True); os.makedirs(fd)
    nfr=int(math.ceil(TOTAL*FPS)); endt=starts[-1]
    for n in range(nfr):
        t=n/FPS; L=Image.new("RGBA",(W,H),(0,0,0,0))
        if t<endt+X:
            ga=1-ease((t-endt)/X) if t>endt else 1
            if ga>0:
                gb=G_BOT if ga==1 else Image.fromarray((np.asarray(G_BOT)*np.array([1,1,1,ga])).astype(np.uint8),"RGBA")
                L.alpha_composite(gb); L.alpha_composite(G_TOP if ga==1 else Image.fromarray((np.asarray(G_TOP)*np.array([1,1,1,ga])).astype(np.uint8),"RGBA"))
                la=np.asarray(LOGO_S).copy(); la[...,3]=(la[...,3]*0.92*ga*ease(t/0.6)).astype(np.uint8)
                L.alpha_composite(Image.fromarray(la,"RGBA"),((W-LOGO_S.width)//2,130))
            for fn in cfg["items"]: fn(L,t)
        endcard(L,t,endt+0.15,cfg)
        L.save(f"{fd}/{n:04d}.png",compress_level=1)
    return fd

def finish(cfg,tag,name):
    fd=render(cfg,tag)
    mus=f"{S}/music_{tag}.wav"
    subprocess.run(["python3",f"{S}/music.py",f"{TOTAL:.3f}",mus],check=True)
    out=f"{OUT}/{name}.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-i",f"{S}/base.mp4","-framerate",str(FPS),"-i",f"{fd}/%04d.png","-i",mus,
        "-filter_complex","[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v];[2:a]loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000[a]",
        "-map","[v]","-map","[a]","-c:v","libx264","-crf","20","-preset","slow","-profile:v","high","-r",str(FPS),
        "-c:a","aac","-b:a","192k","-movflags","+faststart","-t",f"{TOTAL:.3f}",out],check=True)
    print(name,round(TOTAL,2))

s=[seg(i) for i in range(len(SHOTS))]
def T(i): return s[i][0]+0.2
def E(i): return s[i][1]-X-0.05
REEL={"end1":"Posadzki przemysłowe od 2000 roku","end2":"Zapytaj o wycenę posadzki","items":[
 lambda L,t: counter(L,t,T(0),E(0),"PŁYTA FUNDAMENTOWA · HALA","betonu wylane w 2 godziny"),
 lambda L,t: caption(L,t,T(1),E(1),"01 · BETONOWANIE",["Płyta fundamentowa","z funkcją posadzki"],"fundament i posadzka hali w jednym",big=78),
 lambda L,t: caption(L,t,T(2),E(3),"SPRZĘT",["Zacieraczki","mechaniczne"],"gotowe do wejścia na beton"),
 lambda L,t: tracker(L,t,T(4),E(5),1 if t<s[5][0] else 2,y=1060),
 lambda L,t: caption(L,t,T(4),E(4),"02 · WIĄZANIE",["Czekamy, aż","beton zwiąże"],"wejście za wcześnie = ślady na posadzce",y=1190),
 lambda L,t: caption(L,t,T(5),E(5),"03 · ZACIERANIE",["15–20 h pracy"],"do zatarcia na gładko",y=1190),
 lambda L,t: caption(L,t,T(6),E(6),"REALIZACJA · LISTOPAD 2026",["Hala 400 m²"],None,y=1220),
 lambda L,t: pin_chip(L,t,T(6)+0.3,E(6),[("pin","Okolice Sochaczewa"),("truck","Beton: Atrans")],y=1420),
]}
TT={"end1":"Posadzki przemysłowe od 2000 roku","end2":"Jaki był Twój typ? Napisz w komentarzu","items":[
 lambda L,t: caption(L,t,T(0),E(0),"POV",["400 m² wylane","w 2 godziny…"],"a robota dopiero się zaczyna",big=88),
 lambda L,t: caption(L,t,T(1),E(1),"PŁYTA FUNDAMENTOWA",["Od razu","posadzka hali"],"jeden etap zamiast dwóch",big=88),
 lambda L,t: caption(L,t,T(2),E(3),"SPRZĘT",["Zacieraczki","czekają na start"],None),
 lambda L,t: tracker(L,t,T(4),E(5),1 if t<s[5][0] else 2,y=1060),
 lambda L,t: caption(L,t,T(4),E(4),"ZGADNIJ",["Ile godzin do","zatarcia na gładko?"],"odpowiedź za chwilę",y=1190,big=74),
 lambda L,t: caption(L,t,T(5),E(5),"ODPOWIEDŹ",["15–20 godzin"],"bez przerwy, aż będzie gładko",y=1190),
 lambda L,t: pin_chip(L,t,T(6),E(6),[("pin","Okolice Sochaczewa"),("truck","Beton: Atrans")],y=1300),
]}
if "base" in sys.argv: build_base()
if "reel" in sys.argv: finish(REEL,"reel","benon_reel_instagram")
if "tt" in sys.argv: finish(TT,"tt","benon_tiktok")
if "test" in sys.argv:
    os.makedirs(f"{S}/test",exist_ok=True)
    for cfg,tag in ((REEL,"reel"),(TT,"tt")):
        for i in range(len(SHOTS)):
            t=s[i][0]+min(1.6,durs[i]*0.6); L=Image.new("RGBA",(W,H),(0,0,0,0)); L.alpha_composite(G_BOT); L.alpha_composite(G_TOP); L.alpha_composite(LOGO_S,((W-LOGO_S.width)//2,130))
            for fn in cfg["items"]: fn(L,t)
            L.save(f"{S}/test/{tag}_{i}.png")
        L=Image.new("RGBA",(W,H),DARK+(255,)); endcard(L,starts[-1]+3,starts[-1],cfg); L.save(f"{S}/test/{tag}_end.png")
print("TOTAL",TOTAL, [round(x,2) for x in starts])
