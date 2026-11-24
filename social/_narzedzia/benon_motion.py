"""Benon – wspólny silnik montażu filmów 9:16 (TikTok / Reels).

Każdy projekt (sochaczew.py, stp_mory_45000.py, stp_mory_220m.py) opisuje ujęcia i napisy,
a ten moduł robi resztę: montaż ujęć z przejściami, animowaną grafikę, muzykę
i eksport.

Dźwięk: sama melodia (music.py), bez efektów.

Bezpieczne strefy: logo i napisy omijają górny pasek aplikacji (y < 220), prawą kolumnę
przycisków (x > 900) i dolny opis (y > 1560).
"""
import math, os, shutil, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
WORK = os.environ.get("BENON_WORK", "/tmp/benon_work")
W, H, FPS, X = 1080, 1920, 30, 0.45
SAFE_R = 880                     # tekst nie wchodzi pod przyciski po prawej
YEL = (223, 255, 26); WHITE = (255, 255, 255); DARK = (15, 17, 20); GREY = (190, 195, 205)
FD = "/usr/share/fonts/opentype/inter/"
FB, FXB, FBo, FSB = FD + "Inter-Black.otf", FD + "Inter-ExtraBold.otf", FD + "Inter-Bold.otf", FD + "Inter-SemiBold.otf"
GRADE = ("eq=contrast=1.06:saturation=1.10:gamma=0.99,"
         "colorbalance=rs=-0.02:bs=0.03:rh=0.03:bh=-0.02,"
         "unsharp=5:5:0.8:5:5:0,vignette=PI/7")

_fc = {}
def F(p, s):
    if (p, s) not in _fc: _fc[(p, s)] = ImageFont.truetype(p, int(s))
    return _fc[(p, s)]

def run(*a): subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)

# ---------------------------------------------------------------- timeline
class Timeline:
    def __init__(self, durs, end=3.6):
        self.durs = list(durs) + [end]; self.starts = []; t = 0
        for d in self.durs: self.starts.append(t); t += d - X
        self.total = self.starts[-1] + self.durs[-1]
        self.end_t = self.starts[-1]
    def T(self, i, pad=0.2): return self.starts[i] + pad
    def E(self, i): return self.starts[i] + self.durs[i] - X - 0.05

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def fade_ab(t, t0, t1, fi=0.5, fo=0.35):
    return min(ease((t - t0) / fi), ease((t1 - t) / fo)) if t0 <= t <= t1 else 0.0

# ---------------------------------------------------------------- video
def clip_video(src, i, d, a=None, b=None, speed=1.0, z=(1.0, 1.05), c0=(0.5, 0.45), c1=None, still=False, pan_x=None):
    """Jedno ujęcie 1080x1920 z płynnym najazdem/panoramą. Zwraca ścieżkę mp4."""
    c1 = c1 or c0; o = f"{WORK}/shot{i}.mp4"
    e = f"((1-cos(PI*min(t/{d:.3f}\\,1)))/2)"
    if pan_x is not None:   # poziome zdjęcie: przesuw wzdłuż osi X
        x0, x1 = pan_x
        vf = (f"fps={FPS},scale=-2:1920:flags=lanczos,"
              f"crop=1080:1920:'max(0\\,min(iw-1080\\,{x0:.0f}+({x1 - x0:.0f})*{e}))':0")
    else:
        Z = f"({z[0]}+({z[1]}-{z[0]})*{e})"
        CX = f"({c0[0]}+({c1[0]}-{c0[0]})*{e})"; CY = f"({c0[1]}+({c1[1]}-{c0[1]})*{e})"
        pre = "" if still else f"trim={a}:{b},setpts=(PTS-STARTPTS)/{speed},"
        vf = (f"{pre}fps={FPS},scale=w='2*trunc(1080.5*{Z}/2)':h=-2:eval=frame:flags=lanczos,"
              f"crop=1080:1920:'max(0\\,min(iw-1080\\,{CX}*iw-540))':'max(0\\,min(ih-1920\\,{CY}*ih-960))'")
    vf += f",{GRADE},format=yuv420p,setsar=1"
    inp = ["-loop", "1", "-t", f"{d}", "-i", src] if (still or pan_x is not None) else ["-i", src]
    run(*inp, "-vf", vf, "-an", "-c:v", "libx264", "-crf", "14", "-preset", "fast", o)
    return o

def assemble(parts, tl, out):
    endbg = f"{WORK}/endbg.mp4"
    run("-f", "lavfi", "-i", f"color=c=0x0f1114:s={W}x{H}:r={FPS}:d={tl.durs[-1]}", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", endbg)
    parts = parts + [endbg]; inp = []
    for p in parts: inp += ["-i", p]
    fc = ""; last = "[0:v]"
    for i in range(1, len(parts)):
        tr = "fadeblack" if i == len(parts) - 1 else "fade"
        fc += f"{last}[{i}:v]xfade=transition={tr}:duration={X}:offset={tl.starts[i]:.3f}[x{i}];"; last = f"[x{i}]"
    run(*inp, "-filter_complex", fc[:-1], "-map", last, "-c:v", "libx264", "-crf", "14", "-preset", "fast", "-pix_fmt", "yuv420p", out)

# ---------------------------------------------------------------- graphics
def text(d, xy, s, font, fill, alpha=1.0, spacing=0, anchor="la"):
    col = fill + (int(255 * max(0, min(1, alpha))),)
    if not spacing: d.text(xy, s, font=font, fill=col, anchor=anchor); return d.textlength(s, font=font)
    x, y = xy
    for ch in s: d.text((x, y), ch, font=font, fill=col, anchor=anchor); x += d.textlength(ch, font=font) + spacing
    return x - xy[0]

def fit(d, s, path, size, maxw):
    """Zmniejsza czcionkę, aż tekst zmieści się przed prawą kolumną przycisków."""
    while size > 20 and d.textlength(s, font=F(path, size)) > maxw: size -= 2
    return F(path, size)

def white_logo(w):
    lg = Image.open(os.path.join(REPO, "logo.jpg")).convert("L")
    lg = lg.resize((w, int(lg.height * w / lg.width)), Image.LANCZOS)
    a = np.clip((235 - np.asarray(lg, float)) / 135, 0, 1) * 255
    im = Image.new("RGBA", lg.size, (255, 255, 255, 0)); im.putalpha(Image.fromarray(a.astype(np.uint8))); return im

def grad(h0, h1, a0, a1):
    ys = np.arange(H); a = np.clip((ys - h0) / (h1 - h0), 0, 1); a = a0 + (a1 - a0) * a ** 1.4
    g = np.zeros((H, W, 4), np.uint8); g[..., :3] = 8; g[..., 3] = (a * 255).astype(np.uint8)[:, None]
    return Image.fromarray(g, "RGBA")

LOGO_S = None; LOGO_L = None
def _logos():
    global LOGO_S, LOGO_L
    if LOGO_S is None: LOGO_S, LOGO_L = white_logo(230), white_logo(780)

def with_alpha(im, a):
    arr = np.asarray(im).copy(); arr[..., 3] = (arr[..., 3] * a).astype(np.uint8); return Image.fromarray(arr, "RGBA")

def caption(L, t, t0, t1, kicker, title, sub=None, y=1170, big=86):
    a = fade_ab(t, t0, t1)
    if a <= 0: return
    d = ImageDraw.Draw(L); x = 84; off = (1 - ease((t - t0) / 0.6)) * 40; maxw = SAFE_R - x
    lines = title if isinstance(title, list) else [title]
    size = min(F(FB, big).size, *[fit(d, ln, FB, big, maxw).size for ln in lines]); tf = F(FB, size); lh = size * 1.08
    hb = 46 + len(lines) * lh + (64 if sub else 0)
    d.rectangle([x - 34, y + 4, x - 24, y + 4 + hb * ease((t - t0) / 0.5)], fill=YEL + (int(255 * a),))
    text(d, (x, y + off * 0.5), kicker, F(FBo, 30), YEL, a, spacing=4)
    yy = y + 48 + off
    for ln in lines: text(d, (x, yy), ln, tf, WHITE, a); yy += lh
    if sub:
        text(d, (x, yy + 10 + off * 0.5), sub, fit(d, sub, FSB, 42, maxw), (235, 237, 240), min(a, ease((t - t0 - 0.2) / 0.5)) * 0.95)

def counter(L, t, t0, t1, kicker, value, unit, subs, y=1080, size=190, step=1, dur=1.4):
    a = fade_ab(t, t0, t1)
    if a <= 0: return
    d = ImageDraw.Draw(L); x = 84; off = (1 - ease((t - t0) / 0.6)) * 40
    v = int(round(value * ease((t - t0 - 0.1) / dur) / step)) * step
    s = f"{v:,}".replace(",", " ")
    subs = subs if isinstance(subs, list) else [subs]
    d.rectangle([x - 34, y + 4, x - 24, y + 4 + (250 + 58 * len(subs)) * ease((t - t0) / 0.5)], fill=YEL + (int(255 * a),))
    text(d, (x, y + off * 0.5), kicker, F(FBo, 30), YEL, a, spacing=4)
    w = text(d, (x - 6, y + 215 + off), s, F(FB, size), WHITE, a, anchor="ls")
    text(d, (x + w + 14, y + 215 + off), unit, F(FB, size // 2), YEL, a, anchor="ls")
    a2 = min(a, ease((t - t0 - 0.35) / 0.5))
    for k, sb in enumerate(subs): text(d, (x, y + 238 + 58 * k + off * 0.5), sb, fit(d, sb, FSB, 46, SAFE_R - x), (240, 240, 240), a2)

def tracker(L, t, t0, t1, active, y=1040):
    a = fade_ab(t, t0, t1)
    if a <= 0: return
    d = ImageDraw.Draw(L); names = ["Betonowanie", "Wiązanie", "Zacieranie"]; xs = [102, 382, 642]; f = F(FSB, 30)
    for i in range(2):
        c = YEL if i < active else WHITE
        d.line([xs[i] + 26, y, xs[i + 1] - 26, y], fill=c + (int(255 * a * (1 if i < active else .45)),), width=4)
    for i, (nx, nm) in enumerate(zip(xs, names)):
        A = int(255 * a)
        if i < active:
            d.ellipse([nx - 18, y - 18, nx + 18, y + 18], fill=YEL + (A,))
            d.line([(nx - 8, y + 1), (nx - 2, y + 8), (nx + 9, y - 7)], fill=DARK + (A,), width=5)
        elif i == active:
            pr = 0.5 + 0.5 * math.sin((t - t0) * 5); r = 18 + 5 * pr
            d.ellipse([nx - r - 6, y - r - 6, nx + r + 6, y + r + 6], outline=YEL + (int(110 * a * (1 - pr)),), width=3)
            d.ellipse([nx - 18, y - 18, nx + 18, y + 18], outline=YEL + (A,), width=5)
            d.ellipse([nx - 7, y - 7, nx + 7, y + 7], fill=YEL + (A,))
        else:
            d.ellipse([nx - 18, y - 18, nx + 18, y + 18], outline=(255, 255, 255, int(140 * a)), width=4)
        text(d, (nx - 18, y + 32), nm, f, YEL if i == active else WHITE, a * (1 if i <= active else .6))

def chips(L, t, t0, t1, items, y=1420):
    a = fade_ab(t, t0, t1)
    if a <= 0: return
    d = ImageDraw.Draw(L); x = 84
    for k, (ic, s) in enumerate(items):
        ak = min(a, ease((t - t0 - 0.15 * k) / 0.5)); yy = y + k * 92 + (1 - ak) * 20
        f = F(FBo, 40); w = d.textlength(s, font=f); A = int(255 * ak)
        d.rounded_rectangle([x - 24, yy - 10, x + w + 86, yy + 62], radius=36, fill=(15, 17, 20, int(170 * ak)))
        cx, cy = x + 18, yy + 26
        if ic == "pin":
            d.ellipse([cx - 14, cy - 20, cx + 14, cy + 8], fill=YEL + (A,)); d.polygon([(cx - 11, cy + 1), (cx + 11, cy + 1), (cx, cy + 22)], fill=YEL + (A,))
            d.ellipse([cx - 5, cy - 11, cx + 5, cy - 1], fill=DARK + (A,))
        else:
            d.rounded_rectangle([cx - 17, cy - 10, cx + 13, cy + 12], radius=3, fill=YEL + (A,)); d.rectangle([cx + 13, cy - 3, cx + 22, cy + 12], fill=YEL + (A,))
            for wx in (cx - 9, cx + 14): d.ellipse([wx - 6, cy + 8, wx + 6, cy + 20], fill=DARK + (A,), outline=YEL + (A,), width=3)
        text(d, (x + 50, yy + 4), s, f, WHITE, ak)

def endcard(L, t, t0, *_):
    """Plansza końcowa: logo, dwa atuty firmy, adres strony jako przycisk, telefon."""
    lt = t - t0
    if lt < 0: return
    d = ImageDraw.Draw(L); a = ease(lt / 0.7); sc = 0.94 + 0.06 * ease(lt / 0.9)
    lg = with_alpha(LOGO_L.resize((int(LOGO_L.width * sc), int(LOGO_L.height * sc)), Image.LANCZOS), a)
    L.alpha_composite(lg, ((W - lg.width) // 2, 560 - lg.height // 2))
    lw = int(480 * ease((lt - 0.3) / 0.6)); d.rectangle([(W - lw) // 2, 718, (W + lw) // 2, 724], fill=YEL + (255,))
    # atuty
    f = F(FSB, 46); items = ["Działamy od 2000 roku", "Działamy w całej Polsce"]
    wmax = max(d.textlength(s_, font=f) for s_ in items); x0 = (W - (wmax + 64)) / 2
    for k, s_ in enumerate(items):
        al = ease((lt - 0.45 - 0.15 * k) / 0.5); y = 790 + 78 * k + (1 - al) * 16; A = int(255 * al)
        d.ellipse([x0, y + 4, x0 + 44, y + 48], fill=YEL + (A,))
        d.line([(x0 + 12, y + 27), (x0 + 19, y + 35), (x0 + 33, y + 18)], fill=DARK + (A,), width=5)
        text(d, (x0 + 64, y + 2), s_, f, WHITE, al)
    # adres strony jako przycisk
    al = ease((lt - 0.85) / 0.5); A = int(255 * al); y = 1010 + (1 - al) * 20
    fu = F(FB, 70); parts = [("www.", (150, 156, 168)), ("benon", YEL), (".com.pl", WHITE)]
    tw = sum(d.textlength(p_, font=fu) for p_, _ in parts); x = (W - tw) / 2
    d.rounded_rectangle([x - 48, y - 26, x + tw + 48, y + 100], radius=63, fill=(28, 31, 37, A), outline=YEL + (A,), width=4)
    for p_, c in parts: text(d, (x, y), p_, fu, c, al); x += d.textlength(p_, font=fu)
    # telefon
    al = ease((lt - 1.05) / 0.5); y = 1180 + (1 - al) * 20
    s_ = "tel. 781 555 519"; f2 = F(FXB, 54); w = d.textlength(s_, font=f2); text(d, ((W - w) / 2, y), s_, f2, WHITE, al)

def render_overlay(tl, items, end1, end2, tag, grad_bottom=0.75):
    _logos()
    g_bot = grad(980, 1720, 0, grad_bottom); g_top = grad(-1, 420, 0.5, 0)
    g_top = Image.fromarray((np.asarray(g_top).astype(float) * (np.arange(H) < 420)[:, None, None]).astype(np.uint8), "RGBA")
    fd = f"{WORK}/ov_{tag}"; shutil.rmtree(fd, ignore_errors=True); os.makedirs(fd)
    for n in range(int(math.ceil(tl.total * FPS))):
        t = n / FPS; L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if t < tl.end_t + X:
            ga = 1 - ease((t - tl.end_t) / X) if t > tl.end_t else 1.0
            L.alpha_composite(with_alpha(g_bot, ga) if ga < 1 else g_bot)
            L.alpha_composite(with_alpha(g_top, ga) if ga < 1 else g_top)
            # logo w lewym górnym rogu, poniżej paska aplikacji
            L.alpha_composite(with_alpha(LOGO_S, 0.95 * ga * ease(t / 0.6)), (84, 236))
            for fn in items: fn(L, t)
        endcard(L, t, tl.end_t + 0.15, end1, end2)
        L.save(f"{fd}/{n:04d}.png", compress_level=1)
    return fd

# ---------------------------------------------------------------- export
def export(base, tl, items, end1, end2, out, tag, counters=(), grad_bottom=0.75, music_seed_dur=None):
    fd = render_overlay(tl, items, end1, end2, tag, grad_bottom)
    mus = f"{WORK}/music_{tag}.wav"
    subprocess.run(["python3", os.path.join(HERE, "music.py"), f"{tl.total:.3f}", mus], check=True)
    mixp = mus   # sama melodia, bez efektów dźwiękowych
    run("-i", base, "-framerate", str(FPS), "-i", f"{fd}/%04d.png", "-i", mixp,
        "-filter_complex", "[0:v][1:v]overlay=0:0:format=auto,format=yuv420p[v];[2:a]loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000[a]",
        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-preset", "slow", "-profile:v", "high", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{tl.total:.3f}", out)
    cover = os.path.splitext(out)[0].replace("benon_", "okladka_") + ".jpg"
    run("-ss", f"{tl.T(0) + 1.9:.2f}", "-i", out, "-frames:v", "1", "-q:v", "2", cover)
    print("OK", os.path.basename(out), round(tl.total, 2), "s")

def preview(base, tl, items, end1, end2, path, times):
    """Arkusz kontrolny: wybrane klatki z grafiką."""
    _logos(); ims = []
    for tt in times:
        fr = f"{WORK}/pv.png"; run("-ss", f"{tt:.2f}", "-i", base, "-frames:v", "1", fr)
        im = Image.open(fr).convert("RGBA"); L = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        L.alpha_composite(with_alpha(LOGO_S, 0.95), (84, 236))
        for fn in items: fn(L, tt)
        endcard(L, tt, tl.end_t + 0.15, end1, end2)
        im.alpha_composite(L); ims.append(im.convert("RGB").resize((270, 480)))
    sh = Image.new("RGB", (270 * len(ims), 480))
    for k, im in enumerate(ims): sh.paste(im, (270 * k, 0))
    sh.save(path)
