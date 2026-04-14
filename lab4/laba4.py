import sys
sys.path.insert(0, r'F:\python_libs')

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import butter, filtfilt


DEFAULTS = {
    "amplitude":        1.0,
    "frequency":        1.0,
    "phase":            0.0,
    "noise_mean":       0.0,
    "noise_covariance": 0.1,
    "cutoff":           5.0,
}

T = np.linspace(0, 10, 2000)  


state = {**DEFAULTS}
noise_cache = None      
show_noise  = True


def harmonic(amplitude, frequency, phase):
    return amplitude * np.sin(2 * np.pi * frequency * T + phase)


def generate_noise(noise_mean, noise_covariance):
    return np.random.normal(noise_mean, np.sqrt(noise_covariance), size=T.shape)


def harmonic_with_noise(amplitude, frequency, phase,
                        noise_mean, noise_covariance, cached_noise=None):
    """Повертає (чиста_гармоніка, шум, зашумлена)."""
    clean = harmonic(amplitude, frequency, phase)
    noise = cached_noise if cached_noise is not None else generate_noise(noise_mean, noise_covariance)
    return clean, noise, clean + noise


def lowpass_filter(signal, cutoff, fs=None, order=4):
    """Фільтр Батерворта низьких частот."""
    if fs is None:
        fs = 1.0 / (T[1] - T[0])
    nyq = 0.5 * fs
    normal_cutoff = min(cutoff / nyq, 0.99)   # не більше 1
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, signal)



fig = plt.figure(figsize=(12, 9))
fig.suptitle("Гармоніка з шумом та фільтрацією", fontsize=13, fontweight='bold')


ax_orig = fig.add_axes([0.07, 0.55, 0.88, 0.35])
ax_filt = fig.add_axes([0.07, 0.16, 0.88, 0.35])

ax_orig.set_title("Оригінальна гармоніка")
ax_filt.set_title("Відфільтрована гармоніка (Butterworth low-pass)")
for ax in (ax_orig, ax_filt):
    ax.set_xlabel("t")
    ax.set_ylabel("y(t)")
    ax.grid(True, alpha=0.3)


noise_cache = generate_noise(state["noise_mean"], state["noise_covariance"])
clean0, _, noisy0 = harmonic_with_noise(
    state["amplitude"], state["frequency"], state["phase"],
    state["noise_mean"], state["noise_covariance"], noise_cache
)
filtered0 = lowpass_filter(noisy0, state["cutoff"])


line_clean,  = ax_orig.plot(T, clean0,  color='royalblue',  lw=2,   label='Чиста гармоніка', zorder=3)
line_noisy,  = ax_orig.plot(T, noisy0,  color='darkorange', lw=0.8, alpha=0.85, label='З шумом')


line_filt_noisy, = ax_filt.plot(T, noisy0,   color='darkorange', lw=0.8, alpha=0.5, label='З шумом')
line_filt,       = ax_filt.plot(T, filtered0, color='crimson',   lw=2,   label='Відфільтрована')
line_filt_clean, = ax_filt.plot(T, clean0,    color='royalblue', lw=1.5, ls='--', label='Чиста (ідеал)', zorder=3)

ax_orig.legend(loc='upper right', fontsize=8)
ax_filt.legend(loc='upper right', fontsize=8)


slider_specs = [
    # (назва,          x,    y,     min,  max,  init,               key)
    ("Amplitude",      0.15, 0.108, 0.1,  3.0,  DEFAULTS["amplitude"],        "amplitude"),
    ("Frequency",      0.15, 0.088, 0.1,  5.0,  DEFAULTS["frequency"],        "frequency"),
    ("Phase",          0.15, 0.068, -np.pi, np.pi, DEFAULTS["phase"],         "phase"),
    ("Noise Mean",     0.15, 0.048, -1.0, 1.0,  DEFAULTS["noise_mean"],       "noise_mean"),
    ("Noise Cov",      0.15, 0.028, 0.0,  1.0,  DEFAULTS["noise_covariance"], "noise_covariance"),
    ("Cutoff Freq",    0.15, 0.008, 0.5,  20.0, DEFAULTS["cutoff"],           "cutoff"),
]

sliders = {}
for label, x, y, vmin, vmax, vinit, key in slider_specs:
    ax_s = fig.add_axes([x, y, 0.55, 0.015])
    sl = Slider(ax_s, label, vmin, vmax, valinit=vinit, color='steelblue')
    sl.label.set_fontsize(8)
    sl.valtext.set_fontsize(8)
    sliders[key] = sl


ax_chk = fig.add_axes([0.76, 0.005, 0.12, 0.04])
chk_noise = CheckButtons(ax_chk, ["Show Noise"], [True])
chk_noise.labels[0].set_fontsize(8)


ax_btn = fig.add_axes([0.07, 0.005, 0.07, 0.04])
btn_reset = Button(ax_btn, "Reset", color='#f0f0f0', hovercolor='#d0e8ff')
btn_reset.label.set_fontsize(8)


HARMONIC_KEYS = {"amplitude", "frequency", "phase"}
NOISE_KEYS    = {"noise_mean", "noise_covariance"}

def redraw():
    global noise_cache
    clean, _, noisy = harmonic_with_noise(
        state["amplitude"], state["frequency"], state["phase"],
        state["noise_mean"], state["noise_covariance"], noise_cache
    )
    filtered = lowpass_filter(noisy, state["cutoff"])

 
    line_clean.set_ydata(clean)
    if show_noise:
        line_noisy.set_ydata(noisy)
        line_noisy.set_visible(True)
    else:
        line_noisy.set_visible(False)


    line_filt_noisy.set_ydata(noisy)
    line_filt_noisy.set_visible(show_noise)
    line_filt.set_ydata(filtered)
    line_filt_clean.set_ydata(clean)

    for ax in (ax_orig, ax_filt):
        ax.relim()
        ax.autoscale_view()

    fig.canvas.draw_idle()


def on_harmonic_slider(val):
    """Викликається при зміні параметрів гармоніки."""
    for key in HARMONIC_KEYS:
        state[key] = sliders[key].val

    redraw()


def on_noise_slider(val):
    """Викликається при зміні параметрів шуму."""
    global noise_cache
    for key in NOISE_KEYS:
        state[key] = sliders[key].val
    noise_cache = generate_noise(state["noise_mean"], state["noise_covariance"])
    redraw()


def on_cutoff_slider(val):
    state["cutoff"] = sliders["cutoff"].val
    redraw()


def on_checkbox(label):
    global show_noise
    show_noise = not show_noise
    redraw()


def on_reset(event):
    global noise_cache
    for key, val in DEFAULTS.items():
        state[key] = val
        if key in sliders:
            sliders[key].set_val(val)
    noise_cache = generate_noise(state["noise_mean"], state["noise_covariance"])
    redraw()



for key in HARMONIC_KEYS:
    sliders[key].on_changed(on_harmonic_slider)
for key in NOISE_KEYS:
    sliders[key].on_changed(on_noise_slider)
sliders["cutoff"].on_changed(on_cutoff_slider)
chk_noise.on_clicked(on_checkbox)
btn_reset.on_clicked(on_reset)


instructions = (
    "Інструкція: "
    "Amplitude/Frequency/Phase — параметри гармоніки (шум не змінюється).  "
    "Noise Mean/Cov — параметри шуму (гармоніка не змінюється).  "
    "Cutoff Freq — гранична частота фільтра.  "
    "Show Noise — показати/сховати шум.  "
    "Reset — відновити початкові значення."
)
fig.text(0.5, 0.145, instructions, ha='center', va='top', fontsize=7.5,
         color='#444', wrap=True,
         bbox=dict(boxstyle='round,pad=0.3', facecolor='#fffbe6', edgecolor='#ccc'))

plt.show()