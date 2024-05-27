import os

from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QStyle, QFileDialog
from PyQt6.QtCore import Qt, QUrl, QEvent

from common import show_error
from main_window import Ui_MainWindow


class PlayerWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.set_icon()
        self.setWindowTitle('视频播放器')
        # self.setWindowOpacity(0.9)
        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput()
        self.player.setVideoOutput(self.video)
        self.player.setAudioOutput(self.audio)
        self.muted = False
        self.vol = 0
        self.progress = 0
        self.bind()

    def playing_file(self) -> str:
        return self.player.source().fileName()

    def is_playing(self):
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def on_pause(self):
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState

    def get_status_text_pre_fix(self):
        play_status = ''
        if self.is_playing():
            play_status = f'正在播放：{self.playing_file()}\t'
        elif self.on_pause():
            play_status = '已暂停'

        full_screen_status = '全屏：开启\t' if self.video.isFullScreen() else ''
        muted_status = '静音：开启\t' if self.muted else ''
        vol_status = f'音量：{self.vol}\t'
        progress_status = f'进度：{self.progress}\t' if self.is_playing() else ''
        return f'{play_status}{full_screen_status}{muted_status}{vol_status}{progress_status}'

    def update_status_bar(self, info=''):
        if info:
            info = f'{info}\t'
        self.statusbar.showMessage(self.get_status_text_pre_fix() + info)

    def set_icon(self):
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        self.btn_start.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.btn_pause.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.btn_stop.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop))
        self.btn_vol.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        self.btn_full_screen.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))
        self.btn_open.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))

    def bind(self):
        self.btn_open.clicked.connect(self.open_file)
        self.btn_start.clicked.connect(self.play)
        self.btn_pause.clicked.connect(self.pause)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_vol.clicked.connect(self.click_volume)
        self.btn_full_screen.clicked.connect(self.fullscreen)
        self.sl_vol.valueChanged.connect(self.set_volume)
        self.sl_progress.valueChanged.connect(self.set_progress)
        self.video.installEventFilter(self)

    def play(self):
        if self.is_playing():
            return
        if self.player.source().isEmpty() or (not self.player.source().isValid()):
            show_error(self, '请先选择需要播放的文件')
            return
        self.player.play()
        self.update_status_bar()

    def closeEvent(self, _event):
        if self.is_playing():
            self.player.stop()

    def eventFilter(self, to_catch, event: QEvent):
        if to_catch != self.video:
            return super().eventFilter(to_catch, event)
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button == Qt.MouseButton.Left:
                self.switch()
        if event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Escape:
                self.video.setFullScreen(False)
            elif event.key() == Qt.Key.Key_Space:
                self.switch()
        return super().eventFilter(to_catch, event)

    def switch(self):
        if self.is_playing():
            self.player.pause()
        else:
            self.player.play()

    def open_file(self):
        tmp, _ = QFileDialog.getOpenFileName(self, '请选择要播放的文件', '.',
                                             filter='视频文件(*.wmv *.avi *.mp4 *.mov);;所有文件(*.*)')
        if os.path.isfile(tmp):
            self.player.setSource(QUrl.fromLocalFile(tmp))
            self.update_status_bar()

    def set_volume(self, vol):
        self.vol = vol
        self.update_status_bar()

    def set_progress(self, progress):
        self.progress = progress
        self.update_status_bar()

    def pause(self):
        if self.is_playing():
            self.player.pause()
        self.update_status_bar()

    def stop(self):
        if self.is_playing() or self.on_pause():
            self.player.stop()
        self.update_status_bar()

    def click_volume(self):
        self.muted = not self.muted
        self.set_vol_icon()
        self.update_status_bar()

    def fullscreen(self):
        self.video.setFullScreen(not self.video.isFullScreen())

    def set_vol_icon(self):
        if self.muted:
            self.btn_vol.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted))
        else:
            self.btn_vol.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))


if __name__ == '__main__':
    app = QApplication([])
    window = PlayerWindow()
    window.show()
    app.exec()
