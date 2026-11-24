# Benon – materiały do social mediów

Gotowe filmy pionowe (1080×1920) na TikTok, Instagram Reels i Facebook Reels.
Każda realizacja ma własny folder: film, okładkę, gotowe opisy z hashtagami i oryginalne materiały z budowy.

| Data | Realizacja | Film | Długość | Gdzie publikować |
|---|---|---|---|---|
| 20.11.2026 | Płyta fundamentowa 400 m², okolice Sochaczewa | `benon_sochaczew_reels.mp4` | 23 s | Instagram, Facebook |
| 20.11.2026 | jw. (wersja z pytaniem do widzów) | `benon_sochaczew_tiktok.mp4` | 23 s | TikTok |
| 24.11.2026 | STP Mory: 45 000 m² posadzek DST dla metra | `benon_stp-mory_45000m2.mp4` | 17 s | TikTok, Instagram, Facebook |
| 24.11.2026 | STP Mory: obiekt 220 m przed betonowaniem | `benon_stp-mory_220m.mp4` | 13 s | TikTok, Instagram, Facebook |

## Struktura

```
social/
├── README.md                              ← ten spis
├── 2026-11-20_sochaczew_plyta-400m2/
│   ├── benon_sochaczew_reels.mp4          ← film na Instagram / Facebook
│   ├── benon_sochaczew_tiktok.mp4         ← film na TikTok
│   ├── okladka_sochaczew_*.jpg            ← okładki
│   ├── OPISY.md                           ← opisy, hashtagi, komentarz do przypięcia
│   └── materialy/                         ← oryginalne nagranie z placu
├── 2026-11-24_stp-mory_posadzki-45000m2/
│   ├── benon_stp-mory_45000m2.mp4
│   ├── okladka_stp-mory_45000m2.jpg
│   ├── OPISY.md
│   └── materialy/                         ← 9 zdjęć gotowych hal
├── 2026-11-24_stp-mory_hala-220m/
│   ├── benon_stp-mory_220m.mp4
│   ├── okladka_stp-mory_220m.jpg
│   ├── OPISY.md
│   └── materialy/                         ← zdjęcie hali przed betonowaniem
└── _narzedzia/                            ← silnik montażu (dla Claude / technicznie)
```

## Kolejność publikacji (propozycja)

1. **STP Mory 45 000 m²**: najmocniejsza realizacja, buduje wiarygodność.
2. **STP Mory 220 m**: druga część serii o metrze, „od kulis”.
3. **Sochaczew 400 m²**: pokazuje, że firma robi też mniejsze obiekty.

Odstęp 2–3 dni między filmami.

## Styl serii

- Logo Benon w lewym górnym rogu, żółte akcenty w kolorze kurtek firmowych.
- Napisy i logo poza strefami przycisków TikToka i Instagrama.
- Na końcu każdego filmu plansza: www.benon.com.pl, tel. 781 555 519.
- Muzyka i efekty dźwiękowe są własne, bez praw autorskich, więc można je promować płatnie.

## Nowy film

Wyślij Claude nagranie lub zdjęcia z budowy z krótkim opisem (co, gdzie, ile m², ile godzin, kto dostarczył beton).
Nowy projekt powstaje w `_narzedzia/` jako kolejny skrypt w tym samym stylu.
