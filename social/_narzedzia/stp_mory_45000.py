"""STP Mory – 45 000 m² posadzek DST dla metra warszawskiego (zdjęcia gotowych hal)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benon_motion as bm
P = os.path.join(bm.REPO, "social", "2026-11-24_stp-mory_posadzki-45000m2")
M = lambda n: os.path.join(P, "materialy", f"hala_{n:02d}.jpg")
os.makedirs(bm.WORK, exist_ok=True)
SC = 1920 / 924
def pan(vp): v = vp * SC; return (v - 800, v - 280)       # przesuw w okolicy punktu zbiegu
# (zdjęcie, czas, parametry ruchu)
SHOTS = [(1, 2.9, dict(z=(1.00, 1.08))),
         (8, 2.3, dict(pan_x=pan(940))),
         (2, 2.2, dict(z=(1.08, 1.00))),
         (7, 2.3, dict(pan_x=pan(790))),
         (3, 2.3, dict(pan_x=pan(1060))),
         (5, 2.2, dict(z=(1.00, 1.07))),
         (6, 2.4, dict(z=(1.07, 1.00)))]
tl = bm.Timeline([d for _, d, _ in SHOTS])
def base():
    parts = [bm.clip_video(M(n), i, d, still=True, c0=(0.5, 0.5), **kw) for i, (n, d, kw) in enumerate(SHOTS)]
    bm.assemble(parts, tl, f"{bm.WORK}/base_mory45.mp4")
T, E = tl.T, tl.E
ITEMS = [
    lambda L, t: bm.counter(L, t, T(0), E(0), "METRO WARSZAWSKIE · STP MORY", 45000, "m²", ["posadzek w halach", "obsługi taboru metra"], size=160, step=100),
    lambda L, t: bm.caption(L, t, T(1), E(2), "TECHNOLOGIA", ["Posadzki DST"], "utwardzane powierzchniowo"),
    lambda L, t: bm.caption(L, t, T(3), E(3), "BETON", ["C25/30", "+ włókna"], "kopolimerowe Bautech"),
    lambda L, t: bm.caption(L, t, T(4), E(5), "KOMPLEKSOWO", ["Wykonanie", "z projektem"], "system utwardzenia Bautech"),
    lambda L, t: bm.caption(L, t, T(6), E(6), "REALIZACJA", ["2024–2026"], None, y=1200),
    lambda L, t: bm.chips(L, t, T(6) + 0.25, E(6), [("pin", "Warszawa · STP Mory")], y=1400),
]
END = ("Posadzki przemysłowe od 2000 roku", "Duża inwestycja? Zapytaj o wycenę")
if __name__ == "__main__":
    if "base" in sys.argv: base()
    b = f"{bm.WORK}/base_mory45.mp4"
    if "preview" in sys.argv: bm.preview(b, tl, ITEMS, *END, f"{bm.WORK}/pv_mory45.jpg", [s + 1.5 for s in tl.starts[:-1]] + [tl.total - 0.5])
    if "export" in sys.argv: bm.export(b, tl, ITEMS, *END, os.path.join(P, "benon_stp-mory_45000m2.mp4"), "m45", counters=[(T(0), 1.4)], grad_bottom=0.6)
