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
    abilities: Optional[List[Ability]]
    stats: Optional[List[Stat]]
    types: Optional[List[Type]]

class PokemonCreate(BaseModel):
    name: str
    height: int = Field(gt=0)
    weight: int = Field(gt=0)
    xp: int = Field(gt=0)
    image_url: HttpUrl
    pokemon_url: HttpUrl
    abilities: Optional[List[Ability]]
    stats: Optional[List[Stat]]
    types: Optional[List[Type]]

class PokemonUpdate(BaseModel):
    name: Optional[str] = None
    height: Optional[int] = None
    weight: Optional[int] = None
    xp: Optional[int] = None
    image_url: Optional[str] = None
    pokemon_url: Optional[str] = None

    class Config:
        orm_mode = True


    def get_serialized_data(self):
        data = self.dict(exclude_unset=True)
        if 'image_url' in data and isinstance(data['image_url'], HttpUrl):
            data['image_url'] = str(data['image_url'])
        if 'pokemon_url' in data and isinstance(data['pokemon_url'], HttpUrl):
            data['pokemon_url'] = str(data['pokemon_url'])
        return data
