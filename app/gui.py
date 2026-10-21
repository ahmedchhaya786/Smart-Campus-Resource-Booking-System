"""Tkinter graphical interface for the Smart Campus Resource Booking System."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from app import database as db
from app.models import build_user

BG = "#f2f5f9"
NAVY = "#17324d"
BLUE = "#1769aa"

class CampusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Campus Resource Booking System")
        self.root.geometry("1120x720")
        self.root.minsize(920, 600)
        self.root.configure(bg=BG)
        self.user = None
        self.active_campus_id = None
        self.active_campus_name = None
        self.style = ttk.Style()
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.style.configure("Treeview", rowheight=27, font=("Arial", 10))
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        self.show_login()

    def clear(self):
        for child in self.root.winfo_children():
            child.destroy()

    def header(self, title, subtitle=""):
        top = tk.Frame(self.root, bg=NAVY, padx=22, pady=16)
        top.pack(fill="x")
        tk.Label(top, text=title, bg=NAVY, fg="white", font=("Arial", 19, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(top, text=subtitle, bg=NAVY, fg="#d9e8f5", font=("Arial", 10)).pack(anchor="w", pady=(5,0))

    def field(self, parent, label, show=None):
        tk.Label(parent, text=label, bg=BG, fg=NAVY, font=("Arial", 10, "bold")).pack(anchor="w", pady=(8,3))
        entry = tk.Entry(parent, font=("Arial", 11), relief="solid", bd=1, show=show)
        entry.pack(fill="x", ipady=7)
        return entry

    def show_login(self):
        self.clear()
        self.header("Smart Campus Resource Booking System", "Richfield Graduate Institution • Secure resource booking")
        wrap = tk.Frame(self.root, bg=BG, padx=30, pady=24)
        wrap.pack(fill="both", expand=True)
        panel = tk.Frame(wrap, bg="white", padx=30, pady=24, highlightbackground="#d7e0ea", highlightthickness=1)
        panel.place(relx=.5, rely=.45, anchor="center", width=420)
        tk.Label(panel, text="Welcome back", bg="white", fg=NAVY, font=("Arial", 18, "bold")).pack(anchor="w")
        tk.Label(panel, text="Sign in to continue", bg="white", fg="#617386").pack(anchor="w", pady=(4,12))
        tk.Label(panel, text="Username", bg="white", fg=NAVY).pack(anchor="w", pady=(8,3))
        self.username_entry = tk.Entry(panel, font=("Arial", 11), relief="solid", bd=1)
        self.username_entry.pack(fill="x", ipady=7)
        tk.Label(panel, text="Password", bg="white", fg=NAVY).pack(anchor="w", pady=(12,3))
        self.password_entry = tk.Entry(panel, font=("Arial", 11), show="*", relief="solid", bd=1)
        self.password_entry.pack(fill="x", ipady=7)
        tk.Button(panel, text="LOG IN", command=self.login, bg=BLUE, fg="white",
                  activebackground=NAVY, activeforeground="white", relief="flat",
                  font=("Arial", 10, "bold"), pady=10).pack(fill="x", pady=(18,8))
        tk.Button(panel, text="Create lecturer account", command=self.show_register,
                  bg="white", fg=BLUE, relief="flat").pack()
        tk.Label(panel, text="Demo: lecturer / lecturer123", bg="white", fg="#68798a",
                 font=("Arial", 9)).pack(anchor="w", pady=(15,0))
        self.password_entry.bind("<Return>", lambda event: self.login())
        self.username_entry.focus_set()

    def login(self):
        row = db.get_user(self.username_entry.get(), self.password_entry.get())
        if not row:
            messagebox.showerror("Login failed", "Incorrect username or password.")
            return
        self.user = build_user(row)
        self.choose_campus()

    def show_register(self):
        self.clear()
        self.header("Create Lecturer Account", "Registration is available to lecturers.")
        panel = tk.Frame(self.root, bg=BG, padx=35, pady=25)
        panel.pack(fill="both", expand=True)
        self.reg_name = self.field(panel, "Full name")
        self.reg_username = self.field(panel, "Choose username")
        self.reg_password = self.field(panel, "Choose password", show="*")
        tk.Button(panel, text="CREATE ACCOUNT", command=self.register, bg=BLUE, fg="white",
                  relief="flat", padx=18, pady=9).pack(anchor="w", pady=18)
        tk.Button(panel, text="Back to login", command=self.show_login).pack(anchor="w")

    def register(self):
        ok, msg = db.register_lecturer(self.reg_name.get(), self.reg_username.get(), self.reg_password.get())
        (messagebox.showinfo if ok else messagebox.showerror)("Registration", msg)
        if ok:
            self.show_login()

    def choose_campus(self):
        self.clear()
        self.header("Choose a Campus", f"Signed in as {self.user.full_name} • {self.user.role}")
        body = tk.Frame(self.root, bg=BG, padx=35, pady=25)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Select the campus you want to work with.", bg=BG,
                 fg=NAVY, font=("Arial", 13, "bold")).pack(anchor="w", pady=(0,10))
        self.campus_rows = db.get_campuses()
        names = [row["name"] for row in self.campus_rows]
        self.campus_choice = ttk.Combobox(body, values=names, state="readonly", width=45, font=("Arial", 11))
        if self.user.campus_id:
            self.campus_choice.set(self.user.campus_name)
            self.campus_choice.configure(state="disabled")
        elif names:
            self.campus_choice.current(0)
        self.campus_choice.pack(anchor="w", ipady=5)
        policy = tk.Frame(body, bg="white", padx=15, pady=15)
        policy.pack(fill="x", pady=18)
        tk.Label(policy, text="Campus booking policies", bg="white", fg=NAVY,
                 font=("Arial", 11, "bold")).pack(anchor="w")
        for row in self.campus_rows:
            tk.Label(policy, text=f"• {row['name']}: {row['opening_hour']:02d}:00–{row['closing_hour']:02d}:00; "
                     f"maximum {row['max_duration']} hours per booking",
                     bg="white", fg="#43566a").pack(anchor="w", pady=2)
        tk.Button(body, text="CONTINUE", command=self.enter_campus, bg=BLUE, fg="white",
                  relief="flat", padx=22, pady=10).pack(anchor="w")
        tk.Button(body, text="Log out", command=self.show_login).pack(anchor="w", pady=10)

    def enter_campus(self):
        name = self.campus_choice.get()
        row = next((c for c in self.campus_rows if c["name"] == name), None)
        if not row:
            messagebox.showerror("Campus required", "Please select a campus.")
            return
        self.active_campus_id, self.active_campus_name = row["id"], row["name"]
        self.show_dashboard()

    def show_dashboard(self):
        self.clear()
        self.header("Smart Campus • Dashboard",
                    f"Active campus: {self.active_campus_name}    |    {self.user.full_name} ({self.user.role})")
        nav = tk.Frame(self.root, bg="#e3ebf3", padx=10, pady=8)
        nav.pack(fill="x")
        self.nav_button(nav, "Resources", self.show_resources)
        self.nav_button(nav, "Bookings", self.show_bookings)
        self.nav_button(nav, "Reports", self.show_reports)
        if self.user.role in ("Campus Administrator", "System Operator"):
            self.nav_button(nav, "Add resource", self.add_resource_window)
        self.nav_button(nav, "Change campus", self.choose_campus)
        self.nav_button(nav, "Log out", self.show_login)
        body = tk.Frame(self.root, bg=BG, padx=24, pady=22)
        body.pack(fill="both", expand=True)
        tk.Label(body, text=f"Welcome, {self.user.full_name.split()[0]}!", bg=BG, fg=NAVY,
                 font=("Arial", 20, "bold")).pack(anchor="w")
        tk.Label(body, text="Manage shared academic resources in one place.", bg=BG,
                 fg="#526579", font=("Arial", 11)).pack(anchor="w", pady=(4,18))
        cards = tk.Frame(body, bg=BG)
        cards.pack(fill="x")
        resources = db.get_resources(self.active_campus_id)
        bookings = db.get_bookings(self.active_campus_id, user_id=self.user.user_id if self.user.role == "Lecturer" else None, status="Active")
        self.stat_card(cards, "ACTIVE RESOURCES", str(len(resources)), 0)
        self.stat_card(cards, "ACTIVE BOOKINGS", str(len(bookings)), 1)
        self.stat_card(cards, "BOOKING POLICY", f"Max {next(c['max_duration'] for c in self.campus_rows if c['id']==self.active_campus_id)} hours", 2)
        info = tk.Frame(body, bg="white", padx=18, pady=16)
        info.pack(fill="x", pady=22)
        tk.Label(info, text="Quick start", bg="white", fg=NAVY, font=("Arial", 12, "bold")).pack(anchor="w")
        steps = ("1. Open Resources to see active equipment and rooms.",
                 "2. Open Bookings to create, view or cancel bookings.",
                 "3. Open Reports to view campus usage and cross-campus comparisons.")
        for step in steps:
            tk.Label(info, text=step, bg="white", fg="#43566a").pack(anchor="w", pady=3)
        tk.Label(body, text="Demo staff accounts and setup instructions are listed in README.md.",
                 bg=BG, fg="#68798a").pack(anchor="w")

    def nav_button(self, parent, label, command):
        tk.Button(parent, text=label, command=command, bg="#e3ebf3", fg=NAVY,
                  activebackground="#cbdbea", relief="flat", padx=10, pady=6).pack(side="left", padx=3)

    def stat_card(self, parent, label, value, column):
        card = tk.Frame(parent, bg="white", padx=18, pady=16, highlightbackground="#d7e0ea", highlightthickness=1)
        card.grid(row=0, column=column, sticky="nsew", padx=(0,12))
        parent.grid_columnconfigure(column, weight=1)
        tk.Label(card, text=label, bg="white", fg="#607386", font=("Arial", 9, "bold")).pack(anchor="w")
        tk.Label(card, text=value, bg="white", fg=BLUE, font=("Arial", 18, "bold")).pack(anchor="w", pady=(7,0))

    def table(self, parent, columns, headings, widths=None):
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="both", expand=True, pady=10)
        tree = ttk.Treeview(frame, columns=columns, show="headings")
        for index, (col, heading) in enumerate(zip(columns, headings)):
            tree.heading(col, text=heading)
            tree.column(col, width=(widths[index] if widths else 130), anchor="w")
        yscroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=yscroll.set)
        tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")
        return tree

    def page(self, title, description=""):
        self.clear()
        self.header(title, description)
        body = tk.Frame(self.root, bg=BG, padx=22, pady=16)
        body.pack(fill="both", expand=True)
        top = tk.Frame(body, bg=BG)
        top.pack(fill="x")
        tk.Button(top, text="← Dashboard", command=self.show_dashboard).pack(side="left")
        return body

    def show_resources(self):
        body = self.page("Campus Resources", f"Active campus: {self.active_campus_name}")
        if self.user.role == "System Operator":
            tk.Label(body, text="System Operator view: all campuses", bg=BG, fg=NAVY).pack(anchor="w", pady=4)
            rows = db.get_all_resources()
        else:
            rows = db.get_resources(self.active_campus_id, active_only=(self.user.role == "Lecturer"))
        tree = self.table(body, ("code","name","type","campus","status"),
                          ("Resource code","Resource name","Type","Campus","Status"), (130,230,150,190,90))
        for r in rows:
            tree.insert("", "end", iid=str(r["id"]), values=(r["resource_code"],r["name"],r["resource_type"],r["campus_name"],
                                                             "Active" if r["active"] else "Inactive"))
        if self.user.role in ("Campus Administrator", "System Operator"):
            controls = tk.Frame(body, bg=BG)
            controls.pack(anchor="w", pady=6)
            tk.Button(controls, text="Edit selected", command=lambda: self.edit_resource(tree)).pack(side="left", padx=(0,8))
            tk.Button(controls, text="Deactivate selected", command=lambda: self.remove_resource(tree)).pack(side="left")

    def add_resource_window(self):
        campuses = db.get_campuses()
        window = tk.Toplevel(self.root)
        window.title("Add resource")
        window.geometry("400x410")
        window.configure(bg=BG)
        tk.Label(window, text="Register a resource", bg=BG, fg=NAVY, font=("Arial", 15, "bold")).pack(pady=12)
        code = self.field(window, "Unique resource code")
        name = self.field(window, "Resource name")
        kind = self.field(window, "Resource type")
        tk.Label(window, text="Campus", bg=BG, fg=NAVY).pack(anchor="w", padx=8, pady=(10,3))
        campus_combo = ttk.Combobox(window, state="readonly", values=[c["name"] for c in campuses])
        campus_combo.pack(fill="x", padx=8)
        if self.user.role == "Campus Administrator":
            campus_combo.set(self.user.campus_name); campus_combo.configure(state="disabled")
        else:
            campus_combo.set(self.active_campus_name)
        def save():
            campus = next((c for c in campuses if c["name"] == campus_combo.get()), None)
            if not code.get().strip() or not name.get().strip() or not kind.get().strip() or not campus:
                messagebox.showerror("Missing information", "Complete all fields.", parent=window); return
            if self.user.role == "Campus Administrator" and campus["id"] != self.user.campus_id:
                messagebox.showerror("Permission denied", "You can only manage your assigned campus.", parent=window); return
            ok, msg = db.add_resource(code.get(), name.get(), kind.get(), campus["id"])
            (messagebox.showinfo if ok else messagebox.showerror)("Resource", msg, parent=window)
            if ok:
                window.destroy()
                self.show_resources()
        tk.Button(window, text="SAVE RESOURCE", command=save, bg=BLUE, fg="white", relief="flat", pady=8).pack(fill="x", padx=8, pady=18)

    def selected_resource(self, tree):
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Select a resource", "Select a resource in the table first.")
            return None
        return int(selection[0])

    def edit_resource(self, tree):
        resource_id = self.selected_resource(tree)
        if resource_id is None: return
        rows = db.get_all_resources()
        resource = next(r for r in rows if r["id"] == resource_id)
        if self.user.role == "Campus Administrator" and resource["campus_id"] != self.user.campus_id:
            messagebox.showerror("Permission denied", "You can only edit resources at your assigned campus."); return
        campuses = db.get_campuses()
        win = tk.Toplevel(self.root); win.title("Edit resource"); win.geometry("400x410"); win.configure(bg=BG)
        code = self.field(win, "Resource code"); code.insert(0, resource["resource_code"])
        name = self.field(win, "Resource name"); name.insert(0, resource["name"])
        kind = self.field(win, "Resource type"); kind.insert(0, resource["resource_type"])
        tk.Label(win, text="Campus", bg=BG).pack(anchor="w", padx=8, pady=(10,3))
        combo = ttk.Combobox(win, state="readonly", values=[c["name"] for c in campuses]); combo.pack(fill="x", padx=8)
        combo.set(resource["campus_name"])
        if self.user.role == "Campus Administrator": combo.configure(state="disabled")
        def save():
            campus = next(c for c in campuses if c["name"] == combo.get())
            ok, msg = db.update_resource(resource_id, code.get(), name.get(), kind.get(), campus["id"])
            (messagebox.showinfo if ok else messagebox.showerror)("Resource", msg, parent=win)
            if ok: win.destroy(); self.show_resources()
        tk.Button(win, text="SAVE CHANGES", command=save, bg=BLUE, fg="white", relief="flat", pady=8).pack(fill="x", padx=8, pady=18)

    def remove_resource(self, tree):
        resource_id = self.selected_resource(tree)
        if resource_id is None: return
        resource = next((r for r in db.get_all_resources() if r["id"] == resource_id), None)
        if self.user.role == "Campus Administrator" and resource["campus_id"] != self.user.campus_id:
            messagebox.showerror("Permission denied", "You can only manage your assigned campus."); return
        if messagebox.askyesno("Deactivate resource", "Deactivate this resource? Existing booking history will be kept."):
            db.deactivate_resource(resource_id); self.show_resources()

    def show_bookings(self):
        body = self.page("Booking Management", f"Active campus: {self.active_campus_name}")
        controls = tk.Frame(body, bg=BG); controls.pack(fill="x", pady=(8,0))
        if self.user.role == "Lecturer":
            tk.Button(controls, text="Create booking", command=self.create_booking_window,
                      bg=BLUE, fg="white", relief="flat", padx=14, pady=7).pack(side="left", padx=(0,8))
            rows = db.get_bookings(campus_id=self.active_campus_id, user_id=self.user.user_id)
        elif self.user.role == "Campus Administrator":
            rows = db.get_bookings(campus_id=self.user.campus_id)
        else:
            rows = db.get_bookings()
        tree = self.table(body, ("id","lecturer","resource","campus","date","start","duration","status"),
                          ("ID","Booked by","Resource","Campus","Date","Start","Hours","Status"),
                          (55,150,190,170,100,75,65,90))
        for r in rows:
            tree.insert("", "end", iid=str(r["id"]), values=(r["id"],r["full_name"],r["resource_code"]+" - "+r["resource_name"],
                r["campus_name"],r["booking_date"],r["start_time"],r["duration"],r["status"]))
        if self.user.role in ("Lecturer", "Campus Administrator", "System Operator"):
            tk.Button(body, text="Cancel selected active booking", command=lambda: self.cancel_selected_booking(tree)).pack(anchor="w", pady=6)

    def create_booking_window(self):
        resources = db.get_resources(self.active_campus_id)
        if not resources:
            messagebox.showinfo("No resources", "There are no active resources at this campus."); return
        win = tk.Toplevel(self.root); win.title("Create booking"); win.geometry("470x470"); win.configure(bg=BG)
        tk.Label(win, text="Create a resource booking", bg=BG, fg=NAVY,
                 font=("Arial", 15, "bold")).pack(pady=12)
        tk.Label(win, text=f"Policy: {self.active_campus_name}", bg=BG, fg="#526579").pack()
        tk.Label(win, text="Resource", bg=BG).pack(anchor="w", padx=10, pady=(12,3))
        resource_combo = ttk.Combobox(win, state="readonly", values=[f"{r['resource_code']} — {r['name']}" for r in resources])
        resource_combo.pack(fill="x", padx=10, ipady=4); resource_combo.current(0)
        date_entry = self.field(win, "Booking date (YYYY-MM-DD)"); date_entry.insert(0, date.today().isoformat())
        time_entry = self.field(win, "Start time (HH:MM, 24-hour)"); time_entry.insert(0, "10:00")
        duration_entry = self.field(win, "Duration in whole hours"); duration_entry.insert(0, "1")
        def save():
            try:
                duration = int(duration_entry.get())
            except ValueError:
                messagebox.showerror("Invalid duration", "Enter duration as a whole number of hours.", parent=win); return
            resource = resources[resource_combo.current()]
            ok, msg = db.create_booking(self.user.user_id, resource["id"], self.active_campus_id,
                                        date_entry.get().strip(), time_entry.get().strip(), duration)
            (messagebox.showinfo if ok else messagebox.showerror)("Booking", msg, parent=win)
            if ok: win.destroy(); self.show_bookings()
        tk.Button(win, text="CONFIRM BOOKING", command=save, bg=BLUE, fg="white",
                  relief="flat", pady=9).pack(fill="x", padx=10, pady=18)

    def cancel_selected_booking(self, tree):
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Select a booking", "Select a booking in the table first."); return
        booking_id = int(selection[0])
        user_id = self.user.user_id if self.user.role == "Lecturer" else None
        campus_id = self.user.campus_id if self.user.role == "Campus Administrator" else None
        if messagebox.askyesno("Cancel booking", "Cancel the selected active booking?"):
            ok, msg = db.cancel_booking(booking_id, user_id=user_id, campus_id=campus_id)
            (messagebox.showinfo if ok else messagebox.showerror)("Booking", msg)
            self.show_bookings()

    def show_reports(self):
        body = self.page("Reports and Management Information", "Campus-level statistics and cross-campus comparison")
        if self.user.role == "Lecturer":
            tk.Label(body, text="Reports are available to campus administrators and system operators.",
                     bg=BG, fg=NAVY).pack(anchor="w", pady=15); return
        campus_id = self.user.campus_id if self.user.role == "Campus Administrator" else None
        reports = db.get_campus_reports()
        if campus_id:
            campus = next(c for c in db.get_campuses() if c["id"] == campus_id)
            reports = [r for r in reports if r["name"] == campus["name"]]
            tk.Label(body, text=f"Campus report: {campus['name']}", bg=BG, fg=NAVY,
                     font=("Arial", 12, "bold")).pack(anchor="w", pady=(8,0))
        else:
            tk.Label(body, text="Cross-campus comparison", bg=BG, fg=NAVY,
                     font=("Arial", 12, "bold")).pack(anchor="w", pady=(8,0))
        tree = self.table(body, ("campus","bookings","average"), ("Campus","Active bookings","Average duration (hours)"), (250,180,230))
        for r in reports:
            tree.insert("", "end", values=(r["name"], r["total_bookings"], r["average_duration"] if r["average_duration"] is not None else "N/A"))
        tk.Label(body, text="Most frequently used resources", bg=BG, fg=NAVY,
                 font=("Arial", 12, "bold")).pack(anchor="w", pady=(14,0))
        popular = self.table(body, ("resource","code","campus","uses"), ("Resource","Code","Campus","Active bookings"), (250,130,230,140))
        for r in db.get_popular_resources(campus_id):
            popular.insert("", "end", values=(r["name"],r["resource_code"],r["campus_name"],r["use_count"]))

def run_app():
    db.initialize_database()
    root = tk.Tk()
    CampusApp(root)
    root.mainloop()
