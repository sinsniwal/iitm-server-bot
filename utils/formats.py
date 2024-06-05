class plural:
    def __init__(self, value: int) -> None:
        self.value = value

    def __format__(self, __format_spec: str) -> str:
        singular, _, plural = __format_spec.partition("|")
        if not plural:
            plural = singular + "s"
        return f"{self.value} {singular if self.value == 1 else plural}"
