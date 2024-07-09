import os
import sys
import json
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from responder import ChatGPT
from dotenv import load_dotenv, set_key, find_dotenv
load_dotenv()
import fitz  # PyMuPDF

class ChatThread(QThread):
    response_received = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, chatbot, messages, rag, file_path):
        super().__init__()
        self.chatbot = chatbot
        self.messages = messages
        self.rag = rag
        self.file_path = file_path

    def run(self):
        try:
            if self.rag:
                user_message = self.messages[-1]["content"]
                if self.file_path.endswith('.pdf'):
                    contents = self.get_pdf_contents(self.file_path)
                else:
                    contents = self.chatbot.get_file_contents(self.file_path, query=user_message)
                self.messages[-1]["content"] = f"answer this query: {user_message} using following context \n {contents}"
            response = self.chatbot.create_chat_completion(self.messages)
            self.response_received.emit(response)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def get_pdf_contents(self, file_path):
        document = fitz.open(file_path)
        contents = []
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            contents.append(page.get_text())
        return "\n".join(contents)



class Conversation:
    def __init__(self, title=None):
        self.title = title
        self.chatbot = ChatGPT(openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.messages = []
        self.created_at = datetime.now()

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
        if not self.title and len(self.messages) >= 4:
            self.title = self.generate_title()

    def generate_title(self):
        user_messages = [msg['content'] for msg in self.messages[:4]]
        prompt = f'choose one word name for following conversation: \n {user_messages}'

        title = self.chatbot.create_chat_completion(
            [{'role': 'user', 'content': prompt}])

        return title if title else "Untitled Chat"

    def to_dict(self):
        return {
            "title": self.title,
            "messages": self.messages,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        conv = cls(data["title"])
        conv.messages = data["messages"]
        conv.created_at = datetime.fromisoformat(data["created_at"])
        return conv


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT")
        self.setGeometry(200, 50, 100, 100)
        self.setMinimumSize(1000, 660)

        self.conversations = []
        self.current_conversation = None
        self.load_conversations()
        self.rag = False
        self.file_path = None

        # Define is_dark_mode here
        self.is_dark_mode = False

        self.setup_ui()
        self.setup_chatgpt()

        # Set default theme
        self.apply_theme()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left sidebar
        self.left_widget = QWidget()
        self.left_widget.setMaximumWidth(300)  # Set maximum width for sidebar
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(10, 10, 10, 10)
        self.left_layout.setSpacing(10)

        # Add Search Bar for Conversations
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Conversations...")
        self.search_bar.textChanged.connect(self.filter_conversations)
        self.left_layout.addWidget(self.search_bar)

        self.conversation_list = QListWidget()
        self.conversation_list.setFixedHeight(300)
        self.conversation_list.setObjectName("conversation-list")
        self.conversation_list.itemClicked.connect(self.switch_conversation)
        self.conversation_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.conversation_list.customContextMenuRequested.connect(self.show_context_menu)
        self.left_layout.addWidget(self.conversation_list)

        clear_btn = QPushButton("Clear conversations")
        clear_btn.setObjectName("clear-btn")
        clear_btn.clicked.connect(self.clear_conversations)
        upgrade_btn = QPushButton("Upgrade to Plus")
        upgrade_btn.setObjectName("upgrade-btn")
        self.left_layout.addWidget(clear_btn)
        self.left_layout.addWidget(upgrade_btn)
        self.left_layout.addStretch()

        # Add dark mode switch button
        self.theme_button = QPushButton("Dark Mode")
        self.theme_button.setObjectName("theme-button")
        self.theme_button.clicked.connect(self.toggle_theme)
        self.left_layout.addWidget(self.theme_button)

        settings_btn = QPushButton("Settings")
        settings_btn.setObjectName("settings-btn")
        self.left_layout.addWidget(settings_btn)
        settings_btn.clicked.connect(self.edit_settings)

        # Right content area
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(10)

        top_layout = QHBoxLayout()
        right_layout.addLayout(top_layout)
        # Add Model dropdown
        self.model_dropdown = QComboBox()
        self.model_dropdown.addItems(
            ["gpt-3.5-turbo", "gpt-4o"])  # Add your models here
        self.model_dropdown.setCurrentText("gpt-3.5-turbo")
        self.model_dropdown.setFixedWidth(150)
        self.model_dropdown.currentIndexChanged.connect(self.change_model)
        top_layout.addWidget(self.model_dropdown, 0, Qt.AlignLeft)

        new_chat_btn = QPushButton("New Chat")
        # new_chat_btn.setIcon(QIcon("new_chat.png"))
        new_chat_btn.setFixedWidth(150)
        new_chat_btn.setObjectName("new-chat-btn")
        new_chat_btn.clicked.connect(self.new_chat)
        top_layout.addWidget(new_chat_btn, 0, Qt.AlignRight)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setObjectName("chat-display")
        right_layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()

        self.upload_button = QPushButton()
        self.upload_button.setIcon(QIcon("document.png"))
        self.upload_button.setObjectName("upload-btn")
        self.upload_button.clicked.connect(self.upload_document)
        input_layout.addWidget(self.upload_button)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Message ChatGPT...")
        self.input_field.setObjectName("input-field")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        send_btn = QPushButton("Send")
        send_btn.setObjectName("send-btn")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)

        right_layout.addLayout(input_layout)

        main_layout.addWidget(self.left_widget, 1)
        main_layout.addWidget(right_widget, 3)

        self.apply_macos_style()
        self.update_conversation_list()

    def apply_light_theme(self):
        light_theme = open('light_theme.css', 'r', encoding='utf-8').read()
        self.setStyleSheet(light_theme)
        self.upload_button.setIcon(QIcon("document.png"))

    def apply_dark_theme(self):
        dark_theme = open('dark_theme.css', 'r', encoding='utf-8').read()
        self.setStyleSheet(dark_theme)
        self.upload_button.setIcon(QIcon("document_dark.png"))

    def apply_macos_style(self):
        if self.is_dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()
        self.theme_button.setText(
            "Light Mode" if self.is_dark_mode else "Dark Mode")

    def apply_theme(self):
        if self.is_dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()


    def setup_chatgpt(self):
        try:
            load_dotenv()
            OPENAI_KEY = os.getenv("OPENAI_API_KEY")
            
            if not OPENAI_KEY:
                OPENAI_KEY, ok = QInputDialog.getText(self, "API Key Required", "Please enter your OpenAI API Key:")
                
                if ok and OPENAI_KEY:
                    dotenv_path = find_dotenv()
                    if not dotenv_path:
                        with open('.env', 'w') as f:
                            f.write('')
                        dotenv_path = find_dotenv()
                    
                    set_key(dotenv_path, "OPENAI_API_KEY", OPENAI_KEY)
                else:
                    QMessageBox.critical(self, "API Key Error", "API key is required to proceed.")
                    sys.exit(1)
            self.chatbot = ChatGPT(OPENAI_KEY, model="gpt-3.5-turbo")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to initialize ChatGPT: {str(e)}")
            sys.exit(1)

    def edit_settings(self):
        # Prompt user to input a new API key
        new_key, ok = QInputDialog.getText(self, "Edit API Key", "Enter new OpenAI API Key:")
        if ok and new_key:
            try:
                dotenv_path = find_dotenv()
                if not dotenv_path:
                    with open('.env', 'w') as f:
                        f.write('')
                    dotenv_path = find_dotenv()
                set_key(dotenv_path, "OPENAI_API_KEY", new_key)
                os.environ["OPENAI_API_KEY"] = new_key
                self.chatbot = ChatGPT(new_key, model=self.model_dropdown.currentText())
                QMessageBox.information(self, "Success", "API Key updated successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update API Key: {str(e)}")

    def new_chat(self):
        new_conversation = Conversation()
        self.conversations.append(new_conversation)
        self.current_conversation = new_conversation
        self.update_conversation_list()
        self.clear_chat_display()

    def switch_conversation(self, item):
        index = self.conversation_list.row(item)
        self.current_conversation = self.conversations[index]
        self.clear_chat_display()
        self.display_conversation()
        self.title_label.setText(self.current_conversation.title)

    def handle_response(self, response):
        self.current_conversation.add_message("assistant", response)
        self.display_message("ChatGPT", response)
        self.save_conversations()
        self.update_conversation_list()

    def send_message(self):
        if not self.current_conversation:
            self.new_chat()
        user_message = self.input_field.text().strip()
        if not user_message:
            return

        self.current_conversation.add_message("user", user_message)

        self.display_message("You", user_message)
        self.input_field.clear()

        self.chat_thread = ChatThread(
            self.chatbot, self.current_conversation.messages, self.rag, self.file_path
        )
        self.chat_thread.response_received.connect(self.handle_response)
        self.chat_thread.error_occurred.connect(self.handle_error)
        self.chat_thread.start()

        self.update_conversation_list()

    def handle_error(self, error_message):
        QMessageBox.warning(
            self, "Error", f"An error occurred: {error_message}")

    def display_message(self, sender, message):
        if sender == "ChatGPT":
            icon_path = "chatgpt.png"
            message_html = f"""
            <div
                <div style="display: flex; align-items: center; justify-content: flex-start; margin-bottom: 10px;">
                    <img src="{icon_path}" alt="ChatGPT" width="16" height="16" style="margin-right: 10px;">
                    {message}
                </div>
            </div>    
            """
        else:
            message_html = f"""
                <div style="text-align: right; margin-bottom: 10px;">
                    <div style="display: inline-block; text-align: left;">
                        {message}
                    </div>
                </div>
            """

        self.chat_display.append(message_html)
        self.chat_display.append("")

    def clear_chat_display(self):
        self.chat_display.clear()

    def display_conversation(self):
        for message in self.current_conversation.messages:
            sender = "You" if message["role"] == "user" else "ChatGPT"
            self.display_message(sender, message["content"])

    def update_conversation_list(self):
        self.conversation_list.clear()
        for conversation in self.conversations:
            item = QListWidgetItem(conversation.title or "New Chat")
            self.conversation_list.addItem(item)

    def clear_conversations(self):
        reply = QMessageBox.question(self, "Clear Conversations",
                                     "Are you sure you want to clear all conversations?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.conversations.clear()
            self.current_conversation = None
            self.update_conversation_list()
            self.clear_chat_display()
            self.title_label.setText("ChatGPT")
            self.save_conversations()

    def show_context_menu(self, position):
        if not self.conversation_list.itemAt(position):
            return

        context_menu = QMenu(self)
        rename_action = QAction("Rename", self)
        delete_action = QAction("Delete", self)

        context_menu.addAction(rename_action)
        context_menu.addAction(delete_action)

        action = context_menu.exec(
            self.conversation_list.mapToGlobal(position))

        if action == rename_action:
            self.rename_conversation()
        elif action == delete_action:
            self.delete_conversation()

    def rename_conversation(self):
        current_item = self.conversation_list.currentItem()
        if current_item:
            index = self.conversation_list.row(current_item)
            conversation = self.conversations[index]
            new_title, ok = QMessageBox.getText(self, "Rename Conversation",
                                                "Enter new title:", text=conversation.title)
            if ok and new_title:
                conversation.title = new_title
                current_item.setText(new_title)
                if self.current_conversation == conversation:
                    self.title_label.setText(new_title)
                self.save_conversations()

    def delete_conversation(self):
        current_item = self.conversation_list.currentItem()
        if current_item:
            reply = QMessageBox.question(self, "Delete Conversation",
                                         "Are you sure you want to delete this conversation?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                index = self.conversation_list.row(current_item)
                del self.conversations[index]
                self.conversation_list.takeItem(index)
                if self.current_conversation == self.conversations[index]:
                    self.current_conversation = None
                    self.clear_chat_display()
                    self.title_label.setText("ChatGPT")
                self.save_conversations()

    def save_conversations(self):
        data = [conv.to_dict() for conv in self.conversations]
        with open("conversations.json", "w") as f:
            json.dump(data, f)

    def load_conversations(self):
        try:
            with open("conversations.json", "r") as f:
                data = json.load(f)
                self.conversations = [Conversation.from_dict(
                    conv_data) for conv_data in data]
        except FileNotFoundError:
            self.conversations = []

    def upload_document(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilters(["Documents (*.pdf *.docx *.txt)"])
        if file_dialog.exec():
            self.file_path = file_dialog.selectedFiles()[0]
            if self.file_path:
                self.rag = True
                self.display_message("📚", f'file uploaded {self.file_path}')


    def change_model(self):
        selected_model = self.model_dropdown.currentText()
        self.chatbot.model = selected_model

    def filter_conversations(self):
        search_text = self.search_bar.text().lower()
        for i in range(self.conversation_list.count()):
            item = self.conversation_list.item(i)
            if search_text in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
