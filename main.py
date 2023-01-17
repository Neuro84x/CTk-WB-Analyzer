import os.path
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import sys
import math
import subprocess
import time
import json

with open('settings.json', 'r', encoding='utf-8') as settings:
    attributes = json.load(settings)
    dateStock = attributes['dateStock']


class Application(ctk.CTk):
    def __init__(self):
        ctk.CTk.__init__(self)
        self.geometry('1450x850')
        self.title('Аналитика CUTECASELLC')
        self.set_UI()

    def set_UI(self):
        # --------------------------------REFRESH----------------------------------------------------------------------#
        self.refresh_button = ctk.CTkButton(self, text='Обновить', command=self.refresh)
        self.refresh_button.grid()
        self.refresh_label = ctk.CTkLabel(self, text="Обновление не запущено")
        self.refresh_label.grid()

        # --------------------------------STATUS-----------------------------------------------------------------------#
        self.bar = ctk.CTkFrame(self)
        self.bar.grid()

        self.article_status_label = ctk.CTkLabel(self.bar, text='Статус')
        self.article_status_label.grid()
        self.article_status = ctk.CTkComboBox(self.bar, values=['Все', 'Критично', 'Внимание', 'Четко'],
                                              state='readonly', text_color='Black', command=self.make_data_table)
        self.article_status.set('Все')
        self.article_status.grid()

        # ----------------------------------DATA-----------------------------------------------------------------------#
        self.sort_statuses = ('-', 'v', '^')
        self.active_sort_status = 0

        self.data_list = []
        if not os.path.exists(f'data{dateStock}.txt'):
            self.refresh()
        else:
            with open(f'data{dateStock}.txt', 'r') as r:
                idx = 0
                for i in r:
                    self.data_list.append(i.split(sep=','))
                    self.data_list[idx][0] = self.data_list[idx][0][2:-1]
                    self.data_list[idx][1] = int(self.data_list[idx][1])
                    self.data_list[idx][2] = int(self.data_list[idx][2])
                    self.data_list[idx][3] = math.ceil(float(self.data_list[idx][3][1:-2]))
                    idx += 1
        treestyle = ttk.Style()
        treestyle.theme_use('default')
        treestyle.configure("Treeview", rowheight=20, background=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1],
                            foreground=ctk.ThemeManager.theme["CTkLabel"]["text_color"][1],
                            fieldbackground=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1],
                            borderwidth=0)
        treestyle.configure("Treeview.Heading", background=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1],
                            foreground=ctk.ThemeManager.theme["CTkLabel"]["text_color"][1],
                            fieldbackground=ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1],
                            borderwidth=0)
        treestyle.map('Treeview',
                      background=[('selected', ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1])],
                      foreground=[('selected', ctk.ThemeManager.theme["CTkButton"]["fg_color"][1])])
        self._img_red = tk.PhotoImage(file='power-off.png')
        self._img_yellow = tk.PhotoImage(file='warning-sign.png')
        self._img_green = tk.PhotoImage(file='check.png')

        self.bind("<<TreeviewSelect>>", lambda event: self.focus_set())

        data_columns = ('article', 'amount', 'shortage', 'storage_central', 'storage_south', 'storage_west')
        self.data_frame = ctk.CTkFrame(self, width=1080)
        self.data_frame.grid()

        self.data = ttk.Treeview(self.data_frame, columns=data_columns, height=30,
                                 selectmode='extended', show='tree headings')

        self.scrollbar = ttk.Scrollbar(self.data_frame, orient=ctk.VERTICAL, command=self.data.yview)
        self.data.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.grid(row=0, column=1, sticky='ns')
        self.data.heading('article', text='Артикль')
        self.data.heading('amount', text='Количество')
        # self.data.heading('status', text='Статус')
        self.data.heading('shortage', text='Недостаток -',
                          command=self.sort_data)
        self.data.heading('storage_central', text='ЦФО')
        self.data.heading('storage_south', text='Юг')
        self.data.heading('storage_west', text='Восток')

        self.make_data_table()
        self.data.grid()

        # ----------------------------------SETTINGS-------------------------------------------------------------------#

        # ----------------------------------EXIT-----------------------------------------------------------------------#
        exit_button = ctk.CTkButton(self, text='Выход', command=self.app_exit)
        exit_button.grid()

    def app_exit(self):
        self.destroy()
        sys.exit()

    def make_data_table(self, event=None, internal_data_list=[]):
        if len(internal_data_list) == 0:
            internal_data_list = self.data_list

        if event in ('Все', 'Критично', 'Внимание', 'Четко'):
            for i in self.data.get_children():
                self.data.delete(i)

        status = self.article_status.get()
        if status == 'Все':
            for i in internal_data_list:
                if i[2] == 0:
                    self.data.insert("", ctk.END,
                                     values=(i[0], i[1], i[3],
                                             math.ceil(i[3] / 100 * 50), #ЦФО
                                             math.ceil(i[3] / 100 * 20), #ЮГ
                                             math.ceil(i[3] / 100 * 30)  #ВОСТОК
                                             ),
                                     tag='red', image=self._img_red)
                elif i[2] == 1:
                    self.data.insert("", ctk.END, values=(i[0], i[1], i[3],
                                             math.ceil(i[3] / 100 * 50), #ЦФО
                                             math.ceil(i[3] / 100 * 20), #ЮГ
                                             math.ceil(i[3] / 100 * 30)  #ВОСТОК
                                             ), tag='yellow', image=self._img_yellow)
                elif i[2] == 2:
                    self.data.insert("", ctk.END, values=(i[0], i[1], i[3],
                                             math.ceil(i[3] / 100 * 50), #ЦФО
                                             math.ceil(i[3] / 100 * 20), #ЮГ
                                             math.ceil(i[3] / 100 * 30)  #ВОСТОК
                                             ), tag='green', image=self._img_green)
        elif status == 'Критично':
            for i in self.data_list:
                if i[2] == 0:
                    self.data.insert("", ctk.END, values=(i[0], i[1], i[3],
                                             math.ceil(i[3] / 100 * 50), #ЦФО
                                             math.ceil(i[3] / 100 * 20), #ЮГ
                                             math.ceil(i[3] / 100 * 30)  #ВОСТОК
                                             ), tag='red', image=self._img_red)
        elif status == 'Внимание':
            for i in self.data_list:
                if i[2] == 1:
                    self.data.insert("", ctk.END, vvalues=(i[0], i[1], i[3],
                                             math.ceil(i[3] / 100 * 50), #ЦФО
                                             math.ceil(i[3] / 100 * 20), #ЮГ
                                             math.ceil(i[3] / 100 * 30)  #ВОСТОК
                                             ), tag='yellow', image=self._img_yellow)
        elif status == 'Четко':
            for i in self.data_list:
                if i[2] == 2:
                    self.data.insert("", ctk.END, values=(i[0], i[1], i[3],
                                             math.ceil(i[3] / 100 * 50), #ЦФО
                                             math.ceil(i[3] / 100 * 20), #ЮГ
                                             math.ceil(i[3] / 100 * 30)  #ВОСТОК
                                             ), tag='green', image=self._img_green)
            # self.data.tag_configure('red', background='red')
            # self.data.tag_configure('yellow', background='yellow')
            # self.data.tag_configure('green', background='green')

    def refresh(self):
        self.update_refresh_label('Обновление запущено')
        subprocess.Popen([sys.executable, 'wb_api.py'])
        print('wb_api started')
        if not os.path.exists(f'data{dateStock}.txt'):
            start = time.perf_counter()
            while time.perf_counter() - start < 70:
                time.sleep(1)
                stage = int(time.perf_counter() - start)
                print(f'Этап {stage}/70')

        self.update_refresh_label('Обновление завершено')
        self.article_status.set('Все')
        self.make_data_table(event=1)

    def update_refresh_label(self, text='Обновление запущено'):
        self.refresh_label.configure(text=text, require_redraw=True)

    def sort_col(self, data):
        return data[3]

    def sort_data(self, event='sort'):
        if event == 'sort':
            idl = self.data_list
            self.active_sort_status += 1
            print(self.active_sort_status)
            if self.active_sort_status == 0:
                self.data.heading('shortage', text=f'Недостаток {self.sort_statuses[self.active_sort_status]}')
                idl = self.data_list
            elif self.active_sort_status == 1:
                self.data.heading('shortage', text=f'Недостаток {self.sort_statuses[self.active_sort_status]}')
                idl = sorted(self.data_list, key=self.sort_col, reverse=True)
            else:
                self.data.heading('shortage', text=f'Недостаток {self.sort_statuses[self.active_sort_status]}')
                idl = sorted(self.data_list, key=self.sort_col, reverse=False)
                self.active_sort_status = -1
            self.make_data_table(event=self.article_status.get(), internal_data_list=idl)


ctk.set_appearance_mode("dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"
root = Application()

root.mainloop()
