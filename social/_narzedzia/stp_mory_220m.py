"""STP Mory – obiekt 220 m przed betonowaniem (jedno zdjęcie, ruch kamery)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benon_motion as bm
P = os.path.join(bm.REPO, "social", "2026-11-24_stp-mory_hala-220m")
IMG = os.path.join(P, "materialy", "hala_220m_przed_betonowaniem.jpg")
os.makedirs(bm.WORK, exist_ok=True)
SHOTS = [(4.4, (1.00, 1.75), (0.50, 0.50), (0.53, 0.37)),   # wjazd w głąb hali
         (3.1, (2.00, 2.18), (0.80, 0.60), (0.74, 0.74)),   # zbrojenie z bliska
         (3.4, (1.40, 1.00), (0.50, 0.42), (0.50, 0.50))]   # odjazd – cała hala
tl = bm.Timeline([s[0] for s in SHOTS])
def base():
    parts = [bm.clip_video(IMG, i, d, still=True, z=z, c0=c0, c1=c1) for i, (d, z, c0, c1) in enumerate(SHOTS)]
    bm.assemble(parts, tl, f"{bm.WORK}/base_mory220.mp4")
T, E = tl.T, tl.E
ITEMS = [
    lambda L, t: bm.counter(L, t, T(0), E(0), "STP MORY · PRZED BETONOWANIEM", 220, "m", "długości obiektu, ok. 1 000 m²", dur=1.8),
    lambda L, t: bm.caption(L, t, T(1), E(1), "LOGISTYKA", ["Pompa + rurociąg"], "z jednego ustawienia na całą długość", big=84),
    lambda L, t: bm.caption(L, t, T(2), E(2), "BETONOWANIE", ["12 h non-stop"], "ciągła praca, bez przerw", y=1190, big=96),
]
END = ("Posadzki przemysłowe od 2000 roku", "Duża inwestycja? Zapytaj o wycenę")
if __name__ == "__main__":
    if "base" in sys.argv: base()
    b = f"{bm.WORK}/base_mory220.mp4"
    if "preview" in sys.argv: bm.preview(b, tl, ITEMS, *END, f"{bm.WORK}/pv_mory220.jpg", [1.8, 3.5, 5.5, 8.5, 10.0, tl.total - 0.5])
    if "export" in sys.argv: bm.export(b, tl, ITEMS, *END, os.path.join(P, "benon_stp-mory_220m.mp4"), "m220", counters=[(T(0), 1.8)], grad_bottom=0.66)
