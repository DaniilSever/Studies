from irep import CRUD_Protocol

class UC:
    def __init__(self, repo: CRUD_Protocol):
        self._repo = repo

    def get_item(self) -> None:
        print(self._repo.get_item())

    def del_item(self) -> None:
        print(self._repo.del_item())

    def clean_table(self) -> None:
        print(self._repo.clean_table())
