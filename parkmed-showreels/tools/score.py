#!/usr/bin/env python3
"""Parkmed showreel scores — every sound is synthesized here from oscillators and
noise. No samples, no audio files, no plug-ins.

    python3 tools/score.py <style> <out.wav> <beats.json>

style: s1 | s2 | s3 | s4
Writes a 48 kHz stereo WAV (exactly 15.0 s) and a JSON with the beat grid, cut
times and a 60 fps loudness envelope (used for audio-reactive visuals).
"""
import json, subprocess, sys
import numpy as np
import scipy.signal as ss

SR = 48000
DUR = 15.0
N = int(SR * DUR)
rng = np.random.default_rng(1013)


# ------------------------------------------------------------------ helpers
def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def t_arr(d):
    return np.arange(int(d * SR)) / SR


def env_adsr(d, a=0.005, dcy=0.1, s=0.6, r=0.1):
    n = int(d * SR)
    t = np.arange(n) / SR
    e = np.ones(n) * s
    e[t < a] = t[t < a] / max(a, 1e-6)
    m = (t >= a) & (t < a + dcy)
    e[m] = 1 - (1 - s) * (t[m] - a) / max(dcy, 1e-6)
    rel = t > d - r
    e[rel] *= np.clip((d - t[rel]) / max(r, 1e-6), 0, 1)
    return e


def env_exp(d, tau):
    return np.exp(-t_arr(d) / tau)


def lp(x, f, order=2):
    b, a = ss.butter(order, min(f, SR * 0.45) / (SR / 2), "low")
    return ss.lfilter(b, a, x)


def hp(x, f, order=2):
    b, a = ss.butter(order, f / (SR / 2), "high")
    return ss.lfilter(b, a, x)


def bp(x, f1, f2, order=2):
    b, a = ss.butter(order, [f1 / (SR / 2), min(f2, SR * 0.45) / (SR / 2)], "band")
    return ss.lfilter(b, a, x)


def saw(f, d, phase=0.0):
    t = t_arr(d)
    # band-limited saw via additive harmonics (clean at any pitch)
    out = np.zeros_like(t)
    k = 1
    while k * f < SR * 0.45 and k <= 60:
        out += ((-1) ** (k + 1)) * np.sin(2 * np.pi * k * f * t + phase * k) / k
        k += 1
    return out * (2 / np.pi)


def square(f, d):
    t = t_arr(d)
    out = np.zeros_like(t)
    k = 1
    while k * f < SR * 0.45 and k <= 59:
        out += np.sin(2 * np.pi * k * f * t) / k
        k += 2
    return out * (4 / np.pi)


def tri(f, d):
    t = t_arr(d)
    out = np.zeros_like(t)
    k = 1
    s = 1
    while k * f < SR * 0.45 and k <= 31:
        out += s * np.sin(2 * np.pi * k * f * t) / (k * k)
        k += 2
        s = -s
    return out * (8 / np.pi ** 2)


def sine(f, d, ph=0.0):
    return np.sin(2 * np.pi * f * t_arr(d) + ph)


def noise(d):
    return rng.standard_normal(int(d * SR))


# ------------------------------------------------------------------ instruments
def kick(punch=1.0, d=0.42, f0=160, f1=44):
    t = t_arr(d)
    f = f1 + (f0 - f1) * np.exp(-t / 0.035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.16)
    click = hp(noise(d), 2500) * np.exp(-t / 0.004) * 0.35
    return np.tanh((body + click) * 1.6 * punch) * 0.9


def snare(d=0.25, tone=190):
    t = t_arr(d)
    n = bp(noise(d), 900, 7000) * np.exp(-t / 0.07)
    b = np.sin(2 * np.pi * tone * t) * np.exp(-t / 0.05)
    return (n * 0.8 + b * 0.5) * 0.8


def clap(d=0.3):
    t = t_arr(d)
    n = bp(noise(d), 800, 5000)
    e = np.zeros_like(t)
    for off in (0.0, 0.011, 0.022):
        m = t >= off
        e[m] += np.exp(-(t[m] - off) / (0.012 if off < 0.02 else 0.11))
    return n * e * 0.7


def hat(open_=False, d=None):
    d = d or (0.22 if open_ else 0.05)
    t = t_arr(d)
    return hp(noise(d), 7500, 3) * np.exp(-t / (0.08 if open_ else 0.012)) * 0.5


def shaker(d=0.07):
    t = t_arr(d)
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return bp(noise(d), 5000, 12000) * e * 0.28


def rim(d=0.06):
    t = t_arr(d)
    return (np.sin(2 * np.pi * 1700 * t) * 0.5 + bp(noise(d), 2000, 6000) * 0.4) * np.exp(-t / 0.012)


def bass(n, d, cutoff=700, sub=0.6, drive=1.4):
    f = hz(n)
    x = saw(f, d) * 0.6 + sine(f / 2, d) * 0 + sine(f, d) * sub
    x = lp(x, cutoff, 2)
    return np.tanh(x * drive) * env_adsr(d, 0.004, 0.08, 0.75, 0.04) * 0.7


def reese(n, d, cutoff=900):
    f = hz(n)
    x = saw(f * 0.995, d) + saw(f * 1.005, d, 1.3) + sine(f / 2, d) * 0.9
    x = lp(x, cutoff, 3)
    return np.tanh(x * 1.2) * env_adsr(d, 0.005, 0.1, 0.85, 0.05) * 0.5


def pluck(n, d=0.3, bright=4500, kind="saw"):
    f = hz(n)
    osc = saw(f, d) if kind == "saw" else square(f, d) * 0.6
    e = env_exp(d, d * 0.28)
    hi = lp(osc, bright, 2)
    lo = lp(osc, 700, 2)
    return (hi * e + lo * (1 - e)) * e * 0.5


def fm_bell(n, d=1.2, ratio=3.5, index=2.5, tau=0.5):
    t = t_arr(d)
    f = hz(n)
    idx = index * np.exp(-t / (tau * 0.4))
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * ratio * t))
    return x * np.exp(-t / tau) * env_adsr(d, 0.002, 0.0, 1.0, 0.05) * 0.45


def epiano(n, d=0.9):
    t = t_arr(d)
    f = hz(n)
    idx = 1.6 * np.exp(-t / 0.25)
    x = np.sin(2 * np.pi * f * t + idx * np.sin(2 * np.pi * f * t))
    x += 0.25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / 0.3)
    return x * np.exp(-t / 0.9) * env_adsr(d, 0.003, 0, 1, 0.08) * 0.35


def pad(notes, d, cutoff=1600, detune=0.006, att=0.25):
    L = np.zeros(int(d * SR))
    R = np.zeros(int(d * SR))
    for n in notes:
        f = hz(n)
        L += saw(f * (1 - detune), d) + saw(f * (1 + detune * 0.4), d, 0.7)
        R += saw(f * (1 + detune), d, 1.1) + saw(f * (1 - detune * 0.4), d, 2.0)
    e = env_adsr(d, att, 0.2, 0.85, min(0.4, d * 0.3))
    L = lp(L, cutoff, 2) * e
    R = lp(R, cutoff, 2) * e
    g = 0.16 / max(1, len(notes) ** 0.5)
    return L * g, R * g


def keys(notes, d, cutoff=2400):
    x = np.zeros(int(d * SR))
    for n in notes:
        f = hz(n)
        x += tri(f, d) * 0.7 + saw(f * 1.003, d) * 0.25
    x = lp(x, cutoff, 2) * env_adsr(d, 0.01, 0.25, 0.55, 0.12)
    return x * 0.22 / max(1, len(notes) ** 0.5)


def stab(notes, d=0.22, cutoff=3200):
    x = np.zeros(int(d * SR))
    for n in notes:
        x += saw(hz(n), d) + saw(hz(n) * 1.007, d, 0.5)
    e = env_exp(d, 0.06)
    return lp(x, cutoff, 2) * e * 0.18


def riser(d, f0=300, f1=6000, gain=0.5):
    n = int(d * SR)
    x = noise(d)
    out = np.zeros(n)
    chunks = 24
    for i in range(chunks):
        a, b = i * n // chunks, (i + 1) * n // chunks
        fc = f0 * (f1 / f0) ** (i / chunks)
        seg = bp(x[max(0, a - 2000):b], fc * 0.7, fc * 1.4)[-(b - a):]
        out[a:b] = seg
    t = t_arr(d)
    e = (t / d) ** 2
    tone = np.sin(2 * np.pi * np.cumsum(200 * (8 ** (t / d))) / SR) * 0.15
    return (out * 1.2 + tone) * e * gain


def downlifter(d=1.2, gain=0.4):
    t = t_arr(d)
    x = bp(noise(d), 300, 4000) * np.exp(-t / (d * 0.35))
    return x * gain


def impact(d=1.6, gain=1.0):
    t = t_arr(d)
    f = 30 + 70 * np.exp(-t / 0.08)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.45)
    burst = lp(noise(d), 3000) * np.exp(-t / 0.05) * 0.6
    return np.tanh((sub * 1.2 + burst) * 1.3) * gain * 0.8


def tick(f=2200, d=0.03):
    t = t_arr(d)
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006) * 0.4


# ------------------------------------------------------------------ mixer
class Mix:
    def __init__(self):
        self.L = np.zeros(N + SR * 3)
        self.R = np.zeros(N + SR * 3)
        self.vL = np.zeros_like(self.L)  # reverb send
        self.vR = np.zeros_like(self.R)
        self.duck = np.ones_like(self.L)
        self.ducked = np.zeros(len(self.L), dtype=bool)

    def add(self, sig, t, gain=1.0, pan=0.0, verb=0.0, duck=False):
        if isinstance(sig, tuple):
            l, r = sig
        else:
            l = r = sig
        i = int(round(t * SR))
        if i >= len(self.L):
            return
        n = min(len(l), len(self.L) - i)
        gl = gain * np.cos((pan + 1) * np.pi / 4) * 1.414
        gr = gain * np.sin((pan + 1) * np.pi / 4) * 1.414
        tgtL, tgtR = (self.dL, self.dR) if duck else (self.L, self.R)
        tgtL[i:i + n] += l[:n] * gl
        tgtR[i:i + n] += r[:n] * gr
        if verb:
            self.vL[i:i + n] += l[:n] * gl * verb
            self.vR[i:i + n] += r[:n] * gr * verb

    def sidechain(self, times, depth=0.55, tau=0.11):
        t = np.arange(len(self.L)) / SR
        for kt in times:
            i = int(kt * SR)
            seg = t[i:i + int(SR * 0.6)] - kt
            self.duck[i:i + len(seg)] = np.minimum(self.duck[i:i + len(seg)], 1 - depth * np.exp(-seg / tau))

    def render(self, verb_rt=1.6, verb_gain=0.35):
        # generated reverb IR: decorrelated decaying noise, damped
        d = verb_rt * 1.2
        tt = t_arr(d)
        irL = lp(noise(d), 5000) * np.exp(-tt / (verb_rt / 6.9))
        irR = lp(noise(d), 5000) * np.exp(-tt / (verb_rt / 6.9))
        irL /= np.sqrt((irL ** 2).sum())
        irR /= np.sqrt((irR ** 2).sum())
        wl = ss.fftconvolve(self.vL, irL)[: len(self.L)]
        wr = ss.fftconvolve(self.vR, irR)[: len(self.R)]
        L = self.L + (self.dL * self.duck) + wl * verb_gain
        R = self.R + (self.dR * self.duck) + wr * verb_gain
        L, R = L[:N], R[:N]
        # gentle master: low-cut, glue compression, soft clip
        L, R = hp(L, 28), hp(R, 28)
        peak = max(np.abs(L).max(), np.abs(R).max(), 1e-9)
        L, R = L / peak, R / peak
        L, R = np.tanh(L * 1.6) / np.tanh(1.6), np.tanh(R * 1.6) / np.tanh(1.6)
        fade = int(SR * 0.012)
        ramp = np.linspace(0, 1, fade)
        L[:fade] *= ramp
        R[:fade] *= ramp
        L[-fade:] *= ramp[::-1]
        R[-fade:] *= ramp[::-1]
        return L, R


def new_mix():
    m = Mix()
    m.dL = np.zeros_like(m.L)
    m.dR = np.zeros_like(m.R)
    return m


# ------------------------------------------------------------------ styles
def style_s1():
    """A minor electro-pop, 120 BPM. Drop on cut 1 (1.5 s)."""
    bpm = 120
    B = 60 / bpm
    cuts = [0, 3, 5, 7, 9, 11, 13, 16, 19, 21, 25]
    m = new_mix()
    prog = [(57, [69, 72, 76]), (53, [65, 69, 72]), (48, [67, 72, 76]), (55, [67, 71, 74])]  # Am F C G
    kicks = []
    # intro: pad + rising pluck, riser into the drop
    m.add(pad([57, 64, 69, 72], 3 * B, cutoff=900, att=0.6), 0, 0.9, verb=0.4)
    for i, n in enumerate([69, 72, 76, 79, 81, 84]):
        m.add(pluck(n, 0.3, 3000), i * B / 2, 0.45, pan=(-0.3 if i % 2 else 0.3), verb=0.5)
    m.add(riser(3 * B - 0.05, 400, 7000, 0.35), 0.05, 1.0)
    for b in range(3, 30):
        t = b * B
        bar = (b - 3) // 4
        root, chord = prog[bar % 4]
        in_break = 24 <= b < 25
        if not in_break and b < 29:
            m.add(kick(), t, 1.0)
            kicks.append(t)
            if (b - 3) % 2 == 1:
                m.add(clap(), t, 0.55, verb=0.25)
            m.add(hat(), t + B / 2, 0.35, pan=0.25)
            for s16 in (0.25, 0.75):
                m.add(shaker(), t + B * s16, 0.5, pan=-0.3)
            # bass: root on beat, octave pop on the and
            m.add(bass(root - 12, B * 0.45, 650), t, 0.8, duck=True)
            m.add(bass(root, B * 0.22, 900), t + B * 0.5, 0.55, duck=True)
            # arp
            for k in range(4):
                n = chord[(b * 4 + k) % 3] + (12 if k == 3 else 0)
                m.add(pluck(n, 0.18, 3800), t + k * B / 4, 0.32, pan=(-0.4 if k % 2 else 0.4), verb=0.3, duck=True)
        if (b - 3) % 4 == 0 and b < 25:
            m.add(pad(chord + [root], 4 * B, cutoff=1400), t, 0.8, verb=0.35, duck=True)
    # cut accents
    for c in cuts[1:]:
        t = c * B
        root, chord = prog[((c - 3) // 4) % 4] if c >= 3 else prog[0]
        m.add(stab(chord + [chord[0] + 12], 0.25), t, 0.8, verb=0.4)
        m.add(hat(True), t, 0.35, pan=-0.2, verb=0.2)
    m.add(riser(B * 1.0, 800, 9000, 0.45), 24 * B, 1.0)
    m.add(impact(2.4), 25 * B, 0.95, verb=0.5)
    m.add(pad([57, 64, 69, 72, 76], 5 * B, cutoff=1800, att=0.05), 25 * B, 0.9, verb=0.5)
    m.add(fm_bell(81, 2.2, tau=0.9), 25 * B, 0.5, verb=0.6)
    m.add(fm_bell(76, 2.0, tau=0.9), 25 * B + B * 0.5, 0.35, pan=0.3, verb=0.6)
    m.add(downlifter(1.6), 25 * B, 0.6, verb=0.3)
    m.sidechain(kicks)
    return m, bpm, cuts, 30


def style_s2():
    """D major, 96 BPM — airy FM keys, soft pulse. Editorial and light."""
    bpm = 96
    B = 60 / bpm
    cuts = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 21]
    m = new_mix()
    prog = [(50, [62, 66, 69]), (47, [59, 62, 66]), (43, [59, 62, 67]), (45, [61, 64, 69])]  # D Bm G A
    melody = [78, 76, 74, 76, 78, 81, 78, 76, 74, 73, 74, 76, 78, 76, 74, 69, 74, 76, 78, 81, 83, 81, 78, 76]
    kicks = []
    for b in range(24):
        t = b * B
        root, chord = prog[(b // 4) % 4]
        if b % 4 == 0 and b < 21:
            m.add(pad(chord, 4 * B, cutoff=1200, att=0.3), t, 0.8, verb=0.5, duck=True)
            m.add(epiano(root - 12, 4 * B), t, 0.6)
        m.add(fm_bell(melody[b], 0.9, ratio=2.0, index=1.6, tau=0.45), t, 0.5, pan=0.15 * ((b % 3) - 1), verb=0.55)
        if b >= 2 and b < 21:
            m.add(kick(0.7, 0.35, 120, 46), t, 0.75 if b % 2 == 0 else 0.45)
            kicks.append(t)
            if b % 2 == 1:
                m.add(rim(), t, 0.5, pan=0.2, verb=0.3)
            m.add(shaker(0.09), t + B / 2, 0.55, pan=-0.25)
            m.add(epiano(chord[b % 3] + 12, 0.4), t + B * 0.75, 0.25, pan=0.35, verb=0.4)
    for c in cuts[1:]:
        m.add(fm_bell(86, 0.6, ratio=3.5, index=1.2, tau=0.25), c * B, 0.22, pan=0.4, verb=0.6)
    m.add(riser(2 * B, 500, 5000, 0.25), 19 * B, 1.0)
    m.add(impact(2.2, 0.7), 21 * B, 0.8, verb=0.6)
    m.add(pad([50, 57, 62, 66, 69, 74], 3 * B, cutoff=1600, att=0.05), 21 * B, 1.0, verb=0.6)
    for i, n in enumerate([74, 78, 81, 86]):
        m.add(fm_bell(n, 2.0, ratio=2.0, index=1.4, tau=0.8), 21 * B + i * B / 4, 0.35, pan=(i - 1.5) * 0.25, verb=0.7)
    m.sidechain(kicks, depth=0.3)
    return m, bpm, cuts, 24


def style_s3():
    """F major chill pop, 112 BPM — warm keys, snaps, glossy pluck."""
    bpm = 112
    B = 60 / bpm
    cuts = [0, 2, 6, 10, 14, 18, 21]
    m = new_mix()
    prog = [(41, [64, 65, 69, 72]), (45, [64, 67, 69, 72]), (38, [62, 65, 69, 72]), (46, [62, 65, 69, 70])]  # Fmaj7 Am7 Dm7 Bbmaj7
    kicks = []
    m.add(fm_bell(84, 1.0, ratio=2.0, index=1.0, tau=0.4), 0, 0.4, verb=0.6)
    m.add(riser(2 * B, 600, 6000, 0.25), 0, 1.0)
    for b in range(28):
        t = b * B
        root, chord = prog[(b // 4) % 4]
        if b % 4 == 0:
            m.add(keys(chord, 4 * B), t, 1.0, verb=0.35, duck=True)
        if 2 <= b < 21 or b >= 23:
            m.add(kick(0.9, 0.38, 140, 48), t, 0.9)
            kicks.append(t)
            if b % 2 == 1:
                m.add(clap(0.22), t, 0.45, verb=0.35)
            for s16 in (0.25, 0.5, 0.75):
                m.add(shaker(0.06), t + B * s16, 0.45 if s16 == 0.5 else 0.3, pan=0.3)
            m.add(bass(root - 12 if root > 40 else root, B * 0.55, 500, sub=0.9), t, 0.75, duck=True)
            if b % 2 == 0:
                m.add(bass(root, B * 0.2, 700), t + B * 0.75, 0.4, duck=True)
            n = chord[(b * 2) % 4] + 12
            m.add(pluck(n, 0.22, 5000, "square"), t + B * 0.5, 0.3, pan=-0.35, verb=0.4, duck=True)
    for c in cuts[1:]:
        m.add(pluck(chord_top := prog[(c // 4) % 4][1][-1] + 12, 0.4, 6000), c * B, 0.4, pan=0.3, verb=0.5)
        m.add(hat(True, 0.3), c * B, 0.25, verb=0.3)
    m.add(riser(2 * B, 700, 8000, 0.35), 19 * B, 1.0)
    m.add(impact(2.0, 0.8), 21 * B, 0.85, verb=0.5)
    m.add(pad([53, 60, 65, 69, 72, 76], 7 * B, cutoff=1700, att=0.05), 21 * B, 0.9, verb=0.55, duck=True)
    for i, n in enumerate([77, 81, 84]):
        m.add(fm_bell(n, 1.8, ratio=2.0, index=1.2, tau=0.7), 21 * B + i * B / 3, 0.35, pan=(i - 1) * 0.3, verb=0.6)
    m.sidechain(kicks, depth=0.45)
    return m, bpm, cuts, 28


def style_s4():
    """E minor high-energy electro, 150 BPM. Clock intro, drop at 1.6 s,
    snare roll into the rapid-word section, impact on the logo."""
    bpm = 150
    B = 60 / bpm
    cuts = [0, 4, 6, 9, 12, 14, 16, 19, 21, 22, 23, 24, 25, 26, 27, 28, 32]
    m = new_mix()
    prog = [(40, [64, 67, 71]), (36, [64, 67, 72]), (43, [62, 67, 71]), (38, [62, 66, 69])]  # Em C G D
    kicks = []
    # intro: clock ticks + sub swell + rising sweep (the easing curve)
    for i in range(8):
        m.add(tick(2600 if i % 2 == 0 else 1900), i * B / 2, 0.5, pan=(0.3 if i % 2 else -0.3))
    m.add(riser(4 * B, 200, 8000, 0.45), 0, 1.0)
    m.add(pad([52, 59, 64, 67], 4 * B, cutoff=700, att=1.0), 0, 0.7, verb=0.4)
    for b in range(4, 38):
        t = b * B
        root, chord = prog[((b - 4) // 4) % 4]
        roll = 21 <= b < 28
        outro = b >= 32
        if not outro:
            m.add(kick(1.1), t, 1.0)
            kicks.append(t)
            if (b - 4) % 2 == 1 and not roll:
                m.add(snare(), t, 0.6, verb=0.25)
            for s in (0.25, 0.5, 0.75):
                m.add(hat(s == 0.5), t + B * s, 0.3 if s != 0.5 else 0.38, pan=0.3 if s == 0.25 else -0.2)
            m.add(reese(root - 12 + 12, B * 0.95, 700 + 400 * ((b % 4) / 3)), t, 0.75, duck=True)
            if b % 2 == 0:
                for k, n in enumerate(chord):
                    m.add(pluck(n + 12, 0.14, 5000), t + B * (0.5 + k * 0.125), 0.22, pan=(k - 1) * 0.4, verb=0.3, duck=True)
        if roll:
            steps = 2 if b < 24 else 4
            for s in range(steps):
                m.add(snare(0.15, 210), t + s * B / steps, 0.32 + 0.05 * (b - 21), verb=0.2)
    for c in cuts[1:]:
        t = c * B
        root, chord = prog[((c - 4) // 4) % 4] if c >= 4 else prog[0]
        m.add(stab(chord + [chord[0] + 12], 0.18, 4200), t, 0.85, verb=0.3)
    m.add(riser(3 * B, 600, 10000, 0.5), 25 * B, 1.0)
    m.add(impact(1.8), 28 * B, 0.9, verb=0.4)
    m.add(riser(2 * B, 800, 9000, 0.4), 30 * B, 1.0)
    m.add(impact(2.6, 1.1), 32 * B, 1.0, verb=0.6)
    m.add(pad([40, 52, 59, 64, 67, 71], 5.5 * B, cutoff=1500, att=0.05), 32 * B, 1.0, verb=0.6)
    m.add(fm_bell(83, 2.2, ratio=3.5, index=2.0, tau=0.8), 32 * B, 0.45, verb=0.6)
    m.add(fm_bell(88, 1.8, ratio=3.5, index=1.6, tau=0.7), 32 * B + B, 0.3, pan=0.35, verb=0.7)
    m.add(downlifter(2.0), 32 * B, 0.55, verb=0.3)
    m.sidechain(kicks, depth=0.6)
    return m, bpm, cuts, 37.5


STYLES = {"s1": style_s1, "s2": style_s2, "s3": style_s3, "s4": style_s4}


def write_wav(path, L, R):
    import wave
    x = np.stack([L, R], 1)
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def loudness(path):
    out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
    I = [l for l in out.splitlines() if l.strip().startswith("I:")][-1]
    P = [l for l in out.splitlines() if l.strip().startswith("Peak:")][-1]
    return float(I.split()[1]), float(P.split()[1])


def main():
    style, out_wav, out_json = sys.argv[1], sys.argv[2], sys.argv[3]
    m, bpm, cuts, beats = STYLES[style]()
    L, R = m.render()
    write_wav(out_wav, L * 0.5, R * 0.5)
    I, P = loudness(out_wav)
    target_I, ceil = -14.0, -1.0
    g = 10 ** ((target_I - I) / 20) * 0.5
    g = min(g, 10 ** (ceil / 20) / max(np.abs(L).max(), np.abs(R).max()))
    write_wav(out_wav, L * g, R * g)
    I2, P2 = loudness(out_wav)
    B = 60 / bpm
    mono = (L + R) * 0.5 * g
    hop = SR // 60
    env = [float(np.sqrt(np.mean(mono[i * hop:(i + 1) * hop] ** 2))) for i in range(int(DUR * 60))]
    mx = max(env) or 1
    json.dump({
        "style": style, "bpm": bpm, "beat": B,
        "beats": [round(i * B, 6) for i in range(int(beats) + 1) if i * B <= DUR + 1e-9],
        "cutBeats": cuts, "cuts": [round(c * B, 6) for c in cuts],
        "env60": [round(e / mx, 4) for e in env],
        "loudnessLUFS": I2, "peakdBFS": P2,
    }, open(out_json, "w"))
    print(f"{style}: {bpm} BPM, beat {B:.4f}s, cuts {[round(c*B,3) for c in cuts]}, {I2} LUFS, peak {P2} dBFS")


if __name__ == "__main__":
    main()
