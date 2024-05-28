import os

from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import QApplication, QMainWindow, QStyle, QFileDialog
from PyQt6.QtCore import Qt, QUrl, QEvent

from common import show_error
from main_window import Ui_MainWindow


class PlayerWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.set_icon()
        self.setWindowTitle('视频播放器')
        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput()
        self.player.setVideoOutput(self.video)
        self.player.setAudioOutput(self.audio)
        self.cur_seconds = 0
        self.total_seconds = 0
        self.bind()
        self.sl_vol.setValue(20)

    def playing_file(self) -> str:
        return self.player.source().fileName()

    def is_playing(self):
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def is_on_pause(self):
        return self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState

    def is_stopped(self):
        return self.player.playbackState() == QMediaPlayer.PlaybackState.StoppedState

    def get_status_text_pre_fix(self):
        sep = '    '
        play_status = ''
        if self.is_playing():
            play_status = f'正在播放：{self.playing_file()}{sep}'
        elif self.is_on_pause():
            play_status = f'已暂停{sep}'

        full_screen_status = f'全屏：开启{sep}' if self.video.isFullScreen() else ''
        muted_status = f'静音：开启{sep}' if self.audio.isMuted() else ''
        vol_status = '' if self.audio.isMuted() else f'音量：{int(self.audio.volume() * 100)}%{sep}'
        return f'{play_status}{full_screen_status}{muted_status}{vol_status}'

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
        self.sl_vol.valueChanged.connect(self.vol_changed)
        self.sl_progress.valueChanged.connect(self.sl_progress_changed)
        self.video.installEventFilter(self)
        self.player.durationChanged.connect(self.duration_changed)
        self.player.positionChanged.connect(self.position_changed)
        self.player.playbackStateChanged.connect(self.play_state_changed)

    def play_state_changed(self):
        if self.is_playing():
            self.btn_start.setEnabled(False)
            self.btn_pause.setEnabled(True)
            self.btn_stop.setEnabled(True)
        elif self.is_on_pause():
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.btn_stop.setEnabled(True)
        elif self.is_stopped():
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(True)
            self.btn_stop.setEnabled(False)

    def update_progress_label(self):
        total_minutes, total_seconds = divmod(self.total_seconds, 60)
        current_minutes, current_seconds = divmod(self.cur_seconds, 60)
        progress_text = f'{current_minutes}:{current_seconds} / {total_minutes}:{total_seconds}'
        self.lb_progress.setText(progress_text)

    def duration_changed(self, new_duration: int):
        seconds = new_duration // 1000
        self.total_seconds = seconds
        self.sl_progress.setMaximum(self.total_seconds)
        self.cur_seconds = 0
        self.update_progress_label()

    def position_changed(self, new_position: int):
        if self.sl_progress.isSliderDown():
            return
        seconds = new_position // 1000
        self.cur_seconds = seconds
        self.sl_progress.setSliderPosition(self.cur_seconds)
        self.update_progress_label()

    def closeEvent(self, _event):
        if self.is_playing() or self.is_on_pause():
            self.player.stop()

    def eventFilter(self, to_catch, event: QEvent):
        if to_catch != self.video:
            return super().eventFilter(to_catch, event)
        if event.type() == QEvent.Type.MouseButtonPress:
            if event.button() == Qt.MouseButton.LeftButton:
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
            self.play()

    def vol_changed(self, vol):
        self.audio.setVolume(vol / 100)
        self.update_status_bar()

    def sl_progress_changed(self, progress):

        if not self.sl_progress.isSliderDown():
            return
        self.cur_seconds = progress
        self.player.setPosition(self.cur_seconds * 1000)

    def play(self):
        if self.is_playing():
            return
        if self.player.source().isEmpty() or (not self.player.source().isValid()):
            show_error(self, '请先选择需要播放的文件')
            return
        self.player.play()
        self.update_status_bar()

    def pause(self):
        if self.is_playing():
            self.player.pause()
        self.update_status_bar()

    def stop(self):
        if self.is_playing() or self.is_on_pause():
            self.player.stop()
        self.update_status_bar()

    def click_volume(self):
        self.audio.setMuted(not self.audio.isMuted())
        self.set_vol_icon()
        self.update_status_bar()

    def fullscreen(self):
        self.video.setFullScreen(not self.video.isFullScreen())

    def set_vol_icon(self):
        if self.audio.isMuted():
            self.btn_vol.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted))
        else:
            self.btn_vol.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))


if __name__ == '__main__':
    app = QApplication([])
    window = PlayerWindow()
    window.show()
    app.exec()
