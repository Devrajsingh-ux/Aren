import sys
import logging
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
                            QLabel, QScrollArea, QFrame, QSplitter, QMenuBar,
                            QMenu, QStatusBar, QToolBar, QStyle, QMessageBox,
                            QComboBox, QSystemTrayIcon, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QTextCursor, QIcon, QAction, QTextCharFormat

logger = logging.getLogger(__name__)

class ThemeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Choose Theme")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark Theme", "Light Theme", "Blue Theme", "Green Theme"])
        layout.addWidget(QLabel("Select Theme:"))
        layout.addWidget(self.theme_combo)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

class ChatThread(QThread):
    """Thread for processing chat messages."""
    response_ready = pyqtSignal(str)

    def __init__(self, processor, message):
        super().__init__()
        self.processor = processor
        self.message = message

    def run(self):
        """Process the message and emit the response."""
        try:
            response = self.processor.process_input(self.message)
            self.response_ready.emit(response)
        except Exception as e:
            logger.error(f"Error in chat thread: {str(e)}")
            self.response_ready.emit("I encountered an error processing your message.")

class MainWindow(QMainWindow):
    def __init__(self, processor):
        super().__init__()
        self.processor = processor
        self.current_theme = "dark"
        self.init_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_tray()
        
        # Auto-save timer
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.auto_save_chat)
        self.save_timer.start(300000)  # Save every 5 minutes

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("A.R.E.N - Advanced Response Engine")
        self.setMinimumSize(1000, 700)

        # Set dark theme by default
        self.apply_theme("dark")

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Create chat display area with custom styling
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setFont(QFont("Segoe UI", 11))
        self.chat_display.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        layout.addWidget(self.chat_display)

        # Create input area with a frame
        input_frame = QFrame()
        input_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add emoji button
        emoji_button = QPushButton("😊")
        emoji_button.setFixedWidth(40)
        emoji_button.clicked.connect(self.show_emoji_picker)
        input_layout.addWidget(emoji_button)
        
        self.input_field = QLineEdit()
        self.input_field.setFont(QFont("Segoe UI", 11))
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        send_button = QPushButton("Send")
        send_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_CommandLink))
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)

        layout.addWidget(input_frame)

        # Add welcome message
        self.add_message("A.R.E.N", "Hello! I'm A.R.E.N, your advanced AI assistant. How can I help you today?")

    def apply_theme(self, theme):
        """Apply the selected theme."""
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #1e1e1e;
                }
                QTextEdit {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    padding: 10px;
                    font-family: 'Segoe UI', Arial;
                    font-size: 11pt;
                }
                QLineEdit {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    padding: 8px;
                    font-family: 'Segoe UI', Arial;
                    font-size: 11pt;
                }
                QPushButton {
                    background-color: #0d47a1;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 5px;
                    font-family: 'Segoe UI', Arial;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #1565c0;
                }
                QPushButton:pressed {
                    background-color: #0a3d91;
                }
                QMenuBar {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QMenuBar::item:selected {
                    background-color: #3d3d3d;
                }
                QMenu {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                }
                QMenu::item:selected {
                    background-color: #3d3d3d;
                }
                QStatusBar {
                    background-color: #1e1e1e;
                    color: #ffffff;
                }
                QToolBar {
                    background-color: #1e1e1e;
                    border: none;
                }
                QToolButton {
                    background-color: transparent;
                    border: none;
                    padding: 5px;
                }
                QToolButton:hover {
                    background-color: #3d3d3d;
                    border-radius: 3px;
                }
                QComboBox {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    border: 1px solid #3d3d3d;
                    border-radius: 5px;
                    padding: 5px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border: none;
                }
            """)
        elif theme == "light":
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #f5f5f5;
                }
                QTextEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    padding: 10px;
                    font-family: 'Segoe UI', Arial;
                    font-size: 11pt;
                }
                QLineEdit {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    padding: 8px;
                    font-family: 'Segoe UI', Arial;
                    font-size: 11pt;
                }
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 5px;
                    font-family: 'Segoe UI', Arial;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
                QMenuBar {
                    background-color: #f5f5f5;
                    color: #000000;
                }
                QMenuBar::item:selected {
                    background-color: #e0e0e0;
                }
                QMenu {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                }
                QMenu::item:selected {
                    background-color: #e0e0e0;
                }
                QStatusBar {
                    background-color: #f5f5f5;
                    color: #000000;
                }
                QToolBar {
                    background-color: #f5f5f5;
                    border: none;
                }
                QToolButton {
                    background-color: transparent;
                    border: none;
                    padding: 5px;
                }
                QToolButton:hover {
                    background-color: #e0e0e0;
                    border-radius: 3px;
                }
                QComboBox {
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    padding: 5px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QComboBox::down-arrow {
                    image: none;
                    border: none;
                }
            """)
        # Add more themes as needed

    def setup_menu(self):
        """Setup the menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        save_action = QAction("Save Chat", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_chat)
        file_menu.addAction(save_action)
        
        load_action = QAction("Load Chat", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_chat)
        file_menu.addAction(load_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        clear_action = QAction("Clear Chat", self)
        clear_action.setShortcut("Ctrl+L")
        clear_action.triggered.connect(self.clear_chat)
        edit_menu.addAction(clear_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        theme_action = QAction("Change Theme", self)
        theme_action.triggered.connect(self.show_theme_dialog)
        view_menu.addAction(theme_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_toolbar(self):
        """Setup the toolbar."""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Add toolbar actions
        save_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "Save Chat", self)
        save_action.triggered.connect(self.save_chat)
        toolbar.addAction(save_action)
        
        clear_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon), "Clear Chat", self)
        clear_action.triggered.connect(self.clear_chat)
        toolbar.addAction(clear_action)
        
        toolbar.addSeparator()
        
        theme_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DesktopIcon), "Change Theme", self)
        theme_action.triggered.connect(self.show_theme_dialog)
        toolbar.addAction(theme_action)
        
        toolbar.addSeparator()
        
        help_action = QAction(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogHelpButton), "Help", self)
        help_action.triggered.connect(self.show_help)
        toolbar.addAction(help_action)

    def setup_statusbar(self):
        """Setup the status bar."""
        status = QStatusBar()
        self.setStatusBar(status)
        status.showMessage("Ready")

    def setup_tray(self):
        """Setup system tray icon."""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def show_emoji_picker(self):
        """Show emoji picker dialog."""
        # This is a placeholder for emoji picker functionality
        # You can implement a proper emoji picker here
        emojis = ["😊", "😂", "❤️", "👍", "🎉", "🔥", "✨", "🌟"]
        menu = QMenu(self)
        for emoji in emojis:
            action = QAction(emoji, self)
            action.triggered.connect(lambda checked, e=emoji: self.insert_emoji(e))
            menu.addAction(action)
        menu.exec(self.mapToGlobal(self.sender().pos()))

    def insert_emoji(self, emoji):
        """Insert emoji at cursor position."""
        self.input_field.insert(emoji)

    def show_theme_dialog(self):
        """Show theme selection dialog."""
        dialog = ThemeDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            theme = dialog.theme_combo.currentText().lower().replace(" theme", "")
            self.apply_theme(theme)

    def save_chat(self):
        """Save chat history to file."""
        from PyQt6.QtWidgets import QFileDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Chat History", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.chat_display.toPlainText())
                self.statusBar().showMessage("Chat history saved successfully", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save chat history: {str(e)}")

    def load_chat(self):
        """Load chat history from file."""
        from PyQt6.QtWidgets import QFileDialog
        file_name, _ = QFileDialog.getOpenFileName(self, "Load Chat History", "", "Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    self.chat_display.setPlainText(f.read())
                self.statusBar().showMessage("Chat history loaded successfully", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load chat history: {str(e)}")

    def auto_save_chat(self):
        """Auto-save chat history."""
        try:
            with open("chat_history.txt", 'w', encoding='utf-8') as f:
                f.write(self.chat_display.toPlainText())
        except Exception as e:
            logger.error(f"Error auto-saving chat history: {str(e)}")

    def closeEvent(self, event):
        """Handle window close event."""
        reply = QMessageBox.question(self, "Confirm Exit",
                                   "Do you want to save the chat history before exiting?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.save_chat()
            event.accept()
        elif reply == QMessageBox.StandardButton.No:
            event.accept()
        else:
            event.ignore()

    def send_message(self):
        """Send the user's message and get a response."""
        message = self.input_field.text().strip()
        if not message:
            return

        # Clear input field
        self.input_field.clear()

        # Add user message to chat
        self.add_message("You", message)

        # Create and start chat thread
        self.chat_thread = ChatThread(self.processor, message)
        self.chat_thread.response_ready.connect(self.handle_response)
        self.chat_thread.start()

        # Update status
        self.statusBar().showMessage("Processing...")

    def handle_response(self, response):
        """Handle the response from the chat thread."""
        self.add_message("A.R.E.N", response)
        self.statusBar().showMessage("Ready")

    def add_message(self, sender: str, message: str):
        """Add a message to the chat display."""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Add timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M")
        
        # Style based on sender
        if sender == "You":
            style = "color: #64B5F6;"
        else:
            style = "color: #81C784;"
        
        # Add message with styling
        cursor.insertHtml(f'''
            <div style="margin: 10px 0;">
                <span style="{style} font-weight: bold;">{sender}</span>
                <span style="color: #888; font-size: 0.8em; margin-left: 10px;">{timestamp}</span>
                <div style="margin: 5px 0 5px 20px; color: #E0E0E0;">{message}</div>
            </div>
        ''')
        
        # Scroll to bottom
        self.chat_display.setTextCursor(cursor)
        self.chat_display.ensureCursorVisible()

    def clear_chat(self):
        """Clear the chat display."""
        reply = QMessageBox.question(self, "Confirm Clear",
                                   "Are you sure you want to clear the chat history?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.chat_display.clear()
            self.add_message("A.R.E.N", "Chat history cleared.")

    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About A.R.E.N",
            "A.R.E.N - Advanced Response Engine\n\n"
            "Version 1.0\n"
            "A sophisticated AI assistant with advanced natural language processing capabilities.\n\n"
            "Features:\n"
            "• Natural Language Processing\n"
            "• Multiple Themes\n"
            "• Chat History Management\n"
            "• System Tray Integration\n"
            "• Auto-save Functionality")

    def show_help(self):
        """Show help dialog."""
        help_text = """
        <h3>How to use A.R.E.N</h3>
        <p>You can interact with A.R.E.N in several ways:</p>
        <ul>
            <li>Type your message in the input field and press Enter or click Send</li>
            <li>Use natural language to ask questions or give commands</li>
            <li>Clear the chat history using the toolbar or Edit menu</li>
            <li>Save and load chat history</li>
            <li>Change themes to suit your preference</li>
            <li>Use emojis in your messages</li>
        </ul>
        <p>Available commands:</p>
        <ul>
            <li>Ask for time or date</li>
            <li>Search the web</li>
            <li>Get information about topics</li>
            <li>Set reminders</li>
            <li>Open applications</li>
            <li>Interact with personality features:
                <ul>
                    <li>Ask about A.R.E.N's identity</li>
                    <li>Request jokes or motivation</li>
                    <li>Get weather reactions</li>
                    <li>Have casual conversations</li>
                </ul>
            </li>
        </ul>
        <p>Keyboard Shortcuts:</p>
        <ul>
            <li>Ctrl+S: Save chat</li>
            <li>Ctrl+O: Load chat</li>
            <li>Ctrl+L: Clear chat</li>
            <li>Ctrl+Q: Exit</li>
        </ul>
        """
        QMessageBox.information(self, "Help", help_text)

def run_gui(processor):
    """Run the GUI application."""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow(processor)
    window.show()
    
    sys.exit(app.exec()) 