from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.app.services.services import PokemonRepository  
from src.app.schemas.schemas import Pokemon as PokemonSchema, PokemonUpdate
from src.app.schemas.schemas import PokemonCreate
from src.app.auth.auth import JWTBearer
from src.app.config.database import get_db
from src.app.models.models import User
router = APIRouter(prefix="/pokemon", tags=["Pokémon"])

@router.get("/users", dependencies= [Depends(JWTBearer())])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {"users": users}


@router.get("/", dependencies=[Depends(JWTBearer())])
def get_all_pokemon(
    page: int = 1, size: int = 10, db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer)
):
    """Fetch a paginated list of all Pokémon."""
    repository = PokemonRepository(db)
    return repository.get_all_pokemon(page, size)  


import logging

logger = logging.getLogger("uvicorn.error")

@router.post("/", dependencies=[Depends(JWTBearer())])
def create_pokemon(
    pokemon: PokemonCreate,  
    db: Session = Depends(get_db),  # Ensuring to get session from dependency
    current_user: dict = Depends(JWTBearer)  
):
    """Create a new Pokémon in the database."""
    repository = PokemonRepository(db) 
    try:
        return repository.create_pokemon(pokemon.dict()) 
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{pokemon_id}", dependencies=[Depends(JWTBearer())])
def get_pokemon_by_id(
    pokemon_id: int,  
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer)
):
    repository = PokemonRepository(db)
    pokemon = repository.get_pokemon_by_id(pokemon_id)
    if pokemon is None:
        raise HTTPException(status_code=404, detail="Pokémon not found")
    return pokemon
 


@router.put("/pokemon/{pokemon_id}", dependencies=[Depends(JWTBearer())])
async def update_pokemon(pokemon_id: int, pokemon_update: PokemonUpdate, db: Session = Depends(get_db), current_user: dict = Depends(JWTBearer)):

    repository = PokemonRepository(db)
    

    try:

        result = repository.update_pokemon(pokemon_id, pokemon_update.dict(exclude_unset=True))  
        return {"message": "Pokemon updated successfully", "pokemon": result}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.delete("/{pokemon_id}", dependencies=[Depends(JWTBearer())])
def delete_pokemon(
    pokemon_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(JWTBearer)
):
    """Delete a Pokémon from the database."""
    repository = PokemonRepository(db)
    try:
        repository.delete_pokemon(pokemon_id) 
        return {"message": "Pokémon deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
