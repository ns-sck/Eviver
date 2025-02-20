import re
from PyQt6.Qsci import QsciLexerCustom
from PyQt6.QtGui import QColor, QFont

class LexerCPP(QsciLexerCustom):
    styles = {
        "Default": 0,
        "Comment": 1,
        "Keyword": 2,
        "String": 3,
        "Number": 4,
        "Preprocessor": 5,
        "Operator": 6,
        "Identifier": 7,
        "Type": 8,
    }
    
    keyword_list = [
        "auto", "break", "case", "catch", "class", "const",
        "continue", "default", "delete", "do", "else", "enum",
        "explicit", "export", "extern", "for", "friend", "goto",
        "if", "inline", "namespace", "new", "operator", "private",
        "protected", "public", "return", "sizeof", "static",
        "struct", "switch", "template", "this", "throw", "try",
        "typedef", "typename", "union", "using", "virtual",
        "volatile", "while"
    ]
    
    type_list = [
        "bool", "char", "double", "float", "int", "long",
        "short", "signed", "unsigned", "void", "wchar_t",
        "string", "vector", "map", "set", "list", "queue",
        "stack", "pair", "size_t"
    ]

    def __init__(self, parent):
        super().__init__(parent)

        self.setDefaultColor(QColor("#FFFFFF"))
        self.setDefaultPaper(QColor("#111111"))
        self.setDefaultFont(QFont("Monospace", 20))
        
        self.init_colors()
        
        for i in range(len(self.styles)):
            if i == self.styles["Keyword"] or i == self.styles["Type"]:
                self.setFont(QFont("Monospace", 20), i)
            else:
                self.setFont(QFont("Monospace", 20), i)

    def init_colors(self):
        self.setColor(QColor("#B7F1FF"), self.styles["Default"])
        self.setColor(QColor(0xFF, 0xFF, 0x7f), self.styles["Comment"])
        self.setColor(QColor("#FFFFFF"), self.styles["Keyword"])
        self.setColor(QColor(0xFF, 0xFF, 0x7f), self.styles["String"])
        self.setColor(QColor(0xFF, 0xFF, 0x7f), self.styles["Number"])
        self.setColor(QColor(0xFF, 0xFF, 0x7f), self.styles["Preprocessor"])
        self.setColor(QColor(0xFF, 0xFF, 0x7f), self.styles["Operator"])
        self.setColor(QColor(0xFF, 0xFF, 0x7f), self.styles["Identifier"])
        self.setColor(QColor(0xFF, 0xFF, 0xFF), self.styles["Type"])
        
        for i in range(len(self.styles)):
            self.setPaper(QColor("#111111"), i)

    def language(self):
        return "C++"

    def description(self, style):
        if style < len(self.styles):
            description = "Custom lexer for C++"
        else:
            description = ""
        return description

    def styleText(self, start, end):
        self.startStyling(start)

        text = self.parent().text()[start:end]

        splitter = re.compile(
            r"(\{\.|\.\}|\#|\'|\"\"\"|\n|\s+|\w+|\W)"
        )

        tokens = [
            (token, len(bytearray(token, "utf-8")))
            for token in splitter.findall(text)
        ]

        for i, token in enumerate(tokens):
            if token[0] in self.keyword_list:
                self.setStyling(
                    token[1],
                    self.styles["Keyword"]
                )
            elif token[0] in self.type_list:
                self.setStyling(
                    token[1],
                    self.styles["Type"]
                )
            else:
                self.setStyling(
                    token[1],
                    self.styles["Default"]
                )