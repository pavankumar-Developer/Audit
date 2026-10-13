# Parkmed — NABH Accredited · Showreel series (4 styles × 2 themes)

Eight 15-second 4K films, 60 fps, each with its own soundtrack **synthesized entirely in code** (no samples, no audio files, no plug-ins). Every cut lands on a beat of that soundtrack.

| # | Style (based on reference) | Format | Tempo | Parkmed theme | Reference theme |
|---|---|---|---|---|---|
| 1 | Kinetic — dark showreel, floods, echo type, particles, orbs, UI card | 2160×3840 portrait | 120 BPM | navy · green · blue | black · orange · blue |
| 2 | Editorial — white page, serif word morphs, line-art constructions, 3D plus | 2160×3840 portrait | 96 BPM | white · ink · green | white · ink · terracotta |
| 3 | Product — light, soft glows, headline pill, card carousel, collage | 3840×2160 landscape | 112 BPM | white · blue · green glows | white · orange · peach glows |
| 4 | On the beat — easing curve, Bauhaus grid, tunnel, cube field, word-per-beat | 3840×2160 landscape | 150 BPM | navy · green · blue | near-black · red · lime · blue |

Final files: `deliver/` (named `Parkmed-NABH_<Style>_<Theme>_<WxH>_60fps.mp4`).

## Wording used (company-approved)
Parkmed Healthcare · NABH Accredited · Parkmed Healthcare is now NABH accredited. · Held to the nation’s highest standard. · Safety. Quality. Trust. · Patient safety. Quality of care. Delivered. · Committed to Quality. · Focused on Patient Safety. · Healthcare Delivered (logo tagline).
Not used: “LLP”, clinic type, city. No NABH seal is recreated; the official mark can be added if the original file is supplied.

## Project layout
- `style1-kinetic/`, `style2-editorial/`, `style3-product/`, `style4-beat/` — Hyperframes compositions (`index.html` + `assets/`). The theme is a composition variable.
- `tools/score.py` — the synthesizer and the four arrangements (oscillators, noise drums, generated reverb, sidechain, limiter).
- `tools/assemble.sh` — copies shared assets and writes `assets/audio/score.wav` + `assets/beats.js` (beat grid, cut times, loudness envelope).
- `tools/render.sh`, `tools/queue.sh` — 4K renders.
- `shared/` — fonts (SIL OFL), logo layers split pixel-exactly from the original artwork, GSAP, `kit.js` helpers.

## Re-render
```bash
tools/assemble.sh s4 style4-beat          # regenerate score + beats for a style
cd style4-beat && npx hyperframes check
npx hyperframes render --quality delivery --fps 60 --resolution landscape-4k --variables '{"theme":"parkmed"}' --output ../renders/out.mp4
# theme: "parkmed" or "ref"; resolution: landscape-4k (styles 3–4) or portrait-4k (styles 1–2)
```
