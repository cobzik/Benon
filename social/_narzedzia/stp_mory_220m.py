"""STP Mory – obiekt 220 m przed betonowaniem (jedno zdjęcie, ruch kamery)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benon_motion as bm
P = os.path.join(bm.REPO, "social", "2026-11-24_stp-mory_hala-220m")
IMG = os.path.join(P, "materialy", "hala_220m_przed_betonowaniem.jpg")
os.makedirs(bm.WORK, exist_ok=True)
# Jedno zdjęcie = jedno ujęcie: delikatny najazd i lekki ruch w dół, kadr na posadzce i zbrojeniu (bez sufitu)
SHOTS = [(10.8, (1.20, 1.32), (0.50, 0.62), (0.50, 0.66))]
tl = bm.Timeline([s[0] for s in SHOTS])
def base():
    parts = [bm.clip_video(IMG, i, d, still=True, z=z, c0=c0, c1=c1) for i, (d, z, c0, c1) in enumerate(SHOTS)]
    bm.assemble(parts, tl, f"{bm.WORK}/base_mory220.mp4")
t0 = tl.T(0); tE = tl.E(0)
ITEMS = [
    lambda L, t: bm.counter(L, t, t0, t0 + 3.4, "STP MORY · PRZED BETONOWANIEM", 220, "m", "długości obiektu, ok. 1 000 m²", dur=1.8),
    lambda L, t: bm.caption(L, t, t0 + 3.7, t0 + 6.9, "LOGISTYKA", ["Pompa + rurociąg"], "z jednego ustawienia na całą długość", big=84),
    lambda L, t: bm.caption(L, t, t0 + 7.2, tE, "BETONOWANIE", ["12 godzin"], "ciągłej pracy", y=1190, big=96),
]
END = ("", "")   # plansza końcowa ma stały układ (benon_motion.endcard)
if __name__ == "__main__":
    if "base" in sys.argv: base()
    b = f"{bm.WORK}/base_mory220.mp4"
    if "preview" in sys.argv: bm.preview(b, tl, ITEMS, *END, f"{bm.WORK}/pv_mory220.jpg", [0.3, 2.5, 5.5, 9.0, 10.3, tl.total - 0.3])
    if "export" in sys.argv: bm.export(b, tl, ITEMS, *END, os.path.join(P, "benon_stp-mory_220m.mp4"), "m220", grad_bottom=0.66)
