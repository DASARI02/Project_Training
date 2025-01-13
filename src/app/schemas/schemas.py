from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional
from typing_extensions import Literal

class Ability(BaseModel):
    name: str
    is_hidden: bool

class Stat(BaseModel):
    name: str
    base_stat: int = Field(gt=0)

class Type(BaseModel):
    name: str

class Pokemon(BaseModel):
    id: Optional[int] = None
    name: str
    height: int = Field(gt=0)
    weight: int = Field(gt=0)
    xp: int = Field(gt=0)
    image_url: HttpUrl
    pokemon_url: HttpUrl
    abilities: List[Ability]
    stats: List[Stat]
    types: List[Type]

class PokemonCreate(BaseModel):
    name: str
    height: float
    weight: float
    xp: int
    image_url: HttpUrl  # Use HttpUrl instead of Url
    pokemon_url: HttpUrl
    abilities: list
    stats: list
    types: list

class PokemonUpdate(BaseModel):
    name: str
    height: int = Field(gt=0)
    weight: int = Field(gt=0)
    xp: int = Field(gt=0)
    image_url: str
    pokemon_url: str
    abilities: List[Ability]
    stats: List[Stat]
    types: List[Type]

    class Config:
        orm_mode = True

    # Custom method to serialize URLs to strings when updating
    def get_serialized_data(self):
        data = self.dict(exclude_unset=True)
        if 'image_url' in data and isinstance(data['image_url'], HttpUrl):
            data['image_url'] = str(data['image_url'])
        if 'pokemon_url' in data and isinstance(data['pokemon_url'], HttpUrl):
            data['pokemon_url'] = str(data['pokemon_url'])
        return data
