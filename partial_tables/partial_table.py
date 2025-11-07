from typing import Annotated, Optional, get_args, get_origin, get_type_hints
from sqlalchemy.orm import mapped_column


class PartialAllowed:
    """Marker for fields that can be nullable"""


class PartialTable:
    """
    Marker for tables that are Partial.

    Any field that has the PartialAllowed() annotation will be nullable.
    """


class PartialBase:
    def __init_subclass__(cls, **kwargs):
        # For partial tables, rewrite annotations to Optional and inject mapped_column(nullable=True)
        if issubclass(cls, PartialTable):
            type_hints = get_type_hints(cls, include_extras=True)
            raw_annotations = dict(getattr(cls, "__annotations__", {}))

            def rewrite_with_optional(a: object) -> object:
                origin = get_origin(a)
                if origin is Annotated:
                    base, *meta = get_args(a)
                    if any(isinstance(m, PartialAllowed) for m in meta):
                        return Annotated[
                            Optional[base], mapped_column(nullable=True), *meta
                        ]
                    new_base = rewrite_with_optional(base)
                    if new_base is not base:
                        return Annotated[new_base, *meta]
                    return a
                args = get_args(a)
                if not args:
                    return a
                new_args = tuple(rewrite_with_optional(x) for x in args)
                if new_args != args and origin is not None:
                    try:
                        return origin[tuple(new_args)]  # type: ignore[index]
                    except Exception:
                        return a
                return a

            for name, ann in type_hints.items():
                new_ann = rewrite_with_optional(ann)
                if new_ann is not ann:
                    raw_annotations[name] = new_ann
                    # Override the inherited mapped_column assignment on this subclass
                    setattr(cls, name, mapped_column(nullable=True))
            if raw_annotations:
                cls.__annotations__ = raw_annotations
        super().__init_subclass__(**kwargs)
