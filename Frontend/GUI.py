from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy 
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os


env_vars = dotenv_values(".env")
Assistantname=env_vars.get("Assistantname")
current_dir=os.getcwd()
old_chat_message=""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"


def AnswerModifier(Answer):
    Lines =Answer.split('\n')
    non_empty_Lines=[Line for Line in Lines if Line.strip()]
    modified_answer='\n'.join(non_empty_Lines)
    return modified_answer


def QueryModifier(Query):
    new_query=Query.lower().strip()
    query_words= new_query.split()
    question_words=["how", "what", "who", "where", "ahen", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    if any(word in new_query for word in question_words):
        if query_words[-1][-1] in['.','?','!']:
            new_query=new_query[:-1]+"?"

        else:
            new_query+="?"


    else:

        if query_words[-1][-1]in ['.','?','!']:
            new_query=new_query[:-1] +  "."

        else:
            new_query+="."

        
    return new_query

def SetMicrophoneStatus(Command):
    with open (rf"{TempDirPath}\Mic.data","w",encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open (rf"{TempDirPath}\Mic.data","r",encoding='utf-8') as file:
        Status = file.read()           
    return Status

def SetAssistanceStatus(Status):
    with open (rf"{TempDirPath}\Status.data","w",encoding='utf-8') as file:
        file.write(Status)
SetAssistanceStatus("translating...")

def GetAssistanceStatus():
    with open (rf"{TempDirPath}\Status.data","r",encoding='utf-8') as file:
        Status=file.read()
    return Status

def MicButtonInitilized():
    SetMicrophoneStatus("False")

def MicButtonClosed():
    SetMicrophoneStatus("True")

def GraphicsDirectoryPath(Filename):
    path=rf'{GraphicsDirPath}\{Filename}'
    return path

def TempDirectoryPath(Filename):
    path=rf'{TempDirPath}\{Filename}'
    return path

def ShowTextToScreen(text):
    with open (rf"{TempDirPath}\Responses.data","w",encoding='utf-8') as file:
        file.write(text)





class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        # Chat window
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        layout.addWidget(self.chat_text_edit)

        # Initial text color
        text_color = QTextCharFormat()
        text_color.setForeground(QColor(Qt.blue))
        self.chat_text_edit.setCurrentCharFormat(text_color)

        # Jarvis GIF
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath("jarvis.gif"))
        movie.setScaledSize(QSize(480, 270))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        # Status label
        self.label = QLabel("")
        self.label.setStyleSheet(
            "color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;"
        )
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        # Microphone icon
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.icon_label)
        self.toggled = False
        self.load_icon(GraphicsDirectoryPath("mic-off.png"))

        # Auto-refresh timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessage)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(1000)  # refresh every 1s

        # Scrollbar style
        self.chat_text_edit.setStyleSheet("""
            QScrollBar:vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: black;
                height: 10px;
            }
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                background:none;
                border:none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

    def loadMessage(self):
        """Load new chat messages if file changed"""
        global old_chat_message
        try:
            with open(TempDirectoryPath("Responses.data"), "r", encoding="utf-8") as file:
                messages = file.read().strip()
            if not messages or messages == old_chat_message:
                return
            self.addMessage(messages, color="white")
            old_chat_message = messages
        except FileNotFoundError:
            pass

    def SpeechRecogText(self):
        """Load recognition status"""
        try:
            with open(TempDirectoryPath("Status.data"), "r", encoding="utf-8") as file:
                messages = file.read().strip()
            self.label.setText(messages)
        except FileNotFoundError:
            self.label.setText("")

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print(f"⚠️ Icon not found: {path}")
            return
        new_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath("mic-on.png"))
            MicButtonInitilized()
        else:
            self.load_icon(GraphicsDirectoryPath("mic-off.png"))
            MicButtonClosed()
        self.toggled = not self.toggled

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)


class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)

        # 🎞️ GIF
        gif_label = QLabel()
        self.movie = QMovie(GraphicsDirectoryPath('jarvis.gif'))
        self.movie.start()

        gif_width = self.movie.frameRect().width()
        gif_height = self.movie.frameRect().height()

        if gif_width == 0 or gif_height == 0:
            gif_width, gif_height = screen_width, screen_height

        scale_w = screen_width / gif_width
        scale_h = screen_height / gif_height
        scale_factor = min(scale_w, scale_h)

        new_width = int(gif_width * scale_factor)
        new_height = int(gif_height * scale_factor)

        self.movie.setScaledSize(QSize(new_width, new_height))
        gif_label.setMovie(self.movie)
        gif_label.setAlignment(Qt.AlignCenter)
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # 🎤 mic icon
        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath('mic-on.png'))
        new_pixmap = pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.toggled = True
        self.toggle_icon()
        self.icon_label.mousePressEvent = self.toggle_icon

        # 📝 status label
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size: 16px; margin-bottom:0;")

        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)

        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        # timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(1000)

    def SpeechRecogText(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read().strip()
            self.label.setText(messages)
        except FileNotFoundError:
            self.label.setText("")

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('mic-on.png'))
            MicButtonInitilized()
        else:
            self.load_icon(GraphicsDirectoryPath('mic-off.png'))
            MicButtonClosed()

        self.toggled = not self.toggled





class MessageScreen (QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop= QApplication.desktop()
        screen_width =desktop.screenGeometry().width()
        screen_height= desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight (screen_height)
        self.setFixedWidth(screen_width)
class CustomTopBar (QWidget):
   
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen=None
        self.current_screen = None
        self.stacked_widget = stacked_widget
    def initUI(self):
        self.setFixedHeight(50)
        layout =QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        home_button =QPushButton()
        home_icon =QIcon(GraphicsDirectoryPath("Home.png"))
        home_button.setIcon(home_icon)
        home_button.setText(" Home")
        home_button.setStyleSheet("height:40px; line-height:40px; background-color: white; color: black")
        message_button =QPushButton()
        message_icon =QIcon(GraphicsDirectoryPath("Chats.png"))
        message_button.setIcon(message_icon)
        message_button.setText(" Chat")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color:white; color: black")
        minimize_button =QPushButton()
        message_icon =QIcon(GraphicsDirectoryPath("Chats.png"))
        message_button.setIcon(message_icon)
        message_button.setText(" Chat")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color: white; color: black")
        minimize_button =QPushButton()
        minimize_icon =QIcon(GraphicsDirectoryPath('minus.png'))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button =QPushButton()
        self.maximize_icon= QIcon (GraphicsDirectoryPath('maximize.png'))
        self.restore_icon =QIcon(GraphicsDirectoryPath('minus.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        close_button =QPushButton()
        close_icon = QIcon (GraphicsDirectoryPath('cancel.png'))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)
        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape (QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")
        title_label = QLabel(f" {str(Assistantname).capitalize()} AI ")
        title_label.setStyleSheet("color: black; font-size: 18px;; background-color:white")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)
        self.draggable = True
        self.offset = None
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)
    def minimizeWindow(self):
        self.parent().showMinimized()
    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)
    def closeWindow(self):
        self.parent().close()

    def mousePressEvent (self, event):
        if self.draggable: self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos()-self.offset
            self.parent().move(new_pos)

    def showMessageScreen(self):

        if self.current_screen is not None: 
            self.current_screen.hide()

        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen= message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        initial_screen=InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen =initial_screen


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop =QApplication.desktop()
        screen_width =desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen =InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry (0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        
        self.setCentralWidget(stacked_widget)
def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    GraphicalUserInterface()

       

        


