import re
from PyQt6.Qsci import QsciLexerCustom
from PyQt6.QtGui import QColor, QFont
from utils.properties import *

class LexerCPP(QsciLexerCustom):
    styles = {
        "Default": 0,
        "Comment": 1,
        "DoubleSlashComment": 2,
        "Keyword": 3,
        "String": 4,
        "Number": 5,
        "Preprocessor": 6,
        "Operator": 7,
        "Identifier": 8,
        "Type": 9,
        "Symbol": 10,
        "Parantheses": 11,
    }
    
    keyword_list = [
        "auto", "break", "case", "catch", "class", "const",
        "continue", "default", "delete", "do", "else", "enum",
        "explicit", "export", "extern", "for", "friend", "goto",
        "if", "inline", "namespace", "new", "operator", "private",
        "protected", "public", "return", "sizeof", "static",
        "struct", "switch", "template", "this", "throw", "try",
        "typedef", "typename", "union", "using", "virtual",
        "volatile", "while", "constexpr"
    ]
    
    type_list = [
        "bool", "char", "double", "float", "int", "long",
        "short", "signed", "unsigned", "void", "wchar_t",
        "string", "vector", "map", "set", "list", "queue",
        "stack", "pair", "size_t"
    ]

    number_list = [
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"
    ]

    parantheses_list = [
        "(", ")", "[", "]", "{", "}"
    ]

    symbol_list = [
        ">", "<", "=", "+", "-", "*", "/", "%",
        "!", "~", "&", "|", "^", "?", ":",
        ".", ",","->", "!", "~", "+", "&",
    ]
    
    # Default colors in case properties are not available
    default_colors = {
        "Default": "#FFFFFF",
        "Comment": "#37743f",
        "DoubleSlashComment": "#37743f",
        "Keyword": "#50B0FF",
        "String": "#FFFF7F",
        "Number": "#EDFFAF",
        "Preprocessor": "#C586C0",
        "Operator": "#FFFF7F",
        "Identifier": "#FFFFFF",
        "Type": "#50B0FF",
        "Symbol": "#CC0099",
        "Parantheses": "#50B0FF"
    }
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setDefaultColor(EDITOR_TEXT_COLOR)
        self.setDefaultPaper(EDITOR_BACKGROUND_COLOR)
        self.setDefaultFont(EDITOR_FONT)
        
        self.init_colors()
        
        for i in range(len(self.styles)):
            self.setFont(EDITOR_FONT, i)

    def init_colors(self):
        # Helper function to get color safely
        def get_color(style_name):
            color_key = f"SYNTAX_{style_name.upper()}"
            if color_key in globals():
                return globals()[color_key]
            return QColor(self.default_colors[style_name])

        # Set colors for each style with fallback to defaults
        for style_name, style_id in self.styles.items():
            color = get_color(style_name)
            self.setColor(color, style_id)
            self.setPaper(EDITOR_BACKGROUND_COLOR, style_id)
            
        # Explicitly set comment colors to ensure they're applied
        self.setColor(SYNTAX_COMMENT, self.styles["Comment"])
        self.setColor(SYNTAX_DOUBLE_SLASH_COMMENT, self.styles["DoubleSlashComment"])

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
        
        lines = text.split('\n')
        pos = 0
        
        for line in lines:
            stripped_line = line.lstrip()
            if stripped_line.startswith('#'):
                leading_spaces = len(line) - len(stripped_line)
                if leading_spaces > 0:
                    self.setStyling(leading_spaces, self.styles["Default"])
                    pos += leading_spaces
                self.setStyling(len(line) - leading_spaces, self.styles["Preprocessor"])
                pos += len(line) - leading_spaces
            elif stripped_line.startswith('//'):
                leading_spaces = len(line) - len(stripped_line)
                if leading_spaces > 0:
                    self.setStyling(leading_spaces, self.styles["Default"])
                    pos += leading_spaces
                self.setStyling(len(line) - leading_spaces, self.styles["DoubleSlashComment"])
                pos += len(line) - leading_spaces
            else:
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
                    elif token in self.parantheses_list:
                        self.setStyling(token_len, self.styles["Parantheses"])
                    else:
                        self.setStyling(token_len, self.styles["Default"])
                    pos += token_len
            
            if pos < len(text):
                self.setStyling(1, self.styles["Default"])
                pos += 1