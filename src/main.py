from fastapi import FastAPI
from src.app.router import router, auth_router
from src.app.utils.utils import load_json_to_db
 
app = FastAPI()
 
load_json_to_db(json_path="C:/Users/sai.chaitanya/OneDrive - OneWorkplace/Desktop/Pokemon_database/src/app/pokedex_raw_array.json")

app.include_router(auth_router.router, tags=["Authentication"])
app.include_router(router.router, tags=["Pokémon"])