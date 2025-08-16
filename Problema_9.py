import requests
import time

BASE_URL = "https://pokeapi.co/api/v2/"


def get_json(url):
    """Descarga y devuelve JSON de una URL con manejo de errores."""
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener {url}: {e}")
        return None


# -----------------------------
# 🔹 Clasificación por tipos
# -----------------------------

def pokemon_tipo_en_region(tipo, region):
    """Retorna lista de Pokémon de cierto tipo en una región."""
    region_data = get_json(f"{BASE_URL}pokedex/{region}")
    if not region_data:
        return []
    entries = [p["pokemon_species"]["name"] for p in region_data["pokemon_entries"]]

    tipo_data = get_json(f"{BASE_URL}type/{tipo}")
    if not tipo_data:
        return []
    tipo_pokemon = [p["pokemon"]["name"] for p in tipo_data["pokemon"]]

    return sorted(set(entries) & set(tipo_pokemon))


def pokemon_tipo_altura(tipo, altura_min):
    """Lista Pokémon de un tipo con altura mayor a X."""
    tipo_data = get_json(f"{BASE_URL}type/{tipo}")
    if not tipo_data:
        return []
    result = []
    for p in tipo_data["pokemon"]:
        poke_info = get_json(p["pokemon"]["url"])
        if poke_info and poke_info["height"] > altura_min:
            result.append(poke_info["name"])
    return result


# -----------------------------
# 🔹 Evoluciones
# -----------------------------

def cadena_evolutiva(pokemon_nombre):
    """Devuelve cadena evolutiva de un Pokémon."""
    species = get_json(f"{BASE_URL}pokemon-species/{pokemon_nombre}")
    if not species:
        return []
    evo_chain_url = species["evolution_chain"]["url"]
    evo_chain = get_json(evo_chain_url)

    def recorrer_cadena(chain):
        result = [chain["species"]["name"]]
        for evo in chain["evolves_to"]:
            result.extend(recorrer_cadena(evo))
        return result

    return recorrer_cadena(evo_chain["chain"])


def electricos_sin_evolucion():
    """Lista Pokémon eléctricos sin evoluciones."""
    electric_type = get_json(f"{BASE_URL}type/electric")
    if not electric_type:
        return []
    result = []
    for p in electric_type["pokemon"]:
        species = get_json(f"{BASE_URL}pokemon-species/{p['pokemon']['name']}")
        if species and not species["evolves_from_species"] and not species["evolution_chain"]["url"]:
            result.append(p["pokemon"]["name"])
    return result


# -----------------------------
# 🔹 Estadísticas de batalla
# -----------------------------

def mayor_ataque_region(region):
    """Pokémon con mayor ataque base en una región."""
    region_data = get_json(f"{BASE_URL}pokedex/{region}")
    if not region_data:
        return None
    max_attack = {"name": None, "value": -1}
    for entry in region_data["pokemon_entries"]:
        name = entry["pokemon_species"]["name"]
        poke_data = get_json(f"{BASE_URL}pokemon/{name}")
        if poke_data:
            for stat in poke_data["stats"]:
                if stat["stat"]["name"] == "attack" and stat["base_stat"] > max_attack["value"]:
                    max_attack = {"name": name, "value": stat["base_stat"]}
    return max_attack


def mas_rapido_no_legendario():
    """Pokémon más rápido no legendario."""
    # Requiere recorrer TODA la API o filtrado especial
    url = f"{BASE_URL}pokemon?limit=10000"
    all_pokemon = get_json(url)
    max_speed = {"name": None, "value": -1}
    for p in all_pokemon["results"]:
        poke_data = get_json(p["url"])
        species = get_json(f"{BASE_URL}pokemon-species/{poke_data['name']}")
        if not species["is_legendary"]:
            speed_stat = next(stat["base_stat"] for stat in poke_data["stats"] if stat["stat"]["name"] == "speed")
            if speed_stat > max_speed["value"]:
                max_speed = {"name": poke_data["name"], "value": speed_stat}
    return max_speed


# -----------------------------
# 🔹 Extras
# -----------------------------

def habitat_mas_comun_planta():
    """Habitat más común de Pokémon tipo planta."""
    plant_type = get_json(f"{BASE_URL}type/grass")
    habitats = {}
    for p in plant_type["pokemon"]:
        species = get_json(f"{BASE_URL}pokemon-species/{p['pokemon']['name']}")
        if species and species["habitat"]:
            hab = species["habitat"]["name"]
            habitats[hab] = habitats.get(hab, 0) + 1
    return max(habitats, key=habitats.get)


def pokemon_menor_peso():
    """Pokémon con menor peso en toda la API."""
    url = f"{BASE_URL}pokemon?limit=10000"
    all_pokemon = get_json(url)
    min_weight = {"name": None, "value": float("inf")}
    for p in all_pokemon["results"]:
        poke_data = get_json(p["url"])
        if poke_data and poke_data["weight"] < min_weight["value"]:
            min_weight = {"name": poke_data["name"], "value": poke_data["weight"]}
    return min_weight


# Ejemplo de ejecución:
if __name__ == "__main__":
    print("🔥 Fuego en Kanto:", len(pokemon_tipo_en_region("fire", "kanto")))
    print("💧 Agua altura > 10:", pokemon_tipo_altura("water", 10))
    print("🌱 Evolución Bulbasaur:", cadena_evolutiva("bulbasaur"))
    print("⚡ Eléctricos sin evolución:", electricos_sin_evolucion())
    print("💪 Mayor ataque en Johto:", mayor_ataque_region("original-johto"))
    print("💨 Más rápido no legendario:", mas_rapido_no_legendario())
    print("🍃 Hábitat más común planta:", habitat_mas_comun_planta())
    print("⚖️ Pokémon más ligero:", pokemon_menor_peso())
