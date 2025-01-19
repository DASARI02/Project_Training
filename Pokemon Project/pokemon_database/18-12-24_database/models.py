from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional

class Ability(BaseModel):
    name: str
    is_hidden: bool

class Stat(BaseModel):
    name: str
    base_stat: int = Field(gt=0)

class Type(BaseModel):
    name: str

class Pokemon(BaseModel):
    id: int = Field(gt=0)  
    name: str
    height: int = Field(ge=0)
    weight: int = Field(ge=0)
    xp: int
    image_url: HttpUrl  
    pokemon_url: HttpUrl  
    abilities: List[Ability]  
    stats: List[Stat]         
    types: List[Type] 

class PokemonUpdate(BaseModel):
    name: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    xp: Optional[int] = None
    image_url: Optional[HttpUrl] = None
    pokemon_url: Optional[HttpUrl] = None
    abilities: Optional[List[Ability]] = None
    stats: Optional[List[Stat]] = None
    types: Optional[List[Type]] = None