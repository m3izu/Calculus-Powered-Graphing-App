import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import numpy as np
from scipy import integrate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk 

# =============================================
# Splash Screen
# =============================================
class SplashScreen(tk.Toplevel):
    def __init__(self, parent, duration=3000):
        super().__init__(parent)
        self.duration = duration
        self.overrideredirect(True)
        self.configure(bg='#2c3e50')
        self.label = ttk.Label(self, text="CS2D Function Visualizer", font=("Helvetica", 24, 'bold'), foreground='white', background='#2c3e50')
        self.label.pack(expand=True, fill='both', padx=20, pady=20)
        self.progress = ttk.Progressbar(self, mode='indeterminate')
        self.progress.pack(fill='x', padx=20, pady=(0, 20))
        self.center()
        self.after(100, self.start)

    def center(self):
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def start(self):
        self.progress.start(10)
        self.after(self.duration, self.close)

    def close(self):
        self.progress.stop()
        self.destroy()

# =============================================
# Computational methods
# =============================================
def numerical_derivative(x, y):
    return np.gradient(y, x)

def numerical_integral(x, y):
    return integrate.cumtrapz(y, x, initial=0)

# =============================================
# Main Application
# =============================================
class FunctionVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure(bg='#ecf0f1')
        self.title("Function & Derivative/Integral Visualizer")
        SplashScreen(self, duration=2000).wait_window()
        self.deiconify()
        self._create_widgets()
        self._layout_widgets()
        self._configure_grid()

    def _create_widgets(self):
        # Input Frame
        self.control_frame = ttk.Frame(self, padding=10)
        self.control_frame.configure(relief='raised')
        ttk.Label(self.control_frame, text="f(x) =", font=('Arial', 12)).grid(row=0, column=0, sticky="W")
        self.func_entry = ttk.Entry(self.control_frame, width=30)
        self.func_entry.insert(0, "np.sin(x)")
        self.x_start = ttk.Entry(self.control_frame, width=10)
        self.x_start.insert(0, "0")
        self.x_end = ttk.Entry(self.control_frame, width=10)
        self.x_end.insert(0, "2*np.pi")
        self.num_points = ttk.Entry(self.control_frame, width=10)
        self.num_points.insert(0, "500")
        
        # Buttons
        self.plot_btn = ttk.Button(self.control_frame, text="Plot", command=self._on_plot)
        self.export_btn = ttk.Button(self.control_frame, text="Export PNG", command=self._export_png)

        try:
            image = Image.open("logo.png")
            image = image.resize((300, 400))  # Adjust size as needed
            self.logo_image = ImageTk.PhotoImage(image)
            self.logo_label = ttk.Label(self.control_frame, image=self.logo_image)
        except FileNotFoundError:
            self.logo_label = ttk.Label(self.control_frame, text="Logo not found")

        # Matplotlib Figure
        self.fig = plt.Figure(figsize=(6, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        
    def _layout_widgets(self):
        # Controls
        self.control_frame.grid(row=0, column=0, sticky='NSEW', padx=10, pady=10)
        # Input layout
        labels = ['f(x) =', 'x start:', 'x end:', 'Points:']
        entries = [self.func_entry, self.x_start, self.x_end, self.num_points]
        for i, (lbl, entry) in enumerate(zip(labels, entries)):
            ttk.Label(self.control_frame, text=lbl).grid(row=i, column=0, pady=5, sticky='W')
            entry.grid(row=i, column=1, pady=5, sticky='EW')
        # Buttons
        self.plot_btn.grid(row=4, column=0, columnspan=2, pady=(10, 5), sticky='EW')
        self.export_btn.grid(row=5, column=0, columnspan=2, pady=(5, 10), sticky='EW')
        self.logo_label.grid(row=6, column=0, columnspan=2, pady=10)
        # Canvas
        self.canvas.get_tk_widget().grid(row=0, column=1, rowspan=6, sticky='NSEW', padx=(0,10), pady=10)

    def _configure_grid(self):
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.control_frame.columnconfigure(1, weight=1)

    def _on_plot(self):
        # Run computation in thread to keep UI responsive
        threading.Thread(target=self._compute_and_plot, daemon=True).start()

    def _compute_and_plot(self):
        try:
            func_str = self.func_entry.get()
            x0 = float(eval(self.x_start.get(), {"np": np}))
            x1 = float(eval(self.x_end.get(), {"np": np}))
            n = int(self.num_points.get())
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            return
        x = np.linspace(x0, x1, n)
        try:
            y = eval(func_str, {"np": np, "x": x})
        except Exception as e:
            messagebox.showerror("Function Error", f"Could not evaluate f(x): {e}")
            return
        dydx = numerical_derivative(x, y)
        integral = numerical_integral(x, y)
        # Plot
        self.fig.clf()
        axs = self.fig.subplots(3,1, sharex=True)
        axs[0].plot(x, y, label="f(x)"); axs[0].set_ylabel("f(x)"); axs[0].legend(); axs[0].grid(True)
        axs[1].plot(x, dydx, label="f'(x)"); axs[1].set_ylabel("f'(x)"); axs[1].legend(); axs[1].grid(True)
        axs[2].plot(x, integral, label="∫f(x)dx"); axs[2].set_xlabel("x"); axs[2].set_ylabel("Integral"); axs[2].legend(); axs[2].grid(True)
        self.canvas.draw()

    def _export_png(self):
        file_path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG files','*.png')])
        if file_path:
            try:
                self.fig.savefig(file_path)
                messagebox.showinfo("Export Successful", f"Figure saved as {file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not save figure: {e}")

if __name__ == "__main__":
    app = FunctionVisualizer()
    app.mainloop()