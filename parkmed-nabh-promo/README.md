# Parkmed — NABH Accredited (15 s promo)

`parkmed-nabh-promo.mp4` — 1080×1920 portrait, H.264, 60 fps, 15.0 s, AAC stereo (−20 LUFS). `poster.jpg` is the thumbnail (also frame 0).

## Shots (cut on a 120 BPM grid)
1. 0.0 Dot draws a ring → green check
2. 1.0 Blue circle flood, kinetic "Parkmed is now" over moving PARKMED — NABH rows
3. 2.0 NABH letters slam on the music lift, brush stroke, block-reveal ACCREDITED, blur zoom-through
4. 4.0 2,600 particles converge into QUALITY — "Committed to"
5. 5.75 Green diagonal wipe, dot grid morphs into plus signs — "Focused on Patient Safety."
6. 7.5 3D card: NABH Accredited toggle switches on, three ticks, ACCREDITED stamp with shake
7. 9.85 Two 3D word rings (Quality · Trust / Patient Safety · Care) orbit NABH
8. 11.25 "Healthcare Delivered." — words fly into the logo's own tagline
9. 12.5 Logo builds from its exact artwork layers (Park, med, bird mark, arc) + NABH Accredited pill

## Edit / re-render
```bash
npx hyperframes check
npx hyperframes preview
npx hyperframes render --quality delivery --fps 60 --output parkmed-nabh-promo.mp4
```

## Assets
- Logo: original Parkmed artwork; `assets/logo/part-*.png` are pixel-exact layers split from it (re-stacked they equal the original).
- Fonts (SIL OFL): Archivo Black, Instrument Serif, IBM Plex Sans, IBM Plex Mono.
- Music: "Happy Beats / Business Moves Vol. 1", ende.app — CC BY 4.0 (commercial use allowed), starts at 14.02 s of the track.
- SFX: Kenney (CC0).
