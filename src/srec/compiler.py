from string import ascii_letters, digits
from .util import debuggable, ParseError, set_debug_enabled
from .tokenizer import Token, TokenType, tokenize
from .dfa import DFA, DFAState

set_debug_enabled(False)

class RDCompiler:
    """
    The Recursive Descent compiler class.
    """
    def __init__(self) -> None:
        self.index = 0
        self.tokens = []
        self.start_state = DFAState()
        self.current_state = self.start_state
        self.__highlighted_states: set[DFAState] = set()
        self.__zo_state_parent: DFAState | None = None
        self.__list_open = False
        self.__open_list_items = {"z"}

    def __perform_lookahead(self, k: int=1) -> TokenType:
        if self.index + k < len(self.tokens):
            return self.tokens[self.index + k].type
        
        return TokenType.EOI

    @debuggable
    def __match_terminal(self, match_token_type: TokenType) -> bool:
        if self.index >= len(self.tokens) or self.tokens[self.index].type != match_token_type:
            return False

        if match_token_type == TokenType.CHAR or match_token_type == TokenType.ALL_CHAR:
            weights = set()
            if match_token_type == TokenType.CHAR:
                weights = {self.tokens[self.index].text}
            elif match_token_type == TokenType.ALL_CHAR:
                weights = {c for c in ascii_letters + digits}

            if self.__list_open:
                self.__open_list_items |= weights
            else:
                self.__highlighted_states.clear()
                if self.__perform_lookahead() == TokenType.ZERO_OR_MORE_INDICATOR:
                    self.current_state.connect(self.current_state, weights)
                elif self.__perform_lookahead() == TokenType.ONE_OR_MORE_INDICATOR:
                    new_state = DFAState()
                    new_state.connect(new_state, weights)
                    self.current_state.connect(new_state, weights)
                    self.current_state = new_state
                else:
                    new_state = DFAState()
                    if self.__zo_state_parent is not None:
                        self.__zo_state_parent.connect(new_state, weights)
                        self.__zo_state_parent = None

                    self.current_state.connect(new_state, weights)
                    if self.__perform_lookahead() == TokenType.ZERO_OR_ONE_INDICATOR:
                        self.__zo_state_parent = self.current_state
                        self.__highlighted_states.add(self.current_state)
                    self.current_state = new_state
        elif match_token_type == TokenType.OPEN_LIST:
            self.__list_open = True
        elif match_token_type == TokenType.CLOSE_LIST:
            new_state = DFAState()
            if self.__zo_state_parent is not None:
                self.__zo_state_parent.connect(new_state, self.__open_list_items)
                self.__zo_state_parent = None

            self.current_state.connect(new_state, self.__open_list_items)
            if self.__perform_lookahead() == TokenType.ZERO_OR_ONE_INDICATOR:
                self.__zo_state_parent = self.current_state
            self.current_state = new_state
            self.__list_open = False
            self.__open_list_items.clear()

        self.index += 1
        return True

    @debuggable
    def __match_epsilon(self) -> bool:
        return True

    @debuggable
    def __r_prime_2(self) -> bool:
        return self.__match_terminal(TokenType.CHAR) and self.__r_prime_2() \
            or self.__match_epsilon()
    
    @debuggable
    def __r_prime(self) -> bool:
        return self.__match_terminal(TokenType.CHAR) and self.__r_prime_2()

    @debuggable
    def __r(self) -> bool:
        return self.__match_terminal(TokenType.CHAR) and self.__r() \
            or self.__match_terminal(TokenType.OPEN_LIST) and self.__r_prime() and self.__match_terminal(TokenType.CLOSE_LIST) and self.__r() \
            or self.__match_terminal(TokenType.ALL_CHAR) and self.__r() \
            or self.__ind() \
            or self.__match_epsilon()

    @debuggable
    def __ind(self) -> bool:
        return self.__match_terminal(TokenType.ZERO_OR_MORE_INDICATOR) \
            or self.__match_terminal(TokenType.ONE_OR_MORE_INDICATOR) \
            or self.__match_terminal(TokenType.ZERO_OR_ONE_INDICATOR)

    @debuggable
    def __p_prime(self) -> bool:
        return self.__ind() or self.__r()

    @debuggable
    def __p(self) -> bool:
        return self.__match_terminal(TokenType.CHAR) and self.__p_prime() \
            or self.__match_terminal(TokenType.OPEN_LIST) and self.__r_prime() and self.__match_terminal(TokenType.CLOSE_LIST) and self.__p_prime() \
            or self.__match_terminal(TokenType.ALL_CHAR) and self.__p_prime()

    @debuggable
    def __stmnt_prime(self) -> bool:
        return self.__stmnt() or self.__match_epsilon()

    @debuggable
    def __stmnt(self) -> bool:
        return self.__p() and self.__stmnt_prime()

    def parse(self, tokens: list[Token]):
        self.tokens = tokens
        stmnt_state = self.__stmnt()
        if not (stmnt_state and self.index == len(self.tokens)):
            raise ParseError(f"There was an error while parsing!")
        
        self.current_state.set_accept_state(True)
        for state in self.__highlighted_states:
            state.set_accept_state(True)

        return DFA(self.start_state)

    def compile(self, pattern: str) -> DFA:
        """
        Compile a regular expression pattern into a Deterministic Finite Automaton.

        :param pattern: The pattern that will be compiled.
        :return: A DFA object representing the `DFA` that can be traversed.
        """
        return self.parse(tokenize(pattern))
