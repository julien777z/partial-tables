from typing import get_origin, get_args, get_type_hints, Annotated
from sqlmodel import SQLModel
from .markers import PartialAllowed, PartialTable


class PartialBase(SQLModel):
    """
    Inheriting from this table will make all fields nullable
    if the field has the PartialAllowed() annotation AND the
    current table sub-classes with PartialTable.
    """

    def __init_subclass__(cls, **kwargs):
        """Set fields to nullable if the table is partial."""

        super().__init_subclass__(**kwargs)

        is_partial_table = issubclass(cls, PartialTable)
        type_hints = get_type_hints(cls, include_extras=True)

        for name, annotation in type_hints.items():
            if get_origin(annotation) is Annotated:
                if any(isinstance(a, PartialAllowed) for a in get_args(annotation)):
                    field = cls.__fields__.get(name)

                    if field is None:
                        continue

                    field.nullable = is_partial_table
