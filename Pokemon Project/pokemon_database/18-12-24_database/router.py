from fastapi import FastAPI, HTTPException, Query
import psycopg2
import psycopg2.extras
from math import ceil
from models import Pokemon, PokemonUpdate

app = FastAPI()


def get_db_connection():
    try:
        return psycopg2.connect(
            dbname="pokemon_database",
            user="postgres",
            password="Chaitu@2002",
            host="localhost",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to connect to the database.")


@app.get("/pokemon/all")
def get_all_pokemon(page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=30)):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("SELECT COUNT(*) FROM pokemons;")
        total_items = cur.fetchone()["count"]
        total_pages = ceil(total_items / size)

        if page > total_pages:
            raise HTTPException(status_code=404, detail=f"Only {total_pages} pages available.")

        offset = (page - 1) * size
        cur.execute("SELECT * FROM pokemons ORDER BY id ASC LIMIT %s OFFSET %s;", (size, offset))
        data = cur.fetchall()

        return {
            "page": page,
            "size": size,
            "total": total_items,
            "total_pages": total_pages,
            "data": data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching Pokémon.")
    finally:
        cur.close()
        conn.close()


@app.get("/pokemon/{pokemon_id}")
def get_pokemon_by_id(pokemon_id: int):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    try:
        cur.execute("SELECT * FROM pokemons WHERE id = %s;", (pokemon_id,))
        pokemon = cur.fetchone()

        if not pokemon:
            raise HTTPException(status_code=404, detail="Pokemon not found.")

        return pokemon
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching Pokémon.")
    finally:
        cur.close()
        conn.close()


@app.post("/pokemon")
def create_pokemon(pokemon: Pokemon):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """
            INSERT INTO pokemons (id, name, height, weight, xp, image_url, pokemon_url, abilities, stats, types)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """,
            (
                pokemon.id,
                pokemon.name.lower(),
                pokemon.height,
                pokemon.weight,
                pokemon.xp,
                str(pokemon.image_url),
                str(pokemon.pokemon_url),
                psycopg2.extras.Json(pokemon.abilities),
                psycopg2.extras.Json(pokemon.stats),
                psycopg2.extras.Json(pokemon.types),
            ),
        )
        conn.commit()
        return {"message": "Pokemon created successfully.", "pokemon": pokemon}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error creating Pokémon.")
    finally:
        cur.close()
        conn.close()


@app.delete("/pokemon/{pokemon_id}")
def delete_pokemon(pokemon_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM pokemons WHERE id = %s;", (pokemon_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Pokemon not found.")
        conn.commit()
        return {"message": f"Pokemon with ID {pokemon_id} deleted successfully."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Error deleting Pokémon.")
    finally:
        cur.close()
        conn.close()


@app.put("/pokemon/{pokemon_id}", operation_id="update_pokemon")
def update_pokemon(pokemon_id: int, pokemon_update: PokemonUpdate):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        set_clause = []
        values = []

        if pokemon_update.name is not None:
            set_clause.append("name = %s")
            values.append(pokemon_update.name.lower())

        if pokemon_update.height is not None:
            set_clause.append("height = %s")
            values.append(pokemon_update.height)

        if pokemon_update.weight is not None:
            set_clause.append("weight = %s")
            values.append(pokemon_update.weight)

        if pokemon_update.xp is not None:
            set_clause.append("xp = %s")
            values.append(pokemon_update.xp)

        if pokemon_update.image_url is not None:
            set_clause.append("image_url = %s")
            values.append(str(pokemon_update.image_url))

        if pokemon_update.pokemon_url is not None:
            set_clause.append("pokemon_url = %s")
            values.append(str(pokemon_update.pokemon_url))

        if pokemon_update.abilities is not None:
            set_clause.append("abilities = %s")
            values.append(psycopg2.extras.Json([ability.dict() for ability in pokemon_update.abilities]))

        if pokemon_update.stats is not None:
            set_clause.append("stats = %s")
            values.append(psycopg2.extras.Json([stat.dict() for stat in pokemon_update.stats]))

        if pokemon_update.types is not None:
            set_clause.append("types = %s")
            values.append(psycopg2.extras.Json([type.dict() for type in pokemon_update.types]))

        if not set_clause:
            raise HTTPException(status_code=400, detail="No fields provided to update.")

        set_clause_str = ", ".join(set_clause)
        values.append(pokemon_id)

        cur.execute(f"UPDATE pokemons SET {set_clause_str} WHERE id = %s;", values)
        conn.commit()
        return {"message": "Pokémon updated successfully."}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Error updating Pokémon.")
    finally:
        cur.close()
        conn.close()
