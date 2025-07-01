from .editor_widget import EditorWidget
from PySide6.QtCore import QPointF, Qt, Signal
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QGraphicsEllipseItem, QGraphicsSimpleTextItem, QMenu, QTreeWidgetItem, QHBoxLayout, QDoubleSpinBox, QLabel, QWidget, QTreeWidget, QHeaderView
from PySide6.QtCharts import QChart, QChartView, QLineSeries, QScatterSeries, QValueAxis


class Timeline(EditorWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.open_button = QPushButton()
        self.main_layout.addWidget(self.open_button)
        self.open_button.setText('Edit Timeline')
        self.timeline_dialog = None

        self.open_button.clicked.connect(self.open_timeline)

    def open_timeline(self):
        self.timeline_dialog = TimelineEditorDialog(initial_range=1.0)
        self.timeline_dialog.load(self.value[1])
        self.timeline_dialog.show()
        self.timeline_dialog.closed.connect(self.save_timeline_data)

    def save_timeline_data(self):
        self.value[0] = self.timeline_dialog.export()
        self.value[1] = self.timeline_dialog.save()
        self.change_property()


class TimelineChartView(QChartView):
    pointSelected = Signal(int, float, float)
    def __init__(self, parent=None, initial_range=1.0):
        super().__init__(parent)
        self.initial_range = initial_range
        self._chart = QChart()
        self._chart.legend().hide()
        self._chart.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self._chart.setPlotAreaBackgroundBrush(QBrush(QColor(20, 20, 20)))
        self._chart.setPlotAreaBackgroundVisible(True)
        self.setChart(self._chart)
        self.line_color = QColor(200, 200, 200)
        self.selection_color = QColor(100, 100, 255)
        self.control_color = QColor(255, 100, 100)
        self.line_series = QLineSeries()
        self.line_series.setColor(self.line_color)
        self._chart.addSeries(self.line_series)
        self.scatter_series = QScatterSeries()
        self.scatter_series.setMarkerSize(10)
        self.scatter_series.setColor(self.line_color)
        self._chart.addSeries(self.scatter_series)
        self.control_series = QScatterSeries()
        self.control_series.setMarkerSize(8)
        self.control_series.setColor(self.control_color)
        self._chart.addSeries(self.control_series)
        self.x_axis = QValueAxis()
        self.x_axis.setRange(0, self.initial_range)
        self.x_axis.setTitleText('Time (s)')
        self.x_axis.setLabelFormat('%.2f')
        self.x_axis.setTickCount(int(self.initial_range / 0.1) + 1)
        self.x_axis.setLabelsColor(QColor(220, 220, 220))
        self.x_axis.setTitleBrush(QBrush(QColor(220, 220, 220)))
        self._chart.addAxis(self.x_axis, Qt.AlignBottom)
        self.line_series.attachAxis(self.x_axis)
        self.scatter_series.attachAxis(self.x_axis)
        self.control_series.attachAxis(self.x_axis)
        self.y_axis = QValueAxis()
        self.y_axis.setTitleText('Value')
        self.y_axis.setLabelsColor(QColor(220, 220, 220))
        self.y_axis.setTitleBrush(QBrush(QColor(220, 220, 220)))
        self._chart.addAxis(self.y_axis, Qt.AlignLeft)
        self.line_series.attachAxis(self.y_axis)
        self.scatter_series.attachAxis(self.y_axis)
        self.control_series.attachAxis(self.y_axis)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setRenderHint(QPainter.Antialiasing)
        self.points = []
        self.dragging_point_index = None
        self.selected_point_index = None
        self.selected_protected = False
        self._isPanning = False
        self._lastPanPoint = None
        self.manual_dragged = None
        self.manual_drag_segment = None
        self.hover_marker = QGraphicsEllipseItem()
        self.hover_marker.setPen(QPen(self.selection_color))
        self.hover_marker.setBrush(QBrush(self.selection_color))
        self.hover_marker.setVisible(False)
        self.hover_marker.setZValue(10)
        self.chart().scene().addItem(self.hover_marker)
        self.drag_label = QGraphicsSimpleTextItem()
        self.drag_label.setFont(QFont("Arial", 10))
        self.drag_label.setPen(QPen(QColor(220, 220, 220)))
        self.drag_label.setZValue(11)
        self.drag_label.setVisible(False)
        self.chart().scene().addItem(self.drag_label)
        self.ghost_marker = QGraphicsEllipseItem()
        self.ghost_marker.setPen(QPen(QColor(150, 150, 150, 100)))
        self.ghost_marker.setBrush(QBrush(QColor(150, 150, 150, 50)))
        self.ghost_marker.setVisible(True)
        self.ghost_marker.setZValue(9)
        self.chart().scene().addItem(self.ghost_marker)
        self.ghost_label = QGraphicsSimpleTextItem()
        self.ghost_label.setFont(QFont("Arial", 10))
        self.ghost_label.setPen(QPen(QColor(220, 220, 220)))
        self.ghost_label.setZValue(9)
        self.ghost_label.setVisible(True)
        self.chart().scene().addItem(self.ghost_label)
        self.selected_marker = QGraphicsEllipseItem()
        self.selected_marker.setPen(QPen(QColor(255, 255, 0)))
        self.selected_marker.setBrush(QBrush(QColor(255, 255, 0)))
        self.selected_marker.setVisible(False)
        self.selected_marker.setZValue(12)
        self.chart().scene().addItem(self.selected_marker)

    def snap_x(self, x):
        return round(x * 100) / 100

    def snap_y(self, y):
        return round(y * 100) / 100

    def update_selected_marker(self):
        sorted_points = sorted(self.points, key=lambda d: d["pt"].x())
        if self.selected_point_index is not None and 0 <= self.selected_point_index < len(sorted_points):
            pt = sorted_points[self.selected_point_index]["pt"]
            screen_pos = self.chart().mapToPosition(pt)
            diameter = 12
            self.selected_marker.setRect(screen_pos.x() - diameter / 2, screen_pos.y() - diameter / 2, diameter, diameter)
            self.selected_marker.setVisible(True)
        else:
            self.selected_marker.setVisible(False)

    def update_series(self):
        sorted_points = sorted(self.points, key=lambda d: d["pt"].x())
        if sorted_points:
            y0 = sorted_points[0]["pt"].y()
            sorted_points[0]["pt"] = QPointF(0, y0)
        pts = [d["pt"] for d in sorted_points]
        self.line_series.clear()
        self.scatter_series.clear()
        self.control_series.clear()
        for s in list(self._chart.series()):
            if isinstance(s, QLineSeries) and s not in [self.line_series]:
                self._chart.removeSeries(s)
        if not pts:
            return
        self.line_series.append(pts[0])
        self.scatter_series.append(pts[0])
        for i in range(1, len(pts)):
            p0 = pts[i - 1]
            p1 = pts[i]
            mode = sorted_points[i - 1].get("mode", 0)
            if mode == 0:
                self.line_series.append(p1)
            elif mode == 1:
                cp1 = QPointF(p0.x() + (p1.x() - p0.x()) * 0.3, p0.y() + (p1.y() - p0.y()) * 0.1)
                cp2 = QPointF(p0.x() + (p1.x() - p0.x()) * 0.7, p0.y() + (p1.y() - p0.y()) * 0.9)
                samples = 20
                for j in range(1, samples):
                    t = j / samples
                    invt = 1 - t
                    x = (invt ** 3) * p0.x() + 3 * (invt ** 2) * t * cp1.x() + 3 * invt * (t ** 2) * cp2.x() + (t ** 3) * p1.x()
                    y = (invt ** 3) * p0.y() + 3 * (invt ** 2) * t * cp1.y() + 3 * invt * (t ** 2) * cp2.y() + (t ** 3) * p1.y()
                    self.line_series.append(QPointF(x, y))
                self.line_series.append(p1)
            elif mode == 2:
                if "control" in sorted_points[i - 1]:
                    cp1, cp2 = sorted_points[i - 1]["control"]
                else:
                    cp1 = QPointF(p0.x() + (p1.x() - p0.x()) / 3, p0.y())
                    cp2 = QPointF(p0.x() + 2 * (p1.x() - p0.x()) / 3, p1.y())
                eps = 1e-6
                cp1 = QPointF(max(p0.x() + eps, min(cp1.x(), p1.x() - eps)), cp1.y())
                cp2 = QPointF(max(p0.x() + eps, min(cp2.x(), p1.x() - eps)), cp2.y())
                sorted_points[i - 1]["control"] = (cp1, cp2)
                samples = 20
                for j in range(1, samples):
                    t = j / samples
                    invt = 1 - t
                    x = (invt ** 3) * p0.x() + 3 * (invt ** 2) * t * cp1.x() + 3 * invt * (t ** 2) * cp2.x() + (t ** 3) * p1.x()
                    y = (invt ** 3) * p0.y() + 3 * (invt ** 2) * t * cp1.y() + 3 * invt * (t ** 2) * cp2.y() + (t ** 3) * p1.y()
                    self.line_series.append(QPointF(x, y))
                self.line_series.append(p1)
                self.control_series.append(cp1)
                self.control_series.append(cp2)
                dash_pen = QPen(self.control_color)
                dash_pen.setStyle(Qt.DashLine)
                cs1 = QLineSeries()
                cs1.setPen(dash_pen)
                cs1.append(p0)
                cs1.append(cp1)
                self._chart.addSeries(cs1)
                cs1.attachAxis(self.x_axis)
                cs1.attachAxis(self.y_axis)
                cs2 = QLineSeries()
                cs2.setPen(dash_pen)
                cs2.append(cp2)
                cs2.append(p1)
                self._chart.addSeries(cs2)
                cs2.attachAxis(self.x_axis)
                cs2.attachAxis(self.y_axis)
            elif mode == 3:
                corner = QPointF(p1.x(), p0.y())
                self.line_series.append(corner)
                self.line_series.append(p1)
            self.scatter_series.append(p1)
        for s in [self.line_series, self.scatter_series, self.control_series]:
            s.attachAxis(self.x_axis)
            s.attachAxis(self.y_axis)
        self.update_selected_marker()

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._isPanning = True
            self._lastPanPoint = event.position()
            event.accept()
            return
        if event.button() != Qt.LeftButton:
            event.ignore()
            return
        pos = event.position()
        chart_pos = self.chart().mapToValue(pos)
        chart_pos.setX(self.snap_x(chart_pos.x()))
        chart_pos.setY(self.snap_y(chart_pos.y()))
        threshold = 10
        if self.points:
            sorted_points = sorted(self.points, key=lambda d: d["pt"].x())
            first_point_screen = self.chart().mapToPosition(sorted_points[0]["pt"])
            if (first_point_screen - pos).manhattanLength() < threshold:
                self.dragging_point_index = 0
                self.selected_point_index = 0
                self.selected_protected = True
                self.pointSelected.emit(0, sorted_points[0]["pt"].x(), sorted_points[0]["pt"].y())
                event.accept()
                self.update_selected_marker()
                return
        sorted_points = sorted(self.points, key=lambda d: d["pt"].x())
        for i, d in enumerate(sorted_points):
            if d.get("mode", 0) == 2 and "control" in d:
                cp1, cp2 = d["control"]
                cp1_screen = self.chart().mapToPosition(cp1)
                cp2_screen = self.chart().mapToPosition(cp2)
                if (cp1_screen - pos).manhattanLength() < threshold:
                    self.manual_dragged = 'c1'
                    self.manual_drag_segment = i
                    event.accept()
                    return
                if (cp2_screen - pos).manhattanLength() < threshold:
                    self.manual_dragged = 'c2'
                    self.manual_drag_segment = i
                    event.accept()
                    return
        self.manual_dragged = None
        self.manual_drag_segment = None
        for i, d in enumerate(self.points):
            point = d["pt"]
            screen_pos = self.chart().mapToPosition(point)
            if (screen_pos - pos).manhattanLength() < threshold:
                self.dragging_point_index = i
                sorted_points = sorted(self.points, key=lambda d: d["pt"].x())
                for j, sd in enumerate(sorted_points):
                    if sd is d:
                        self.selected_point_index = j
                        break
                self.selected_protected = (self.selected_point_index == 0)
                self.pointSelected.emit(self.selected_point_index, point.x(), point.y())
                event.accept()
                self.update_selected_marker()
                return
        new_x = self.snap_x(chart_pos.x())
        new_y = self.snap_y(chart_pos.y())
        new_d = {"pt": QPointF(new_x, new_y), "mode": 0}
        self.points.append(new_d)
        sorted_points = sorted(self.points, key=lambda d: d["pt"].x())
        for j, sd in enumerate(sorted_points):
            if sd is new_d:
                self.selected_point_index = j
                break
        self.dragging_point_index = None
        self.selected_protected = (self.selected_point_index == 0)
        self.update_series()
        self.pointSelected.emit(self.selected_point_index, new_d["pt"].x(), new_d["pt"].y())
        event.accept()

    def contextMenuEvent(self, event):
        pos = event.pos()
        threshold = 10
        sorted_points = sorted(self.points, key=lambda d: d["pt"].x())
        pts = [d["pt"] for d in sorted_points]
        clicked_index = None
        for i, point in enumerate(pts):
            screen_pos = self.chart().mapToPosition(point)
            if (screen_pos - pos).manhattanLength() < threshold:
                clicked_index = i
                break
        if clicked_index is None or clicked_index == len(pts) - 1:
            return
        seg_index = clicked_index
        menu = QMenu()
        act_linear = menu.addAction('Linear')
        act_curved = menu.addAction('Curved')
        act_bezier = menu.addAction('Bezier')
        act_constant = menu.addAction('Constant')
        chosen = menu.exec(self.mapToGlobal(event.pos()))
        if chosen == act_linear:
            sorted_points[seg_index]["mode"] = 0
            if "control" in sorted_points[seg_index]:
                del sorted_points[seg_index]["control"]
        elif chosen == act_curved:
            sorted_points[seg_index]["mode"] = 1
            if "control" in sorted_points[seg_index]:
                del sorted_points[seg_index]["control"]
        elif chosen == act_bezier:
            sorted_points[seg_index]["mode"] = 2
            p0 = pts[seg_index]
            p1 = pts[seg_index + 1]
            c1 = QPointF(p0.x() + (p1.x() - p0.x()) / 3, p0.y())
            c2 = QPointF(p0.x() + 2 * (p1.x() - p0.x()) / 3, p1.y())
            sorted_points[seg_index]["control"] = (c1, c2)
        elif chosen == act_constant:
            sorted_points[seg_index]["mode"] = 3
            if "control" in sorted_points[seg_index]:
                del sorted_points[seg_index]["control"]
        self.update_series()

    def mouseDoubleClickEvent(self, event):
        pos = event.position()
        threshold = 10
        sorted_points = sorted(self.points, key=lambda d: d["pt"].x())
        for i, d in enumerate(sorted_points):
            point = d["pt"]
            screen_pos = self.chart().mapToPosition(point)
            if (screen_pos - pos).manhattanLength() < threshold:
                del self.points[self.points.index(d)]
                self.update_series()
                event.accept()
                return

    def mouseMoveEvent(self, event):
        if self._isPanning:
            current_pos = event.position()
            delta = current_pos - self._lastPanPoint
            self.chart().scroll(-delta.x(), delta.y())
            self._lastPanPoint = current_pos
            event.accept()
            return
        pos = event.position()
        ghost_chart_pos = self.chart().mapToValue(pos)
        ghost_point = QPointF(max(ghost_chart_pos.x(), 0), ghost_chart_pos.y())
        ghost_point.setX(self.snap_x(ghost_point.x()))
        ghost_point.setY(self.snap_y(ghost_point.y()))
        ghost_screen = self.chart().mapToPosition(ghost_point)
        r = 5
        self.ghost_marker.setRect(ghost_screen.x() - r, ghost_screen.y() - r, 2 * r, 2 * r)
        ghost_text = f'x: {ghost_point.x():.2f} s, y: {ghost_point.y():.2f}'
        self.ghost_label.setText(ghost_text)
        ghost_rect = self.ghost_label.boundingRect()
        self.ghost_label.setPos(ghost_screen.x() - ghost_rect.width() / 2, ghost_screen.y() - ghost_rect.height() - 5)
        self.ghost_label.setVisible(True)
        if self.manual_dragged is not None:
            chart_pos = self.chart().mapToValue(pos)
            chart_pos.setX(self.snap_x(chart_pos.x()))
            chart_pos.setY(self.snap_y(chart_pos.y()))
            seg = self.manual_drag_segment
            sorted_points = sorted(self.points, key=lambda d: d["pt"].x())
            if seg < 0 or seg >= len(sorted_points):
                event.accept()
                return
            if seg == 0:
                p0 = sorted_points[0]["pt"]
                p1 = sorted_points[1]["pt"] if len(sorted_points) > 1 else sorted_points[0]["pt"]
            else:
                p0 = sorted_points[seg - 1]["pt"]
                p1 = sorted_points[seg]["pt"]
            new_x = chart_pos.x()
            new_y = chart_pos.y()
            if self.manual_dragged == 'c1':
                if "control" in sorted_points[seg]:
                    cp1, cp2 = sorted_points[seg]["control"]
                else:
                    cp1 = QPointF(p0.x() + (p1.x() - p0.x()) / 3, p0.y())
                    cp2 = QPointF(p0.x() + 2 * (p1.x() - p0.x()) / 3, p1.y())
                cp1 = QPointF(new_x, new_y)
                sorted_points[seg]["control"] = (cp1, cp2)
            else:
                if "control" in sorted_points[seg]:
                    cp1, cp2 = sorted_points[seg]["control"]
                else:
                    cp1 = QPointF(p0.x() + (p1.x() - p0.x()) / 3, p0.y())
                    cp2 = QPointF(p0.x() + 2 * (p1.x() - p0.x()) / 3, p1.y())
                cp2 = QPointF(new_x, new_y)
                sorted_points[seg]["control"] = (cp1, cp2)
            self.update_series()
            event.accept()
            return
        if self.dragging_point_index is not None:
            chart_pos = self.chart().mapToValue(pos)
            new_x = self.snap_x(chart_pos.x())
            new_y = self.snap_y(chart_pos.y())
            self.points[self.dragging_point_index]["pt"] = QPointF(new_x, new_y)
            self.update_series()
            sorted_points = sorted(self.points, key=lambda d: d["pt"].x())
            if self.dragging_point_index is not None:
                for j, d in enumerate(sorted_points):
                    if d is self.points[self.dragging_point_index]:
                        self.pointSelected.emit(j, d["pt"].x(), d["pt"].y())
                        break
            event.accept()
            return
        found_hover = False
        threshold = 10
        for d in self.points:
            screen_pos = self.chart().mapToPosition(d["pt"])
            if (screen_pos - pos).manhattanLength() < threshold:
                diameter = 15
                self.hover_marker.setRect(screen_pos.x() - diameter / 2, screen_pos.y() - diameter / 2, diameter, diameter)
                self.hover_marker.setVisible(True)
                found_hover = True
                break
        if not found_hover:
            self.hover_marker.setVisible(False)
        self.drag_label.setVisible(False)
        event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self._isPanning = False
            self._lastPanPoint = None
            event.accept()
            return
        self.dragging_point_index = None
        self.selected_protected = False
        self.manual_dragged = None
        self.manual_drag_segment = None
        self.drag_label.setVisible(False)
        self.update_selected_marker()
        event.accept()

    def wheelEvent(self, event):
        angle = event.angleDelta().y()
        factor = 1.1 if angle > 0 else 0.9
        self.chart().zoom(factor)
        event.accept()

    def _update_drag_label(self, point):
        txt = f'x: {point.x():.2f} s, y: {point.y():.2f}'
        self.drag_label.setText(txt)
        scr = self.chart().mapToPosition(point)
        rect = self.drag_label.boundingRect()
        self.drag_label.setPos(scr.x() - rect.width() / 2, scr.y() - rect.height() - 5)
        self.drag_label.setVisible(True)

    def export_timeline(self):
        count = self.line_series.count()
        if count == 0:
            return []
        pts = [self.line_series.at(i) for i in range(count)]
        start_time = pts[0].x()
        end_time = pts[-1].x()
        total_ms = int(round((end_time - start_time) * 1000))
        timeline = [pts[0].y()] * (total_ms + 1)
        for i in range(count - 1):
            p0 = pts[i]
            p1 = pts[i + 1]
            seg_start = int(round((p0.x() - start_time) * 1000))
            seg_end = int(round((p1.x() - start_time) * 1000))
            if seg_end - seg_start == 0:
                continue
            for t in range(seg_start, seg_end + 1):
                u = (t - seg_start) / (seg_end - seg_start)
                timeline[t] = p0.y() + (p1.y() - p0.y()) * u
        return timeline

    def save(self):
        pts_data = []
        sorted_points = sorted(self.points, key=lambda d: d["pt"].x())
        for d in sorted_points:
            pt = d["pt"]
            mode = d.get("mode", 0)
            cp = None
            if mode == 2 and "control" in d:
                cp1, cp2 = d["control"]
                cp = [cp1.x(), cp1.y(), cp2.x(), cp2.y()]
            pts_data.append((pt.x(), pt.y(), mode, cp))
        return pts_data

    def load(self, data):
        if not data:
            return
        self.points = []
        for row in data:
            if len(row) < 3:
                d = {"pt": QPointF(row[0], row[1]), "mode": 0}
            else:
                d = {"pt": QPointF(row[0], row[1]), "mode": row[2]}
                if d["mode"] == 2 and len(row) > 3 and row[3]:
                    cp = row[3]
                    d["control"] = (QPointF(cp[0], cp[1]), QPointF(cp[2], cp[3]))
            self.points.append(d)
        self.update_series()


class ChannelWidget(QWidget):
    def __init__(self, parent=None, initial_range=1.0):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.chart = TimelineChartView(self, initial_range=initial_range)
        self.layout.addWidget(self.chart)
        self.spin_layout = QHBoxLayout()
        self.x_spin = QDoubleSpinBox()
        self.x_spin.setPrefix("X: ")
        self.x_spin.setDecimals(2)
        self.x_spin.setSingleStep(0.01)
        self.y_spin = QDoubleSpinBox()
        self.y_spin.setPrefix("Y: ")
        self.y_spin.setDecimals(2)
        self.y_spin.setSingleStep(0.01)
        self.spin_layout.addWidget(QLabel("Edit Selected Point:"))
        self.spin_layout.addWidget(self.x_spin)
        self.spin_layout.addWidget(self.y_spin)
        self.fitHButton = QPushButton("Fit Horizontal")
        self.fitVButton = QPushButton("Fit Vertical")
        self.spin_layout.addWidget(self.fitHButton)
        self.spin_layout.addWidget(self.fitVButton)
        self.layout.addLayout(self.spin_layout)
        self.chart.pointSelected.connect(self.on_point_selected)
        self.x_spin.valueChanged.connect(self.update_selected_point_from_spin)
        self.y_spin.valueChanged.connect(self.update_selected_point_from_spin)
        self.fitHButton.clicked.connect(self.fitHorizontal)
        self.fitVButton.clicked.connect(self.fitVertical)

    def on_point_selected(self, index, x, y):
        self.x_spin.blockSignals(True)
        self.y_spin.blockSignals(True)
        self.x_spin.setValue(x)
        self.y_spin.setValue(y)
        self.x_spin.blockSignals(False)
        self.y_spin.blockSignals(False)

    def update_selected_point_from_spin(self):
        if self.chart.selected_point_index is not None:
            sorted_points = sorted(self.chart.points, key=lambda d: d["pt"].x())
            if 0 <= self.chart.selected_point_index < len(sorted_points):
                new_y = self.y_spin.value()
                new_x = 0 if self.chart.selected_point_index == 0 else self.x_spin.value()
                sorted_points[self.chart.selected_point_index]["pt"] = QPointF(new_x, new_y)
                self.chart.update_series()

    def fitHorizontal(self):
        if not self.chart.points:
            return
        sorted_points = sorted(self.chart.points, key=lambda d: d["pt"].x())
        min_x = sorted_points[0]["pt"].x()
        max_x = sorted_points[-1]["pt"].x()
        margin = 0.01
        new_min = min_x - margin
        new_max = max_x + margin
        self.chart.x_axis.setRange(new_min, new_max)

    def fitVertical(self):
        ls = self.chart.line_series
        count = ls.count()
        if count == 0:
            return
        ys = [ls.at(i).y() for i in range(count)]
        min_y = min(ys)
        max_y = max(ys)
        margin = 0.01
        new_min = min_y - margin
        new_max = max_y + margin
        self.chart.y_axis.setRange(new_min, new_max)

    def export_timeline(self):
        return self.chart.export_timeline()

    def save(self):
        return self.chart.save()

    def load(self, data):
        self.chart.load(data)
        self.chart.update_series()


class TimelineEditorDialog(QDialog):
    closed = Signal()
    def __init__(self, parent=None, initial_range=1.0):
        super().__init__(parent)
        self.setWindowTitle('Timeline Editor')
        self.resize(1000, 600)
        self.layout = QVBoxLayout(self)
        self.tree = QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.setHeaderHidden(True)
        self.tree.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.layout.addWidget(self.tree)
        self.add_channel_button = QPushButton("Add Channel")
        self.add_channel_button.clicked.connect(self.add_channel)
        self.layout.addWidget(self.add_channel_button)
        self.channels = []
        self.add_channel()

    def add_channel(self):
        channel = ChannelWidget(self, initial_range=1.0)
        channel.setFixedHeight(350)
        item = QTreeWidgetItem(self.tree)
        self.tree.setItemWidget(item, 0, channel)
        self.channels.append((item, channel))
        self.tree.setCurrentItem(item)

    def load(self, multi_channel_data):
        for item, ch in self.channels:
            self.tree.takeTopLevelItem(self.tree.indexOfTopLevelItem(item))
        self.channels = []
        while self.tree.topLevelItemCount():
            self.tree.takeTopLevelItem(0)
        for channel_data in multi_channel_data:
            channel = ChannelWidget(self, initial_range=1.0)
            channel.load(channel_data)
            channel.setFixedHeight(350)
            item = QTreeWidgetItem(self.tree)
            self.tree.setItemWidget(item, 0, channel)
            self.channels.append((item, channel))

    def export(self):
        channel_exports = [ch.export_timeline() for _, ch in self.channels]
        if not channel_exports:
            return []
        L = max(len(data) for data in channel_exports)
        for i, data in enumerate(channel_exports):
            if len(data) < L:
                last_val = data[-1] if data else None
                channel_exports[i] = data + [None] * (L - len(data))
        combined = []
        for t in range(L):
            combined.append([channel_exports[ch][t] for ch in range(len(channel_exports))])
        return combined

    def save(self):
        return [ch.save() for _, ch in self.channels]

    def closeEvent(self, event):
        self.closed.emit()
