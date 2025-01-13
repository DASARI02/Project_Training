from math import ceil
from sqlalchemy.orm import Session
from src.app.models.models import Pokemon
from sqlalchemy.exc import SQLAlchemyError
from src.app.models.models import Pokemon
from src.app.schemas.schemas import PokemonUpdate
from src.app.models.models import Pokemon

class PokemonRepository:
    def __init__(self, session: Session):
        self.session = session

    def update_pokemon(self, pokemon_id: int, pokemon_update: dict):
        # Find the Pokémon by ID
        pokemon = self.session.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
        if not pokemon:
            raise ValueError(f"Pokemon with ID {pokemon_id} not found.")
        
        # Apply the updates to the Pokémon's attributes
        for key, value in pokemon_update.items():
            setattr(pokemon, key, value)

        # Commit the changes to the database
        self.session.commit()
        return pokemon
    
    def reorder(self, pokemon):
        # Convert Pokemon objects to dictionaries as required
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
            "data": self.reorder(pokemons),  # Reorder the results
        }, None


    def create_pokemon(self, pokemon_data: dict):
            try:
                existing = self.session.query(Pokemon).filter_by(name=pokemon_data["name"].lower()).first()
                if existing:
                    return None, f"Pokémon with name '{pokemon_data['name']}' already exists."

                pokemon_data["image_url"] = str(pokemon_data.get("image_url", ""))  # Convert URL to string
                pokemon_data["pokemon_url"] = str(pokemon_data.get("pokemon_url", ""))  # Convert URL to string

                new_pokemon = Pokemon(**pokemon_data)
                self.session.add(new_pokemon)
                self.session.commit()

                # Return the created Pokemon's data, including id
                return self.reorder([new_pokemon])[0], None
            except SQLAlchemyError as e:
                self.session.rollback()
                return None, str(e)


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
