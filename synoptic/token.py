"""Management for Synoptic API Token."""


class Token:
    """Synoptic API Token."""

    def __init__(self, token):
        self.token = token

    def __str__(self) -> str:
        return self.token

    def test(self):
        print(self.token)
