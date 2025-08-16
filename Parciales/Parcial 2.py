# Importaciones necesarias
from typing import List
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
import uvicorn


# --------------------- MODELOS ---------------------

class RegistroVacunacion(BaseModel):
    """Modelo de datos para un registro de vacunación."""
    anio: int
    cobertura: float
    fuente: str = "Banco Mundial - SH.IMM.MEAS"


# --------------------- DATOS ---------------------

datos_vacunacion = {
    1983: 85.0, 1984: 72.0, 1985: 85.0, 1986: 74.0, 1987: 78.0,
    1988: 73.0, 1989: 73.0, 1990: 73.0, 1991: 80.0, 1992: 76.0,
    1993: 83.0, 1994: 84.0, 1995: 84.0, 1996: 90.0, 1997: 92.0,
    1998: 96.0, 1999: 90.0, 2000: 97.0, 2001: 95.0, 2002: 95.0,
    2003: 95.0, 2004: 97.0, 2005: 99.0, 2006: 95.0, 2007: 95.0,
    2008: 96.0, 2009: 96.0, 2010: 97.0, 2011: 97.0, 2012: 98.0,
    2013: 92.0, 2014: 90.0, 2015: 93.0, 2016: 95.0, 2017: 98.0,
    2018: 98.0
}

# --------------------- API ---------------------

app = FastAPI(
    title="API Vacunación Sarampión Panamá",
    description="Datos históricos de vacunación contra sarampión en Panamá (1983-2018)",
    version="1.0.0"
)


@app.get("/")
async def inicio():
    """Información básica de la API."""
    return {
        "mensaje": "API de vacunación contra sarampión en Panamá",
        "datos": "1983-2018",
        "endpoints": ["/vacunas", "/vacunas/{anio}"]
    }


@app.get("/vacunas", response_model=List[RegistroVacunacion])
async def obtener_todas_vacunas():
    """Obtiene todos los registros de vacunación."""
    return sorted([
        RegistroVacunacion(anio=anio, cobertura=cobertura)
        for anio, cobertura in datos_vacunacion.items()
    ], key=lambda x: x.anio)


@app.get("/vacunas/{anio}", response_model=RegistroVacunacion)
async def obtener_vacuna_por_anio(anio: int = Path(..., ge=1983, le=2018)):
    """Obtiene el registro de vacunación para un año específico."""
    if anio not in datos_vacunacion:
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos para el año {anio}"
        )

    return RegistroVacunacion(anio=anio, cobertura=datos_vacunacion[anio])


# --------------------- EJECUCIÓN ---------------------

if __name__ == "__main__":
    uvicorn.run("__main__:app", host="127.0.0.1", port=8080, reload=True)