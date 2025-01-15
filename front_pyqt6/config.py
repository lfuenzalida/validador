import json

DATA = {
    "validadores": ["Marcos","Sebastian", "Victor", "Andreina"],
    "conductores": {
        "Ricardo Ponce": {
            "recomendada": {"peoneta": "Oliver", "vehiculo": "Mitzubichi fuso"},
            "opciones": {
                "peonetas": ["Oliver", "Christofer", "Camilo"],
                "vehiculos": ["Mitzubichi fuso", "Camión B", "Mitzubichi fuso chico"]
            }
        },
        "Pablo Garcia": {
            "recomendada": {"peoneta": "Christofer", "vehiculo": "Peugot Boxer"},
            "opciones": {
                "peonetas": ["Oliver", "Christofer", "Camilo"],
                "vehiculos": ["Mitzubichi fuso", "Peugot Boxer", "Mitzubichi fuso chico"]
            }
        },
        "Hector": {
            "recomendada": {"peoneta": "Camilo", "vehiculo": "Mitzubichi fuso chico"},
            "opciones": {
                "peonetas": ["Oliver", "Christofer", "Camilo"],
                "vehiculos": ["Mitzubichi fuso", "Peugot Boxer", "Mitzubichi fuso chico"]
            }
        }
    },
    "vehiculos": {
        "Mitzubichi fuso": "KKLK82",
        "Peugot Boxer": "SJXR58",
        "Mitzubichi fuso chico": "LJTB90"
    }
}

# Guardar la configuración local en un archivo JSON
with open("datos_locales.json", "w") as file:
    json.dump(DATA, file, indent=4)

