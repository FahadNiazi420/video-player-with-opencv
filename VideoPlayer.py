import sys
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5 import uic

class VideoPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("PlayerUI.ui", self)
        self.speeds = {'2x': 2.0,'1.75x': 1.75,'1.5x': 1.5,'1.25x': 1.25,'1.0x': 1.0,'0.75x': 0.75,'0.5x': 0.5,'0.25x': 0.25}
        self.speed = 1.0
        self.populate_cameras()
        # Connect button signals
        self.btnBrowse.clicked.connect(self.browse_video)
        self.btnPlay.clicked.connect(self.toggle_playback)
        self.btnForward.clicked.connect(self.move_forward)
        self.btnReplay.clicked.connect(self.replay_backward)
        self.cmbxSpeed.currentIndexChanged.connect(self.change_speed)
        self.cmbxFilter.currentIndexChanged.connect(self.apply_filter)
        self.btnShow.clicked.connect(self.select_camera)
        

        # Video capture
        self.video_capture = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.play_pause_count = 0
        self.current_filter = None
    
    def populate_cameras(self):
        # Enumerate all available cameras
        num_cameras = 0
        for camera in range(10):  # Try up to 10 cameras
            cap = cv2.VideoCapture(camera)
            if not cap.isOpened():
                break
            num_cameras += 1
            cap.release()
            self.cmbxCamera.addItem(f"Camera {num_cameras}")

    def select_camera(self, index):
        self.video_capture = cv2.VideoCapture(0)
        fps = int(self.video_capture.get(cv2.CAP_PROP_FPS))
        self.timer.start(1000 // fps)

    def browse_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "Open Video", "", "Video Files (*.mp4 *.avi)")
        if video_path:
            self.display_video_specs(video_path)
            self.txtBrowse.setText(video_path)
            self.play_video(video_path)
            
    def play_video(self, video_path):
        self.video_capture = cv2.VideoCapture(video_path)
        fps = int(self.video_capture.get(cv2.CAP_PROP_FPS))
        self.timer.start(1000 // fps)  # Set timer interval based on video's frame rate

    def change_speed(self, index):
        speed_text = self.cmbxSpeed.currentText()
        self.speed = self.speeds.get(speed_text, 1.0)

    def apply_filter(self, index):
        filter_name = self.cmbxFilter.currentText()
        if filter_name == 'RGB':
            self.current_filter = lambda frame: frame
        elif filter_name == 'Black & White':
            self.current_filter = lambda frame: cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        elif filter_name == 'Grayscale':
            self.current_filter = lambda frame: cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def move_forward(self):
        current_position = self.video_capture.get(cv2.CAP_PROP_POS_MSEC)
        self.video_capture.set(cv2.CAP_PROP_POS_MSEC, current_position + 10000)  # Move forward by 10 seconds

    def replay_backward(self):
        current_position = self.video_capture.get(cv2.CAP_PROP_POS_MSEC)
        new_position = max(0, current_position - 10000)  # Ensure not to go below 0
        self.video_capture.set(cv2.CAP_PROP_POS_MSEC, new_position)  # Replay 10 seconds back

    def toggle_playback(self):
        # Increment play/pause count
        self.play_pause_count += 1

        if self.play_pause_count % 2 == 0:
            # Even click count, so play video
            self.timer.start()
            self.btnPlay.setIcon(QIcon("Icons/pause.png"))# Change icon to pause
        else:
            # Odd click count, so pause video
            self.timer.stop()
            self.btnPlay.setIcon(QIcon("Icons/play.png")) # Change icon to play

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            # Apply selected filter to the frame
            if self.current_filter:
                frame = self.current_filter(frame)
    
            # Check if frame is grayscale
            if len(frame.shape) == 2:  
                qImg = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1], QImage.Format_Grayscale8)
            else:
                qImg = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1] * frame.shape[2], QImage.Format_RGB888)
    
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
