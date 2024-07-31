from typing import Protocol

class Techical_Protocol(Protocol):
    def clean_table(self) -> bool: ...

class CRUD_Protocol(Techical_Protocol, Protocol):

    def get_item(self) -> str: ...

    def del_item(self) -> str: ...