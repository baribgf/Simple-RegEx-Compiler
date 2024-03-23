from enum import Enum

class TokenType(Enum):
    CHAR                    = 0
    ALL_CHAR                = 1
    ZERO_OR_MORE_INDICATOR  = 2
    ONE_OR_MORE_INDICATOR   = 3
    ZERO_OR_ONE_INDICATOR   = 4
    OPEN_LIST               = 5
    CLOSE_LIST              = 6
    EOI                     = 7

class Token:
    def __init__(self, token_type: TokenType, text: str) -> None:
        self.type = token_type
        self.text = text

    def __str__(self) -> str:
        return f"{self.type}"
    
    def __repr__(self) -> str:
        return str(self)

def tokenize(text: str) -> list[Token]:
    """
    Tokenize a string and return a list of tokens.

    :param text: The string that will be lexicaly analyzed.
    :return: A list of Token objects representing the tokens.
    """
    tokens = []
    for char in text:
        curr_token = None
        if char.isalnum() or char == '_':
            curr_token = Token(TokenType.CHAR, char)
        elif char == '.':
            curr_token = Token(TokenType.ALL_CHAR, char)
        elif char == '*':
            curr_token = Token(TokenType.ZERO_OR_MORE_INDICATOR, char)
        elif char == '+':
            curr_token = Token(TokenType.ONE_OR_MORE_INDICATOR, char)
        elif char == '?':
            curr_token = Token(TokenType.ZERO_OR_ONE_INDICATOR, char)
        elif char == '[':
            curr_token = Token(TokenType.OPEN_LIST, char)
        elif char == ']':
            curr_token = Token(TokenType.CLOSE_LIST, char)
        else:
            raise ValueError(f"Got undefined token: '{char}'")
        
        tokens.append(curr_token)

    return tokens
