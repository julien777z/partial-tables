class PartialAllowed:
    """Marker for fields that can be nullable"""


class PartialTable:
    """
    Marker for tables that are Partial.

    Any field that has the PartialAllowed() annotation will be nullable.
    """
