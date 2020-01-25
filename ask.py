#!/usr/bin/env python3

import random
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

shuffleAnswers = True
chapters = ["1", "2", "3", "4", "5", "6"]

os.chdir(os.path.dirname(os.path.realpath(sys.argv[0])))

#
# Loading questions
#

questions = []

class Answer:
    text = ""
    checked = False
    def __init__(self, text, checked):
        self.text = text
        self.checked = checked

class Question:
    text = ""
    answers = []

for chapter in chapters:
    with open(chapter) as fp:
        first = True
        question = Question()

        line = fp.readline()
        while line:
            line = line.strip()

            # new question
            if line.startswith("--"):
                if not first:
                    questions.append(question)
                    question = Question()
                    question.answers = []
                first = False
            # option
            elif line.startswith(("[ ]","[x]")):
                question.answers.append(Answer(line[3:].strip(), line.startswith("[x]")))
            # title
            else:
                question.text += '\n' + line

            line = fp.readline()

        questions.append(question)

print(f"{len(questions)} Questions")

random.shuffle(questions)

#
# GUI
#
def wordWrap(text):
    result = ""

    for line in text.split('\n'):
        lineLength = 0
        for word in line.split(' '):
            result += word + " "
            if lineLength > 70:
                result += "\n"
                lineLength = 0
            lineLength += len(word) + 1
        line += '\n'

    return result

class Window(QWidget):
    currentQuestion = 0

    def __init__(self):
        QWidget.__init__(self)
        self.setStyleSheet("font-size: 18px")
        self.outer = QVBoxLayout()

        # title
        self.titleLabel = QLabel()
        self.titleLabel.setAlignment(Qt.AlignRight)
        self.outer.addWidget(self.titleLabel)

        # question
        self.questionLabel = QLabel()
        self.questionLabel.setTextFormat(Qt.TextFormat.PlainText)
        self.outer.addWidget(self.questionLabel)

        # checkboxes
        self.checkboxes = QVBoxLayout()
        self.outer.addLayout(self.checkboxes)

        self.outer.addStretch(1)

        # buttons
        buttons = QHBoxLayout()
        self.outer.addLayout(buttons)
        self.nextButton = QPushButton("Next")
        self.nextButton.clicked.connect(self.nextQuestion)
        self.validateButton = QPushButton("Validate")
        self.validateButton.clicked.connect(self.validateAnswers);
        buttons.addWidget(self.validateButton)
        buttons.addWidget(self.nextButton)

        # misc
        self.setLayout(self.outer)

        self.nextQuestion(None)

    def nextQuestion(self, _2):
        index = self.currentQuestion % len(questions)
        q = questions[index]
        self.questionLabel.setText(wordWrap(q.text))
        self.titleLabel.setText(f"[{index+1}/{len(questions)}]")

        # clear checkboxes
        while self.checkboxes.count() > 0:
            self.checkboxes.takeAt(0).widget().deleteLater()

        # add new checkboxes
        self.correctAnswers = []
        answers = q.answers.copy()
        if shuffleAnswers:
            random.shuffle(answers)

        for answer in answers:
            checkbox = QCheckBox(wordWrap(answer.text))
            self.checkboxes.addWidget(checkbox)
            self.correctAnswers.append(answer.checked)

        self.currentQuestion += 1
        self.nextButton.setEnabled(False)

    def validateAnswers(self, _2):
        i = 0
        all_good = True

        for checked in self.correctAnswers:
            checkbox = self.checkboxes.itemAt(i).widget()
            if checked != checkbox.isChecked():
                checkbox.setStyleSheet("color: #f00")
                all_good = False
            else:
                checkbox.setStyleSheet("")

            i += 1

        if all_good:
            for i in range(0, self.checkboxes.count()):
                self.checkboxes.itemAt(i).widget().setStyleSheet("color: #070")

        self.nextButton.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = Window()
    window.resize(500, 500)
    window.show()
    sys.exit(app.exec_())
