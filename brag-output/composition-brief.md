# Hyperframes Composition Brief: Parkmed Healthcare LLP — NABH Accreditation

## Objective
A 21-second formal corporate announcement film for Parkmed Healthcare LLP's NABH accreditation, built in Hyperframes.

## Output
- Vertical composition: `brag-output/composition/` → `brag-output/brag.mp4` (1080×1920, 30 fps, H.264)
- Landscape composition: `brag-output/composition-landscape/` → `brag-output/brag-landscape.mp4` (1920×1080, 30 fps, H.264)
- Silent variants: `brag-silent.mp4`, `brag-landscape-silent.mp4`
- Duration: 21.0 s

## Source Material
- Logo: original artwork supplied by Parkmed (`assets/logo/parkmed-logo.png`, 1083×474 RGBA). Never redrawn, recoloured, cropped or distorted; uniform scale only.
- All on-screen statements are the verbatim wording supplied in the brief (see brag-plan.md → Wording).

## Creative Direction
- Tone preset: polished
- Direction: annual-report editorial spread; typography is the primary visual element
- Hook: the logo alone on the sheet, settling into place
- Outro: logo + "Thank you for your continued trust." held to the end
- Avoid: medical icons, stock imagery, glows, gradients, 3D, particles, random shapes, zooms, spins, bounces, typewriter, slideshow transitions, constant movement, any invented fact or mark

## Visual Identity
- Sheet `#F7F7F4`; panels `#FFFFFF`; tinted panel `#EEF3F8`
- Text `#2B2C2E`; secondary `#4C4D4F`; tertiary labels `#6B6C6F` (contrast-checked)
- Green `#1FB25A`, blue `#0065B2` (exact logo values) for rules and labels only
- Newsreader 300/400 (display), IBM Plex Sans 400/500/600 (labels/data); local `@font-face`
- Persistent furniture across all scenes: margins, running head with hairline, folio 01–05

## Motion system
- One easing family: entrances `power3.out` (0.9–1.1 s), exits `power2.in` (0.45 s)
- Movement limited to opacity, 14–24 px vertical settles, line masks, and rule draws (`scaleX`)
- Scenes hand over content-out-then-in on the same sheet; furniture never leaves, so the film reads as one piece

## Audio
- Music: `assets/music/happy-beats-business-moves-vol-12-by-ende-dot-app.mp3`, volume 0.45 (≈ -23 LUFS), fade in 1.2 s, fade out from 19.2 s
- Cues: preset `.../cues/happy-beats-business-moves-vol-12-by-ende-dot-app.music-cues.json`; soft locks at 9.29 s and 18.02 s
- Audio-reactive: none (intentional; brief rejects constant movement)
- SFX: none (intentional)

## Hyperframes Instructions
Follow hyperframes-core contract: standalone root, one paused GSAP timeline registered on `window.__timelines["main"]`, clips by `data-start`/`data-duration`, `npx hyperframes check` must pass before render.
