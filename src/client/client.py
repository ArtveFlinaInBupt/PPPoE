# -*- coding: utf-8 -*-
import threading

from .requests import *
from config.project_meta import __project__
from projection import Point2D, Point3D, project

from tkinter import messagebox, simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
import logging


class AddPointDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None):
        self.result = None
        self.latitude_entry = None
        self.longitude_entry = None
        self.latitude = None
        self.longitude = None
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text='经度 (-180 ~ 180): ').grid(row=0)
        tk.Label(master, text='纬度 (-90 ~ 90):').grid(row=1)

        self.longitude_entry = tk.Entry(master)
        self.latitude_entry = tk.Entry(master)

        self.longitude_entry.grid(row=0, column=1)
        self.latitude_entry.grid(row=1, column=1)

        return self.longitude_entry

    def apply(self):
        try:
            longitude = float(self.longitude_entry.get())
            latitude = float(self.latitude_entry.get())
            self.result = Point3D.from_deg(longitude, latitude)
        except ValueError as e:
            messagebox.showerror('出错了！', f'输入不合法！\n{e}')
            self.result = None


class Client(tk.Tk):
    def __init__(self, addr, port):
        super().__init__()

        self.request_grid_button = None
        self.request_total_button = None
        self.point_listbox = None
        self.delete_point_button = None
        self.add_point_button = None
        self.plot = None
        self.server_label = None

        self.server = (addr, port)
        self.title(f'{__project__}/C')
        self.points = []
        self.setup_ui()
        self.mock_data()

        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.run_loop, args=(self.loop,))

    def run_loop(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def mock_data(self):
        mock_coord = (
            # 世界
            # (180, 90), (-180, 90), (-180, -90), (180, -90),

            # 山东
            (117.90, 38.39), (114.81, 36.10), (114.81, 34.38),
            (118.50, 34.38), (119.32, 35.06), (122.87, 36.75),
            (122.87, 38.39),

            # 中国（粗糙）
            # (70, 15), (140, 15), (140, 55), (70, 55),

            # 新加坡
            # (103.60, 1.50), (104.10, 1.50), (104.10, 1.24), (103.60, 1.24),

            # 中国（精细）
            # (72.95, 39.39), (80.24, 29.02), (109.60, 17.33), (122.25, 21.06),
            # (124.63, 39.45), (131.64, 42.68), (136.22, 48.63),
            # (128.66, 49.89), (126.47, 53.54), (119.96, 53.64),
            # (112.76, 45.09), (110.74, 44.77), (110.65, 43.51), (96.50, 43.19),
            # (95.71, 44.77), (91.57, 45.39), (91.49, 47.87), (87.71, 49.49),
            # (73.38, 40.64),
        )
        for coord in mock_coord:
            self.points.append(Point3D.from_deg(coord[0], coord[1]))
            self.point_listbox.insert(tk.END, str(self.points[-1]))
            self.point_listbox.see(tk.END)

    def setup_ui(self):
        self.server_label = tk.Label(
            self, text=f'服务器: {self.server[0]}:{self.server[1]}'
        )
        self.server_label.grid(
            row=0, column=1, padx=5, pady=5, columnspan=2, sticky='w'
        )

        self.plot = FigureCanvasTkAgg(
            plt.Figure(figsize=(13, 8), dpi=120), self
        )
        self.plot.get_tk_widget().grid(
            row=0, column=0, rowspan=6, padx=5, pady=5, sticky='nsew'
        )

        self.add_point_button = tk.Button(
            self, text='添加点', command=self.add_coordinate
        )
        self.add_point_button.grid(
            row=1, column=1, padx=5, sticky='ew'
        )

        self.delete_point_button = tk.Button(
            self, text='删除选中点', command=self.delete_selected
        )
        self.delete_point_button.grid(
            row=2, column=1, padx=5, sticky='ew'
        )

        self.point_listbox = tk.Listbox(self, height=50)
        self.point_listbox.grid(
            row=3, column=1, padx=5, pady=5, sticky='nsew'
        )

        self.request_total_button = tk.Button(
            self, text='查询总人口数',
            command=lambda: self.loop.run_until_complete(self.request_total())
        )
        self.request_total_button.grid(
            row=4, column=1, padx=5, sticky='ew'
        )

        self.request_grid_button = tk.Button(
            self, text='绘制热力图',
            command=lambda: self.loop.run_until_complete(self.request_grid())
        )
        self.request_grid_button.grid(
            row=5, column=1, padx=5, sticky='ew'
        )

    def add_coordinate(self):
        dialog = AddPointDialog(self, '添加坐标点')
        if dialog.result is not None:
            logging.info(f'Point added: {dialog.result}')
            self.points.append(dialog.result)
            self.point_listbox.insert(tk.END, str(dialog.result))
            self.point_listbox.see(tk.END)

    def delete_selected(self):
        try:
            index = self.point_listbox.curselection()[0]
            self.point_listbox.delete(index)
            self.points.pop(index)
        except IndexError:
            messagebox.showerror('出错了！', '没有选中坐标点。')

    async def request_total(self):
        geojson = encap_geojson([project(p) for p in self.points])
        logging.info(f'Requesting total population: {geojson}')
        url = f'{self.server[0]}:{self.server[1]}/api/total'
        response = await request(url, {'geometry': geojson})

        logging.info(f'Response: {response}')
        if 'error' in response:
            messagebox.showerror('出错了！', response['error'])
        else:
            messagebox.showinfo(
                '总人口',
                f'总人口: {int(response["population"])}'
            )

    async def request_grid(self):
        points2d = [project(p) for p in self.points]
        max_x = max(p.x for p in points2d)
        min_x = min(p.x for p in points2d)
        max_y = max(p.y for p in points2d)
        min_y = min(p.y for p in points2d)
        grid_count = min(100, max(max_x - min_x, max_y - min_y) // 3)
        width = max(1, (max_x - min_x) // grid_count)

        geojson = encap_geojson([project(p) for p in self.points])
        logging.info(f'Requesting grid population: {geojson}')
        url = f'{self.server[0]}:{self.server[1]}/api/grid'
        response = await request(url, {
            'geometry': geojson,
            'grid_width': width
        })

        logging.info(f'Response: {response}')
        if 'error' in response:
            messagebox.showerror('出错了！', response['error'])
        else:
            self.plot_data(response['grid'])

    def plot_data(self, data):
        max_lat = max(p.latitude for p in self.points)
        min_lat = min(p.latitude for p in self.points)
        max_lon = max(p.longitude for p in self.points)
        min_lon = min(p.longitude for p in self.points)
        data = np.array(data)
        data = np.where(data == -1, np.nan, data)
        data = np.log2(data, out=np.zeros_like(data), where=(data != 0))

        # draw heatmap
        self.plot.figure.clear()
        ax = self.plot.figure.subplots()
        ax.set_title('热力图')
        ax.invert_yaxis()

        if data.shape[0] <= 90 and data.shape[1] <= 90:
            ax.set_xlabel('经度')
            ax.set_ylabel('纬度')
            ax.set_xticks(range(data.shape[1]))
            ax.set_yticks(range(data.shape[0]))

            lon_sticks = np.linspace(min_lon, max_lon, data.shape[1])
            lat_sticks = np.linspace(min_lat, max_lat, data.shape[0])
            ax.set_xticklabels([f'{x:.3g}' for x in lon_sticks])
            ax.set_yticklabels([f'{x:.3g}' for x in lat_sticks])
            ax.tick_params(axis='both', labelsize=6)
        else:
            ax.set_xlabel('[坐标轴过长忽略]')
            ax.set_xticks([])
            ax.set_yticks([])

        im = ax.imshow(data, interpolation='nearest', cmap='viridis')
        self.plot.figure.colorbar(im, format="2^{x:.0f}",
                                  label='相对人口密度（对数）')

        plt.xlim((min_lon, max_lon))
        plt.ylim((min_lat, max_lat))
        self.plot.figure.tight_layout()
        self.plot.draw()

    def run(self):
        logging.info('Loading font...')
        plt.rcParams['font.sans-serif'] = ['HYZhengYuan']  # 在其他环境中可能需要修改字体
        plt.rcParams['axes.unicode_minus'] = False
        logging.info('Starting GUI...')
        self.mainloop()
