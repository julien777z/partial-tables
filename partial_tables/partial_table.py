from typing import get_origin, get_args, get_type_hints, Annotated
from sqlmodel import SQLModel, Field
from .markers import PartialAllowed, PartialTable


class PartialBase(SQLModel):
    """
    Inheriting from this table will make all fields nullable
    if the field has the PartialAllowed() annotation AND the
    current table sub-classes with PartialTable.
    """

    def __init_subclass__(cls, **kwargs):
        """Set fields to nullable if the table is partial."""

        is_partial_table = issubclass(cls, PartialTable)

        if is_partial_table:
            names_to_update: set[str] = set()

            # Collect Annotated fields with PartialAllowed across the MRO
            for base in cls.__mro__:
                if base is object:
                    continue

                try:
                    base_hints = get_type_hints(base, include_extras=True)
                except Exception:
                    continue

                for name, annotation in base_hints.items():
                    if get_origin(annotation) is Annotated and any(
                        isinstance(a, PartialAllowed) for a in get_args(annotation)
                    ):
                        names_to_update.add(name)

            # Override on the subclass before SQLModel processes the model
            for name in names_to_update:
                setattr(cls, name, Field(default=None, nullable=True))

        super().__init_subclass__(**kwargs)
