import typing as t


class Meta(type):
    """Provides some meta-helper utilites for custom types"""

    _validators: dict[str, t.Any] = {}

    @property
    def validators(cls):
        """Validators are any class-level value that has
        a type of t.ClassVar and is not private. These values should
        be validated at type instantiation for verification of validity"""
        if not cls._validators:
            cls._validators = {
                name: getattr(cls, name, None)
                for name, annotation in cls.__annotations__.items()
                if not name.startswith("__") and t.get_origin(annotation) is t.ClassVar
            }
        return cls._validators

    def __repr__(cls):
        args = ", ".join(f"{key}={val!r}" for key, val in cls.validators.items())
        return f"{cls.__name__}({args})"
