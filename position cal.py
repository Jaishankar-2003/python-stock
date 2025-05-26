import tkinter as tk
from tkinter import messagebox, ttk
from math import floor
import webbrowser


class SwingTradeCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced Swing Trade Position & Risk Manager")
        self.root.geometry("1920x1050")
        self.root.configure(bg="#f2f4f8")

        # Style configuration
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f2f4f8")
        self.style.configure("TLabel", background="#f2f4f8", font=("Segoe UI", 10, "bold"))
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=5)
        self.style.configure("Red.TLabel", foreground="red", background="#f2f4f8")
        self.style.configure("Green.TLabel", foreground="green", background="#f2f4f8")
        self.style.configure("Yellow.TLabel", foreground="#b8860b", background="#f2f4f8")

        # Fonts
        self.LABEL_FONT = ("Segoe UI", 10, "bold")
        self.ENTRY_FONT = ("Segoe UI", 10)
        self.BUTTON_FONT = ("Segoe UI", 10, "bold")
        self.HEADER_FONT = ("Segoe UI", 12, "bold")

        # Initialize variables
        self.consecutive_losses = 0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.max_drawdown = 0
        self.current_drawdown = 0
        self.equity_curve = []

        self.create_widgets()
        self.setup_tabs()

    def create_widgets(self):
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True)

    def setup_tabs(self):
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True)

        # Create tabs
        self.calculator_tab = ttk.Frame(self.notebook)
        self.psychology_tab = ttk.Frame(self.notebook)
        self.journal_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.calculator_tab, text="Position Calculator")
        self.notebook.add(self.psychology_tab, text="Trading Psychology")
        self.notebook.add(self.journal_tab, text="Trade Journal")
        self.notebook.add(self.stats_tab, text="Performance Stats")

        self.setup_calculator_tab()
        self.setup_psychology_tab()
        self.setup_journal_tab()
        self.setup_stats_tab()

    def setup_calculator_tab(self):
        # === LEFT SCROLLABLE FRAME ===
        left_container = ttk.Frame(self.calculator_tab)
        left_container.pack(side="left", fill="y")

        left_canvas = tk.Canvas(left_container, bg="#f2f4f8", width=400, highlightthickness=0)
        left_canvas.pack(side="left", fill="y", expand=False)

        left_scrollbar = ttk.Scrollbar(left_container, orient="vertical", command=left_canvas.yview)
        left_scrollbar.pack(side="left", fill="y")

        left_canvas.configure(yscrollcommand=left_scrollbar.set)

        left_frame = ttk.Frame(left_canvas)
        left_canvas.create_window((0, 0), window=left_frame, anchor="nw")

        def on_left_frame_configure(event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))

        left_frame.bind("<Configure>", on_left_frame_configure)

        # === RIGHT SCROLLABLE FRAME ===
        right_container = ttk.Frame(self.calculator_tab)
        right_container.pack(side="left", fill="both", expand=True)

        right_canvas = tk.Canvas(right_container, bg="#f2f4f8", highlightthickness=0)
        right_canvas.pack(side="left", fill="both", expand=True)

        right_scrollbar = ttk.Scrollbar(right_container, orient="vertical", command=right_canvas.yview)
        right_scrollbar.pack(side="left", fill="y")

        right_canvas.configure(yscrollcommand=right_scrollbar.set)

        right_frame = ttk.Frame(right_canvas)
        right_canvas.create_window((0, 0), window=right_frame, anchor="nw")

        def on_right_frame_configure(event):
            right_canvas.configure(scrollregion=right_canvas.bbox("all"))

        right_frame.bind("<Configure>", on_right_frame_configure)

        # Input fields
        self.inputs = {
            "Entry Price (₹)": tk.StringVar(),
            "Stop Loss Price (₹) [optional if % given]": tk.StringVar(),
            "Stop Loss % below Entry [optional if price given]": tk.StringVar(),
            "Target Price (₹) [optional if % given]": tk.StringVar(),
            "Target % above Entry [optional if price given]": tk.StringVar(),
            "Capital (₹) [optional]": tk.StringVar(value="500000"),
            "Risk % of Capital [optional]": tk.StringVar(value="0.5"),
            "ATR Value (₹) [Optional]": tk.StringVar(),
            "Manual Position Size (shares) [optional]": tk.StringVar(),
            "Max Trade Exposure % (Default 20%)": tk.StringVar(value="20"),
            "Max Sector Exposure % (Default 30%)": tk.StringVar(value="30"),
            "Consecutive Losses": tk.StringVar(value=str(self.consecutive_losses)),
            "Current Drawdown %": tk.StringVar(value="0"),
        }

        for label_text, var in self.inputs.items():
            ttk.Label(left_frame, text=label_text).pack(anchor='w', pady=(8, 2))
            tk.Entry(left_frame, textvariable=var, font=self.ENTRY_FONT, width=30).pack(anchor='w')

        # Risk management tips
        tips_frame = ttk.LabelFrame(left_frame, text="Risk Management Tips", padding=10)
        tips_frame.pack(fill="x", pady=20)

        tips = [
            "• Never risk >1% of capital per trade",
            "• Keep sector exposure <30%",
            "• Maintain RRR ≥ 2:1",
            "• Reduce size during drawdowns",
            "• Use ATR for dynamic stops"
        ]

        for tip in tips:
            ttk.Label(tips_frame, text=tip).pack(anchor='w')

        # Calculate button
        ttk.Button(left_frame, text="Calculate Position & Risk",
                   command=self.calculate, style="TButton").pack(pady=20)

        # Result box
        self.result_box = tk.Text(right_frame, height=30, width=100, font=("Consolas", 11),
                                  wrap="word", bd=2, relief="sunken")
        self.result_box.pack(fill="both", expand=True, pady=10)

        # Configure text tags for styling
        self.result_box.tag_config("header", foreground="#007acc", font=("Segoe UI", 12, "bold"))
        self.result_box.tag_config("subheader", font=("Segoe UI", 10, "bold"))
        self.result_box.tag_config("warning", foreground="red")
        self.result_box.tag_config("success", foreground="green")

        # Trade action buttons
        btn_frame = ttk.Frame(right_frame)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Record Win", command=lambda: self.record_trade_outcome(True)).pack(side="left",
                                                                                                       padx=5)
        ttk.Button(btn_frame, text="Record Loss", command=lambda: self.record_trade_outcome(False)).pack(side="left",
                                                                                                         padx=5)
        ttk.Button(btn_frame, text="Reset Stats", command=self.reset_stats).pack(side="left", padx=5)

    def setup_psychology_tab(self):
        # Psychology tips and exercises
        main_frame = ttk.Frame(self.psychology_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Emotional state assessment
        state_frame = ttk.LabelFrame(main_frame, text="Current Emotional State", padding=10)
        state_frame.pack(fill="x", pady=10)

        self.emotional_state = tk.StringVar(value="Neutral")
        states = ["Confident", "Neutral", "Anxious", "Fearful", "Greedy", "Reckless"]

        for state in states:
            ttk.Radiobutton(state_frame, text=state, variable=self.emotional_state,
                            value=state).pack(anchor='w', padx=5)

        # Psychology tips
        tips_frame = ttk.LabelFrame(main_frame, text="Psychology Tips", padding=10)
        tips_frame.pack(fill="both", expand=True, pady=10)

        psychology_tips = [
            "✅ Stick to your trading plan no matter what",
            "✅ Take breaks after consecutive losses",
            "✅ Journal every trade to identify emotional patterns",
            "✅ Practice meditation to improve discipline",
            "✅ Set realistic expectations - trading is a marathon",
            "✅ Avoid revenge trading after losses",
            "✅ Celebrate process over outcomes",
            "✅ Visualize successful trades before executing"
        ]

        for tip in psychology_tips:
            ttk.Label(tips_frame, text=tip).pack(anchor='w', pady=2)

        # Breathing exercise
        breath_frame = ttk.LabelFrame(main_frame, text="Calming Exercise (4-7-8 Breathing)", padding=10)
        breath_frame.pack(fill="x", pady=10)

        ttk.Label(breath_frame, text="1. Inhale deeply for 4 seconds").pack(anchor='w')
        ttk.Label(breath_frame, text="2. Hold breath for 7 seconds").pack(anchor='w')
        ttk.Label(breath_frame, text="3. Exhale completely for 8 seconds").pack(anchor='w')
        ttk.Label(breath_frame, text="Repeat 4 times before trading").pack(anchor='w')

        ttk.Button(breath_frame, text="Start 5-Minute Meditation Timer",
                   command=self.start_meditation_timer).pack(pady=5)

    def setup_journal_tab(self):
        # Trade journal section
        main_frame = ttk.Frame(self.journal_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Journal entry fields
        ttk.Label(main_frame, text="Trade Notes:", font=self.HEADER_FONT).pack(anchor='w')

        self.trade_notes = tk.Text(main_frame, height=10, width=80, wrap="word", font=self.ENTRY_FONT)
        self.trade_notes.pack(fill="x", pady=5)

        # Lessons learned
        ttk.Label(main_frame, text="Lessons Learned:", font=self.HEADER_FONT).pack(anchor='w', pady=(10, 0))

        self.lessons_learned = tk.Text(main_frame, height=5, width=80, wrap="word", font=self.ENTRY_FONT)
        self.lessons_learned.pack(fill="x", pady=5)

        # Emotional state during trade
        ttk.Label(main_frame, text="Emotional State During Trade:", font=self.HEADER_FONT).pack(anchor='w',
                                                                                                pady=(10, 0))

        self.trade_emotion = tk.StringVar()
        emotions = ["Confident", "Anxious", "Fearful", "Greedy", "Patient", "Impulsive", "Disciplined"]

        for emotion in emotions:
            ttk.Radiobutton(main_frame, text=emotion, variable=self.trade_emotion,
                            value=emotion).pack(anchor='w', padx=5)

        # Save journal button
        ttk.Button(main_frame, text="Save Journal Entry", command=self.save_journal_entry).pack(pady=10)

        # Previous entries
        ttk.Label(main_frame, text="Previous Entries:", font=self.HEADER_FONT).pack(anchor='w', pady=(10, 0))

        self.journal_display = tk.Text(main_frame, height=15, width=80, wrap="word",
                                       font=("Consolas", 10), state="disabled")
        self.journal_display.pack(fill="both", expand=True, pady=5)

    def setup_stats_tab(self):
        # Performance statistics
        main_frame = ttk.Frame(self.stats_tab)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Stats display
        self.stats_text = tk.Text(main_frame, height=20, width=80, wrap="word",
                                  font=("Consolas", 11), state="disabled")
        self.stats_text.pack(fill="both", expand=True)

        # Update stats display
        self.update_stats_display()

        # Resources section
        resources_frame = ttk.LabelFrame(main_frame, text="Trading Psychology Resources", padding=10)
        resources_frame.pack(fill="x", pady=10)

        resources = [
            ("Trading in the Zone - Mark Douglas",
             "https://www.amazon.com/Trading-Zone-Confidence-Discipline-Attitude/dp/0735201447"),
            ("The Daily Trading Coach - Brett Steenbarger",
             "https://www.amazon.com/Daily-Trading-Coach-Lessons-Developing/dp/0470443460"),
            ("Market Wizards - Jack Schwager",
             "https://www.amazon.com/Market-Wizards-Updated-Interviews-Traders/dp/1118273052"),
            ("Mind Over Markets - James Dalton",
             "https://www.amazon.com/Mind-Over-Markets-Updated-Auction/dp/1118809238")
        ]

        for text, url in resources:
            link = ttk.Label(resources_frame, text=text, cursor="hand2", foreground="blue")
            link.pack(anchor='w', pady=2)
            link.bind("<Button-1>", lambda e, u=url: webbrowser.open_new(u))

    def calculate(self):
        try:
            # Get input values
            entry_price = self.get_float("Entry Price (₹)", mandatory=True)

            # Stop Loss calculation
            sl_price = self.get_float("Stop Loss Price (₹) [optional if % given]", mandatory=False)
            sl_percent = self.get_float("Stop Loss % below Entry [optional if price given]", mandatory=False)

            if sl_price is None and sl_percent is None:
                raise ValueError("Please provide either Stop Loss Price or Stop Loss % below Entry.")
            elif sl_price is None and sl_percent is not None:
                sl_price = round(entry_price * (1 - sl_percent / 100), 2)
            elif sl_price is not None and sl_percent is not None:
                # Both given, prefer price but warn if inconsistent
                calculated_sl_percent = (entry_price - sl_price) / entry_price * 100
                if abs(calculated_sl_percent - sl_percent) > 0.5:  # More than 0.5% difference
                    messagebox.showwarning("Inconsistent Input",
                                           f"Stop Loss price ({sl_price}) and percentage ({sl_percent}%) don't match.\n"
                                           f"Using price value ({sl_price}). Calculated percentage is {calculated_sl_percent:.2f}%")

            # Target calculation
            target_price = self.get_float("Target Price (₹) [optional if % given]", mandatory=False)
            target_percent = self.get_float("Target % above Entry [optional if price given]", mandatory=False)

            if target_price is None and target_percent is None:
                raise ValueError("Please provide either Target Price or Target % above Entry.")
            elif target_price is None and target_percent is not None:
                target_price = round(entry_price * (1 + target_percent / 100), 2)
            elif target_price is not None and target_percent is not None:
                # Both given, prefer price but warn if inconsistent
                calculated_target_percent = (target_price - entry_price) / entry_price * 100
                if abs(calculated_target_percent - target_percent) > 0.5:  # More than 0.5% difference
                    messagebox.showwarning("Inconsistent Input",
                                           f"Target price ({target_price}) and percentage ({target_percent}%) don't match.\n"
                                           f"Using price value ({target_price}). Calculated percentage is {calculated_target_percent:.2f}%")

            # Other parameters
            capital = self.get_float("Capital (₹) [optional]", mandatory=False, default=500000)
            risk_percent = self.get_float("Risk % of Capital [optional]", mandatory=False, default=0.5)
            atr_value = self.get_float("ATR Value (₹) [Optional]", mandatory=False)
            manual_position_size = self.get_int("Manual Position Size (shares) [optional]", mandatory=False)
            max_trade_exp_pct = self.get_float("Max Trade Exposure % (Default 20%)", mandatory=False, default=20)
            max_sector_exp_pct = self.get_float("Max Sector Exposure % (Default 30%)", mandatory=False, default=30)
            consecutive_losses = self.get_int("Consecutive Losses", mandatory=False, default=self.consecutive_losses)
            current_drawdown = self.get_float("Current Drawdown %", mandatory=False, default=0)

            # Risk per share validation
            risk_per_share = entry_price - sl_price
            if risk_per_share <= 0:
                raise ValueError("Stop Loss must be less than Entry Price for valid risk calculation.")

            # Reward to risk ratio
            reward_risk_ratio = (target_price - entry_price) / risk_per_share

            # Dynamic risk adjustment based on drawdown
            risk_adjustment_factor = 1.0
            if current_drawdown > 5:  # Reduce risk if in drawdown
                risk_adjustment_factor = max(0.5, 1 - (current_drawdown / 20))  # Reduce by up to 50%
                risk_percent *= risk_adjustment_factor
                messagebox.showinfo("Risk Adjusted",
                                    f"Reduced risk to {risk_percent:.2f}% due to {current_drawdown:.1f}% drawdown")

            # Capital risk limit
            capital_risk_limit = capital * (risk_percent / 100)

            # Position size calculation
            if manual_position_size is not None and manual_position_size > 0:
                position_size = manual_position_size
                manual_override = True
            else:
                position_size = floor(capital_risk_limit / risk_per_share)
                manual_override = False

            estimated_investment = position_size * entry_price
            exposure_pct = (estimated_investment / capital) * 100

            # Further reduce position if exceeding max exposure
            if exposure_pct > max_trade_exp_pct:
                max_allowed_size = floor((capital * max_trade_exp_pct / 100) / entry_price)
                position_size = min(position_size, max_allowed_size)
                estimated_investment = position_size * entry_price
                exposure_pct = (estimated_investment / capital) * 100
                messagebox.showwarning("Exposure Limit",
                                       f"Position reduced to {position_size} shares to stay within {max_trade_exp_pct}% exposure")

            # Calculate potential outcomes
            net_potential_profit = (target_price - entry_price) * position_size
            net_potential_loss = (sl_price - entry_price) * position_size

            # Emotional impact assessment
            emotional_impact = "Moderate"
            if abs(net_potential_loss) > capital * 0.02:  # More than 2% of capital at risk
                emotional_impact = "High"
            elif abs(net_potential_loss) < capital * 0.005:  # Less than 0.5% of capital at risk
                emotional_impact = "Low"

            # Prepare results
            self.result_box.delete("1.0", tk.END)

            # Header
            self.result_box.insert(tk.END, "🧮 ADVANCED POSITION & RISK ANALYSIS\n\n", "header")

            # Trade details
            self.result_box.insert(tk.END, "📊 Trade Parameters:\n", "subheader")
            self.result_box.insert(tk.END, f"• Entry Price: ₹{entry_price:.2f}\n")
            self.result_box.insert(tk.END,
                                   f"• Stop Loss: ₹{sl_price:.2f} ({((entry_price - sl_price) / entry_price * 100):.2f}% below entry)\n")
            self.result_box.insert(tk.END,
                                   f"• Target: ₹{target_price:.2f} ({((target_price - entry_price) / entry_price * 100):.2f}% above entry)\n")
            self.result_box.insert(tk.END, f"• Risk per Share: ₹{risk_per_share:.2f}\n")
            self.result_box.insert(tk.END, f"• Reward/Risk Ratio: {reward_risk_ratio:.2f}:1\n")

            if atr_value:
                atr_ratio = risk_per_share / atr_value
                self.result_box.insert(tk.END, f"• ATR Ratio (Risk/ATR): {atr_ratio:.2f}\n")

            # Position sizing
            self.result_box.insert(tk.END, "\n📈 Position Sizing:\n", "subheader")
            self.result_box.insert(tk.END, f"• Capital: ₹{capital:,.0f}\n")
            self.result_box.insert(tk.END, f"• Risk % of Capital: {risk_percent:.2f}%")
            if risk_adjustment_factor < 1.0:
                self.result_box.insert(tk.END, f" (Adjusted for drawdown)", "warning")
            self.result_box.insert(tk.END, "\n")

            self.result_box.insert(tk.END, f"• Capital Risk Limit: ₹{capital_risk_limit:,.2f}\n")

            if manual_override:
                self.result_box.insert(tk.END, f"• Manual Position Size: {position_size:,} shares\n", "warning")
            else:
                self.result_box.insert(tk.END, f"• Calculated Position Size: {position_size:,} shares\n")

            self.result_box.insert(tk.END, f"• Estimated Investment: ₹{estimated_investment:,.2f}\n")
            self.result_box.insert(tk.END, f"• Exposure %: {exposure_pct:.2f}% of capital")

            if exposure_pct > max_trade_exp_pct:
                self.result_box.insert(tk.END, " (OVER LIMIT)", "warning")
            self.result_box.insert(tk.END, "\n")

            # Risk assessment
            self.result_box.insert(tk.END, "\n⚠️ Risk Assessment:\n", "subheader")
            self.result_box.insert(tk.END, f"• Potential Profit: ₹{net_potential_profit:,.2f}\n")
            self.result_box.insert(tk.END, f"• Potential Loss: ₹{net_potential_loss:,.2f}\n")
            self.result_box.insert(tk.END, f"• Emotional Impact: {emotional_impact}\n")
            self.result_box.insert(tk.END, f"• Consecutive Losses: {consecutive_losses}\n")
            self.result_box.insert(tk.END, f"• Current Drawdown: {current_drawdown:.1f}%\n")

            # Trade management
            self.result_box.insert(tk.END, "\n🎯 Trade Management:\n", "subheader")
            trail_sl_price = round(entry_price + (risk_per_share * 1.5), 2)
            partial_booking_price = round(entry_price + ((target_price - entry_price) * 0.5), 2)

            self.result_box.insert(tk.END, f"• Trail Stop Price (1.5R): ₹{trail_sl_price:.2f}\n")
            self.result_box.insert(tk.END, f"• Partial Booking Price (50% target): ₹{partial_booking_price:.2f}\n")

            # Psychology tips based on emotional state
            current_emotion = self.emotional_state.get()
            self.result_box.insert(tk.END, f"\n🧠 Psychology Check ({current_emotion}):\n", "subheader")

            if current_emotion in ["Anxious", "Fearful"]:
                self.result_box.insert(tk.END, "• Consider reducing position size by 50%\n", "warning")
                self.result_box.insert(tk.END, "• Review trade rationale before proceeding\n")
                self.result_box.insert(tk.END, "• Practice 4-7-8 breathing exercise\n")
            elif current_emotion in ["Greedy", "Reckless"]:
                self.result_box.insert(tk.END, "• Consider waiting 30 minutes before trading\n", "warning")
                self.result_box.insert(tk.END, "• Review your trading plan\n")
                self.result_box.insert(tk.END, "• Remember: Discipline > Opportunity\n")
            else:
                self.result_box.insert(tk.END, "• Emotional state appears balanced\n")
                self.result_box.insert(tk.END, "• Still recommend reviewing trade plan\n")

        except Exception as e:
            messagebox.showerror("Input Error", str(e))
            self.result_box.delete("1.0", tk.END)

    def record_trade_outcome(self, is_win):
        # Update trade statistics
        self.total_trades += 1

        if is_win:
            self.winning_trades += 1
            self.consecutive_losses = 0
            messagebox.showinfo("Trade Recorded", "Win recorded successfully!")
        else:
            self.losing_trades += 1
            self.consecutive_losses += 1
            messagebox.showinfo("Trade Recorded", "Loss recorded. Review your journal for lessons.")

        # Update the consecutive losses field
        self.inputs["Consecutive Losses"].set(str(self.consecutive_losses))

        # Update drawdown calculation
        if not is_win and self.consecutive_losses > 1:
            self.current_drawdown += 1  # Simplified for demo - would use actual P&L in real app
            self.inputs["Current Drawdown %"].set(f"{self.current_drawdown:.1f}")

        # Update stats display
        self.update_stats_display()

        # Prompt to journal the trade
        if messagebox.askyesno("Journal Entry", "Would you like to journal this trade now?"):
            self.notebook.select(self.journal_tab)

    def reset_stats(self):
        # Reset all performance statistics
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all performance statistics?"):
            self.consecutive_losses = 0
            self.total_trades = 0
            self.winning_trades = 0
            self.losing_trades = 0
            self.max_drawdown = 0
            self.current_drawdown = 0
            self.equity_curve = []

            self.inputs["Consecutive Losses"].set("0")
            self.inputs["Current Drawdown %"].set("0")

            self.update_stats_display()
            messagebox.showinfo("Stats Reset", "All performance statistics have been reset.")

    def update_stats_display(self):
        # Calculate performance metrics
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        avg_win = 1.5  # Placeholder - would use real data
        avg_loss = 1.0  # Placeholder
        expectancy = (win_rate / 100 * avg_win) - ((100 - win_rate) / 100 * avg_loss) if self.total_trades > 0 else 0

        # Update stats display
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", tk.END)

        self.stats_text.insert(tk.END, "📊 Trading Performance Statistics\n\n", "header")
        self.stats_text.insert(tk.END, f"• Total Trades: {self.total_trades}\n")
        self.stats_text.insert(tk.END, f"• Winning Trades: {self.winning_trades}\n")
        self.stats_text.insert(tk.END, f"• Losing Trades: {self.losing_trades}\n")
        self.stats_text.insert(tk.END, f"• Win Rate: {win_rate:.1f}%\n")
        self.stats_text.insert(tk.END, f"• Consecutive Losses: {self.consecutive_losses}\n")
        self.stats_text.insert(tk.END, f"• Current Drawdown: {self.current_drawdown:.1f}%\n")
        self.stats_text.insert(tk.END, f"• Max Drawdown: {self.max_drawdown:.1f}%\n")
        self.stats_text.insert(tk.END, f"• Expectancy: {expectancy:.2f}R per trade\n\n")

        # Add performance feedback
        self.stats_text.insert(tk.END, "📈 Performance Feedback:\n", "subheader")

        if self.total_trades == 0:
            self.stats_text.insert(tk.END, "No trades recorded yet. Start trading to see statistics.\n")
        else:
            if win_rate > 60:
                self.stats_text.insert(tk.END, "• Excellent win rate! Maintain discipline.\n", "success")
            elif win_rate < 40:
                self.stats_text.insert(tk.END, "• Low win rate. Review your strategy.\n", "warning")
            else:
                self.stats_text.insert(tk.END, "• Average win rate. Focus on risk management.\n")

            if self.consecutive_losses >= 3:
                self.stats_text.insert(tk.END,
                                       f"• {self.consecutive_losses} consecutive losses. Consider reducing position size.\n",
                                       "warning")

            if expectancy > 0.5:
                self.stats_text.insert(tk.END, "• Positive expectancy. Keep following your edge.\n", "success")
            elif expectancy < 0:
                self.stats_text.insert(tk.END, "• Negative expectancy. Need strategy adjustment.\n", "warning")
            else:
                self.stats_text.insert(tk.END, "• Neutral expectancy. Room for improvement.\n")

        self.stats_text.config(state="disabled")

    def save_journal_entry(self):
        # Save trade journal entry
        notes = self.trade_notes.get("1.0", tk.END).strip()
        lessons = self.lessons_learned.get("1.0", tk.END).strip()
        emotion = self.trade_emotion.get()

        if not notes or not emotion:
            messagebox.showwarning("Incomplete Entry", "Please provide both notes and emotional state")
            return

        entry = f"=== Journal Entry ===\n"
        entry += f"Emotion: {emotion}\n"
        entry += f"Notes: {notes}\n"
        entry += f"Lessons: {lessons}\n\n"

        # Add to journal display
        self.journal_display.config(state="normal")
        self.journal_display.insert("1.0", entry)
        self.journal_display.config(state="disabled")

        # Clear fields
        self.trade_notes.delete("1.0", tk.END)
        self.lessons_learned.delete("1.0", tk.END)
        self.trade_emotion.set("")

        messagebox.showinfo("Saved", "Journal entry saved successfully!")

    def start_meditation_timer(self):
        # Placeholder for meditation timer functionality
        messagebox.showinfo("Meditation Timer", "Starting 5-minute meditation timer...\n\n"
                                                "Close your eyes and focus on your breathing.")

    def get_float(self, var_name, mandatory=False, default=None):
        val = self.inputs[var_name].get().strip()
        if not val:
            if mandatory:
                raise ValueError(f"{var_name} is required.")
            else:
                return default
        try:
            return float(val)
        except ValueError:
            raise ValueError(f"Invalid number for {var_name}: '{val}'")

    def get_int(self, var_name, mandatory=False, default=None):
        val = self.inputs[var_name].get().strip()
        if not val:
            if mandatory:
                raise ValueError(f"{var_name} is required.")
            else:
                return default
        try:
            return int(val)
        except ValueError:
            raise ValueError(f"Invalid integer for {var_name}: '{val}'")


if __name__ == "__main__":
    root = tk.Tk()
    app = SwingTradeCalculator(root)
    root.mainloop()