from typing import _GenericAlias as GenericAlias  # type: ignore

from arc import errors
from .base_converter import BaseConverter


class GenericConverter(BaseConverter[GenericAlias]):
    def __init__(self, annotation: GenericAlias):
        super().__init__(annotation)
        self.args: tuple[type, ...] = annotation.__args__
        self.origin: type = annotation.__origin__

    def handle_union(self, val: str):
        ...


class UnionConverter(GenericConverter):
    def convert(self, value: str):
        breakpoint()
        for union_type in self.args:
            try:
                # if is_alias(union_type):
                #     return self.convert_alias(union_type, value)

                converter = get_converter(union_type)
                return converter(self.annotation).convert(value)
            except errors.ConversionError:
                continue

        raise errors.ConversionError(
            value,
            expected="a valid Union type",
            helper_text=f"Failed to convert {self.annotation}",
        )


class ListConverter(BaseConverter[list[str]]):
    """Converts arguement into an array
    argument: my_list=1,2,3,4,5,6
    return : ["1", "2", "3", "4", "5", "6"]
    """

    def convert(self, value: str):
        return list(value.strip(" ") for value in value.split(","))


# class AliasConverter(BaseConverter):
#     """
#     convert string inputs into their appropriate types
#     based on the type alias provided

#     Union[int, str]

#         - i: '1234'
#         - o: 1234

#         - i: 'hello'
#         - o: 'hello'

#     List[int]

#         - i: '1,2,3,4,5,6'
#         - o: [1, 2, 3, 4, 5, 6]
#     """

#     def convert(self, value):
#         return self.convert_alias(self.annotation, value)

#     def convert_alias(self, alias: Type[GenericAlias], value: str) -> Any:
#         if not is_alias(alias):
#             raise ConversionError(
#                 value, "Provided alias must inherit from GenericAlias"
#             )

#         origin = alias.__origin__
#         if origin is Union:
#             return self.convert_union(alias, value)
#         elif origin is list:
#             return self.convert_list(alias, value)
#         elif origin is set:
#             return self.convert_set(alias, value)
#         elif origin is tuple:
#             return self.convert_tuple(alias, value)
#         else:
#             raise ConversionError(
#                 value=None,
#                 expected="a valid type alias",
#                 helper_text=f"Type Alias for '{origin}' not supported",
#             )

# def convert_union(self, alias, value):
#     for union_type in alias.__args__:
#         try:
#             if is_alias(union_type):
#                 return self.convert_alias(union_type, value)

#             converter = get_converter(union_type)
#             if converter:
#                 return converter(alias).convert(value)
#         except ConversionError:
#             continue

#     raise ConversionError(
#         value, "a valid Union type", helper_text=f"Failed to convert {alias}"
#     )

#     def collection_setup(self, collection_alias, value):
#         contains_type = collection_alias.__args__[0]
#         if is_alias(contains_type):
#             raise ConversionError(
#                 contains_type,
#                 "a valid alias type",
#                 helper_text="Arc only supports shallow Collection Type Aliases",
#             )

#         value = value.replace(" ", "")

#         return value.split(","), get_converter(contains_type)

#     def convert_list(self, alias, value):
#         items, converter = self.collection_setup(alias, value)
#         return list([converter(list).convert(item) for item in items])

#     def convert_set(self, alias, value):
#         items, converter = self.collection_setup(alias, value)
#         return set(converter(set).convert(item) for item in items)

#     def convert_tuple(self, alias, value):
#         items, _ = self.collection_setup(alias, value)
#         if (i_len := len(items)) != (a_len := len(alias.__args__)):
#             raise ConversionError(
#                 value=items,
#                 expected=f"a tuple of {a_len} item(s), was {i_len} item(s)",
#             )

#         return tuple(
#             get_converter(alias.__args__[idx])(tuple).convert(item)
#             for idx, item in enumerate(items)
#         )
