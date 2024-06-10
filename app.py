import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QHBoxLayout, QMainWindow
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# Import the ChatBot class from your module
from modules.chatbot import ChatBotModule
from modules.talk import TalkModule

# Initialize the ChatBot with the desired model type and necessary parameters
chatbot = ChatBotModule(model_type="diablo")  # Change to "openai" or "gemini" as needed
talk_module = TalkModule()

class LoadingThread(QThread):
    update_loading = pyqtSignal(str)

    def run(self):
        loading_wave = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.loading = True
        while self.loading:
            for wave in loading_wave:
                if not self.loading:
                    break
                self.update_loading.emit(wave)
                self.msleep(100)

class ResponseThread(QThread):
    response_ready = pyqtSignal(str)

    def __init__(self, user_msg):
        super().__init__()
        self.user_msg = user_msg

    def run(self):
        try:
            answer = chatbot.get_response(self.user_msg)
        except Exception as e:
            answer = f"Error: {str(e)}"
        self.response_ready.emit(answer)

class VoiceInputThread(QThread):
    voice_input_ready = pyqtSignal(str)
    stop_listening = pyqtSignal()

    def __init__(self, keywords):
        super().__init__()
        self.keywords = keywords

    def run(self):
        while True:
            # Continuously listen for keywords
            text, stop = talk_module.listen_for_keywords(self.keywords)
            if stop:
                self.stop_listening.emit()
                break
            self.voice_input_ready.emit(text)


class ChatApplication(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.loading_thread = LoadingThread()
        self.loading_thread.update_loading.connect(self.update_loading_animation)

    def initUI(self):
        self.setWindowTitle('JARVIS Chat Application')
        self.setGeometry(100, 100, 480, 600)

        # Set overall palette for the window
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(24, 24, 24))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        self.setPalette(palette)

        # Set main layout
        main_layout = QVBoxLayout()

        # Header label
        header_label = QLabel('JARVIS Chat', self)
        header_label.setFont(QFont('Helvetica', 20, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #00FF00;")
        main_layout.addWidget(header_label)

        # Chat display area
        self.chat_area = QTextEdit(self)
        self.chat_area.setReadOnly(True)
        self.chat_area.setStyleSheet("background-color: #2E2E2E; color: #FFFFFF; padding: 10px; border: 1px solid #00FF00;")
        main_layout.addWidget(self.chat_area)

        # Message entry area
        msg_layout = QHBoxLayout()
        
        self.msg_entry = QLineEdit(self)
        self.msg_entry.setFont(QFont('Helvetica', 14))
        self.msg_entry.setStyleSheet("background-color: #2E2E2E; color: #FFFFFF; padding: 10px; border: 1px solid #00FF00;")
        self.msg_entry.returnPressed.connect(self.on_send)
        msg_layout.addWidget(self.msg_entry)
        
        send_button = QPushButton('Send', self)
        send_button.setFont(QFont('Helvetica', 14, QFont.Bold))
        send_button.setStyleSheet("background-color: #00FF00; color: #000000; padding: 10px; border: 1px solid #00FF00;")
        send_button.clicked.connect(self.on_send)
        msg_layout.addWidget(send_button)

        # Voice input button
        voice_button = QPushButton('Voice Input', self)
        voice_button.setFont(QFont('Helvetica', 14, QFont.Bold))
        voice_button.setStyleSheet("background-color: #00FF00; color: #000000; padding: 10px; border: 1px solid #00FF00;")
        voice_button.clicked.connect(self.on_voice_input)
        msg_layout.addWidget(voice_button)

        # Setting the central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        main_layout.addLayout(msg_layout)

    def on_send(self):
        msg = self.msg_entry.text()
        if not msg:
            return
        
        self.msg_entry.clear()
        self.insert_message(f"You: {msg}")
        self.generate_response(msg)
        
    def on_voice_input(self):
        self.voice_input_thread = VoiceInputThread(keywords=["stop listening", "exit", "quit"])
        self.voice_input_thread.voice_input_ready.connect(self.handle_voice_input)
        self.voice_input_thread.stop_listening.connect(self.handle_stop_listening)
        self.voice_input_thread.start()
        
    def handle_voice_input(self, text):
        self.insert_message(f"You: {text}")
        self.generate_response(text)
        
    def handle_stop_listening(self):
        self.insert_message("Bot: Stopping voice input.")

    def insert_message(self, msg):
        self.chat_area.append(msg)
        
    def generate_response(self, user_msg):
        self.loading_message_id = self.chat_area.toPlainText().count('\n') + 1
        self.chat_area.append("Bot: ⠋")
        self.loading_thread.start()
        
        # Call the custom chatbot API to get a response in a separate thread
        self.response_thread = ResponseThread(user_msg)
        self.response_thread.response_ready.connect(self.insert_response)
        self.response_thread.start()

    def update_loading_animation(self, wave):
        cursor = self.chat_area.textCursor()
        cursor.movePosition(cursor.End, cursor.MoveAnchor)
        cursor.select(cursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.insertText(f"Bot: {wave}")
        self.chat_area.setTextCursor(cursor)

    def insert_response(self, response):
        self.loading_thread.loading = False
        self.loading_thread.quit()
        
        cursor = self.chat_area.textCursor()
        cursor.movePosition(cursor.End, cursor.MoveAnchor)
        cursor.select(cursor.LineUnderCursor)
        cursor.removeSelectedText()
        cursor.insertText(f"Bot: {response}")
        self.chat_area.setTextCursor(cursor)

        # Speak the response
        talk_module.speak(response)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    chat_app = ChatApplication()
    chat_app.show()
    sys.exit(app.exec_())
