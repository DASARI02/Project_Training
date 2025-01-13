from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.app.services.services import PokemonRepository  # Ensure this contains CRUD methods like create, read, etc.
from src.app.schemas.schemas import Pokemon as PokemonSchema, PokemonUpdate
from src.app.auth.auth import JWTBearer
from src.app.config.database import get_db

router = APIRouter(prefix="/pokemon", tags=["Pokémon"])

# Endpoint to get all Pokémon with pagination
@router.get("/", dependencies=[Depends(JWTBearer())])
def get_all_pokemon(
    page: int = 1, size: int = 10, db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer)
):
    """Fetch a paginated list of all Pokémon."""
    repository = PokemonRepository(db)  # Use the service layer for database calls
    return repository.get_all_pokemon(page, size)  # Implement pagination logic in the repository

# Endpoint to create a new Pokémon
@router.post("/", dependencies=[Depends(JWTBearer())])
def create_pokemon(
    pokemon: PokemonSchema,  # Pydantic schema that validates input
    db: Session = Depends(get_db),  # Dependency that provides the DB session
    current_user: dict = Depends(JWTBearer)  # JWT authorization
):
    """Create a new Pokémon in the database."""
    repository = PokemonRepository(db)
    try:
        # Ensure input is correctly processed, and any errors in repository layer are caught
        return repository.create_pokemon(pokemon.dict())  # Pydantic validation ensures proper input data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint to fetch a Pokémon by ID
@router.get("/{pokemon_id}", dependencies=[Depends(JWTBearer())])
def get_pokemon_by_id(
    pokemon_id: int,  
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer)
):
    """Fetch a Pokémon by its ID."""
    repository = PokemonRepository(db)
    return repository.get_pokemon_by_id(pokemon_id)  # Ensure the repository handles this fetch correctly

# Endpoint to update an existing Pokémon
@router.put("/pokemon/{pokemon_id}")
async def update_pokemon(pokemon_id: int, pokemon_update: PokemonUpdate, db: Session = Depends(get_db)):
    # Create an instance of the repository
    repository = PokemonRepository(db)
    
    # Pass the ID and dictionary of values to update
    try:
        # Pass 'exclude_unset=True' to only update unset values
        result = repository.update_pokemon(pokemon_id, pokemon_update.dict(exclude_unset=True))  # Notice how the dict is passed
        return {"message": "Pokemon updated successfully", "pokemon": result}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


# Endpoint to delete a Pokémon by ID
@router.delete("/{pokemon_id}", dependencies=[Depends(JWTBearer())])
def delete_pokemon(
    pokemon_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer)
):
    """Delete a Pokémon from the database."""
    repository = PokemonRepository(db)
    try:
        repository.delete_pokemon(pokemon_id)  # Handle the deletion process
        return {"message": "Pokémon deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
