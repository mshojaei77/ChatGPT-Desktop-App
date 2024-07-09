import os
from openai import OpenAI
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt


class ChatGPT():
    def __init__(self, openai_api_key, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model

    def create_chat_completion(self, messages):
        # Simplified method call for UI integration
        try:
            response = self.client.chat.completions.create(model=self.model, messages=messages)
            return response.choices[0].message.content
        except Exception as e:
            print(f"create_chat_completion Failed : {e}")
            return ""


class MainWindow(QMainWindow):
    def __init__(self, chatbot):
        super().__init__()
        self.chatbot = chatbot
        self.initUI()

    def initUI(self):
        # Create central widget and layout
        centralWidget = QWidget()
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)

        # Chat history text edit
        self.chatHistory = QTextEdit()
        self.chatHistory.setReadOnly(True)
        layout.addWidget(self.chatHistory)

        # User input line edit and send button
        userInputLayout = QHBoxLayout()
        self.userInput = QLineEdit()
        self.userInput.returnPressed.connect(self.sendMessage)
        userInputLayout.addWidget(self.userInput)

        sendButton = QPushButton("Send")
        sendButton.clicked.connect(self.sendMessage)
        userInputLayout.addWidget(sendButton)

        layout.addLayout(userInputLayout)

        # Set window properties
        self.setWindowTitle('ChatGPT UI')
        self.setGeometry(100, 100, 600, 400)

    def sendMessage(self):
        user_message = self.userInput.text().strip()
        if user_message:
            self.chatHistory.append(f"User: {user_message}")
            self.userInput.clear()

            # Generate assistant message
            messages = [{'role': 'system', 'content': "You are a helpful assistant."}, {'role': 'user', 'content': user_message}]
            assistant_message = self.chatbot.create_chat_completion(messages)
            self.chatHistory.append(f"Assistant: {assistant_message}")


if __name__ == "__main__":
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    chatbot = ChatGPT(OPENAI_KEY, model="gpt-3.5-turbo")

    app = QApplication([])
    mainWindow = MainWindow(chatbot)
    mainWindow.show()
    app.exec()
