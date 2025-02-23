import re
from PyQt6.Qsci import QsciLexerCustom
from PyQt6.QtGui import QColor, QFont
from utils.properties import *

class LexerCPP(QsciLexerCustom):
    styles = {
        "Default": 0,
        "Comment": 1,
        "DoubleSlashComment": 2,  # New style for // comments
        "Keyword": 3,
        "String": 4,
        "Number": 5,
        "Preprocessor": 6,
        "Operator": 7,
        "Identifier": 8,
        "Type": 9,
        "Symbol": 10,
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

    number_list = [
        # "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
    ]

    symbol_list = [
        ">", "<", "=", "+", "-", "*", "/", "%",
        "!", "~", "&", "|", "^", "?", ":", ";",
        ".", ",", "(", ")", "[", "]", "{", "}",
        "->", "::", "++", "--", "!", "~", "*", "&",
        "(", ")", "[", "]", ".", "->", "::", "++", "--",
        "!", "~", "*", "&"
    ]

    def __init__(self, parent):
        super().__init__(parent)

        self.setDefaultColor(QColor("#FFFFFF"))
        self.setDefaultPaper(QColor("#111111"))
        self.setDefaultFont(QFont("Monospace", 16))
        
        self.init_colors()
        
        for i in range(len(self.styles)):
            if i == self.styles["Keyword"] or i == self.styles["Type"]:
                self.setFont(QFont("Monospace", 16), i)
            else:
                self.setFont(QFont("Monospace", 16), i)

    def init_colors(self):
        self.setColor(SYNTAX_DEFAULT, self.styles["Default"])
        self.setColor(SYNTAX_COMMENT, self.styles["Comment"])
        self.setColor(SYNTAX_DOUBLE_SLASH_COMMENT, self.styles["DoubleSlashComment"])
        self.setColor(SYNTAX_KEYWORD, self.styles["Keyword"])
        self.setColor(SYNTAX_STRING, self.styles["String"])
        self.setColor(SYNTAX_NUMBER, self.styles["Number"])
        self.setColor(SYNTAX_PREPROCESSOR, self.styles["Preprocessor"])
        self.setColor(SYNTAX_OPERATOR, self.styles["Operator"])
        self.setColor(SYNTAX_IDENTIFIER, self.styles["Identifier"])
        self.setColor(SYNTAX_TYPE, self.styles["Type"])
        self.setColor(SYNTAX_SYMBOL, self.styles["Symbol"])
        for i in range(len(self.styles)):
            self.setPaper(SYNTAX_BACKGROUND, i)

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
        
        # Split text into lines to check for // comments
        lines = text.split('\n')
        pos = 0
        
        for line in lines:
            stripped_line = line.lstrip()
            # Handle double-slash comments
            if stripped_line.startswith('//'):
                # Style the leading spaces
                leading_spaces = len(line) - len(stripped_line)
                if leading_spaces > 0:
                    self.setStyling(leading_spaces, self.styles["Default"])
                    pos += leading_spaces
                # Style the rest of the line as a double-slash comment
                self.setStyling(len(line) - leading_spaces, self.styles["DoubleSlashComment"])
                pos += len(line) - leading_spaces
            else:
                # Normal line processing
                tokens = re.findall(r'(\{\.|\.\}|\#|\'|\"\"\"|\s+|\w+|\W)', line)
                for token in tokens:
                    token_len = len(token)
                    if token in self.keyword_list:
                        self.setStyling(token_len, self.styles["Keyword"])
                    elif token in self.type_list:
                        self.setStyling(token_len, self.styles["Type"])
                    elif token in self.number_list:
                        self.setStyling(token_len, self.styles["Number"])
                    elif token in self.symbol_list:
                        self.setStyling(token_len, self.styles["Symbol"])
                    else:
                        self.setStyling(token_len, self.styles["Default"])
                    pos += token_len
            
            # Add newline character length
            if pos < len(text):
                self.setStyling(1, self.styles["Default"])
                pos += 1