from typing import Annotated
from repo import Repo
from uc import UC


def deps():
    repo = Repo
    return UC(repo)


AapiUC = Annotated[UC, deps()]
