

#Sistema de Exploración Neuroambiental
#Universidad de Antioquia – Bioingeniería – Informática II 2026-1

#Contiene:
# Funciones de validación numérica
# Clase SiataCSV   -> manejo de archivos CSV de calidad del aire (SIATA)
# Clase ArchivoEEG -> manejo de archivos MAT de electroencefalografía
# Clase Repositorio -> almacén de objetos con búsqueda (puntos extra)


import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.io as sio

#  FUNCIONES DE VALIDACIÓN NUMÉRICA
def validar_entero(mensaje: str, minimo: int = None, maximo: int = None) -> int:
    #Pide un entero al usuario con validación de rango opcional.
    while True:
        try:
            valor = int(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"  ⚠  El valor debe ser ≥ {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  ⚠  El valor debe ser ≤ {maximo}.")
                continue
            return valor
        except ValueError:
            print("  ⚠  Ingrese un número entero válido.")


def validar_float(mensaje: str, minimo: float = None, maximo: float = None) -> float:
    #Pide un flotante al usuario con validación de rango opcional.
    while True:
        try:
            valor = float(input(mensaje))
            if minimo is not None and valor < minimo:
                print(f"  ⚠  El valor debe ser ≥ {minimo}.")
                continue
            if maximo is not None and valor > maximo:
                print(f"  ⚠  El valor debe ser ≤ {maximo}.")
                continue
            return valor
        except ValueError:
            print("  ⚠  Ingrese un número decimal válido.")


def validar_opcion(mensaje: str, opciones: list) -> str:
    #Valida que la entrada pertenezca a una lista de opciones válidas.
    while True:
        valor = input(mensaje).strip()
        if valor in opciones:
            return valor
        print(f"  ⚠  Opción inválida. Elija entre: {opciones}")


#  _________________CLASE SiataCSV_________________


class SiataCSV:
  

#Atributos
#ruta:tipo str  – ruta completa del archivo
#nombre:tipo str  – nombre del archivo sin extensión
#df: tipo DataFrame – datos cargados con fecha_hora como índice
# carpeta_g:tipo str  – carpeta donde se guardan los gráficos
   

    COLUMNAS_CALIDAD = {
        "pm25": "PM2.5 (µg/m³)",
        "pm10": "PM10 (µg/m³)",
        "no":   "NO (ppb)",
        "no2":  "NO₂ (ppb)",
        "nox":  "NOx (ppb)",
        "ozono":"Ozono (ppb)",
        "co":   "CO (ppm)",
    }

    def __init__(self, ruta: str, carpeta_graficos: str = "graficos"):
        if not os.path.isfile(ruta):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
        if not ruta.lower().endswith(".csv"):
            raise ValueError("El archivo debe ser .csv")

        self.ruta = ruta
        self.nombre = os.path.splitext(os.path.basename(ruta))[0]
        self.carpeta_g = carpeta_graficos
        os.makedirs(self.carpeta_g, exist_ok=True)
        #indice hora
        self.df = pd.read_csv(ruta, parse_dates=["fecha_hora"])
        self.df.set_index("fecha_hora", inplace=True)
        print(f"  ✔  Archivo '{self.nombre}' cargado correctamente. "
              f"({len(self.df)} registros, {len(self.df.columns)} columnas)")
