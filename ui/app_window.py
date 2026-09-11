"""
ui/app_window.py
=================
واجهة بسيطة بـ tkinter بتعرض آخر نتايج CBC اللي وصلت، بتعمل polling على
الداتابيز كل كام ثانية، وفيها زرار Refresh يدوي.
"""

import sqlite3
import tkinter as tk
from tkinter import ttk
from pathlib import Path

# --- إعدادات قابلة للتعديل بسهولة ---
DB_PATH = Path(__file__).resolve().parent.parent / "storage" / "cbc_results.db"
TABLE_NAME = "results"
POLL_INTERVAL_MS = 5000  # كل 5 ثواني - غيّرها لو عايز أسرع/أبطأ
MAX_ROWS_SHOWN = 50

COLUMNS = [
    ("sample_id", "Sample ID"),
    ("wbc", "WBC"),
    ("rbc", "RBC"),
    ("hgb", "HGB"),
    ("hct", "HCT"),
    ("plt", "PLT"),
    ("received_at", "وقت الاستلام"),
]


def fetch_results():
    """
    يرجع list of tuples لآخر النتائج، الأحدث الأول.
    لو الداتابيز أو الجدول مش موجود لسه (السيرفر لسه ما استقبلش حاجة)،
    بيرجع list فاضية بدل ما يرمي exception يوقف الواجهة.
    """
    if not DB_PATH.exists():
        return []

    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        col_names = ", ".join(c for c, _ in COLUMNS)
        cur.execute(
            f"SELECT {col_names} FROM {TABLE_NAME} "
            f"ORDER BY received_at DESC LIMIT ?",
            (MAX_ROWS_SHOWN,),
        )
        rows = cur.fetchall()
        conn.close()
        return [tuple(row) for row in rows]
    except sqlite3.OperationalError:
        # الجدول لسه مش اتعمل (أول تشغيل قبل أي رسالة توصل) - مش خطأ حقيقي
        return []


class CBCResultsWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("CBC Interface - آخر النتائج")
        self.root.geometry("780x420")

        self._build_widgets()
        self._poll()  # يبدأ دورة التحديث التلقائي

    def _build_widgets(self):
        top_bar = ttk.Frame(self.root, padding=8)
        top_bar.pack(fill="x")

        self.status_label = ttk.Label(top_bar, text="", foreground="gray")
        self.status_label.pack(side="left")

        refresh_btn = ttk.Button(top_bar, text="Refresh", command=self._refresh_now)
        refresh_btn.pack(side="right")

        # جدول النتائج
        table_frame = ttk.Frame(self.root, padding=(8, 0, 8, 8))
        table_frame.pack(fill="both", expand=True)

        col_ids = [c for c, _ in COLUMNS]
        self.tree = ttk.Treeview(
            table_frame, columns=col_ids, show="headings", height=15
        )
        for col_id, header in COLUMNS:
            self.tree.heading(col_id, text=header)
            self.tree.column(col_id, width=100, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # رسالة "مفيش نتائج لسه" - بتتحط فوق الجدول وتتخفي لما فيه بيانات
        self.empty_label = ttk.Label(
            self.root,
            text="لسه مفيش نتائج وصلت.\nتأكد إن السيرفر (main.py) شغال ومستني اتصال من الجهاز.",
            justify="center",
            foreground="gray",
            font=("TkDefaultFont", 11),
        )

    def _refresh_now(self):
        """زرار Refresh اليدوي - بينادي على نفس منطق الـ polling فورًا."""
        self._load_and_render()

    def _poll(self):
        """بتتعاد كل POLL_INTERVAL_MS - تحديث تلقائي في الخلفية."""
        self._load_and_render()
        self.root.after(POLL_INTERVAL_MS, self._poll)

    def _load_and_render(self):
        rows = fetch_results()

        # امسح الجدول الحالي وارسمه تاني (أبسط طريقة مع عدد صفوف صغير زي ده)
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not rows:
            self.tree.pack_forget()
            self.empty_label.pack(expand=True, fill="both", pady=40)
            self.status_label.config(text="")
            return

        self.empty_label.pack_forget()
        self.tree.pack(side="left", fill="both", expand=True)

        for row in rows:
            self.tree.insert("", "end", values=row)

        self.status_label.config(
            text=f"آخر تحديث: {len(rows)} نتيجة معروضة (تحديث كل "
            f"{POLL_INTERVAL_MS // 1000} ثانية)"
        )


def main():
    root = tk.Tk()
    CBCResultsWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()
