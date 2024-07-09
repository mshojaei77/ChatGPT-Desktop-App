import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QLineEdit, QTextEdit, QListWidget, 
                               QListWidgetItem, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor, QPalette, QColor
from openai import OpenAI

class ChatGPT:
    def __init__(self, openai_api_key, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model

    def create_chat_completion(self, messages, **kwargs):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response
        except Exception as e:
            raise Exception(f"An error occurred: {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT Desktop App")
        self.setGeometry(100, 100, 1200, 800)

        # Set light theme
        app.setStyle("Fusion") 
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(245, 245, 245))  # Light background
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.Text, Qt.black)
        app.setPalette(palette)

        self.openai_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_key:
            QMessageBox.critical(self, "Error", 
                                "OPENAI_API_KEY environment variable not set!")
            sys.exit(1)

        self.chatbot = ChatGPT(self.openai_key)
        self.messages = [{'role': 'system', 'content': "You are a helpful assistant."}]

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(250)
        self.layout.addWidget(self.sidebar)

        self.sidebar.addItem("ChatGPT")
        self.sidebar.addItem("Prompt Professor")
        self.sidebar.addItem("Machine Learning")
        self.sidebar.currentItemChanged.connect(self.update_chat_content)

        # Content Area
        self.content_area = QVBoxLayout()
        self.layout.addLayout(self.content_area)

        # Chat Display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.content_area.addWidget(self.chat_display)

        # User Input Area
        self.user_input = QLineEdit()
        self.user_input.returnPressed.connect(self.send_message)
        self.content_area.addWidget(self.user_input)

        # Send Button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        self.content_area.addWidget(self.send_button)

    def send_message(self):
        user_prompt = self.user_input.text()
        if not user_prompt:
            return

        self.display_message(user_prompt, "User")
        self.user_input.clear()

        try:
            response = self.chatbot.create_chat_completion(
                self.messages, stream=True
            )

            self.display_message("...", "Assistant")

            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    self.update_last_message(full_response, "Assistant")

            self.messages.append({'role': 'assistant', 'content': full_response})

        except Exception as e:
            self.display_message(f"Error: {str(e)}", "System")

    def display_message(self, message, sender):
        self.chat_display.append(f"<strong>{sender}:</strong> {message}")

    def update_last_message(self, new_text, sender):
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End) 
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        cursor.removeSelectedText()
        self.chat_display.append(f"<strong>{sender}:</strong> {new_text}")

    def update_chat_content(self, current, previous):
        item_text = current.text()
        self.chat_display.clear()
        self.display_message(f"Selected: {item_text}", "System")
        self.messages = [{'role': 'system', 'content': "You are a helpful assistant."}]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())