import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5 import uic

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("PlayerUI.ui", self)
        
        self.btnBrowse.clicked.connect(self.browse_video)
        # Video capture
        self.video_capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.fps = 28

    def browse_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi)")
        if video_path:
            self.display_video_specs(video_path)
            self.txtBrowse.setText(video_path)
            self.play_video(video_path)

    def play_video(self, video_path):
        self.video_capture = cv2.VideoCapture(video_path)
        self.fps = int(self.video_capture.get(cv2.CAP_PROP_FPS))
        self.timer.start(1000 // self.fps)  

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            # Convert frame to QImage
            height, width, channel = frame.shape
            bytesPerLine = 3 * width
            qImg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            
            # Resize QImage to fit QLabel
            labelWidth = self.lblVideo.width()
            labelHeight = self.lblVideo.height()
            scaled_qImg = qImg.scaled(labelWidth, labelHeight, Qt.KeepAspectRatio)

            # Convert QImage to QPixmap and set it to QLabel
            pixmap = QPixmap.fromImage(scaled_qImg)
            self.lblVideo.setPixmap(pixmap)
            self.lblVideo.setAlignment(Qt.AlignCenter)
        else:
            self.timer.stop()
            self.video_capture.release()

    def display_video_specs(self, video_path):
        video_capture = cv2.VideoCapture(video_path)
        fps = int(video_capture.get(cv2.CAP_PROP_FPS))
        frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps
        video_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        codec = int(video_capture.get(cv2.CAP_PROP_CODEC_PIXEL_FORMAT))
        self.lblSpecs.setText(f"FPS: {fps}\n"
                              f"Frame Count: {frame_count}\n"
                              f"Duration: {duration} seconds\n"
                              f"Width: {video_width}\n"
                              f"Height: {video_height}\n"
                              f"Codec: {codec}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    sys.exit(app.exec_())
