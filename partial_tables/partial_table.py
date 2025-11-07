from typing import Annotated, Optional, get_args, get_origin, get_type_hints
from sqlalchemy.orm import mapped_column


class PartialAllowed:
    """Marker for fields that can be nullable"""


class PartialTable:
    """
    Marker for tables that are Partial.

    Any field that has the PartialAllowed() annotation will be nullable.
    """


def _rewrite_with_optional(a: object) -> object:
    origin = get_origin(a)

    if origin is Annotated:
        base, *meta = get_args(a)

        if any(isinstance(m, PartialAllowed) for m in meta):
            return Annotated[Optional[base], *meta]

        new_base = _rewrite_with_optional(base)

        if new_base is not base:
            return Annotated[new_base, *meta]

        return a

    args = get_args(a)

    if not args:
        return a

    new_args = tuple(_rewrite_with_optional(x) for x in args)

    if new_args != args and origin is not None and hasattr(origin, "__class_getitem__"):
        # Avoid passing a single-element tuple which would produce origin[(T,)].
        param = new_args[0] if len(new_args) == 1 else new_args

        return origin[param]  # type: ignore[index]

    return a


class PartialSQLAlchemyMixin:
    """
    Base class for all partial tables.

    Any class that sub-classes this base class will have all fields that have the PartialAllowed() annotation set to nullable.
    """

    def __init_subclass__(cls, **kwargs):
        if not issubclass(cls, PartialTable):
            super().__init_subclass__(**kwargs)
            return

        type_hints = get_type_hints(cls, include_extras=True)
        raw_annotations = dict(getattr(cls, "__annotations__", {}))

        for name, ann in type_hints.items():
            new_ann = _rewrite_with_optional(ann)

            if new_ann is not ann:
                raw_annotations[name] = new_ann
                # Override the inherited mapped_column assignment on this subclass
                setattr(cls, name, mapped_column(nullable=True))

        if raw_annotations:
            cls.__annotations__ = raw_annotations

        super().__init_subclass__(**kwargs)


class PartialSQLModelMixin:
    """
    Base class for SQLModel partial tables.
    Converts fields marked with PartialAllowed() to Optional[...] so SQLModel
    derives NULL columns without mutating FieldInfo or columns directly.
    """

    def __init_subclass__(cls, **kwargs):
        if not issubclass(cls, PartialTable):
            super().__init_subclass__(**kwargs)
            return

        type_hints = get_type_hints(cls, include_extras=True)
        raw_annotations = dict(getattr(cls, "__annotations__", {}))

        for name, ann in type_hints.items():
            new_ann = _rewrite_with_optional(ann)

            if new_ann is not ann:
                raw_annotations[name] = new_ann

        if raw_annotations:
            cls.__annotations__ = raw_annotations

        super().__init_subclass__(**kwargs)
