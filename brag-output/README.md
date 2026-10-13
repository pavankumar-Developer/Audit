# Parkmed Healthcare LLP — NABH Accreditation Film

21-second corporate announcement film, made with the `/brag` skill (Hyperframes workflow).

## Deliverables
| File | Format |
|---|---|
| `brag.mp4` | Primary — 1080×1920 vertical (9:16), H.264 High, 30 fps, 21.0 s, AAC stereo |
| `brag-landscape.mp4` | 1920×1080 landscape (16:9), H.264 High, 30 fps, 21.0 s, AAC stereo — re-composed, not cropped |
| `brag-silent.mp4`, `brag-landscape-silent.mp4` | Same pictures, no audio track |
| `brag.jpg`, `brag-landscape.jpg` | Poster / custom thumbnail (also baked in as frame 0 of each MP4) |
| `share-copy.txt` | Caption for LinkedIn / email |

## Editable source
- `composition/` — vertical Hyperframes project (`index.html` + `assets/`)
- `composition-landscape/` — landscape Hyperframes project
- `brag-plan.md` — creative plan and storyboard; `composition-brief.md` — build brief

Everything needed to re-render is inside each composition folder (logo, fonts, music, GSAP — no network needed).

```bash
cd composition            # or composition-landscape
npx hyperframes check     # gate: lint, runtime, layout, contrast
npx hyperframes preview   # open in Hyperframes Studio to edit
npx hyperframes render --quality delivery --fps 30 --output ../brag.mp4
```
Requires Node.js 22+, FFmpeg, and `npx hyperframes browser ensure` once.

## Assets and licences
- Logo: original Parkmed artwork (`assets/logo/parkmed-logo.png`, 1083×474), used unmodified — uniform scaling only.
- Fonts: Newsreader and IBM Plex Sans — SIL Open Font License 1.1 (licence texts in `assets/fonts/`).
- Music: "Happy Beats / Business Moves Vol. 12" by ende.app — CC BY 4.0, commercial use permitted (https://ende.app/en). Attribution optional; credit: "Music: ende.app".
- GSAP 3.14.2 (`assets/vendor/gsap.min.js`) — standard GSAP licence.

## Quality checks performed
- `hyperframes check`: 0 errors; 39–42/42 text elements pass WCAG AA contrast.
- Wording verified against the brief; no grades, certificate numbers, dates, seals or official marks added.
- Logo in render compared with source artwork: aspect within 0.2%, mean pixel deviation 2/255, brand colours exact.
- No flashes or blank frames (frame-to-frame luma step ≤ 1.0); final second fully static.
- Audio: −23.1 LUFS integrated, −9.5 dBFS peak; fade-in 1.2 s, fade-out ends at 20.9 s.
