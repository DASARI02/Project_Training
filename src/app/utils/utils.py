import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from src.app.models.models import Pokemon

# Make sure the database session setup is correct

DATABASE_URL = "postgresql+psycopg2://postgres:Chaitu%402002@localhost:5432/pokemon_database"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

def load_json_to_db(json_path: str):
    """Load JSON data from the provided file into the database"""
    print("Attempting to load JSON data...")

    try:
        with open(json_path, 'r') as file:
            data = json.load(file)

        print(f"Successfully loaded {len(data)} records from the JSON file.")
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return

    try:
        count=0
        for pokemon in data:
            # Check if pokemon already exists in the database
            existing_pokemon = session.query(Pokemon).filter_by(name=pokemon["name"].lower()).first()

            if existing_pokemon:
                # print(f"Skipping duplicate Pokémon: {pokemon['name']}")
                continue  

            types = [{"name": typ} for typ in pokemon.get("types", [])]
            abilities = [
                {"name": ability["name"], "is_hidden": ability.get("is_hidden", False)}
                for ability in pokemon.get("abilities", [])
            ]
            count+=1
            pokemon_entry = Pokemon(
                id = count,
                name=pokemon.get("name", "").lower(),
                height=pokemon.get("height", 0),
                weight=pokemon.get("weight", 0),
                xp=pokemon.get("xp", 0),
                image_url=pokemon.get("image_url", ""),
                pokemon_url=pokemon.get("pokemon_url", ""),
                abilities=abilities, 
                stats=pokemon.get("stats", {}),
                types=types,  
            )

            session.add(pokemon_entry)

        session.commit()  # Commit to save all Pokemon to the DB
        print("All records inserted successfully.")
    except Exception as e:
        session.rollback()  # Roll back if error occurs
        print(f"Error inserting records: {e}")
    finally:
        session.close()
        print("Database session closed.")


