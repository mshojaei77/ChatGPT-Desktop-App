import os
import sys
from openai import OpenAI
from PySide6.QtWidgets import QApplication, QMainWindow, QTextEdit, QLineEdit, QVBoxLayout, QWidget

class ChatGPT():
    def __init__(self, openai_api_key,model="gpt-3.5-turbo"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model

    def create_chat_completion(
        self,
        messages,
        n = 1, # The number of responses to generate.
        max_tokens= 1000,
        temperature = 0.7,
        frequency_penalty = 1, # higher value (up to 2) reduces the model's tendency to repeat phrases.
        response_format =  { "type": "text" },
        function_call = None,
        tools = None,
        presence_penalty = None,
        stream = None,
        tool_choice = None,
        top_p = None,
        user = None,
        extra_headers = None,
        extra_query = None,
        extra_body = None,
        timeout = None
    ):
        try:
            # Create the chat completion request
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                n = n,
                max_tokens= max_tokens,
                temperature = temperature,
                frequency_penalty = frequency_penalty,
                response_format = response_format,
                function_call = function_call,
                tools = tools,
                presence_penalty = presence_penalty,
                stream = stream,
                tool_choice = tool_choice,
                top_p = top_p,
                user = user,
                extra_headers = extra_headers,
                extra_query = extra_query,
                extra_body = extra_body,
                timeout = timeout
            )

            '''response_info = [
                response.id,  # 0 'chatcmpl-9cGPTPYngw7UzgLU3XwMFfLLLKNY9'
                response.choices[0].finish_reason,  # 1 # 'stop'
                response.choices[0].index,  # 2 # 0
                response.choices[0].logprobs,  # 3 # None
                response.choices[0].message.content,  # 4 # [answer]
                response.choices[0].message.role,  # 5 # assistant
                response.choices[0].message.function_call,  # 6 # None
                response.choices[0].message.tool_calls,  # 7 #None
                response.created,  # 8 # 1718906628
                response.model,  # 9 # 'gpt-3.5-turbo-0125'
                response.object,  # 10 # 'chat.completion'
                response.service_tier,  # 11 # None
                response.system_fingerprint,  # 12 # None
                response.usage.completion_tokens,  # 13 #25
                response.usage.prompt_tokens,  # 14 #36
                response.usage.total_tokens  # 15 #61
                ]'''

            return response

        except Exception as e:
            print(f"create_chat_completion Failed : {e}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.chatbot = ChatGPT(os.getenv("OPENAI_API_KEY"), model="gpt-3.5-turbo")
        self.messages = [{'role': 'system', 'content': "You are a helpful assistant."}]

        self.setWindowTitle("ChatGPT UI")

        self.layout = QVBoxLayout()

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.layout.addWidget(self.chat_history)

        self.user_input = QLineEdit()
        self.user_input.returnPressed.connect(self.send_message)
        self.layout.addWidget(self.user_input)

        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

    def send_message(self):
        user_prompt = self.user_input.text()
        self.user_input.clear()

        self.messages.append({'role': 'user', 'content': user_prompt})
        self.chat_history.append(f"User: {user_prompt}")

        response = self.chatbot.create_chat_completion(self.messages)
        assistant_response = response.choices[0].message.content

        self.messages.append({'role': 'assistant', 'content': assistant_response})
        self.chat_history.append(f"Assistant: {assistant_response}")

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
