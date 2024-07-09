import os
from openai import OpenAI
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

class ChatGPT():
    def __init__(self, openai_api_key, model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model

    def create_chat_completion(self, messages, n=1, max_tokens=1000, temperature=0.7, frequency_penalty=1, response_format={"type": "text"}, function_call=None, tools=None, presence_penalty=None, stream=None, tool_choice=None, top_p=None, user=None, extra_headers=None, extra_query=None, extra_body=None, timeout=None):
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
            print(f"create_chat_completion Failed: {e}")

class ChatWindow(QMainWindow):
    def __init__(self, chatbot):
        super().__init__()
        self.chatbot = chatbot
        self.messages = [{'role': 'system', 'content': "You are a helpful assistant."}]
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ChatGPT Interface')
        self.setGeometry(100, 100, 800, 600)

        self.text_display = QTextEdit(self)
        self.text_display.setReadOnly(True)

        self.input_field = QLineEdit(self)
        self.input_field.returnPressed.connect(self.send_message)

        layout = QVBoxLayout()
        layout.addWidget(self.text_display)
        layout.addWidget(self.input_field)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def send_message(self):
        user_prompt = self.input_field.text()
        self.input_field.clear()
        self.messages.append({'role': 'user', 'content': user_prompt})
        self.text_display.append(f"User: {user_prompt}")

        response = self.chatbot.create_chat_completion(self.messages, stream=True)
        if response:
            streamed_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    streamed_response += chunk.choices[0].delta.content
                    self.text_display.insertPlainText(chunk.choices[0].delta.content)
            self.messages.append({'role': 'assistant', 'content': streamed_response})

if __name__ == "__main__":
    import sys
    OPENAI_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_KEY:
        raise ValueError("Please set the OPENAI_API_KEY environment variable.")

    chatbot = ChatGPT(OPENAI_KEY, model="gpt-3.5-turbo")

    app = QApplication(sys.argv)
    window = ChatWindow(chatbot)
    window.show()
    sys.exit(app.exec())