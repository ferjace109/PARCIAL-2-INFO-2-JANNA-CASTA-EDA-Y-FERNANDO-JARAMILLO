import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.io as sio

class ArchivoEEG:
#Maneja archivos MAT de electroencefalografía (EEG).
#Dimensiones esperadas de la matriz 'data': (canales, muestras, epocas)
#Frecuencia de muestreo: 1000 Hz
#Atributos:
    #ruta: str - ruta completa del archivo
    #nombre: str - nombre del archivo sin extensión
    #tipo: str - 'Control' o 'Parkinson' (inferido del nombre)
    #mat_3d: ndarray – matriz original (canales x muestras x épocas)
    #mat_2d: ndarray – matriz aplanada (canales x (muestras x epocas))
    #n_canales: int
    #n_muestras: int
    #n_epocas: int
    #fs: int – frecuencia de muestreo (1000 Hz)
    #carpeta_g: str – carpeta de gráficos

    FS = 1000  # Hz

    NOMBRES_CANALES = [
        "Fz", "Cz", "Pz", "C3", "C4", "P3", "P4", "Oz"
    ]

    def __init__(self, ruta: str, carpeta_graficos: str = "graficos"):
        if not os.path.isfile(ruta):
            raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
        if not ruta.lower().endswith(".mat"):
            raise ValueError("El archivo debe ser .mat")

        self.ruta = ruta
        self.nombre = os.path.splitext(os.path.basename(ruta))[0]
        self.carpeta_g = carpeta_graficos
        os.makedirs(self.carpeta_g, exist_ok=True)

        # Inferir tipo de sujeto, es decir si es Control o Parkinson, a partir del nombre del archivo
        base = self.nombre.upper()
        if "P0" in base or "P1" in base:
            self.tipo = "Parkinson"
        else:
            self.tipo = "Control"