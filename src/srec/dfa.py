from typing import Self

class DFATransition:
    def __init__(self, head, weights: set[str]) -> None:
        self.head = head
        self.weights: set[str] = weights.copy()

    def __str__(self):
        return f"DFATransition(head={'<self>' if self.head == self else self.head}, weights={self.weights})"

    def __repr__(self):
        return self.__str__()

class DFAState:
    def __init__(self, accept=False) -> None:
        self.transitions: list[DFATransition] = []
        self.__accept = accept

    def connect(self, other: Self, weights: set[str]):
        self.transitions.append(DFATransition(other, weights))

    def set_accept_state(self, accept: bool=True):
        self.__accept = accept

    def is_accept_state(self):
        return self.__accept

class DFA:
    def __init__(self, start_state: DFAState) -> None:
        self.start_state = start_state
        self.__match_last_index = 0

    def match(self, text: str) -> bool:
        current_state = self.start_state
        char_index = 0

        while not current_state.is_accept_state():
            if char_index >= len(text):
                return False

            char_pointer = text[char_index]
            for trans in current_state.transitions:
                if char_pointer in trans.weights:
                    current_state = trans.head
                    char_index += 1
                    break
            else:
                return False

        self.__match_last_index = char_index
        return True

    def fullmatch(self, text: str) -> bool:
        return self.match(text) and self.__match_last_index == len(text)
