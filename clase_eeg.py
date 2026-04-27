import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.io as sio

def validar_entero(mensaje: str, minimo: int = None, maximo: int = None) -> int:
    """Pide un entero al usuario con validación de rango opcional."""
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
        
        # Cargar datos
        mat = sio.loadmat(ruta)
        clave = [k for k in mat.keys() if not k.startswith("_")][0]
        self.mat_3d = mat[clave]                     # (canales, muestras, épocas)
        self.n_canales, self.n_muestras, self.n_epocas = self.mat_3d.shape

        # Convertir a 2D: (canales, muestras*épocas)
        self.mat_2d = self.mat_3d.reshape(self.n_canales, -1)

        print(f"  ✔  Archivo '{self.nombre}' cargado correctamente.")
        print(f"     Tipo: {self.tipo} | Canales: {self.n_canales} | "
              f"Muestras/época: {self.n_muestras} | Épocas: {self.n_epocas}")
        
    #Mostrar llaves
    def mostrar_llaves(self):
    #Usa whosmat para mostrar las llaves del archivo MAT
        info = sio.whosmat(self.ruta)
        print(f"\n  Variables en '{self.nombre}.mat':")
        print(f"  {'Variable':<15} {'Dimensiones':<20} {'Tipo'}")
        print("  " + "-"*50)
        for nombre, dims, tipo in info:
            print(f"  {nombre:<15} {str(dims):<20} {tipo}")
        print()

    #Canales disponibles y validación de entrada
    def _elegir_canal(self, mensaje: str) -> int:
    #Solicita un índice de canal válido (1-base → 0-base interna)
        print(f"  Canales disponibles (1–{self.n_canales}):")
        for i in range(self.n_canales):
            nombre = self.NOMBRES_CANALES[i] if i < len(self.NOMBRES_CANALES) else f"CH{i+1}"
            print(f"    {i+1}. {nombre}")
        return validar_entero(mensaje, 1, self.n_canales) - 1 

    # Suma de 3 canales 
    def sumar_canales(self):

    #Suma 3 canales elegidos por el usuario entre un punto minimo y máximo
    #(índices de muestra sobre la señal 2D).
    #Grafica los 3 canales individuales y la suma en 2 subplots.
    #Guarda el gráfico en formato PNG.
        
        print("\n─── Suma de 3 canales (señal 2D) ──────────────────────────")
        n_total = self.mat_2d.shape[1]
        print(f"  Total de muestras en 2D: {n_total} "
              f"(≈ {n_total/self.FS:.1f} segundos)")

        #Elegir canales
        print("\n  Seleccione Canal 1:")
        c1 = self._elegir_canal("    Número de canal: ")
        print("  Seleccione Canal 2:")
        c2 = self._elegir_canal("    Número de canal: ")
        print("  Seleccione Canal 3:")
        c3 = self._elegir_canal("    Número de canal: ")

        # Elegir rango
        print(f"\n  Rango de muestras (0 – {n_total-1}):")
        p_min = validar_entero("    Punto mínimo: ", 0, n_total - 2)
        p_max = validar_entero("    Punto máximo: ", p_min + 1, n_total - 1)

        # Extraer segmento
        seg1 = self.mat_2d[c1, p_min:p_max]
        seg2 = self.mat_2d[c2, p_min:p_max]
        seg3 = self.mat_2d[c3, p_min:p_max]
        suma = seg1 + seg2 + seg3

        n_seg = len(seg1)
        tiempo = np.arange(n_seg) / self.FS  # en segundos

        nombres = self.NOMBRES_CANALES
        n1 = nombres[c1] if c1 < len(nombres) else f"CH{c1+1}"
        n2 = nombres[c2] if c2 < len(nombres) else f"CH{c2+1}"
        n3 = nombres[c3] if c3 < len(nombres) else f"CH{c3+1}"

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
        fig.suptitle(f"Suma de canales – {self.nombre} ({self.tipo})",
                     fontsize=13, fontweight="bold")
        
        # Subplot 1: canales individuales
        ax1.plot(tiempo, seg1, label=n1, linewidth=0.9)
        ax1.plot(tiempo, seg2, label=n2, linewidth=0.9)
        ax1.plot(tiempo, seg3, label=n3, linewidth=0.9)
        ax1.set_title("Canales individuales")
        ax1.set_xlabel("Tiempo (s)")
        ax1.set_ylabel("Amplitud (µV)")
        ax1.legend(loc="upper right")
        ax1.grid(True, alpha=0.3)

        # Subplot 2: suma
        ax2.plot(tiempo, suma, color="crimson", linewidth=1.0, label=f"{n1}+{n2}+{n3}")
        ax2.set_title(f"Suma de canales: {n1} + {n2} + {n3}")
        ax2.set_xlabel("Tiempo (s)")
        ax2.set_ylabel("Amplitud (µV)")
        ax2.legend(loc="upper right")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()
        self._guardar_figura(fig, f"{self.nombre}_suma_canales")