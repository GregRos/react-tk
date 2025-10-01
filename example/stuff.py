class A:
    class B:
        @classmethod
        def __get__(cls, *args, **kwargs) -> "A.B":
            return cls


a = A().B
print
