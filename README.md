# Breaking Point - Studio TV nel Caos

Gioco Python/Pygame con telecamera laterale, menu di selezione e sfondo esteso.

## Struttura del Progetto

```
BREAKING POINT/
├── assets/
│   ├── background.png      # Prima immagine di sfondo
│   ├── background2.png     # Seconda immagine di sfondo in sequenza
│   |── background3.png     # Terza immagine di sfondo in sequenza
|   └── oggetti/
|        ├── cavo.png
|        ├── microfono.png
|        ├── riflettore.png
├── index.py                # Gioco completo
├── config.py               # Costanti e configurazione globale
└── README.md               # Documentazione
```

## Requisiti

- Python 3.7+
- Pygame

## Installazione

1. Installa Pygame:
```bash
pip install pygame
```

## Come Giocare

Esegui il gioco:
```bash
python index.py
```

### Comandi

| Tasto | Funzione |
|-------|----------|
| **SPACE** | Inizia il gioco / Ritorna al menu |
| **ESC** | Esci dal gioco |
| **P** | Pausa/Riprendi (durante il gioco) |
| **D** | Attiva/Disattiva modalità debug |
| **←/→** / **↑/↓** | Cambia coppia protagonista/nemico nel menu |

## Sfondo

Il gioco usa immagini in `assets/` per lo sfondo:

- `background.png` viene visualizzata una sola volta all’inizio
- `background2.png` e `background3.png` vengono ripetute in sequenza infinita dopo la prima immagine

Questo permette uno sfondo esteso e un movimento continuo della telecamera verso destra.

## Stato attuale

- `index.py` contiene la logica di gioco, il menu, la selezione delle coppie e il timer.
- `config.py` contiene le costanti del progetto.
- `assets/` contiene le immagini di sfondo.

## Configurazione

Modifica `config.py` per cambiare:

- `LARGHEZZA_SCHERMO` e `ALTEZZA_SCHERMO`
- `FPS`
- `INTERVALLO_EVENTO`
- `DURATA_PUBBLICITA`
- `MODALITA_DEBUG`
- `MOSTRA_FPS`

## Note Tecniche

- Il gioco gestisce la telecamera e lo sfondo in base alla posizione del protagonista
- La prima immagine di sfondo viene usata come inizio fisso
- Le immagini successive scorrono in loop infinito
---
