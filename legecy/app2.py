import sys
import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QLineEdit, QTextEdit, QListWidget)
from PySide6.QtCore import Qt
from openai import OpenAI

class ChatGPT:
    def __init__(self, openai_api_key, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model

    def create_chat_completion(self, messages, n=1, max_tokens=1000, temperature=0.7,
                               frequency_penalty=1, response_format={"type": "text"},
                               function_call=None, tools=None, presence_penalty=None,
                               stream=None, tool_choice=None, top_p=None, user=None,
                               extra_headers=None, extra_query=None, extra_body=None, timeout=None):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                n=n,
                max_tokens=max_tokens,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                response_format=response_format,
                function_call=function_call,
                tools=tools,
                presence_penalty=presence_penalty,
                stream=stream,
                tool_choice=tool_choice,
                top_p=top_p,
                user=user,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout
            )
            return response
        except Exception as e:
            print(f"create_chat_completion Failed : {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #1E1E1E; color: white;")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Layout
        self.layout = QHBoxLayout(self.central_widget)
        
        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setStyleSheet("background-color: #2D2D2D;")
        self.layout.addWidget(self.sidebar)
        
        # Add items to the sidebar
        sidebar_items = ["ChatGPT", "Prompt Professor", "Machine Learning", "Explore GPTs",
                         "Asyncio Subprocess Not Implemented", "Transform Video Transcripts Efficiently",
                         "Content Transformation Prompt", "Convert List to String",
                         "Print Colab Notebook Python", "Coding Tutorial Features",
                         "Long-Form Blog Creation", "LLM Learning Resources",
                         "Learn LLMs from Scratch", "Intro to LLMs Explanation", "Upgrade plan"]
        self.sidebar.addItems(sidebar_items)

        # Main content area
        self.content_area = QVBoxLayout()
        self.layout.addLayout(self.content_area)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        self.content_area.addLayout(self.button_layout)
        
        button_texts = ["Content calendar for TikTok", "Overcome procrastination",
                        "Morning routine for productivity", "Make me a personal webpage"]
        for text in button_texts:
            button = QPushButton(text)
            button.setStyleSheet("background-color: #3E3E3E;")
            self.button_layout.addWidget(button)
        
        # Chat area
        self.chat_area = QVBoxLayout()
        self.content_area.addLayout(self.chat_area)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #2D2D2D;")
        self.chat_area.addWidget(self.chat_display)
        
        self.user_input = QLineEdit()
        self.user_input.setStyleSheet("background-color: #3E3E3E;")
        self.user_input.returnPressed.connect(self.send_message)
        self.chat_area.addWidget(self.user_input)
        
        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("background-color: #0078D7;")
        self.send_button.clicked.connect(self.send_message)
        self.chat_area.addWidget(self.send_button)
        
        # Initialize ChatGPT
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.chatbot = ChatGPT(self.openai_key, model="gpt-3.5-turbo")
        self.messages = [{'role': 'system', 'content': "You are a helpful assistant."}]
        
    def send_message(self):
        user_prompt = self.user_input.text()
        if not user_prompt:
            return
        
        self.messages.append({'role': 'user', 'content': user_prompt})
        self.chat_display.append(f"User: {user_prompt}")
        
        response = self.chatbot.create_chat_completion(self.messages)
        response_text = response.choices[0].message.content
        
        self.chat_display.append(f"Assistant: {response_text}")
        self.messages.append({'role': 'assistant', 'content': response_text})
        
        self.user_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())