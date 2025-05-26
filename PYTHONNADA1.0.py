import tkinter as tk
from tkhtmlview import HTMLLabel
from PIL import Image, ImageTk
import calendar
import requests
from datetime import datetime, timedelta
import time
import json
import os
import sys
from cefpython3 import cefpython as cef
import threading
import platform
import subprocess
from io import BytesIO
import feedparser
import re
subprocess.Popen(['python', 'WATERMARKPY1.0.py'], creationflags=subprocess.CREATE_NEW_CONSOLE)

GADGETS_FILE = "gadgets.json"
WEATHER_CITY_FILE = "citypogoda.json"
DESK_WALLPAPER_FILE = "deskwallpaper.json"
RSS_SETTINGS_FILE = "rss_settings.json"

root = tk.Tk()
root.attributes('-fullscreen', True)
root.wm_attributes("-transparentcolor", "pink")
root.configure(bg="pink")

desktop_label = tk.Label(root, bg="pink")
desktop_label.place(relwidth=1, relheight=1)

taskbar = tk.Frame(root, height=40, bg="#0078D7")
taskbar.pack(side="bottom", fill="x")

clock_area = tk.Frame(taskbar, bg="#0078D7")
clock_area.pack(side="right")
clock_label = tk.Label(clock_area, font=("Arial", 14), fg="black")
clock_label.pack(pady=5, padx=5)

def update_time():
    clock_label.config(text=time.strftime("%H:%M:%S"))
    root.after(1000, update_time)

update_time()

sidebar = tk.Frame(root, width=220, bg="#2C2C2C")
sidebar.pack(side="right", fill="y")

top_panel = tk.Frame(sidebar, bg="#2C2C2C")
top_panel.pack(side="top", fill="both", expand=True)

def open_gadget_chooser(event=None):
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Часы", command=add_clock_widget)
    menu.add_command(label="HTML-страница", command=add_html_widget)
    menu.add_command(label="Фотографии", command=add_photosslideshow_widget)
    menu.add_command(label="Калькулятор", command=add_calculator_widget)
    menu.add_command(label="Календарь", command=add_calendar_widget)
    menu.add_command(label="Простой файловый проводник", command=add_file_explorer_widget)
    menu.add_command(label="Простая Погода", command=add_weather_widget)
    menu.add_command(label="Простые RSS Новости", command=add_rss_widget)
    menu.add_command(label="CMD", command=add_real_cmd_widget)
    menu.add_command(label="Webview Browser", command=add_browser_widget)

    x = add_button.winfo_rootx()
    y = add_button.winfo_rooty() + add_button.winfo_height()
    menu.tk_popup(x, y)

add_button = tk.Button(top_panel, text="+", font=("Arial", 16), bg="#404040", fg="white", command=open_gadget_chooser)
add_button.pack(anchor="ne", pady=5, padx=5)

gadget_area = tk.Frame(top_panel, bg="#2C2C2C")
gadget_area.pack(side="top", fill="both", expand=True)

gadgets = []

def save_gadgets():
    gadgets.clear()
    for child in gadget_area.winfo_children():
        gadgets.append({"type": getattr(child, "gadget_type", "unknown")})
    with open(GADGETS_FILE, "w") as f:
        json.dump(gadgets, f)

def make_draggable(widget):
    def start(event):
        widget._start_y = event.y_root
        widget.lift()

    def on_drag(event):
        dy = event.y_root - widget._start_y
        widget._start_y = event.y_root
        widget.place_configure(y=widget.winfo_y() + dy)

    def stop(event):
        widget.place_forget()
        widget.pack(padx=5, pady=5, fill="x")
        save_gadgets()

    widget.bind("<Button-1>", start)
    widget.bind("<B1-Motion>", on_drag)
    widget.bind("<ButtonRelease-1>", stop)

def make_removable(widget):
    menu = tk.Menu(widget, tearoff=0)
    menu.add_command(label="Удалить", command=lambda: remove(widget))

    def show_menu(event):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    widget.bind("<Button-3>", show_menu)

def remove(widget):
    widget.destroy()
    save_gadgets()

def add_clock_widget(save=True):
    frame = tk.Frame(gadget_area, bg="#202020", bd=1, relief="sunken")
    frame.gadget_type = "clock"

    label = tk.Label(frame, font=("Arial", 18), fg="white", bg="#202020")
    label.pack(padx=10, pady=10)

    def update():
        label.config(text=time.strftime("%H:%M:%S"))
        label.after(1000, update)

    update()
    frame.pack(padx=5, pady=5, fill="x")
    make_removable(frame)
    make_draggable(frame)
    if save:
        save_gadgets()

def add_real_cmd_widget(save=True):
    frame = tk.Frame(gadget_area, bg="black", bd=1, relief="sunken")
    frame.gadget_type = "real_cmd"

    text = tk.Text(frame, bg="black", fg="white", insertbackground="white", font=("Consolas", 10), height=15)
    text.config(state="disabled")
    text.pack(fill="both", expand=True)

    entry = tk.Entry(frame, bg="black", fg="white", insertbackground="white", font=("Consolas", 10))
    entry.pack(fill="x")

    process = subprocess.Popen(
        "cmd.exe /K chcp 65001",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        text=True,
        bufsize=1,
        encoding="utf-8"
    )

    def read_output():
        while True:
            try:
                output = process.stdout.readline()
                if not output:
                    break
                text.config(state="normal")
                text.insert("end", output)
                text.see("end")
                text.config(state="disabled")
            except UnicodeDecodeError:
                continue


    threading.Thread(target=read_output, daemon=True).start()

    def run_command(event=None):
        cmd = entry.get()
        entry.delete(0, "end")
        text.config(state="normal")
        text.insert("end", f"> {cmd}\n")
        text.config(state="disabled")
        text.see("end")
        process.stdin.write(cmd + "\n")
        process.stdin.flush()

    entry.bind("<Return>", run_command)

    frame.pack(padx=5, pady=5, fill="x")
    make_removable(frame)
    make_draggable(frame)
    if save:
        save_gadgets()

def add_calendar_widget(save=True):
    frame = tk.Frame(gadget_area, bg="#202020", bd=1, relief="sunken")
    frame.gadget_type = "calendar"

    current_date = datetime.today().replace(day=1)

    header = tk.Frame(frame, bg="#303030")
    header.pack(fill="x", padx=5, pady=5)

    def prev_month():
        nonlocal current_date
        first = current_date.replace(day=1)
        current_date = (first - timedelta(days=1)).replace(day=1)
        update_calendar()

    def next_month():
        nonlocal current_date
        year = current_date.year + (current_date.month // 12)
        month = current_date.month % 12 + 1
        current_date = current_date.replace(year=year, month=month, day=1)
        update_calendar()

    btn_prev = tk.Button(header, text="<", command=prev_month, bg="#404040", fg="white", width=3)
    btn_prev.pack(side="left")

    month_label = tk.Label(header, bg="#303030", fg="white", font=("Arial", 14, "bold"))
    month_label.pack(side="left", expand=True)

    btn_next = tk.Button(header, text=">", command=next_month, bg="#404040", fg="white", width=3)
    btn_next.pack(side="right")

    calendar_frame = tk.Frame(frame, bg="#202020")
    calendar_frame.pack(padx=5, pady=5, fill="both")

    def update_calendar():
        month_label.config(text=current_date.strftime("%B %Y"))

        for widget in calendar_frame.winfo_children():
            widget.destroy()

        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        for i, day in enumerate(days):
            lbl = tk.Label(calendar_frame, text=day, bg="#404040", fg="white", font=("Arial", 10, "bold"), width=4)
            lbl.grid(row=0, column=i, padx=1, pady=1)

        cal = calendar.Calendar(firstweekday=0)

        row = 1
        col = 0

        for day in cal.itermonthdays(current_date.year, current_date.month):
            if day == 0:
                lbl = tk.Label(calendar_frame, text="", bg="#202020", width=4, height=2)
                lbl.grid(row=row, column=col, padx=1, pady=1)
            else:
                lbl = tk.Label(calendar_frame, text=str(day), bg="#303030", fg="white",
                               width=4, height=2, font=("Arial", 11))
                today = datetime.today()
                if (current_date.year, current_date.month, day) == (today.year, today.month, today.day):
                    lbl.config(bg="#0078D7")
                lbl.grid(row=row, column=col, padx=1, pady=1)
            col += 1
            if col > 6:
                col = 0
                row += 1

    update_calendar()

    frame.pack(padx=5, pady=5, fill="x")
    make_removable(frame)
    make_draggable(frame)
    if save:
        save_gadgets()

def add_browser_widget(save=True):
    frame = tk.Frame(gadget_area, bg="#202020", bd=1, relief="sunken")
    frame.gadget_type = "browser"

    header = tk.Frame(frame, bg="#404040")
    header.pack(fill="x")

    tk.Label(header, text="Браузер", bg="#404040", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
    tk.Button(header, text="×", bg="#404040", fg="white", bd=0, font=("Arial", 12),
              command=lambda: frame.destroy()).pack(side="right", padx=5)

    browser_frame = tk.Frame(frame, bg="#202020", width=500, height=400)
    browser_frame.pack(fill="both", expand=True)

    def init_browser():
        sys.excepthook = cef.ExceptHook
        cef.Initialize()

        window_info = cef.WindowInfo()
        window_info.SetAsChild(browser_frame.winfo_id(), [
            0, 0, browser_frame.winfo_width(), browser_frame.winfo_height()
        ])
        browser = cef.CreateBrowserSync(window_info, url="https://www.google.com")

        def on_configure(event):
            if browser:
                browser.SetBounds(0, 0, event.width, event.height)
                browser.NotifyMoveOrResizeStarted()

        browser_frame.bind("<Configure>", on_configure)

        def cef_loop():
            cef.MessageLoopWork()
            browser_frame.after(10, cef_loop)

        cef_loop()

    browser_frame.after(100, init_browser)

    make_draggable(frame)
    make_removable(frame)
    frame.pack(padx=5, pady=5, fill="both", expand=True)

    if save:
        save_gadgets()

def add_weather_widget(save=True):
    frame = tk.Frame(gadget_area, bg="#202020", bd=1, relief="sunken")
    frame.gadget_type = "weather"

    def load_city():
        if os.path.exists(WEATHER_CITY_FILE):
            with open(WEATHER_CITY_FILE, "r") as f:
                data = json.load(f)
            return data.get("city", "Kyiv")
        return "Kyiv"

    def save_city(city):
        with open(WEATHER_CITY_FILE, "w") as f:
            json.dump({"city": city}, f)

    city = load_city()

    header = tk.Frame(frame, bg="#303030")
    header.pack(fill="x", padx=5, pady=5)

    city_label = tk.Label(header, text=city, fg="white", bg="#303030", font=("Arial", 12))
    city_label.pack(side="left")

    btn_refresh = tk.Button(header, text="🔄", command=lambda: get_weather(city), bg="#404040", fg="white", width=3)
    btn_refresh.pack(side="right", padx=2)

    btn_settings = tk.Button(header, text="⚙", command=lambda: toggle_settings(), bg="#404040", fg="white", width=3)
    btn_settings.pack(side="right", padx=2)

    content = tk.Frame(frame, bg="#202020")
    content.pack(padx=5, pady=5)

    current_label = tk.Label(content, text="Загрузка...", fg="white", bg="#202020", font=("Arial", 12), wraplength=200, justify="left")
    current_label.pack(anchor="w")

    forecast_frame = tk.Frame(content, bg="#202020")
    forecast_frame.pack(anchor="w", pady=5)

    settings_frame = tk.Frame(frame, bg="#202020")
    settings_visible = [False]

    city_entry = tk.Entry(settings_frame)
    city_entry.insert(0, city)
    city_entry.pack(side="left", padx=5, pady=5)

    def apply_settings():
        new_city = city_entry.get().strip()
        if new_city:
            save_city(new_city)
            city_label.config(text=new_city)
            get_weather(new_city)
            toggle_settings()

    apply_btn = tk.Button(settings_frame, text="Применить", command=apply_settings, bg="#404040", fg="white")
    apply_btn.pack(side="left", padx=5)

    def toggle_settings():
        if settings_visible[0]:
            settings_frame.pack_forget()
        else:
            settings_frame.pack(fill="x", padx=5, pady=5)
        settings_visible[0] = not settings_visible[0]

    def get_weather(city_name):
        url = f"https://wttr.in/{city_name}?format=j1"
        try:
            response = requests.get(url)
            data = response.json()

            current = data["current_condition"][0]
            temp = current["temp_C"]
            desc = current["weatherDesc"][0]["value"]
            current_label.config(text=f"Сейчас: {temp}°C, {desc}")

            for widget in forecast_frame.winfo_children():
                widget.destroy()

            weather = data["weather"][:3]
            for day in weather:
                date = day["date"]
                avg_temp = day["avgtempC"]
                condition = day["hourly"][4]["weatherDesc"][0]["value"]
                label = tk.Label(forecast_frame, text=f"{date}: {avg_temp}°C, {condition}", fg="white", bg="#202020", anchor="w", justify="left")
                label.pack(anchor="w")
        except Exception:
            current_label.config(text="Ошибка соединения")
            for widget in forecast_frame.winfo_children():
                widget.destroy()

    get_weather(city)

    frame.pack(padx=5, pady=5, fill="x")
    make_removable(frame)
    make_draggable(frame)
    if save:
        save_gadgets()

def add_rss_widget(save=True):
    frame = tk.Frame(gadget_area, bg="#202020", bd=1, relief="sunken")
    frame.gadget_type = "rss"

    default_sources = {
        "Россия (Яндекс)": "https://news.yandex.ru/index.rss",
        "Украина (Правда)": "https://www.pravda.com.ua/rss/",
        "Беларусь (БелаПАН)": "https://belapan.by/rss/",
        "Свой RSS": ""
    }

    def load_rss_url():
        if os.path.exists(RSS_SETTINGS_FILE):
            with open(RSS_SETTINGS_FILE, "r") as f:
                data = json.load(f)
            return data.get("rss", default_sources["Россия (Яндекс)"])
        return default_sources["Россия (Яндекс)"]

    def save_rss_url(url):
        with open(RSS_SETTINGS_FILE, "w") as f:
            json.dump({"rss": url}, f)

    rss_url = load_rss_url()

    header = tk.Frame(frame, bg="#303030")
    header.pack(fill="x", padx=5, pady=5)

    rss_label = tk.Label(header, text="Новости", fg="white", bg="#303030", font=("Arial", 12))
    rss_label.pack(side="left")

    btn_refresh = tk.Button(header, text="🔄", command=lambda: load_rss(rss_url), bg="#404040", fg="white", width=3)
    btn_refresh.pack(side="right", padx=2)

    btn_settings = tk.Button(header, text="⚙", command=lambda: toggle_settings(), bg="#404040", fg="white", width=3)
    btn_settings.pack(side="right", padx=2)

    content = tk.Frame(frame, bg="#202020")
    content.pack(padx=5, pady=5, fill="both", expand=True)

    canvas = tk.Canvas(content, bg="#202020", highlightthickness=0)
    scrollbar = tk.Scrollbar(content, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#202020")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    news_widgets = []

    def clear_news():
        for w in news_widgets:
            w.destroy()
        news_widgets.clear()

    def clean_html(raw_html):
        text = re.sub(r'<br\s*/?>', '\n', raw_html, flags=re.I)
        text = re.sub(r'</p>', '\n', text, flags=re.I)
        text = re.sub(r'<.*?>', '', text)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&amp;', '&', text)
        text = re.sub(r'&quot;', '"', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        return text.strip()

    def load_rss(url):
        clear_news()
        try:
            feed = feedparser.parse(url)
            if not feed.entries:
                lbl = tk.Label(scrollable_frame, text="Нет новостей", fg="white", bg="#202020", font=("Arial", 11))
                lbl.pack(anchor="w", pady=5)
                news_widgets.append(lbl)
                return

            for entry in feed.entries[:5]:
                title_lbl = tk.Label(scrollable_frame, text=entry.title, fg="#55aaff", bg="#202020", font=("Arial", 12, "bold"), cursor="hand2", wraplength=350, justify="left")
                title_lbl.pack(anchor="w", pady=(10,0))
                title_lbl.bind("<Button-1>", lambda e, url=entry.link: webbrowser.open(url))
                news_widgets.append(title_lbl)

                description = getattr(entry, "description", "") or getattr(entry, "summary", "")
                description_clean = clean_html(description)
                desc_lbl = tk.Label(scrollable_frame, text=description_clean, fg="white", bg="#202020", font=("Arial", 10), wraplength=350, justify="left")
                desc_lbl.pack(anchor="w")
                news_widgets.append(desc_lbl)

                img_url = None
                if "media_content" in entry and entry.media_content:
                    img_url = entry.media_content[0].get("url", None)
                elif "enclosures" in entry and entry.enclosures:
                    for enc in entry.enclosures:
                        if enc.get("type", "").startswith("image"):
                            img_url = enc.get("href", None)
                            break

                if img_url:
                    try:
                        resp = requests.get(img_url, timeout=5)
                        img_data = resp.content
                        image = Image.open(BytesIO(img_data))
                        image.thumbnail((350, 150))
                        photo = ImageTk.PhotoImage(image)

                        img_lbl = tk.Label(scrollable_frame, image=photo, bg="#202020")
                        img_lbl.image = photo
                        img_lbl.pack(anchor="w", pady=5)
                        news_widgets.append(img_lbl)
                    except Exception:
                        pass

        except Exception as e:
            lbl = tk.Label(scrollable_frame, text=f"Ошибка загрузки: {e}", fg="white", bg="#202020", font=("Arial", 11))
            lbl.pack(anchor="w", pady=5)
            news_widgets.append(lbl)

    settings_frame = tk.Frame(frame, bg="#202020")
    settings_visible = [False]

    selected_var = tk.StringVar()
    selected_var.set("Свой RSS")

    url_entry = tk.Entry(settings_frame, width=45)
    url_entry.insert(0, rss_url)
    url_entry.pack(side="bottom", padx=5, pady=5)

    def on_source_select(*args):
        selected = selected_var.get()
        if selected != "Свой RSS":
            url_entry.delete(0, tk.END)
            url_entry.insert(0, default_sources[selected])

    source_menu = tk.OptionMenu(settings_frame, selected_var, *default_sources.keys(), command=on_source_select)
    source_menu.config(bg="#404040", fg="white", width=25)
    source_menu.pack(side="top", padx=5, pady=5)

    def apply_settings():
        new_url = url_entry.get().strip()
        if new_url:
            nonlocal rss_url
            rss_url = new_url
            save_rss_url(new_url)
            load_rss(new_url)
            toggle_settings()
            load_rss(new_url)

    apply_btn = tk.Button(settings_frame, text="Применить", command=apply_settings, bg="#404040", fg="white")
    apply_btn.pack(pady=5)

    def toggle_settings():
        if settings_visible[0]:
            settings_frame.pack_forget()
        else:
            settings_frame.pack(fill="x", padx=5, pady=5)
        settings_visible[0] = not settings_visible[0]

    load_rss(rss_url)

    frame.pack(padx=5, pady=5, fill="x")
    make_removable(frame)
    make_draggable(frame)
    if save:
        save_gadgets()

def add_file_explorer_widget(save=True):
    frame = tk.Frame(gadget_area, bg="#202020", bd=1, relief="sunken")
    frame.gadget_type = "file_explorer"

    path_var = tk.StringVar()

    nav_frame = tk.Frame(frame, bg="#303030")
    nav_frame.pack(fill="x", padx=5, pady=5)

    back_button = tk.Button(nav_frame, text="← Назад", bg="#404040", fg="white", bd=0)
    back_button.pack(side="left")

    path_label = tk.Label(nav_frame, textvariable=path_var, fg="white", bg="#303030", anchor="w")
    path_label.pack(side="left", fill="x", expand=True, padx=5)

    listbox = tk.Listbox(frame, bg="#202020", fg="white", bd=0, font=("Arial", 12))
    listbox.pack(fill="both", expand=True, padx=5, pady=(0,5))

    history = []

    def get_drives():
        system = platform.system()
        drives = []
        if system == "Windows":
            import string
            for letter in string.ascii_uppercase:
                drive = letter + ":\\"
                if os.path.exists(drive):
                    drives.append(drive)
        else:
            drives = ["/"]
        return drives

    def show_drives():
        listbox.delete(0, tk.END)
        drives = get_drives()
        for d in drives:
            listbox.insert(tk.END, d)
        path_var.set("Выбор диска")
        back_button.config(state="disabled")
        listbox.bind("<Double-Button-1>", on_drive_select)

    def load_path(path):
        if not os.path.exists(path):
            print(f"Путь не существует: {path}")
            if history:
                prev = history.pop()
                if prev == "__DRIVES__":
                    show_drives()
                else:
                    load_path(prev)
            return

        try:
            entries = os.listdir(path)
        except PermissionError:
            entries = []
        entries.sort(key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))

        listbox.delete(0, tk.END)
        for e in entries:
            full_path = os.path.join(path, e)
            display_name = e + ("/" if os.path.isdir(full_path) else "")
            listbox.insert(tk.END, display_name)
        path_var.set(path)
        back_button.config(state="normal" if history else "disabled")

        listbox.unbind("<Double-Button-1>")
        listbox.bind("<Double-Button-1>", on_select)

    def on_drive_select(event):
        if not listbox.curselection():
            return
        idx = listbox.curselection()[0]
        drive = listbox.get(idx)
        history.append("__DRIVES__")
        load_path(drive)

    def on_select(event):
        if not listbox.curselection():
            return
        index = listbox.curselection()[0]
        selected = listbox.get(index)
        current_path = path_var.get()
        selected_name = selected.rstrip("/")
        selected_path = os.path.join(current_path, selected_name)

        if os.path.isdir(selected_path):
            if current_path not in history:
                history.append(current_path)
            load_path(selected_path)
        else:
            try:
                if platform.system() == "Windows":
                    os.startfile(selected_path)
                elif platform.system() == "Darwin":
                    subprocess.run(["open", selected_path])
                else:
                    subprocess.run(["xdg-open", selected_path])
            except Exception as e:
                print("Ошибка открытия файла:", e)

    def go_back():
        if history:
            prev_path = history.pop()
            if prev_path == "__DRIVES__":
                show_drives()
            else:
                load_path(prev_path)
        else:
            back_button.config(state="disabled")

    back_button.config(command=go_back)

    show_drives()

    make_removable(frame)
    make_draggable(frame)
    frame.pack(padx=5, pady=5, fill="both", expand=False)

    if save:
        save_gadgets()

def add_calculator_widget(save=True):
    frame = tk.Frame(gadget_area, bg="#202020", bd=1, relief="sunken")
    frame.gadget_type = "calculator"

    entry = tk.Entry(frame, font=("Arial", 16), bg="#303030", fg="white", bd=0, justify="right")
    entry.pack(fill="x", padx=10, pady=(10,5))

    def on_button_click(char):
        if char == "C":
            entry.delete(0, tk.END)
        elif char == "=":
            expr = entry.get()
            try:
                result = str(eval(expr))
                entry.delete(0, tk.END)
                entry.insert(tk.END, result)
            except Exception:
                entry.delete(0, tk.END)
                entry.insert(tk.END, "Ошибка")
        else:
            entry.insert(tk.END, char)

    buttons = [
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["0", ".", "C", "+"],
        ["="]
    ]

    btn_frame = tk.Frame(frame, bg="#202020")
    btn_frame.pack(padx=10, pady=5)

    for row in buttons:
        row_frame = tk.Frame(btn_frame, bg="#202020")
        row_frame.pack(fill="x", pady=2)
        for b in row:
            btn = tk.Button(row_frame, text=b, font=("Arial", 14), fg="white", bg="#404040", bd=0, 
                            width=4, height=2,
                            command=lambda char=b: on_button_click(char))
            btn.pack(side="left", padx=3)

    make_removable(frame)
    make_draggable(frame)
    frame.pack(padx=5, pady=5, fill="x")

    if save:
        save_gadgets()

def add_html_widget(save=True):
    frame = tk.Frame(gadget_area, bg="white", bd=1, relief="sunken")
    frame.gadget_type = "html"

    html_content = """
<h1>Your text here. (h1)</h1>
<p>Hello World! (p)</p>
    """
    html_label = HTMLLabel(frame, html=html_content)
    html_label.pack(padx=5, pady=5)

    frame.pack(padx=5, pady=5, fill="x")
    make_removable(frame)
    make_draggable(frame)
    if save:
        save_gadgets()

wallpaper_win = None

def add_photosslideshow_widget(save=True):
    images = [
        r"C:/Windows/Web/wallpaper/windows/IMG_20250418_123437.jpg",
        r"C:/Windows/Web/wallpaper/windows/img0.jpg",
    ]

    frame = tk.Frame(gadget_area, bg="#202020", bd=1, relief="sunken")
    frame.gadget_type = "slideshow"

    photos = []

    for img_path in images:
        img = Image.open(img_path)
        img = img.resize((180, 120))
        photo = ImageTk.PhotoImage(img)
        photos.append(photo)

    current_index = 0

    label = tk.Label(frame, image=photos[current_index], bg="#202020")
    label.photos = photos
    label.pack(side="left", padx=5, pady=5)

    def show_image(index):
        nonlocal current_index
        current_index = index % len(photos)
        label.config(image=photos[current_index])

    def prev_image():
        show_image(current_index - 1)

    def next_image():
        show_image(current_index + 1)

    btn_prev = tk.Button(frame, text="<", command=prev_image, bg="#404040", fg="white")
    btn_next = tk.Button(frame, text=">", command=next_image, bg="#404040", fg="white")

    btn_prev.pack(side="left", padx=5, pady=5)
    btn_next.pack(side="right", padx=5, pady=5)

    def set_desktop_wallpaper(image_path):
        global wallpaper_win
        if wallpaper_win is not None and wallpaper_win.winfo_exists():
            wallpaper_win.destroy()

        wallpaper_win = tk.Toplevel(root)
        wallpaper_win.wm_attributes("-disabled", True)
        wallpaper_win.attributes("-fullscreen", True)
        wallpaper_win.attributes("-topmost", False)
        wallpaper_win.lower()
        wallpaper_win.overrideredirect(True)

        img = Image.open(image_path)
        screen_width = wallpaper_win.winfo_screenwidth()
        screen_height = wallpaper_win.winfo_screenheight()
        img = img.resize((screen_width, screen_height), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)

        label_wallpaper = tk.Label(wallpaper_win, image=photo)
        label_wallpaper.image = photo
        label_wallpaper.pack(fill="both", expand=True)

        with open(DESK_WALLPAPER_FILE, "w") as f:
            json.dump({"image": image_path}, f)

    menu = tk.Menu(frame, tearoff=0)
    def on_set_wallpaper():
        set_desktop_wallpaper(images[current_index])
    menu.add_command(label="Установить на рабочий стол", command=on_set_wallpaper)

    def show_menu(event):
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    label.bind("<Button-3>", show_menu)

    frame.pack(padx=5, pady=5, fill="x")
    make_removable(frame)
    make_draggable(frame)
    if save:
        save_gadgets()

    if os.path.exists(DESK_WALLPAPER_FILE):
        try:
            with open(DESK_WALLPAPER_FILE, "r") as f:
                data = json.load(f)
            image_path = data.get("image")
            if image_path and os.path.exists(image_path):
                set_desktop_wallpaper(image_path)
        except Exception as e:
            print("Ошибка при загрузке обоев:", e)

def load_gadgets():
    if not os.path.exists(GADGETS_FILE):
        return
    with open(GADGETS_FILE, "r") as f:
        loaded = json.load(f)
    for g in loaded:
        if g["type"] == "clock":
            add_clock_widget()
        elif g["type"] == "html":
            add_html_widget()
        elif g["type"] == "slideshow":
            add_photosslideshow_widget()
        elif g["type"] == "calculator":
            add_calculator_widget()
        elif g["type"] == "file_explorer":
            add_file_explorer_widget()
        elif g["type"] == "calendar":
            add_calendar_widget()
        elif g["type"] == "weather":
            add_weather_widget()
        elif g["type"] == "rss":
            add_rss_widget()
        elif g["type"] == "real_cmd":
            add_real_cmd_widget()
        elif g["type"] == "browser":
            add_browser_widget()

root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

load_gadgets()

root.mainloop()