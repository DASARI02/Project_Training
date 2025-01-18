from math import ceil
from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.app.models.models import Pokemon
from sqlalchemy.exc import SQLAlchemyError
from src.app.models.models import Pokemon as PokemonModel
from src.app.schemas.schemas import PokemonUpdate, PokemonCreate
from src.app.config.database import get_db

class PokemonRepository:
    def __init__(self, session: Session):
        self.session = session 

    def update_pokemon(self, pokemon_id: int, pokemon_update: dict):
        pokemon = self.session.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
        if not pokemon:
            raise ValueError(f"Pokemon with ID {pokemon_id} not found.")
        
        for key, value in pokemon_update.items():
            setattr(pokemon, key, value)

        self.session.commit()
        return pokemon
    
    def reorder(self, pokemon):
        if isinstance(pokemon, list):
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "height": p.height,
                    "weight": p.weight,
                    "xp": p.xp,
                    "image_url": p.image_url,
                    "pokemon_url": p.pokemon_url,
                    "abilities": p.abilities,
                    "stats": p.stats,
                    "types": [{"name": t} for t in p.types],
                }
                for p in pokemon
            ]
        return {
            "id": pokemon.id,
            "name": pokemon.name,
            "height": pokemon.height,
            "weight": pokemon.weight,
            "xp": pokemon.xp,
            "image_url": pokemon.image_url,
            "pokemon_url": pokemon.pokemon_url,
            "abilities": pokemon.abilities,
            "stats": pokemon.stats,
            "types": [{"name": t} for t in pokemon.types],
        }

    def get_all_pokemon(self, page: int, size: int):
        total_items = self.session.query(Pokemon).count()
        if total_items == 0:
            return None, "No Pokémon found."

        total_pages = ceil(total_items / size)
        if page > total_pages:
            return None, f"Only {total_pages} pages available."

        pokemons = (
            self.session.query(Pokemon)
            .order_by(Pokemon.id.asc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )

        return {
            "page": page,
            "size": size,
            "total": total_items,
            "total_pages": total_pages,
            "data": self.reorder(pokemons), 
        }, None

    def create_pokemon(self, pokemon_data: dict):
        try:
        
            image_url = str(pokemon_data['image_url']) 
            pokemon_url = str(pokemon_data['pokemon_url'])  

            
            db_pokemon = Pokemon(
                name=pokemon_data['name'],
                height=pokemon_data['height'],
                weight=pokemon_data['weight'],
                xp=pokemon_data['xp'],
                image_url=image_url,
                pokemon_url=pokemon_url,
                abilities=pokemon_data.get('abilities', []),  
                stats=pokemon_data.get('stats', []),          
                types=pokemon_data.get('types', [])           
            )

       
            self.session.add(db_pokemon)
            self.session.commit()
            self.session.refresh(db_pokemon) 

            return db_pokemon

        except Exception as e:
            self.session.rollback()  
            raise Exception(f"Failed to create Pokémon: {str(e)}")




    def get_pokemon_by_id(self, pokemon_id: int):
        pokemon = self.session.query(Pokemon).filter_by(id=pokemon_id).first()
        if not pokemon:
            return None, "Pokémon not found."
        return {
            "id": pokemon.id,
            "name": pokemon.name,
            "height": pokemon.height,
            "weight": pokemon.weight,
            "xp": pokemon.xp,
            "image_url": pokemon.image_url,
            "pokemon_url": pokemon.pokemon_url,
            "abilities": pokemon.abilities,
            "stats": pokemon.stats,
            "types": [{"name": t} for t in pokemon.types],
        }, None

    def delete_pokemon(self, pokemon_id: int):
        pokemon = self.session.query(Pokemon).filter_by(id=pokemon_id).first()
        if not pokemon:
            return None, f"Pokémon with ID {pokemon_id} not found."

        self.session.delete(pokemon)
        self.session.commit()
        return f"Pokémon with ID {pokemon_id} deleted successfully.", None
