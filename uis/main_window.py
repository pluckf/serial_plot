import sys
import serial
import serial.tools.list_ports
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QComboBox, QPushButton, QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import threading
import time
import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import random
from save_data import *
from uis.dialog_window import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.pic = None
        self.buff = [0]
        self.data = [0] * 50
        self.setWindowTitle("串口数据可视化")
        self.setGeometry(100, 100, 1000, 800)
        self.serial_port = None
        # 初始化数据缓冲区
        # 主控件
        mainWidget = QWidget()
        self.setCentralWidget(mainWidget)

        # 接收存储函数，防止遗漏数据
        self.t = threading.Thread(target=self.store_data)

        # 布局
        layout = QVBoxLayout()
        mainWidget.setLayout(layout)

        # 串口选择下拉菜单
        self.combobox = QComboBox()
        layout.addWidget(self.combobox)
        self.update_ports()

        # 打开串口按钮
        self.button = QPushButton("打开串口")
        layout.addWidget(self.button)
        self.button.clicked.connect(self.open_serial_port)

        # 弹出图像的按钮
        self.demo_button = QPushButton('点击我弹出窗口')
        layout.addWidget(self.demo_button)
        self.demo_button.clicked.connect(self.on_button_clicked)

        # 保存数据按钮
        self.save_button = QPushButton("保存数据")
        layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_data)

        # 用于显示数据的Matplotlib图表
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.add_subplot(111)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)

    def update_ports(self):
        self.combobox.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.combobox.addItem(port.device)

    def open_serial_port(self):
        port = self.combobox.currentText()
        self.t.start()
        try:
            self.serial_port = serial.Serial(port, 115200)
            print("打开成功")
        except:
            print("无法打开串口")
        self.timer.start(20)  # 每20ms更新一次图表

    def update_plot(self):
        self.data=self.buff
        self.ax.clear()
        self.ax.plot(self.data)
        self.canvas.draw()

    def save_data(self):
        write_data(self.data)

    def on_button_clicked(self):
        self.pic = PicWindow()
        self.pic.show()

    def store_data(self):
        while True:
            if self.serial_port and self.serial_port.is_open:
                try:
                    data = self.serial_port.readline().decode().strip()
                    data = data[2:]
                    data = data[0:-2]
                    value = float(data)
                    if len(self.buff) <= 10000:
                        self.buff += [value]
                    else:
                        self.buff = self.buff[1:]
                        self.buff += [value]
                except:
                    print("还没有数据")
