from PyQt4 import QtGui
from PyQt4 import QtCore
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.dates as mpldates
import datetime
import time
from matplotlib.figure import Figure
import numpy as np


class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = figure.add_subplot(111)
        super(Canvas, self).__init__(figure)
        self.setParent(parent)

    def set_formatter(self, format):
        x_format = mpldates.DateFormatter(format)
        self.axes.xaxis.set_major_formatter(x_format)


class Plot(QtGui.QWidget):
    def __init__(self, parent=None):
        super(Plot, self).__init__(parent)
        self.canvas = self.create_canvas()
        self.settings = dict(grid=True,
                             x_format="%H:%M:%S",
                             x_range=3600*24*3,
                             y_autoscale=True,
                             y_range=(-10, 10),
                             interval=600,)
        x_data = [time.time(), time.time()]
        y_data = [0, 0]
        self.new_plot("Time", "pH", "pH-Sensor")
        self.new_line(x_data, y_data, "pH 1")
        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def create_canvas(self):
        canvas = Canvas(self)
        canvas.setObjectName("canvas")
        canvas.axes.grid()
        return canvas

    def new_plot(self, x_label, y_label, title):
        self.canvas.axes.cla()
        if self.settings["grid"]:
            self.canvas.axes.grid()
        self.canvas.axes.set_xlabel(x_label)
        self.canvas.axes.set_ylabel(y_label)
        self.canvas.axes.set_title(title)

    def new_line(self, x_data, y_data, name):
        x_data = [datetime.datetime.fromtimestamp(i) for i in x_data]
        x_data = mpldates.date2num(x_data)
        self.canvas.axes.plot(x_data, y_data, label=name)

        limits = self._get_new_xlim(time.time())
        self.canvas.axes.set_xlim(limits)
        self._update_ylim()
        self.canvas.axes.legend()
        self.canvas.set_formatter(self.settings["x_format"])
        self.canvas.draw()

    def remove_line(self, name):
        lines = self.canvas.axes.get_lines()
        for line in lines:
            if line.get_label() == name:
                self.canvas.axes.lines.remove(line)
                self.canvas.axes.legend()
                return True

        return False

    def append_to_line(self, x_data, y_data, name):
        x_data = [datetime.datetime.fromtimestamp(i) for i in x_data]
        x_data = mpldates.date2num(x_data)

        line = self._get_line(name)
        if not line:
            return

        x_data = np.append(line.get_xdata(), x_data)
        y_data = np.append(line.get_ydata(), y_data)
        line.set_xdata(x_data)
        line.set_ydata(y_data)
        self.remove_old_data(line)
        self.update_canvas()

    def update_canvas(self):
        limits = self._get_new_xlim(time.time())
        self.canvas.axes.set_xlim(limits)
        self._update_ylim()
        self.canvas.draw()

    @QtCore.pyqtSlot(int)
    def new_ph_without_stamp(self, ph):
        self.append_time_interval(time.time(), ph, "pH 1")
    
    def append_time_interval(self, x, y, name):
        x = datetime.datetime.fromtimestamp(x)
        x = mpldates.date2num(x)
        line = self._get_line(name)
        if not line:
            return

        x_data = line.get_xdata()
        y_data = line.get_ydata()
        x_data[-1] = x
        y_data[-1] = y
        dt = x - x_data[-2]
        new_value = False
        if dt >= self.settings["interval"] / 3600.0 / 24.0:
            new_value = True
            x_data = np.append(x_data, x)
            y_data = np.append(y_data, y)
        line.set_xdata(x_data)
        line.set_ydata(y_data)
        if new_value:
            self.remove_old_data(line)
        self.update_canvas()


    def remove_old_data(self, line):
        x_data = line.get_xdata()
        y_data = line.get_ydata()
        today = x_data[-1]
        x_min = today - self.settings["x_range"] / 3600.0 / 24.0
        y_in_range = y_data[x_min <= x_data]
        x_in_range = x_data[x_min <= x_data]
        line.set_xdata(x_in_range)
        line.set_ydata(y_in_range)

    def get_all_line_names(self):
        lines = self.canvas.axes.get_lines()
        names = []
        for line in lines:
            names.append(line.get_label())
        return names

    def _get_line(self, name):
        lines = self.canvas.axes.get_lines()
        for line in lines:
            if line.get_label() == name:
                return line
        return None

    def _get_new_xlim(self, stamp):
        right_date = datetime.datetime.fromtimestamp(stamp)
        right = mpldates.date2num(right_date)
        left = mpldates.date2num(right_date - datetime.timedelta(
            seconds=self.settings["x_range"]))
        return (left, right)

    def _update_ylim(self):
        def y_limits():
            lines = self.canvas.axes.get_lines()
            min_y = np.Inf
            max_y = -np.Inf
            x_min, x_max = self.canvas.axes.get_xlim()
            for line in lines:
                y_data = line.get_ydata()
                x_data = line.get_xdata()
                y_data_visible = y_data[(x_min <= x_data) & (x_data <= x_max)]
                line_y_min = np.min(y_data_visible)
                line_y_max = np.max(y_data_visible)
                min_y = line_y_min if line_y_min < min_y else min_y
                max_y = line_y_max if line_y_max > max_y else max_y
            return (min_y, max_y)

        if self.settings["y_autoscale"]:
            limits = y_limits()
            margin = np.max(np.abs(limits)) * 0.1
            self.canvas.axes.set_ylim(limits[0] - margin, limits[1] + margin)
        else:
            self.canvas.axes.set_ylim(self.settings["y_range"])

