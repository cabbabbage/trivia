import sys
import random
import requests
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QGridLayout, QLabel, QPushButton, QApplication, QSizeGrip, QDialog, QVBoxLayout, QLineEdit, QSpinBox, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer, QPoint, pyqtSignal, QEvent


# ✅ Create a custom QLabel that emits a signal when Alt + Click is detected
class ClickableLabel(QLabel):
    alt_click = pyqtSignal(str)  # Signal to emit the text of the label when Alt + Click is detected

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and QApplication.keyboardModifiers() == Qt.AltModifier:
            self.alt_click.emit(self.text())  # Emit the signal with the label text


# Import your Character class
from character import Character


class OverlayWindow(QMainWindow):
    def __init__(self, character, rate):
        super().__init__()
        self.character = character
        self.character.gpt_respond_introduction()
        self.rate = rate

        # Window properties
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(300, 200)

        # Central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)

        # Close button
        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet(
            "background-color: red; color: white; font-weight: bold; border: none;"
        )
        self.close_button.clicked.connect(QApplication.quit)
        self.layout.addWidget(self.close_button, 0, 2, 1, 1, alignment=Qt.AlignRight | Qt.AlignTop)

        # Question label
        self.question_label = QLabel("")
        self.question_label.setStyleSheet(
            "background-color: yellow; "
            "font-size: 15px; "
            "font-weight: bold; "
            "padding: 10px;"
        )
        self.question_label.setAlignment(Qt.AlignCenter)
        self.question_label.setWordWrap(True)
        self.layout.addWidget(self.question_label, 0, 0, 1, 2)

        # Answer labels
        self.answer_labels = []
        for i in range(2):
            for j in range(2):
                answer_label = ClickableLabel("")
                answer_label.setStyleSheet(
                    "background-color: lightblue; "
                    "font-size: 20px; "
                    "padding: 10px;"
                )
                answer_label.setAlignment(Qt.AlignCenter)
                answer_label.alt_click.connect(self.save_answer_to_file)  # Connect Alt + Click signal
                self.layout.addWidget(answer_label, i + 1, j)
                self.answer_labels.append(answer_label)

        # Resize grip
        self.resize_grip = QSizeGrip(self)
        self.layout.addWidget(self.resize_grip, 3, 1, 1, 1, alignment=Qt.AlignBottom | Qt.AlignRight)

        # Show the window
        self.show()

        # Start by asking the first question
        self.ask_question()

    def clear_labels(self):
        """Clear all the labels."""
        self.question_label.setText("")
        for label in self.answer_labels:
            label.setText("")

    def ask_question(self):
        """Fetch a new question from the Character class and display it."""
        self.clear_labels()

        self.character.fetch_trivia_question()
        self.question, answers = self.character.get_question_and_answers()

        self.question_label.setText(self.question)
        for i in range(len(self.answer_labels)):
            if i < len(answers):
                self.answer_labels[i].setText(answers[i])
            else:
                self.answer_labels[i].setText("")

        QTimer.singleShot(750, self.start_listening)

    def start_listening(self):
        """Start listening for the player's response."""
        self.character.ask_question()
        self.clear_labels()
        self.schedule_next_question()

    def schedule_next_question(self):
        """Schedule the next question."""
        random_variability = random.randint(-10, 10)
        adjusted_rate = max(1, (self.rate + random_variability))
        QTimer.singleShot(adjusted_rate * 1000, self.ask_question)

    def save_answer_to_file(self, answer):
        """Save the clicked answer to 'answer.txt', replacing any existing content."""
        with open("answer.txt", "w") as file:
            file.write(answer)
        print(f"Answer saved: {answer}")

    # Drag the window
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mouse_click_offset = event.pos()

    def mouseMoveEvent(self, event):
        if self._mouse_click_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(self.pos() + event.pos() - self._mouse_click_offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mouse_click_offset = None


class SetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Setup Window")
        self.setModal(True)

        layout = QVBoxLayout()

        # Prompt label + input
        self.prompt_label = QLabel("Enter Prompt:")
        self.prompt_input = QLineEdit()
        layout.addWidget(self.prompt_label)
        layout.addWidget(self.prompt_input)

        # Rate label + spinbox
        self.rate_label = QLabel("Enter Rate (seconds):")
        self.rate_spin = QSpinBox()
        self.rate_spin.setRange(1, 3600)
        self.rate_spin.setValue(15)  # Default
        layout.addWidget(self.rate_label)
        layout.addWidget(self.rate_spin)

        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def get_values(self):
        return self.prompt_input.text().strip(), self.rate_spin.value()


def main(prompt_input, rate_input):
    app = QApplication(sys.argv)
    character = Character(prompt=prompt_input)
    rate = rate_input
    window = OverlayWindow(character, rate)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = SetupDialog()
    if dialog.exec_() == QDialog.Accepted:
        user_prompt, user_rate = dialog.get_values()
        main(user_prompt, user_rate)
    else:
        sys.exit(0)

