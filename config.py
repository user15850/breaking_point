"""
Arena Dinamica - Configurazione Globale
Costanti, colori e impostazioni del gioco
"""

# ========== DIMENSIONI SCHERMO ==========
LARGHEZZA_SCHERMO = 800
ALTEZZA_SCHERMO = 600
FPS = 60

# ========== STATI DEL GIOCO ==========
class StatoGioco:
    """Enum per gli stati del gioco"""
    MENU = "MENU"
    GIOCANDO = "GIOCANDO"
    PUBBLICITA = "PUBBLICITA"
    FINE_GIOCO = "FINE_GIOCO"
    IN_PAUSA = "IN_PAUSA"

# ========== COLORI (RGB) ==========
class Colori:
    """Colori dello studio TV nel caos"""
    NERO = (25, 25, 25)                   # Sfondo principale
    BIANCO = (255, 255, 255)           # Testo e elementi neutri
    ROSSO_DIRETTA = (220, 20, 60)      # Rosso "DIRETTA"
    ROSSO_SCURO = (139, 0, 0)          # Rosso scuro per sfondo
    GIALLO = (255, 255, 0)             # Avvertimento
    ARANCIO = (255, 165, 0)            # Riflettori
    GRIGIO = (100, 100, 100)           # Cavi e ostacoli
    GRIGIO_CHIARO = (200, 200, 200)    # Elementi secondari
    CIANO = (0, 255, 255)              # Effetti speciali
    VERDE = (0, 255, 0)                # Informazioni positive

# ========== TIMING GLOBALE ==========
INTERVALLO_EVENTO = 15  # Secondi tra gli eventi dinamici
DURATA_PUBBLICITA = 2  # Durata della pubblicità in secondi
VELOCITA_CADUTA_RIFLETTORI = 7  # Velocità di caduta dei riflettori

# ========== DIFFICOLTÀ ==========
DIFFICOLTA_NORMALE = 1.0
DIFFICOLTA_DIFFICILE = 1.5
DIFFICOLTA_ESTREMA = 2.0

# ========== DIFFICOLTÀ DELLA DIRETTA ==========
TEMPO_PER_VINCERE = 30.0      # Sopravvivi 1 minuto per finire la diretta

# ========== DEBUG ==========
MODALITA_DEBUG = False
MOSTRA_FPS = True
