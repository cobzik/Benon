import numpy as np, wave, sys
SR=48000; DUR=float(sys.argv[1]); OUT=sys.argv[2]
N=int(SR*(DUR+3)); L=np.zeros(N); R=np.zeros(N)
def hz(m): return 440*2**((m-69)/12)
bpm=72; beat=60/bpm; bar=4*beat
# D major: Dmaj9, Bm9, Gmaj9, Asus4->A ; voicings (midi)
chords=[[50,57,61,64,66,69],[47,54,57,61,62,66],[43,50,54,57,59,62],[45,52,57,59,62,64],
        [50,57,61,64,66,69],[47,54,57,61,62,66],[43,50,54,57,59,62],[50,57,62,64,66,69]]
rng=np.random.default_rng(7)
def env(n,a,r,sus=1.0):
    e=np.ones(n)*sus; ai=int(a*SR); ri=int(r*SR)
    e[:ai]=np.linspace(0,sus,ai)**1.5; e[-ri:]*=np.linspace(1,0,ri)**2; return e
def add(sig,start,pan=0.0,gain=1.0):
    i=int(start*SR); n=min(len(sig),N-i)
    if n<=0: return
    L[i:i+n]+=sig[:n]*gain*np.sqrt(0.5*(1-pan)); R[i:i+n]+=sig[:n]*gain*np.sqrt(0.5*(1+pan))
nbars=int(np.ceil(DUR/bar))+1
for b in range(nbars):
    ch=chords[min(b,len(chords)-1)] if b<len(chords) else chords[-1]
    if b>=nbars-2: ch=chords[-1]
    t0=b*bar; ln=bar+2.0; n=int(ln*SR); t=np.arange(n)/SR
    # pad: soft additive saw with few harmonics, detuned, slow LFO
    for k,m in enumerate(ch[1:]):
        for det,pan in((-0.07,-0.6),(0.07,0.6)):
            f=hz(m+det); s=np.zeros(n)
            for h in range(1,6): s+=np.sin(2*np.pi*f*h*t+rng.random()*6)/(h**1.6)
            s*=1+0.15*np.sin(2*np.pi*0.2*t+k)
            add(s*env(n,1.4,2.2)*0.035,t0,pan)
    # bass
    f=hz(ch[0]-12); s=np.sin(2*np.pi*f*t)+0.25*np.sin(4*np.pi*f*t)
    add(s*env(n,0.25,2.0)*0.16,t0,0)
    # piano arpeggio (from bar 1)
    if b>=1 and b<nbars-1:
        pat=[3,4,5,4, 2,4,5,3] 
        for i,ix in enumerate(pat):
            st=t0+i*beat/2*1.0
            if st>DUR-1.5: break
            m=ch[ix]+12; f=hz(m); nn=int(2.5*SR); tt=np.arange(nn)/SR
            s=(np.sin(2*np.pi*f*tt)+0.3*np.sin(4*np.pi*f*tt)*np.exp(-tt*6)+0.08*np.sin(6*np.pi*f*tt)*np.exp(-tt*9))
            s*=np.exp(-tt*1.6)*(1-np.exp(-tt*400))
            add(s*(0.05+0.02*rng.random()),st,(-0.35 if i%2 else 0.35))
# final bell chord
for m in [74,78,81,85]:
    f=hz(m); nn=int(4*SR); tt=np.arange(nn)/SR
    add((np.sin(2*np.pi*f*tt)+0.2*np.sin(4*np.pi*f*tt))*np.exp(-tt*1.0)*(1-np.exp(-tt*300))*0.035, DUR-3.2, rng.uniform(-.4,.4))
irn=int(2.8*SR); ti=np.arange(irn)/SR
def rev(x,seed):
    ir=np.random.default_rng(seed).standard_normal(irn); ir=np.convolve(ir,np.ones(48)/48,'same')*np.exp(-ti/0.8); ir[:int(0.02*SR)]=0
    M=1<<int(np.ceil(np.log2(len(x)+irn))); y=np.fft.irfft(np.fft.rfft(x,M)*np.fft.rfft(ir,M),M)[:len(x)]
    return y/np.max(np.abs(ir))*0.012
L2=L+rev(L,1)*0.6; R2=R+rev(R,2)*0.6
n=int(DUR*SR); L2=L2[:n]; R2=R2[:n]
fi=int(1.0*SR); fo=int(2.5*SR)
for X in (L2,R2): X[:fi]*=np.linspace(0,1,fi)**2; X[-fo:]*=np.linspace(1,0,fo)**1.5
m=max(np.abs(L2).max(),np.abs(R2).max()); st=np.stack([L2,R2],1)/m*0.8
w=wave.open(OUT,'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes()); w.close()
