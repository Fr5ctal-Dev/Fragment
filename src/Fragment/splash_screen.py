from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtGui import QMovie
from PySide6.QtCore import Signal


class SplashScreen(QWidget):
    splash_ended = Signal()
    def __init__(self):
        super().__init__()
        self.can_exit = False

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.label = QLabel()
        self.movie = QMovie('fragment/icon/splash_screens/splash_screen.gif')
        self.label.setMovie(self.movie)
        self.movie.frameChanged.connect(self.check_movie_has_ended)
        self.movie.start()

        self.main_layout.addWidget(self.label)

    def check_movie_has_ended(self):
        if self.movie.currentFrameNumber() == 1:
            if self.can_exit:
                self.movie.stop()
                self.hide()
                self.splash_ended.emit()
        if self.movie.currentFrameNumber() >= self.movie.frameCount() - 1:
            self.can_exit = True
