# main.py
# NEU Banking Management System — Tkinter GUI

import tkinter as tk
from tkinter import ttk, messagebox
import tkinter.font as tkfont
from datetime import date
from config import COLORS, FONTS, APP_TITLE, APP_VERSION
import database as db

# =============================================================
# REUSABLE UI COMPONENTS
# =============================================================
class NavyButton(tk.Button):
    def __init__(self, parent, text, command=None, style='primary', **kwargs):
        bg = {
            'primary': COLORS['accent'],
            'success': COLORS['success'],
            'danger':  COLORS['danger'],
            'warning': COLORS['warning'],
            'ghost':   COLORS['navy_light'],
        }.get(style, COLORS['accent'])

        super().__init__(parent, text=text, command=command,
            bg=bg, fg=COLORS['white'],
            font=FONTS['heading'],
            relief='flat', bd=0,
            padx=18, pady=8,
            cursor='hand2',
            activebackground=COLORS['navy_light'],
            activeforeground=COLORS['white'],
            **kwargs)
        self.bind('<Enter>', lambda e: self.config(bg=COLORS['navy_light']))
        self.bind('<Leave>', lambda e: self.config(bg=bg))


class Card(tk.Frame):
    def __init__(self, parent, title='', **kwargs):
        super().__init__(parent,
            bg=COLORS['navy_mid'],
            relief='flat', bd=0,
            padx=20, pady=15,
            **kwargs)
        if title:
            tk.Label(self, text=title,
                font=FONTS['heading'],
                bg=COLORS['navy_mid'],
                fg=COLORS['accent_light']
            ).pack(anchor='w', pady=(0,8))


class StatCard(tk.Frame):
    def __init__(self, parent, title, value, color=None, **kwargs):
        super().__init__(parent,
            bg=COLORS['navy_mid'],
            relief='flat', bd=0,
            padx=20, pady=18,
            **kwargs)
        tk.Label(self, text=title,
            font=FONTS['small'],
            bg=COLORS['navy_mid'],
            fg=COLORS['gray']
        ).pack(anchor='w')
        tk.Label(self, text=value,
            font=FONTS['amount'],
            bg=COLORS['navy_mid'],
            fg=color or COLORS['accent_light']
        ).pack(anchor='w', pady=(4,0))


class DataTable(tk.Frame):
    def __init__(self, parent, columns, **kwargs):
        super().__init__(parent, bg=COLORS['navy'], **kwargs)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Bank.Treeview',
            background=COLORS['navy_mid'],
            foreground=COLORS['white'],
            fieldbackground=COLORS['navy_mid'],
            rowheight=30,
            font=FONTS['body'])
        style.configure('Bank.Treeview.Heading',
            background=COLORS['navy_light'],
            foreground=COLORS['accent_light'],
            font=FONTS['heading'],
            relief='flat')
        style.map('Bank.Treeview',
            background=[('selected', COLORS['accent'])],
            foreground=[('selected', COLORS['white'])])

        scroll_y = ttk.Scrollbar(self, orient='vertical')
        scroll_x = ttk.Scrollbar(self, orient='horizontal')

        self.tree = ttk.Treeview(self,
            columns=columns,
            show='headings',
            style='Bank.Treeview',
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=140, anchor='center')

        scroll_y.pack(side='right',  fill='y')
        scroll_x.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=True)

    def load(self, rows):
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert('', 'end', values=list(row.values()))


class LabeledEntry(tk.Frame):
    def __init__(self, parent, label, **kwargs):
        super().__init__(parent, bg=COLORS['navy_mid'])
        tk.Label(self, text=label,
            font=FONTS['small'],
            bg=COLORS['navy_mid'],
            fg=COLORS['gray']
        ).pack(anchor='w')
        self.var = tk.StringVar()
        self.entry = tk.Entry(self,
            textvariable=self.var,
            font=FONTS['body'],
            bg=COLORS['navy_light'],
            fg=COLORS['white'],
            insertbackground=COLORS['white'],
            relief='flat', bd=0,
            highlightthickness=1,
            highlightbackground=COLORS['accent'],
            highlightcolor=COLORS['accent_light'],
            **kwargs)
        self.entry.pack(fill='x', pady=(2,8), ipady=6)

    def get(self): return self.var.get().strip()
    def set(self, v): self.var.set(v)
    def clear(self): self.var.set('')


# =============================================================
# SCREENS
# =============================================================
class DashboardScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['navy'])
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=COLORS['navy'], pady=20)
        hdr.pack(fill='x', padx=30)
        tk.Label(hdr, text="📊  Dashboard",
            font=FONTS['title'],
            bg=COLORS['navy'], fg=COLORS['white']
        ).pack(side='left')
        tk.Label(hdr, text=f"Today: {date.today()}",
            font=FONTS['small'],
            bg=COLORS['navy'], fg=COLORS['gray']
        ).pack(side='right', pady=10)

        # Stats row
        stats_frame = tk.Frame(self, bg=COLORS['navy'])
        stats_frame.pack(fill='x', padx=30, pady=(0,20))

        try:
            stats = db.get_db_stats()
            stat_data = [
                ("👥 Total Customers",   stats['customers'],       COLORS['accent_light']),
                ("🏦 Active Accounts",   stats['active_accounts'], COLORS['success']),
                ("💸 Transactions",      stats['transactions'],    COLORS['gold']),
                ("⚠️  High Alerts",       stats['high_alerts'],    COLORS['danger']),
            ]
        except:
            stat_data = [
                ("👥 Total Customers",  "N/A", COLORS['accent_light']),
                ("🏦 Active Accounts",  "N/A", COLORS['success']),
                ("💸 Transactions",     "N/A", COLORS['gold']),
                ("⚠️  High Alerts",      "N/A", COLORS['danger']),
            ]

        for title, value, color in stat_data:
            card = StatCard(stats_frame, title, str(value), color)
            card.pack(side='left', fill='x', expand=True, padx=5)

        # Total balance
        try:
            bal_frame = tk.Frame(self, bg=COLORS['navy_mid'], pady=15)
            bal_frame.pack(fill='x', padx=30, pady=(0,20))
            tk.Label(bal_frame, text="💰  Total Vault Value",
                font=FONTS['heading'],
                bg=COLORS['navy_mid'], fg=COLORS['gray']
            ).pack(side='left', padx=20)
            tk.Label(bal_frame,
                text=f"₫ {stats['total_balance']} VND",
                font=('Georgia', 16, 'bold'),
                bg=COLORS['navy_mid'], fg=COLORS['gold']
            ).pack(side='right', padx=20)
        except: pass

        # Recent transactions table
        sec = tk.Frame(self, bg=COLORS['navy'])
        sec.pack(fill='both', expand=True, padx=30, pady=(0,20))
        tk.Label(sec, text="Recent High-Risk Alerts",
            font=FONTS['subtitle'],
            bg=COLORS['navy'], fg=COLORS['white']
        ).pack(anchor='w', pady=(0,8))

        table = DataTable(sec, ['LogDate','Severity','Message'])
        table.pack(fill='both', expand=True)
        try:
            rows = db.get_audit_logs('HIGH', limit=20)
            table.load(rows)
        except: pass


class TransactionScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['navy'])
        self._build()

    def _build(self):
        # Header
        hdr = tk.Frame(self, bg=COLORS['navy'], pady=20)
        hdr.pack(fill='x', padx=30)
        tk.Label(hdr, text="💳  Transactions",
            font=FONTS['title'],
            bg=COLORS['navy'], fg=COLORS['white']
        ).pack(side='left')

        # Tab bar
        tab_bar = tk.Frame(self, bg=COLORS['navy_mid'])
        tab_bar.pack(fill='x', padx=30, pady=(0,20))

        self.tab_var = tk.StringVar(value='deposit')
        for label, val in [('Deposit','deposit'),('Withdrawal','withdrawal'),('Transfer','transfer')]:
            tk.Radiobutton(tab_bar,
                text=label, value=val,
                variable=self.tab_var,
                command=self._switch_tab,
                font=FONTS['heading'],
                bg=COLORS['navy_mid'],
                fg=COLORS['white'],
                selectcolor=COLORS['accent'],
                activebackground=COLORS['navy_mid'],
                padx=20, pady=10,
                indicatoron=False,
                relief='flat',
                cursor='hand2'
            ).pack(side='left')

        # Form area
        self.form_frame = tk.Frame(self, bg=COLORS['navy'])
        self.form_frame.pack(fill='both', expand=True, padx=30)
        self._switch_tab()

    def _switch_tab(self):
        for w in self.form_frame.winfo_children():
            w.destroy()
        tab = self.tab_var.get()
        if   tab == 'deposit':    self._build_deposit()
        elif tab == 'withdrawal': self._build_withdrawal()
        elif tab == 'transfer':   self._build_transfer()

    def _build_deposit(self):
        card = Card(self.form_frame, title='💰  Deposit Funds')
        card.pack(fill='x', pady=10)
        f1 = LabeledEntry(card, 'Account ID')
        f1.pack(fill='x')                          # ← FIX
        f2 = LabeledEntry(card, 'Amount (VND)')
        f2.pack(fill='x')                          # ← FIX
        f3 = LabeledEntry(card, 'Description')
        f3.pack(fill='x')                          # ← FIX
        f3.set('Cash deposit')
        self._result = tk.Label(card, text='', font=FONTS['body'],
            bg=COLORS['navy_mid'], fg=COLORS['success'])
        self._result.pack(anchor='w')

        def submit():
            try:
                ok, msg = db.deposit(int(f1.get()), float(f2.get()), f3.get())
                self._show_result(ok, msg)
            except ValueError:
                self._show_result(False, 'Invalid input — please enter numbers correctly')
        NavyButton(card, '✓  Confirm Deposit', submit, style='success').pack(anchor='w', pady=8)

    def _build_withdrawal(self):
        card = Card(self.form_frame, title='🏧  Withdrawal')
        card.pack(fill='x', pady=10)
        f1 = LabeledEntry(card, 'Account ID')
        f1.pack(fill='x')                          # ← FIX
        f2 = LabeledEntry(card, 'Amount (VND)')
        f2.pack(fill='x')                          # ← FIX
        f3 = LabeledEntry(card, 'Description')
        f3.pack(fill='x')                          # ← FIX
        f3.set('ATM withdrawal')
        self._result = tk.Label(card, text='', font=FONTS['body'],
            bg=COLORS['navy_mid'], fg=COLORS['success'])
        self._result.pack(anchor='w')

        def submit():
            try:
                ok, msg = db.withdrawal(int(f1.get()), float(f2.get()), f3.get())
                self._show_result(ok, msg)
            except ValueError:
                self._show_result(False, 'Invalid input')
        NavyButton(card, '✓  Confirm Withdrawal', submit, style='warning').pack(anchor='w', pady=8)

    def _build_transfer(self):
        card = Card(self.form_frame, title='🔄  Transfer Funds')
        card.pack(fill='x', pady=10)
        f1 = LabeledEntry(card, 'From Account ID')
        f1.pack(fill='x')                          # ← FIX
        f2 = LabeledEntry(card, 'To Account ID')
        f2.pack(fill='x')                          # ← FIX
        f3 = LabeledEntry(card, 'Amount (VND)')
        f3.pack(fill='x')                          # ← FIX
        f4 = LabeledEntry(card, 'Description')
        f4.pack(fill='x')                          # ← FIX
        f4.set('Online transfer')
        self._result = tk.Label(card, text='', font=FONTS['body'],
            bg=COLORS['navy_mid'], fg=COLORS['success'])
        self._result.pack(anchor='w')

        def submit():
            try:
                ok, msg = db.transfer(int(f1.get()), int(f2.get()), float(f3.get()), f4.get())
                self._show_result(ok, msg)
            except ValueError:
                self._show_result(False, 'Invalid input')
        NavyButton(card, '✓  Confirm Transfer', submit, style='primary').pack(anchor='w', pady=8)

    def _show_result(self, ok, msg):
        self._result.config(
            text=f"{'✅' if ok else '❌'}  {msg}",
            fg=COLORS['success'] if ok else COLORS['danger'])


class AccountScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['navy'])
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS['navy'], pady=20)
        hdr.pack(fill='x', padx=30)
        tk.Label(hdr, text="🏦  Account Management",
            font=FONTS['title'],
            bg=COLORS['navy'], fg=COLORS['white']
        ).pack(side='left')

        # Search bar
        search_card = Card(self, title='🔍  Account Lookup')
        search_card.pack(fill='x', padx=30, pady=(0,15))

        row = tk.Frame(search_card, bg=COLORS['navy_mid'])
        row.pack(fill='x')
        self.search_entry = tk.Entry(row,
            font=FONTS['body'],
            bg=COLORS['navy_light'], fg=COLORS['white'],
            insertbackground=COLORS['white'],
            relief='flat', bd=0,
            highlightthickness=1,
            highlightbackground=COLORS['accent'])
        self.search_entry.pack(side='left', fill='x', expand=True, ipady=6, padx=(0,10))
        NavyButton(row, 'Search', self._search).pack(side='left')

        # Info display
        self.info_frame = Card(self, title='Account Details')
        self.info_frame.pack(fill='x', padx=30, pady=(0,15))
        self.info_label = tk.Label(self.info_frame,
            text='Enter an Account ID to view details',
            font=FONTS['body'],
            bg=COLORS['navy_mid'], fg=COLORS['gray'],
            justify='left')
        self.info_label.pack(anchor='w')

        # Transaction history
        hist_frame = tk.Frame(self, bg=COLORS['navy'])
        hist_frame.pack(fill='both', expand=True, padx=30, pady=(0,20))
        tk.Label(hist_frame, text="Transaction History",
            font=FONTS['subtitle'],
            bg=COLORS['navy'], fg=COLORS['white']
        ).pack(anchor='w', pady=(0,8))

        self.hist_table = DataTable(hist_frame,
            ['ID','Type','Amount','Date','Description'])
        self.hist_table.pack(fill='both', expand=True)

    def _search(self):
        try:
            acc_id = int(self.search_entry.get())
            info   = db.get_account_info(acc_id)
            if info:
                self.info_label.config(
                    fg=COLORS['white'],
                    text=(
                        f"Customer : {info['CustomerName']}   "
                        f"Phone: {info['Phone']}\n"
                        f"Account  : #{info['AccountID']}  "
                        f"({info['AccountType']})\n"
                        f"Balance  : ₫ {info['Balance']:,.0f} VND\n"
                        f"Status   : {info['Status']}   "
                        f"Branch: {info['BranchName']}\n"
                        f"Opened   : {info['OpenDate']}"
                    ))
                rows = db.get_transaction_history(acc_id)
                self.hist_table.load(rows)
            else:
                self.info_label.config(
                    text='❌  Account not found', fg=COLORS['danger'])
        except ValueError:
            self.info_label.config(
                text='❌  Please enter a valid Account ID', fg=COLORS['danger'])


class ReportScreen(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=COLORS['navy'])
        self._build()

    def _build(self):
        hdr = tk.Frame(self, bg=COLORS['navy'], pady=20)
        hdr.pack(fill='x', padx=30)
        tk.Label(hdr, text="📈  Reports & Analytics",
            font=FONTS['title'],
            bg=COLORS['navy'], fg=COLORS['white']
        ).pack(side='left')

        # Report selector
        btn_row = tk.Frame(self, bg=COLORS['navy_mid'])
        btn_row.pack(fill='x', padx=30, pady=(0,15))

        reports = [
            ('Customer Balances',    self._rpt_balances),
            ('VIP Customers',        self._rpt_vip),
            ('Cash Flow Summary',    self._rpt_cashflow),
            ('Audit Log — HIGH',     self._rpt_audit),
            ('Daily Report',         self._rpt_daily),
        ]
        for label, cmd in reports:
            NavyButton(btn_row, label, cmd, style='ghost').pack(
                side='left', padx=4, pady=8)

        # Date input for daily report
        date_row = tk.Frame(self, bg=COLORS['navy'])
        date_row.pack(fill='x', padx=30, pady=(0,10))
        tk.Label(date_row, text="Date for Daily Report:",
            font=FONTS['small'],
            bg=COLORS['navy'], fg=COLORS['gray']
        ).pack(side='left')
        self.date_entry = tk.Entry(date_row,
            font=FONTS['body'], width=14,
            bg=COLORS['navy_light'], fg=COLORS['white'],
            insertbackground=COLORS['white'],
            relief='flat', bd=0,
            highlightthickness=1,
            highlightbackground=COLORS['accent'])
        self.date_entry.insert(0, str(date.today()))
        self.date_entry.pack(side='left', ipady=5, padx=8)

        # Table
        self.table_frame = tk.Frame(self, bg=COLORS['navy'])
        self.table_frame.pack(fill='both', expand=True, padx=30, pady=(0,20))
        self.table = None

    def _load_table(self, columns, rows):
        for w in self.table_frame.winfo_children():
            w.destroy()
        self.table = DataTable(self.table_frame, columns)
        self.table.pack(fill='both', expand=True)
        self.table.load(rows)

    def _rpt_balances(self):
        rows = db.get_customer_balances()
        self._load_table(
            ['CustomerName','AccountType','Balance_VND','Status','BranchName'], rows)

    def _rpt_vip(self):
        rows = db.get_vip_customers()
        self._load_table(
            ['CustomerName','Phone','Total_Assets_VND','Total_Accounts','Tier'], rows)

    def _rpt_cashflow(self):
        rows = db.get_transaction_summary()
        self._load_table(
            ['CustomerName','TotalTransactions','Total_In_VND','Total_Out_VND'], rows)

    def _rpt_audit(self):
        rows = db.get_audit_logs('HIGH', limit=50)
        self._load_table(['LogDate','Severity','Message'], rows)

    def _rpt_daily(self):
        rows = db.get_daily_report(self.date_entry.get())
        self._load_table(['TransactionType','TotalCount','TotalAmount'], rows)


# =============================================================
# MAIN APPLICATION WINDOW
# =============================================================
class BankingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE}  {APP_VERSION}")
        self.geometry('1100x700')
        self.minsize(900, 600)
        self.configure(bg=COLORS['navy'])
        self._build_layout()

    def _build_layout(self):
        # ── Sidebar ──────────────────────────────────────────
        sidebar = tk.Frame(self, bg=COLORS['navy_mid'], width=220)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(sidebar, bg=COLORS['navy_light'], pady=25)
        logo.pack(fill='x')
        tk.Label(logo, text="🏛",
            font=('Helvetica', 28),
            bg=COLORS['navy_light'], fg=COLORS['gold']
        ).pack()
        tk.Label(logo, text="NEU Bank",
            font=('Georgia', 14, 'bold'),
            bg=COLORS['navy_light'], fg=COLORS['white']
        ).pack()
        tk.Label(logo, text="Management System",
            font=FONTS['small'],
            bg=COLORS['navy_light'], fg=COLORS['gray']
        ).pack()

        # Nav items
        self.nav_buttons = {}
        self.current_screen = None
        nav_items = [
            ('📊', 'Dashboard',    'dashboard'),
            ('💳', 'Transactions', 'transactions'),
            ('🏦', 'Accounts',     'accounts'),
            ('📈', 'Reports',      'reports'),
        ]

        nav_frame = tk.Frame(sidebar, bg=COLORS['navy_mid'])
        nav_frame.pack(fill='x', pady=20)

        for icon, label, key in nav_items:
            btn = tk.Button(nav_frame,
                text=f"  {icon}  {label}",
                font=FONTS['body'],
                bg=COLORS['navy_mid'],
                fg=COLORS['gray_light'],
                relief='flat', bd=0,
                anchor='w', padx=20, pady=12,
                cursor='hand2',
                activebackground=COLORS['navy_light'],
                activeforeground=COLORS['white'],
                command=lambda k=key: self._navigate(k))
            btn.pack(fill='x')
            self.nav_buttons[key] = btn

        # Version at bottom
        tk.Label(sidebar, text=APP_VERSION,
            font=FONTS['small'],
            bg=COLORS['navy_mid'], fg=COLORS['gray']
        ).pack(side='bottom', pady=15)

        # ── Main content area ─────────────────────────────────
        self.content = tk.Frame(self, bg=COLORS['navy'])
        self.content.pack(side='left', fill='both', expand=True)

        self.screens = {}
        self._navigate('dashboard')

    def _navigate(self, key):
        for k, btn in self.nav_buttons.items():
            btn.config(
                bg=COLORS['accent']     if k == key else COLORS['navy_mid'],
                fg=COLORS['white']      if k == key else COLORS['gray_light'])

        for w in self.content.winfo_children():
            w.destroy()

        screen_map = {
            'dashboard':    DashboardScreen,
            'transactions': TransactionScreen,
            'accounts':     AccountScreen,
            'reports':      ReportScreen,
        }
        screen = screen_map[key](self.content)
        screen.pack(fill='both', expand=True)


# =============================================================
# ENTRY POINT
# =============================================================
if __name__ == '__main__':
    try:
        conn = db.get_connection()
        conn.close()
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ DB connection failed: {e}")
        print("   Check config.py — password and database name")
        exit(1)

    app = BankingApp()
    app.mainloop()