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

    # ── Promedio y desviación estándar
    def estadisticas_3d(self):
    #Calcula promedio y desviación estándar de la matriz 3D a lo largo de un eje elegido por el usuario
    # Muestra dos subplots con stem de cada estadística
    
        print("\n─── Estadísticas sobre matriz 3D ──────────────────────────")
        print("  Ejes disponibles:")
        print("    0 → a lo largo de los canales      (resultado: muestras × épocas)")
        print("    1 → a lo largo de las muestras     (resultado: canales × épocas)")
        print("    2 → a lo largo de las épocas       (resultado: canales × muestras)")
        eje = validar_entero("  Eje para calcular estadísticas (0, 1 ó 2): ", 0, 2)

        promedio = np.mean(self.mat_3d, axis=eje)
        desv_std = np.std(self.mat_3d, axis=eje)

        # Aplanar para stem (visualización 1D)
        prom_flat = promedio.flatten()
        std_flat  = desv_std.flatten()
        x_prom    = np.arange(len(prom_flat))
        x_std     = np.arange(len(std_flat))

        etiqueta_eje = ["canales", "muestras", "épocas"][eje]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
        fig.suptitle(f"Estadísticas 3D (eje={eje}: {etiqueta_eje}) – {self.nombre}",
                     fontsize=13, fontweight="bold")

        # Stem promedio
        markerline, stemlines, baseline = ax1.stem(
            x_prom[:500], prom_flat[:500],
            linefmt="steelblue", markerfmt="C0o", basefmt="k-"
        )
        plt.setp(stemlines, linewidth=0.5)
        plt.setp(markerline, markersize=2)
        ax1.set_title("Promedio")
        ax1.set_xlabel("Índice (aplanado)")
        ax1.set_ylabel("Amplitud media (µV)")
        ax1.grid(True, alpha=0.3)

        # Stem desviación estándar
        markerline2, stemlines2, baseline2 = ax2.stem(
            x_std[:500], std_flat[:500],
            linefmt="darkorange", markerfmt="C1o", basefmt="k-"
        )
        plt.setp(stemlines2, linewidth=0.5)
        plt.setp(markerline2, markersize=2)
        ax2.set_title("Desviación estándar")
        ax2.set_xlabel("Índice (aplanado)")
        ax2.set_ylabel("Desviación estándar (µV)")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()
        self._guardar_figura(fig, f"{self.nombre}_estadisticas_eje{eje}")

    def _guardar_figura(self, fig: plt.Figure, nombre_base: str):
    #Guarda la figura como PNG en la carpeta de gráficos
        ruta_salida = os.path.join(self.carpeta_g, f"{nombre_base}.png")
        fig.savefig(ruta_salida, dpi=150, bbox_inches="tight")
        print(f"  💾  Gráfico guardado → {ruta_salida}")

    def __str__(self):
        return (f"ArchivoEEG | {self.nombre} | Tipo: {self.tipo} | "
                f"Canales: {self.n_canales} | "
                f"Muestras/época: {self.n_muestras} | Épocas: {self.n_epocas}")

    def __repr__(self):
        return f"ArchivoEEG('{self.ruta}')"
    
#CLASE REPOSITORIO
#Almacena objetos SiataCSV y ArchivoEEG con búsqueda por nombre o tipo.
#Internamente mantiene un diccionario:
        #_datos = { nombre_clave: objeto }
#La clave es el nombre del archivo sin extensión.

class Repositorio:
    def __init__(self):
        self._datos: dict = {}
        print("  📦  Repositorio de objetos iniciado.")

    # ── Agregar ──────────────────────────────────────────────────────────────

    def agregar(self, objeto):
    #Almacena un SiataCSV o ArchivoEEG en el repositorio
        if not isinstance(objeto, (SiataCSV, ArchivoEEG)): #SiataCSV este se hace en la otra branch
            raise TypeError("Solo se pueden almacenar objetos SiataCSV o ArchivoEEG.")
        clave = objeto.nombre
        if clave in self._datos:
            print(f"  ⚠  Ya existe un objeto con la clave '{clave}'. Será sobreescrito.")
        self._datos[clave] = objeto
        tipo = type(objeto).__name__
        print(f"  ✔  Objeto '{clave}' ({tipo}) agregado al repositorio.")

    # Buscar por nombre 
    def buscar(self, nombre: str):
    #Busca un objeto por nombre exacto (sin extensión)
        if nombre in self._datos:
            obj = self._datos[nombre]
            print(f"  🔍  Encontrado: {obj}")
            return obj
        
        # Búsqueda parcial (las mayúsculas no afectan)
        coincidencias = {k: v for k, v in self._datos.items()
                         if nombre.lower() in k.lower()}
        if coincidencias:
            print(f"  🔍  Coincidencias parciales para '{nombre}':")
            for k, v in coincidencias.items():
                print(f"    – {k}: {v}")
            if len(coincidencias) == 1:
                return list(coincidencias.values())[0]
            return coincidencias
        print(f"  ⚠  No se encontró ningún objeto con nombre '{nombre}'.")
        return None
    
    # Buscar por tipo
    def buscar_por_tipo(self, tipo: str):
    #Filtra objetos portipo: 'csv', 'eeg', 'control', 'parkinson'
    
        tipo_lower = tipo.lower()
        resultados = {}
        for k, v in self._datos.items():
            if tipo_lower in ("csv", "siata") and isinstance(v, SiataCSV): #de la otra branch pero que uniremos al final
                resultados[k] = v
            elif tipo_lower == "eeg" and isinstance(v, ArchivoEEG):
                resultados[k] = v
            elif tipo_lower == "control" and isinstance(v, ArchivoEEG) and v.tipo == "Control":
                resultados[k] = v
            elif tipo_lower == "parkinson" and isinstance(v, ArchivoEEG) and v.tipo == "Parkinson":
                resultados[k] = v

        if resultados:
            print(f"  🔍  Objetos de tipo '{tipo}':")
            for k, v in resultados.items():
                print(f"    – {k}: {v}")
        else:
            print(f"  ⚠  No hay objetos de tipo '{tipo}' en el repositorio.")
        return resultados

    #Listar todos 

    def listar(self):
        if not self._datos:
            print("  El repositorio está vacío.")
            return
        print(f"\n  📦  Repositorio ({len(self._datos)} objeto(s)):")
        print("  " + "-"*60)
        for i, (k, v) in enumerate(self._datos.items(), 1):
            tipo = type(v).__name__
            print(f"  {i:3}. [{tipo}]  {v}")
        print("  " + "-"*60)

    # Eliminar 
    def eliminar(self, nombre: str) -> bool:
        """Elimina un objeto del repositorio por nombre."""
        if nombre in self._datos:
            del self._datos[nombre]
            print(f"  🗑  Objeto '{nombre}' eliminado del repositorio.")
            return True
        print(f"  ⚠  No se encontró '{nombre}' en el repositorio.")
        return False

    def __len__(self):
        return len(self._datos)

    def __contains__(self, nombre: str):
        return nombre in self._datos

    def __str__(self):
        return f"Repositorio con {len(self._datos)} objeto(s): {list(self._datos.keys())}"
