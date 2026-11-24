"""Płyta fundamentowa 400 m², okolice Sochaczewa – Reels + TikTok z nagrania z placu."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import benon_motion as bm
P = os.path.join(bm.REPO, "social", "2026-11-20_sochaczew_plyta-400m2")
SRC = os.path.join(P, "materialy", "nagranie_plac.mov")
os.makedirs(bm.WORK, exist_ok=True); STAB = f"{bm.WORK}/stab.mp4"

# (od, do, prędkość, zoom od/do) – najlepsze momenty z nagrania
SHOTS = [(1.6, 4.9, 1.0, (1.00, 1.07)),    # rząd zacieraczek na krawędzi płyty
         (6.6, 12.2, 1.45, (1.04, 1.00)),  # panorama płyty
         (16.2, 20.2, 1.1, (1.00, 1.06)),  # zacieraczki z bliska
         (28.5, 30.3, 0.9, (1.06, 1.00)),  # zacieraczki – drugi kadr
         (24.0, 28.0, 1.0, (1.00, 1.05)),  # ekipa BENON
         (12.4, 14.8, 1.0, (1.00, 1.06)),  # mokra powierzchnia
         (32.4, 35.9, 1.0, (1.00, 1.05))]  # panorama z kontenerem
tl = bm.Timeline([(b - a) / s for a, b, s, _ in SHOTS])

def base():
    if not os.path.exists(STAB):
        bm.run("-i", SRC, "-vf", f"vidstabdetect=shakiness=6:accuracy=15:result={bm.WORK}/tr.trf", "-f", "null", "-")
        bm.run("-i", SRC, "-vf", f"vidstabtransform=input={bm.WORK}/tr.trf:smoothing=18:optzoom=1:interpol=bicubic,hqdn3d=2:2:4:4",
               "-an", "-c:v", "libx264", "-crf", "12", "-preset", "fast", STAB)
    parts = [bm.clip_video(STAB, i, tl.durs[i], a, b, sp, z, c0=(0.5, 0.42 + 0.0)) for i, (a, b, sp, z) in enumerate(SHOTS)]
    bm.assemble(parts, tl, f"{bm.WORK}/base_sochaczew.mp4")

T, E, S = tl.T, tl.E, tl.starts
REELS = [
    lambda L, t: bm.counter(L, t, T(0), E(0), "PŁYTA FUNDAMENTOWA · HALA", 400, "m²", "betonu wylane w 2 godziny", dur=1.3),
    lambda L, t: bm.caption(L, t, T(1), E(1), "01 · BETONOWANIE", ["Płyta fundamentowa", "z funkcją posadzki"], "fundament i posadzka hali w jednym", big=78),
    lambda L, t: bm.caption(L, t, T(2), E(3), "SPRZĘT", ["Zacieraczki", "mechaniczne"], "gotowe do wejścia na beton"),
    lambda L, t: bm.tracker(L, t, T(4), E(5), 1 if t < S[5] else 2),
    lambda L, t: bm.caption(L, t, T(4), E(4), "02 · WIĄZANIE", ["Czekamy, aż", "beton zwiąże"], "za wcześnie = ślady na posadzce", y=1190),
    lambda L, t: bm.caption(L, t, T(5), E(5), "03 · ZACIERANIE", ["15–20 h pracy"], "do zatarcia na gładko", y=1190),
    lambda L, t: bm.caption(L, t, T(6), E(6), "REALIZACJA · LISTOPAD 2026", ["Hala 400 m²"], None, y=1200),
    lambda L, t: bm.chips(L, t, T(6) + 0.3, E(6), [("pin", "Okolice Sochaczewa"), ("truck", "Beton: Atrans")], y=1400),
]
TIKTOK = [
    lambda L, t: bm.caption(L, t, T(0), E(0), "POV", ["400 m² wylane", "w 2 godziny…"], "a robota dopiero się zaczyna", big=88),
    lambda L, t: bm.caption(L, t, T(1), E(1), "PŁYTA FUNDAMENTOWA", ["Od razu", "posadzka hali"], "fundament i posadzka w jednym", big=88),
    lambda L, t: bm.caption(L, t, T(2), E(3), "SPRZĘT", ["Zacieraczki", "czekają na start"]),
    lambda L, t: bm.tracker(L, t, T(4), E(5), 1 if t < S[5] else 2),
    lambda L, t: bm.caption(L, t, T(4), E(4), "ZGADNIJ", ["Ile godzin do", "zatarcia na gładko?"], "odpowiedź za chwilę", y=1190, big=74),
    lambda L, t: bm.caption(L, t, T(5), E(5), "ODPOWIEDŹ", ["15–20 godzin"], "bez przerwy, aż będzie gładko", y=1190),
    lambda L, t: bm.chips(L, t, T(6), E(6), [("pin", "Okolice Sochaczewa"), ("truck", "Beton: Atrans")], y=1300),
]
END1 = ""
if __name__ == "__main__":
    if "base" in sys.argv: base()
    b = f"{bm.WORK}/base_sochaczew.mp4"
    if "preview" in sys.argv:
        bm.preview(b, tl, REELS, END1, "", f"{bm.WORK}/pv_sochaczew.jpg", [s + 1.5 for s in S[:-1]] + [tl.total - 0.5])
    if "export" in sys.argv:
        bm.export(b, tl, REELS, END1, "", os.path.join(P, "benon_sochaczew_reels.mp4"), "s_reels", counters=[(T(0), 1.3)])
        bm.export(b, tl, TIKTOK, END1, "", os.path.join(P, "benon_sochaczew_tiktok.mp4"), "s_tt")
