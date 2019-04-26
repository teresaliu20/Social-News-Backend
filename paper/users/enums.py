from enum import Enum

class Relationship(Enum):   # A subclass of Enum
    Explains = "explains"
    Opposes = "opposes"
    Subcategory = "is subcategory of"

class CollectionPermission(Enum):
    Private = "private"
    Public = "public"
    Network = "network"
