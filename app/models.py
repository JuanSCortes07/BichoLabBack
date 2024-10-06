from pydantic import BaseModel, field_validator
from typing import List, Optional

class Taxonomy(BaseModel):
    order: str
    family: str
    specie: str
    genus: str

class Characteristics(BaseModel):
    habitad: str
    diet: str
    life_cycle: str
    IUCN_status: str

class Insect(BaseModel):
    common_name: str
    taxonomy: Taxonomy
    characteristics: Characteristics
    description: str
    image: str

class Location(BaseModel):
    latitude: float
    longitude: float

class UserInsect(BaseModel):
    insect_id: str
    image: str
    location: Location

class User(BaseModel):
    email: str
    name: str
    insects: List[str] = []

class Comment(BaseModel):
    author_id: str
    commment: str

class Post(BaseModel):
    title: str
    content: str
    author_id: str  # Referencia al usuario
    user_insect_id: str
    comments: List[Comment] = []  # Lista de comentarios





