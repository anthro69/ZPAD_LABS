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


class HarmonicApp:
    """Інтерактивний застосунок: гармоніка з шумом та фільтрацією."""

    def __init__(self):
        self.state = {**DEFAULTS}
        self.show_noise = True

        # Генеруємо базовий стандартний нормальний шум один раз.
        # При зміні mean/variance просто масштабуємо його: noise = mean + std * base_noise
        self._base_noise = np.random.standard_normal(T.shape)

        self._build_figure()
        self._connect_widgets()
        self._redraw()

    def _get_noise(self):
        """Повертає шум з поточними mean та std без перегенерації."""
        mean = self.state["noise_mean"]
        std  = np.sqrt(self.state["noise_covariance"])
        return mean + std * self._base_noise

    def _harmonic(self):
        a, f, p = self.state["amplitude"], self.state["frequency"], self.state["phase"]
        return a * np.sin(2 * np.pi * f * T + p)

    def _lowpass_filter(self, signal):
        cutoff = self.state["cutoff"]
        fs     = 1.0 / (T[1] - T[0])
        nyq    = 0.5 * fs
        normal_cutoff = min(cutoff / nyq, 0.99)
        b, a = butter(4, normal_cutoff, btype='low', analog=False)
        return filtfilt(b, a, signal)


    def _build_figure(self):
        self.fig = plt.figure(figsize=(12, 9))
        self.fig.suptitle("Гармоніка з шумом та фільтрацією", fontsize=13, fontweight='bold')

        self.ax_orig = self.fig.add_axes([0.07, 0.55, 0.88, 0.35])
        self.ax_filt = self.fig.add_axes([0.07, 0.16, 0.88, 0.35])

        self.ax_orig.set_title("Оригінальна гармоніка")
        self.ax_filt.set_title("Відфільтрована гармоніка (Butterworth low-pass)")
        for ax in (self.ax_orig, self.ax_filt):
            ax.set_xlabel("t")
            ax.set_ylabel("y(t)")
            ax.grid(True, alpha=0.3)

        dummy = np.zeros_like(T)
        self.line_clean,      = self.ax_orig.plot(T, dummy, color='royalblue',  lw=2,   label='Чиста гармоніка', zorder=3)
        self.line_noisy,      = self.ax_orig.plot(T, dummy, color='darkorange', lw=0.8, alpha=0.85, label='З шумом')
        self.line_filt_noisy, = self.ax_filt.plot(T, dummy, color='darkorange', lw=0.8, alpha=0.5,  label='З шумом')
        self.line_filt,       = self.ax_filt.plot(T, dummy, color='crimson',    lw=2,   label='Відфільтрована')
        self.line_filt_clean, = self.ax_filt.plot(T, dummy, color='royalblue',  lw=1.5, ls='--', label='Чиста (ідеал)', zorder=3)

        self.ax_orig.legend(loc='upper right', fontsize=8)
        self.ax_filt.legend(loc='upper right', fontsize=8)

        # --- Слайдери ---
        slider_specs = [
            ("Amplitude",   0.15, 0.108, 0.1,     3.0,      "amplitude"),
            ("Frequency",   0.15, 0.088, 0.1,     5.0,      "frequency"),
            ("Phase",       0.15, 0.068, -np.pi,  np.pi,    "phase"),
            ("Noise Mean",  0.15, 0.048, -1.0,    1.0,      "noise_mean"),
            ("Noise Cov",   0.15, 0.028,  0.0,    1.0,      "noise_covariance"),
            ("Cutoff Freq", 0.15, 0.008,  0.5,   20.0,      "cutoff"),
        ]
        self.sliders = {}
        for label, x, y, vmin, vmax, key in slider_specs:
            ax_s = self.fig.add_axes([x, y, 0.55, 0.015])
            sl = Slider(ax_s, label, vmin, vmax, valinit=DEFAULTS[key], color='steelblue')
            sl.label.set_fontsize(8)
            sl.valtext.set_fontsize(8)
            self.sliders[key] = sl

        # --- Checkbox ---
        ax_chk = self.fig.add_axes([0.76, 0.005, 0.12, 0.04])
        self.chk_noise = CheckButtons(ax_chk, ["Show Noise"], [True])
        self.chk_noise.labels[0].set_fontsize(8)

        # --- Reset ---
        ax_btn = self.fig.add_axes([0.07, 0.005, 0.07, 0.04])
        self.btn_reset = Button(ax_btn, "Reset", color='#f0f0f0', hovercolor='#d0e8ff')
        self.btn_reset.label.set_fontsize(8)

        # --- Інструкція ---
        instructions = (
            "Інструкція: "
            "Amplitude/Frequency/Phase — параметри гармоніки (шум не змінюється).  "
            "Noise Mean/Cov — параметри шуму (гармоніка не змінюється).  "
            "Cutoff Freq — гранична частота фільтра.  "
            "Show Noise — показати/сховати шум.  "
            "Reset — відновити початкові значення."
        )
        self.fig.text(0.5, 0.145, instructions, ha='center', va='top', fontsize=7.5,
                      color='#444', wrap=True,
                      bbox=dict(boxstyle='round,pad=0.3', facecolor='#fffbe6', edgecolor='#ccc'))

   

    def _connect_widgets(self):
        harmonic_keys = {"amplitude", "frequency", "phase"}
        noise_keys    = {"noise_mean", "noise_covariance"}

        for key in harmonic_keys:
            self.sliders[key].on_changed(self._on_harmonic_slider)
        for key in noise_keys:
            self.sliders[key].on_changed(self._on_noise_slider)
        self.sliders["cutoff"].on_changed(self._on_cutoff_slider)
        self.chk_noise.on_clicked(self._on_checkbox)
        self.btn_reset.on_clicked(self._on_reset)



    def _on_harmonic_slider(self, _val):
        for key in ("amplitude", "frequency", "phase"):
            self.state[key] = self.sliders[key].val
        self._redraw()

    def _on_noise_slider(self, _val):
        for key in ("noise_mean", "noise_covariance"):
            self.state[key] = self.sliders[key].val
        # Шум не перегенеровується — лише змінюється масштаб base_noise
        self._redraw()

    def _on_cutoff_slider(self, _val):
        self.state["cutoff"] = self.sliders["cutoff"].val
        self._redraw()

    def _on_checkbox(self, _label):
        self.show_noise = not self.show_noise
        self._redraw()

    def _on_reset(self, _event):
        for key, val in DEFAULTS.items():
            self.state[key] = val
            if key in self.sliders:
                self.sliders[key].set_val(val)
        self._base_noise = np.random.standard_normal(T.shape)
        self._redraw()


    def _redraw(self):
        clean    = self._harmonic()
        noise    = self._get_noise()
        noisy    = clean + noise
        filtered = self._lowpass_filter(noisy)

        self.line_clean.set_ydata(clean)
        self.line_noisy.set_ydata(noisy)
        self.line_noisy.set_visible(self.show_noise)

        self.line_filt_noisy.set_ydata(noisy)
        self.line_filt_noisy.set_visible(self.show_noise)
        self.line_filt.set_ydata(filtered)
        self.line_filt_clean.set_ydata(clean)

        for ax in (self.ax_orig, self.ax_filt):
            ax.relim()
            ax.autoscale_view()

        self.fig.canvas.draw_idle()

    def run(self):
        plt.show()


if __name__ == "__main__":
    app = HarmonicApp()
    app.run()