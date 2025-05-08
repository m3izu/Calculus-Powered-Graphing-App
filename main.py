import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from scipy import integrate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# =============================================
# Computational methods
# =============================================
def numerical_derivative(x, y):
    """Numerical derivative via central differences."""
    return np.gradient(y, x)

def numerical_integral(x, y):
    """Cumulative integral via trapezoidal rule."""
    return integrate.cumtrapz(y, x, initial=0)

# =============================================
# GUI Application
# =============================================
class FunctionVisualizer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Function & Derivative/Integral Visualizer")
        self._create_widgets()

    def _create_widgets(self):
        frame = ttk.Frame(self, padding=10)
        frame.grid(row=0, column=0, sticky="NSEW")

        ttk.Label(frame, text="Final PIT by Aldwyn Betonio,", font=("Arial", 16)).grid(row=0, column=0, columnspan=2, pady=10)
        ttk.Label(frame, text="Franco Galendez, Rafi Panandigan", font=("Arial", 16)).grid(row=1, column=0, columnspan=2, pady=10)

        # Function input
        ttk.Label(frame, text="f(x) =").grid(row=2, column=0, sticky="W")
        self.func_entry = ttk.Entry(frame, width=30)
        self.func_entry.insert(0, "np.sin(x)")
        self.func_entry.grid(row=2, column=1, pady=5, sticky="EW")

        # Domain inputs
        ttk.Label(frame, text="x start:").grid(row=3, column=0, sticky="W")
        self.x_start = ttk.Entry(frame, width=10)
        self.x_start.insert(0, "0")
        self.x_start.grid(row=3, column=1, sticky="W")

        ttk.Label(frame, text="x end:").grid(row=4, column=0, sticky="W")
        self.x_end = ttk.Entry(frame, width=10)
        self.x_end.insert(0, "2*np.pi")
        self.x_end.grid(row=4, column=1, sticky="W")

        ttk.Label(frame, text="Points:").grid(row=5, column=0, sticky="W")
        self.num_points = ttk.Entry(frame, width=10)
        self.num_points.insert(0, "500")
        self.num_points.grid(row=5, column=1, sticky="W")

        # Plot button
        plot_btn = ttk.Button(frame, text="Plot", command=self._on_plot)
        plot_btn.grid(row=5, column=0, columnspan=2, pady=10)

        # Matplotlib figure setup
        self.fig = plt.Figure(figsize=(6, 8))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0, column=1)

        # Configure resizing
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def _on_plot(self):
        # Fetch and validate inputs
        try:
            func_str = self.func_entry.get()
            x0 = float(eval(self.x_start.get(), {"np": np}))
            x1 = float(eval(self.x_end.get(), {"np": np}))
            n = int(self.num_points.get())
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            return

        # Generate x and compute y
        x = np.linspace(x0, x1, n)
        try:
            # Safe eval context
            y = eval(func_str, {"np": np, "x": x})
        except Exception as e:
            messagebox.showerror("Function Error", f"Could not evaluate f(x): {e}")
            return

        # Compute derivative and integral
        dydx = numerical_derivative(x, y)
        integral = numerical_integral(x, y)

        # Clear previous plots and create new subplots
        self.fig.clf()
        axs = self.fig.subplots(3, 1, sharex=True)

        axs[0].plot(x, y, label="f(x)")
        axs[0].set_ylabel("f(x)")
        axs[0].legend(); axs[0].grid(True)

        axs[1].plot(x, dydx, label="f'(x)")
        axs[1].set_ylabel("f'(x)")
        axs[1].legend(); axs[1].grid(True)

        axs[2].plot(x, integral, label="∫f(x)dx")
        axs[2].set_xlabel("x")
        axs[2].set_ylabel("Integral")
        axs[2].legend(); axs[2].grid(True)

        self.canvas.draw()

if __name__ == "__main__":
    app = FunctionVisualizer()
    app.mainloop()
