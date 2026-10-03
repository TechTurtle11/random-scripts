import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

import sfl


def simulate_balance(
    loan_value: float,
    income: float,
    direct_debit_monthly: float,
    threshold: float,
    annual_loan_interest_rate: float,
    income_growth_percent: float,
    threshold_change_percent: float,
    max_days: int = 365 * 30,
):
    """
    Day-by-day simulation.

    - Interest is applied daily as (annual_rate / 100) / 365 * loan
    - Monthly amounts (mandatory repayment and direct debit) are spread across average month length (365/12)
    - Annual income/threshold growth applied on April 1st each year (matches original behaviour)
    """
    dates: list[datetime.date] = []
    balances: list[float] = []

    loan = loan_value
    income_local = income
    threshold_local = threshold
    current_date = datetime.date.today()
    days = 0

    total_payed = 0.0
    payoff_date = None

    import calendar


    while loan > 0 and days < max_days:
        dates.append(current_date)
        balances.append(loan)

        # apply monthly interest on the 1st of each month
        if current_date.day == 1:
            monthly_interest = ((annual_loan_interest_rate / 100.0) / 12.0) * loan
            loan += monthly_interest
            mandatory_monthly = sfl.get_mandatory_payment(income_local, threshold_local)
            loan -= (mandatory_monthly + direct_debit_monthly)
            if loan < 0:
                # don't overpay
                total_payed += loan  # loan is negative here
                loan = 0.0
            total_payed += (mandatory_monthly + direct_debit_monthly)

        days += 1
        current_date += datetime.timedelta(days=1)

        # apply annual growth on April 1st
        if current_date.month == 4 and current_date.day == 1:
            income_local = sfl.update_annual(income_local, income_growth_percent)
            threshold_local = sfl.update_annual(threshold_local, threshold_change_percent)

        # detect payoff within loop (after interest/payments applied)
        if loan <= 0:
            payoff_date = current_date
            # append final zero balance snapshot (post-payment)
            dates.append(current_date)
            balances.append(loan)
            break

    return dates, balances, total_payed, payoff_date


class SFLGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SFL Payback Monitor")

        self._build_controls()
        self._build_plot()

    def _build_controls(self):
        frm = ttk.Frame(self)
        frm.pack(side=tk.LEFT, fill=tk.Y, padx=8, pady=8)

        # Inputs
        entries = [
            ("Loan value (£)", "loan_value", "27461.87"),
            ("Income (£/yr)", "income", "80000"),
            ("Monthly direct debit (£)", "direct_debit", "1750"),
            ("Threshold (£/yr)", "threshold", "28470"),
            ("Annual loan interest (%)", "interest", "6.2"),
            ("Income growth (%/yr)", "income_growth", "3"),
            ("Threshold change (%/yr)", "threshold_growth", "0"),
        ]

        self.vars = {}
        for idx, (label, name, default) in enumerate(entries):
            ttk.Label(frm, text=label).grid(row=idx, column=0, sticky=tk.W, pady=4)
            v = tk.StringVar(value=default)
            self.vars[name] = v
            e = ttk.Entry(frm, textvariable=v, width=20)
            e.grid(row=idx, column=1, pady=4)
            # trace changes for live update
            v.trace_add("write", lambda *a: self.on_param_change())

        # Sweep controls (direct debit optimization)
        ttk.Label(frm, text="Sweep start (£)").grid(row=len(entries)+2, column=0, sticky=tk.W, pady=4)
        self.sweep_start_var = tk.StringVar(value="0")
        ttk.Entry(frm, textvariable=self.sweep_start_var, width=20).grid(row=len(entries)+2, column=1, pady=4)

        ttk.Label(frm, text="Sweep end (£)").grid(row=len(entries)+3, column=0, sticky=tk.W, pady=4)
        self.sweep_end_var = tk.StringVar(value="2000")
        ttk.Entry(frm, textvariable=self.sweep_end_var, width=20).grid(row=len(entries)+3, column=1, pady=4)

        ttk.Label(frm, text="Steps (int)").grid(row=len(entries)+4, column=0, sticky=tk.W, pady=4)
        self.sweep_steps_var = tk.StringVar(value="20")
        ttk.Entry(frm, textvariable=self.sweep_steps_var, width=20).grid(row=len(entries)+4, column=1, pady=4)

        ttk.Button(frm, text="Sweep", command=self.on_sweep).grid(row=len(entries)+5, column=0, columnspan=2, pady=8)

        ttk.Button(frm, text="Plot", command=self.on_plot).grid(row=len(entries), column=0, columnspan=2, pady=8)
        # live-update toggle
        self.live_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm, text="Live update", variable=self.live_var).grid(row=len(entries)+2, column=0, columnspan=2, pady=2)
        ttk.Button(frm, text="Quit", command=self.destroy).grid(row=len(entries) + 1, column=0, columnspan=2, pady=2)

        # debouncer id for scheduled live updates
        self._after_id = None

        # Status area: months to payoff, payoff date, total paid
        status = ttk.Frame(self)
        status.pack(side=tk.BOTTOM, fill=tk.X, padx=8, pady=6)

        self.status_months_var = tk.StringVar(value="Months: -")
        self.status_payoff_var = tk.StringVar(value="Payoff date: -")
        self.status_total_var = tk.StringVar(value="Total paid: -")

        ttk.Label(status, textvariable=self.status_months_var).pack(side=tk.LEFT, padx=6)
        ttk.Label(status, textvariable=self.status_payoff_var).pack(side=tk.LEFT, padx=6)
        ttk.Label(status, textvariable=self.status_total_var).pack(side=tk.LEFT, padx=6)

    def _build_plot(self):
        self.fig = Figure(figsize=(7, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("Loan balance over time")
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Loan balance (£)")

        canvas = FigureCanvasTkAgg(self.fig, master=self)
        canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=1)
        self.canvas = canvas

    def on_plot(self):
        # explicit user-triggered plot; show errors if inputs invalid
        self.safe_plot(show_errors=True)

    def on_param_change(self):
        # Called via StringVar trace when inputs change. Debounce rapid edits.
        if not getattr(self, "live_var", None) or not self.live_var.get():
            return

        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        # schedule safe_plot without error dialogs (silent failures while typing)
        self._after_id = self.after(400, lambda: self.safe_plot(show_errors=False))

    def safe_plot(self, show_errors: bool = False):
        try:
            loan_value = float(self.vars["loan_value"].get())
            income = float(self.vars["income"].get())
            direct_debit = float(self.vars["direct_debit"].get())
            threshold = float(self.vars["threshold"].get())
            interest = float(self.vars["interest"].get())
            income_growth = float(self.vars["income_growth"].get())
            threshold_growth = float(self.vars["threshold_growth"].get())
        except ValueError:
            if show_errors:
                messagebox.showerror("Invalid input", "Please enter valid numeric values for all fields.")
            return

        dates, balances, total_payed, payoff_date = simulate_balance(
            loan_value,
            income,
            direct_debit,
            threshold,
            interest,
            income_growth,
            threshold_growth,
            max_days=365 * 30,
        )

        if not balances:
            if show_errors:
                messagebox.showinfo("Result", "Loan is already paid off or no simulation steps were generated.")
            return

        # x axis: dates
        self.ax.clear()
        # matplotlib can plot datetime.date objects directly
        self.ax.plot(dates, balances, marker="o")
        # format x-axis to show month and year
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        self.ax.xaxis.set_major_locator(locator)
        self.ax.xaxis.set_major_formatter(formatter)
        self.ax.set_title("Loan balance over time")
        # keep x-axis label as Date (set in _build_plot)
        self.ax.set_xlabel("Date")
        self.ax.set_ylabel("Loan balance (£)")
        self.ax.grid(True)

        # annotate payoff date (first date where balance <= 0)
        # annotate payoff date (first date where balance <= 0)
        if payoff_date is not None:
            self.ax.axvline(payoff_date, color="green", linestyle="--", label="Payoff")
            self.ax.legend()

        # update status fields (days-based)
        days_to_payoff = "N/A"
        if balances:
            idx = next((i for i, b in enumerate(balances) if b <= 0), None)
            if idx is not None:
                days_to_payoff = idx
            else:
                days_to_payoff = len(balances)

        # convert to years + months (approx)
        if isinstance(days_to_payoff, int):
            years = days_to_payoff // 365
            months_approx = (days_to_payoff % 365) // 30
            self.status_months_var.set(f"Days: {days_to_payoff} ({years}y {months_approx}m)")
        else:
            self.status_months_var.set("Days: N/A")

        self.status_payoff_var.set(f"Payoff date: {payoff_date.strftime('%Y-%m-%d') if payoff_date else 'N/A'}")
        self.status_total_var.set(f"Total paid: £{total_payed:,.2f}")

        # format x labels nicely
        self.fig.autofmt_xdate()

        self.canvas.draw()

    def on_sweep(self):
        """Run a sweep over direct debit values and plot direct_debit vs total_payed."""
        try:
            start = float(self.sweep_start_var.get())
            end = float(self.sweep_end_var.get())
            steps = int(self.sweep_steps_var.get())
            if steps < 2:
                raise ValueError("Steps must be >= 2")
        except Exception as exc:
            messagebox.showerror("Invalid sweep parameters", f"Please enter valid sweep parameters: {exc}")
            return

        # parse other simulation parameters once
        try:
            loan_value = float(self.vars["loan_value"].get())
            income = float(self.vars["income"].get())
            threshold = float(self.vars["threshold"].get())
            interest = float(self.vars["interest"].get())
            income_growth = float(self.vars["income_growth"].get())
            threshold_growth = float(self.vars["threshold_growth"].get())
        except Exception as exc:
            messagebox.showerror("Invalid parameters", f"Please ensure all simulation parameters are valid: {exc}")
            return

        # prepare sweep values
        xs = [start + i * (end - start) / (steps - 1) for i in range(steps)]
        totals = []
        payoff_dates = []

        # disable live updates while sweeping
        prev_live = self.live_var.get()
        self.live_var.set(False)
        self.status_total_var.set("Running sweep...")
        self.update()

        for dd in xs:
            # run simulation for each direct debit monthly amount
            dates, balances, total_payed, payoff_date = simulate_balance(
                loan_value, income, dd, threshold, interest, income_growth, threshold_growth, max_days=365 * 30
            )
            totals.append(total_payed)
            payoff_dates.append(payoff_date)
            # update a small progress value in status
            self.status_total_var.set(f"Sweep progress: {len(totals)}/{len(xs)}")
            self.update()

        # restore live update
        self.live_var.set(prev_live)

        # plot results: direct_debit vs total_payed
        self.ax.clear()
        self.ax.plot(xs, totals, marker="o", label="Total paid")
        self.ax.set_xlabel("Monthly direct debit (£)")
        self.ax.set_ylabel("Total paid (£)")
        self.ax.grid(True)

        # find minimum total and annotate
        min_idx = min(range(len(totals)), key=lambda i: totals[i])
        min_x = xs[min_idx]
        min_y = totals[min_idx]
        self.ax.scatter([min_x], [min_y], color="red", zorder=5)
        self.ax.annotate(f"Min: £{min_y:,.2f}\nDD: £{min_x:.2f}", xy=(min_x, min_y), xytext=(10, -30), textcoords="offset points", arrowprops=dict(arrowstyle="->"))

        self.ax.set_title("Sweep: Direct debit vs Total paid")
        self.canvas.draw()

        # update status with optimal result
        optimal_payoff = payoff_dates[min_idx]
        self.status_months_var.set(f"Optimal DD: £{min_x:.2f}")
        self.status_payoff_var.set(f"Payoff date: {optimal_payoff.strftime('%Y-%m-%d') if optimal_payoff else 'N/A'}")
        self.status_total_var.set(f"Min total paid: £{min_y:,.2f}")


if __name__ == "__main__":
    app = SFLGui()
    app.mainloop()
