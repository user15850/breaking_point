"""
Breaking Point - Studio TV nel Caos
Gioco principale

Questo file contiene il gioco completo insieme alla logica di timer
ed alla selezione delle coppie protagonista / nemico.
"""

import os
import re
import sys
import math
import random
import pygame
from dataclasses import dataclass
from config import (
    LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO, FPS, StatoGioco,
    Colori, INTERVALLO_EVENTO, DURATA_PUBBLICITA, MODALITA_DEBUG,
    MOSTRA_FPS, TEMPO_PER_VINCERE, VELOCITA_CADUTA_RIFLETTORI
)


@dataclass
class CoppiaPersonaggi:
    protagonista: str
    nemico: str
    descrizione: str = ""


def carica_coppie_personaggi():
    """Restituisce le coppie di personaggi predefinite"""
    return [
        CoppiaPersonaggi(
            protagonista="Capra",
            nemico="Sgarbi",
            descrizione="La capra deve sfuggire da Sgarbi"
        ),
        CoppiaPersonaggi(
            protagonista="Fedez",
            nemico="Fabrizio Corona",
            descrizione=""
        ),
        CoppiaPersonaggi(
            protagonista="Posto fisso",
            nemico="Checco Zalone",
            descrizione=""
        ),
    ]


class Giocatore:
    """Entità mobile del gioco: protagonista o nemico."""

    def __init__(self, x: int, y: int, colore: tuple, nome: str):
        self.x = float(x)
        self.y = float(y)
        self.rect = pygame.Rect(x, y, 50, 50)
        self.colore = colore
        self.nome = nome
        self.velocita = 260.0
        self.vely = 0.0
        self.gravita = 1600.0
        self.jump_forza = -650.0
        self.ground_y = float(y)
        self.ha_vinto = False
    
    def muovi(self, tasti, key_left, key_right, key_jump, dt: float):
        dx = 0
        if tasti[key_left]:
            dx -= 1
        if tasti[key_right]:
            dx += 1

        if tasti[key_jump] and self.y >= self.ground_y:
            self.vely = self.jump_forza

        self.x += dx * self.velocita * dt # Velocità giocatore
        self.x = max(0, self.x)

        self.vely += self.gravita * dt
        self.y += self.vely * dt
        if self.y > self.ground_y:
            self.y = self.ground_y
            self.vely = 0.0

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def insegui(self, bersaglio, dt: float):
        self.x += self.velocita * 0.85 * dt # Velocità nemico
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def disegna(self, schermo, font, camera_offset_x=0.0):
        draw_rect = self.rect.move(-int(camera_offset_x), 0)
        pygame.draw.rect(schermo, self.colore, draw_rect, border_radius=10)
        etichetta = font.render(self.nome, True, Colori.BIANCO)
        etichetta_rect = etichetta.get_rect(center=(draw_rect.centerx, draw_rect.top - 20))
        schermo.blit(etichetta, etichetta_rect)


class Ostacolo:
    """Ostacolo ambientale che cade dallo studio."""

    def __init__(self, tipo: str, camera_offset_x: float, immagini_ostacoli=None):
        self.tipo = tipo
        self.image = None
        self.colore = None
        self.spawn_offset = 40

        if immagini_ostacoli:
            chiave = tipo.lower()
            self.image = immagini_ostacoli.get(chiave)

        if tipo == "RIFLETTORE":
            larghezza, altezza = 200, 200
            if self.image is not None:
                self.image = pygame.transform.smoothscale(self.image, (larghezza, altezza))
            self.colore = None if self.image is not None else Colori.ARANCIO
        elif tipo == "MICROFONO":
            larghezza, altezza = 150, 225
            if self.image is not None:
                self.image = pygame.transform.smoothscale(self.image, (larghezza, altezza))
            self.colore = None if self.image is not None else Colori.GIALLO
        elif tipo == "CAVO":
            larghezza, altezza = 150, 105
            if self.image is not None:
                self.image = pygame.transform.smoothscale(self.image, (larghezza, altezza))
            self.colore = None if self.image is not None else Colori.GRIGIO_CHIARO
        else:
            if self.image is not None:
                larghezza, altezza = self.image.get_size()
            else:
                larghezza, altezza = 100, 14
                self.colore = Colori.GRIGIO_CHIARO

        min_x = int(camera_offset_x + self.spawn_offset)
        max_x = int(camera_offset_x + max(LARGHEZZA_SCHERMO - larghezza - self.spawn_offset, self.spawn_offset))
        if min_x > max_x:
            spawn_x = min_x
        else:
            spawn_x = int(random.randint(min_x, max_x))

        self.rect = pygame.Rect(
            spawn_x,
            -altezza,
            larghezza,
            altezza,
        )
        self.velocita = VELOCITA_CADUTA_RIFLETTORI + random.uniform(0, 2)

    def update(self, dt: float) -> bool:
        self.rect.y += int(self.velocita * 90 * dt)
        return self.rect.top > ALTEZZA_SCHERMO

    def disegna(self, schermo, camera_offset_x=0.0):
        draw_rect = self.rect.move(-int(camera_offset_x), 0)
        if self.image is not None:
            schermo.blit(self.image, draw_rect)
        else:
            pygame.draw.rect(schermo, self.colore, draw_rect, border_radius=6)


class CronometroGlobale:
    """Timer globale per la gestione del tempo di gioco"""

    def __init__(self):
        self.orologio = pygame.time.Clock()
        self.secondi_totali = 0.0
        self.conteggio_frame = 0
        self.conteggio_eventi = 0
        self.ultimo_tempo_evento = 0
        self.in_esecuzione = True

    def avanza(self):
        if self.in_esecuzione:
            tempo_delta = self.orologio.tick(FPS) / 1000.0
            self.secondi_totali += tempo_delta
            self.conteggio_frame += 1
            return tempo_delta
        return 0.0

    def ottieni_secondi_totali(self) -> float:
        return self.secondi_totali

    def ottieni_fps(self) -> float:
        return self.orologio.get_fps()

    def dovrebbe_attivare_evento(self) -> bool:
        tempo_da_ultimo_evento = self.secondi_totali - self.ultimo_tempo_evento
        if tempo_da_ultimo_evento >= INTERVALLO_EVENTO:
            self.ultimo_tempo_evento = self.secondi_totali
            self.conteggio_eventi += 1
            return True
        return False

    def ottieni_conteggio_eventi(self) -> int:
        return self.conteggio_eventi

    def ripristina(self):
        self.secondi_totali = 0.0
        self.conteggio_frame = 0
        self.conteggio_eventi = 0
        self.ultimo_tempo_evento = 0

    def pausa(self):
        self.in_esecuzione = False

    def riprendi(self):
        self.in_esecuzione = True


class Gioco:
    """Classe principale"""

    def __init__(self):
        pygame.init()
        self.schermo = pygame.display.set_mode((LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO))
        pygame.display.set_caption("Breaking Point - Lo Studio TV nel Caos")

        self.font_grande = pygame.font.Font(None, 72)
        self.font_medio = pygame.font.Font(None, 48)
        self.font_piccolo = pygame.font.Font(None, 32)
        self.font_piccolissimo = pygame.font.Font(None, 24)

        self.cronometro = CronometroGlobale()
        self.stato = StatoGioco.MENU
        self.in_esecuzione = True
        self.timer_pubblicita = 0
        self.pubblicita_attiva = False
        self.ostacoli = []
        self.timer_spawn = 0.0
        self.tempo_tra_spawn = 2.0
        self.protagonista = None
        self.nemico = None
        self.camera_offset_x = 0.0
        self.sfondo_studio_primo = None
        self.sfondo_studio_loop = []
        self.sfondo_studio_loop_width = 0

        self.lista_coppie = carica_coppie_personaggi()
        self.indice_coppia_corrente = 0
        self.coppia_scelta = self.lista_coppie[self.indice_coppia_corrente]

        self.modalita_debug = MODALITA_DEBUG
        self.mostra_fps = MOSTRA_FPS

        self.reset_gioco()
        self.sfondo_studio = self.carica_sfondo_studio()
        self.immagini_ostacoli = self.carica_immagini_ostacoli()
    
    def deb_mode(self):
        return self.modalita_debug
    
    def carica_sfondo_studio(self):
        cartella = os.path.join(os.path.dirname(__file__), "assets")
        immagini = []

        try:
            nomi_file = [
                nome for nome in os.listdir(cartella)
                if nome.lower().endswith(".png") and nome.lower().startswith("background")
            ]
        except OSError:
            return None

        def chiave_ordinamento(nome_file: str) -> int:
            base = nome_file.lower()
            if base == "background.png":
                return 0
            match = re.match(r"background(\d+)\.png$", base)
            if match:
                return int(match.group(1))
            return 9999

        nomi_file.sort(key=chiave_ordinamento)

        for nome_file in nomi_file:
            percorso = os.path.join(cartella, nome_file)
            try:
                sfondo = pygame.image.load(percorso).convert()
            except pygame.error:
                continue

            if sfondo.get_height() != ALTEZZA_SCHERMO:
                ratio = ALTEZZA_SCHERMO / sfondo.get_height()
                larghezza = int(sfondo.get_width() * ratio)
                sfondo = pygame.transform.smoothscale(sfondo, (larghezza, ALTEZZA_SCHERMO))

            immagini.append((nome_file.lower(), sfondo))

        if not immagini:
            return None

        prima = None
        ciclo = []
        for nome_file, sfondo in immagini:
            if nome_file == "background.png":
                if prima is None:
                    prima = sfondo
            else:
                ciclo.append(sfondo)

        if prima is None:
            prima = immagini[0][1]

        self.sfondo_studio_primo = prima
        self.sfondo_studio_loop = ciclo
        self.sfondo_studio_loop_width = sum(img.get_width() for img in ciclo)

        return prima

    def carica_immagini_ostacoli(self):
        cartella = os.path.join(os.path.dirname(__file__), "assets", "oggetti")
        immagini = {}
        try:
            nomi_file = [
                nome for nome in os.listdir(cartella)
                if nome.lower().endswith(".png")
            ]
        except OSError:
            return immagini

        for nome_file in nomi_file:
            percorso = os.path.join(cartella, nome_file)
            try:
                immagine = pygame.image.load(percorso).convert_alpha()
            except pygame.error:
                continue
            chiave = os.path.splitext(nome_file)[0].lower()
            immagini[chiave] = immagine

        return immagini

    def reset_gioco(self):
        self.ha_vinto = False
        self.timer_pubblicita = 0
        self.pubblicita_attiva = False
        self.ostacoli.clear()
        self.timer_spawn = 0.0
        self.camera_offset_x = 0.0
        self.protagonista = None
        self.nemico = None

    def gestisci_input(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.in_esecuzione = False

            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.in_esecuzione = False

                if evento.key == pygame.K_RETURN:
                    if self.stato == StatoGioco.MENU:
                        self.inizia_gioco()
                    elif self.stato == StatoGioco.FINE_GIOCO:
                        self.ritorna_a_menu()

                if self.stato == StatoGioco.MENU and evento.key in (pygame.K_RIGHT, pygame.K_DOWN):
                    self.cambia_coppia_selezionata(1)
                elif self.stato == StatoGioco.MENU and evento.key in (pygame.K_LEFT, pygame.K_UP):
                    self.cambia_coppia_selezionata(-1)

                if evento.key == pygame.K_p and self.stato in (StatoGioco.GIOCANDO, StatoGioco.IN_PAUSA):
                    self.attiva_pausa()

                if evento.key == pygame.K_d:
                    self.modalita_debug = not self.modalita_debug

    def aggiorna(self):
        tempo_delta = self.cronometro.avanza()

        if self.stato == StatoGioco.MENU:
            return

        if self.stato == StatoGioco.GIOCANDO:
            if self.cronometro.dovrebbe_attivare_evento():
                self.attiva_evento_casuale()

            self.timer_spawn += tempo_delta
            if self.timer_spawn >= self.tempo_tra_spawn:
                self.timer_spawn = 0.0
                self.ostacoli.append(Ostacolo(
                    random.choice(["RIFLETTORE", "CAVO", "MICROFONO"]),
                    self.camera_offset_x,
                    self.immagini_ostacoli
                ))

            tasti = pygame.key.get_pressed()
            self.protagonista.muovi(tasti, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, tempo_delta)
            self.nemico.insegui(self.protagonista, tempo_delta)

            self.camera_offset_x = max(0.0, self.protagonista.x - LARGHEZZA_SCHERMO * 0.3)

            if self.protagonista.rect.colliderect(self.nemico.rect):
                self.stato = StatoGioco.FINE_GIOCO
                self.cronometro.pausa()
                return

            for ostacolo in self.ostacoli[:]:
                fuori_limite = ostacolo.update(tempo_delta)
                if fuori_limite:
                    self.ostacoli.remove(ostacolo)
                    continue

                if ostacolo.rect.colliderect(self.protagonista.rect):
                    self.stato = StatoGioco.FINE_GIOCO
                    self.cronometro.pausa()
                    return

            if self.pubblicita_attiva:
                self.timer_pubblicita += tempo_delta
                if self.timer_pubblicita >= DURATA_PUBBLICITA:
                    self.pubblicita_attiva = False
                    self.timer_pubblicita = 0

            if self.cronometro.ottieni_secondi_totali() >= TEMPO_PER_VINCERE:
                self.ha_vinto = True
                self.stato = StatoGioco.FINE_GIOCO
                self.cronometro.pausa()
            return

        elif self.stato == StatoGioco.FINE_GIOCO:
            return

    def disegna(self):
        self.schermo.fill(Colori.NERO)

        if self.stato == StatoGioco.MENU:
            self.disegna_menu()
        elif self.stato == StatoGioco.GIOCANDO:
            self.disegna_giocando()
            if self.pubblicita_attiva:
                self.disegna_pubblicita()
        elif self.stato == StatoGioco.FINE_GIOCO:
            self.disegna_fine_gioco()

        if self.mostra_fps and self.modalita_debug:
            self.disegna_fps()

        pygame.display.flip()

    def disegna_menu(self):
        titolo = self.font_grande.render("BREAKING POINT", True, Colori.ROSSO_DIRETTA)
        titolo_rect = titolo.get_rect(center=(LARGHEZZA_SCHERMO // 2, 80))
        self.schermo.blit(titolo, titolo_rect)

        sottotitolo = self.font_medio.render("Seleziona coppia protagonista / nemico", True, Colori.GIALLO)
        sottotitolo_rect = sottotitolo.get_rect(center=(LARGHEZZA_SCHERMO // 2, 160))
        self.schermo.blit(sottotitolo, sottotitolo_rect)

        pygame.draw.rect(self.schermo, Colori.ROSSO_SCURO, (120, 210, 560, 170), border_radius=12)
        pygame.draw.rect(self.schermo, Colori.ROSSO_DIRETTA, (120, 210, 560, 170), 4, border_radius=12)

        coppia = self.lista_coppie[self.indice_coppia_corrente]
        protagonista = self.font_medio.render(f"Protagonista: {coppia.protagonista}", True, Colori.CIANO)
        nemico = self.font_medio.render(f"Nemico: {coppia.nemico}", True, Colori.GIALLO)
        descrizione = self.font_piccolo.render(coppia.descrizione, True, Colori.BIANCO)

        self.schermo.blit(protagonista, (150, 240))
        self.schermo.blit(nemico, (150, 290))
        self.schermo.blit(descrizione, (150, 340))

        selezione = self.font_piccolissimo.render(
            f"Coppia {self.indice_coppia_corrente + 1} / {len(self.lista_coppie)} | Usa frecce per cambiare",
            True, Colori.GRIGIO_CHIARO
        )
        selezione_rect = selezione.get_rect(center=(LARGHEZZA_SCHERMO // 2, 420))
        self.schermo.blit(selezione, selezione_rect)

        istruzione = self.font_piccolo.render("Premi INVIO per iniziare con la coppia selezionata", True, Colori.BIANCO)
        istruzione_rect = istruzione.get_rect(center=(LARGHEZZA_SCHERMO // 2, 470))
        self.schermo.blit(istruzione, istruzione_rect)

        controlli = self.font_piccolissimo.render("< = Sinistra | > = Destra | SPAZIO = Salto | INVIO = Start", True, Colori.GRIGIO_CHIARO)
        controlli_rect = controlli.get_rect(center=(LARGHEZZA_SCHERMO // 2, 530))
        self.schermo.blit(controlli, controlli_rect)

    def disegna_giocando(self):
        self.disegna_sfondo_studio()
        if self.modalita_debug:
            testo_tempo = self.font_piccolo.render(
                f"Tempo: {self.cronometro.ottieni_secondi_totali():.1f}s | Eventi: {self.cronometro.ottieni_conteggio_eventi()}",
                True, Colori.GIALLO
            )
        else:
            testo_tempo = self.font_piccolo.render(
                f"Tempo: {self.cronometro.ottieni_secondi_totali():.1f}s",
                True, Colori.GIALLO
            )
        self.schermo.blit(testo_tempo, (10, 10))

        if self.ostacoli:
            self.disegna_ostacoli()

        if self.protagonista is not None:
            self.protagonista.disegna(self.schermo, self.font_piccolissimo, self.camera_offset_x)
        if self.nemico is not None:
            self.nemico.disegna(self.schermo, self.font_piccolissimo, self.camera_offset_x)

        descrizione = self.font_piccolissimo.render("Freccia → per destra, ← per sinistra, spazio per saltare.", True, Colori.BIANCO)
        self.schermo.blit(descrizione, (20, ALTEZZA_SCHERMO - 40))

    def disegna_ostacoli(self):
        for ostacolo in self.ostacoli:
            ostacolo.disegna(self.schermo, self.camera_offset_x)

    def disegna_sfondo_studio(self):
        if self.sfondo_studio is not None:
            if not self.sfondo_studio_loop:
                max_offset = max(0, self.sfondo_studio.get_width() - LARGHEZZA_SCHERMO)
                src_x = min(int(self.camera_offset_x), max_offset)
                fonte = pygame.Rect(src_x, 0, LARGHEZZA_SCHERMO, ALTEZZA_SCHERMO)
                self.schermo.blit(self.sfondo_studio, (0, 0), fonte)
            else:
                x = int(self.camera_offset_x)
                pos_schermo = 0
                while pos_schermo < LARGHEZZA_SCHERMO:
                    world_x = x + pos_schermo
                    if world_x < self.sfondo_studio_primo.get_width():
                        src_x = world_x
                        src_width = min(self.sfondo_studio_primo.get_width() - src_x, LARGHEZZA_SCHERMO - pos_schermo)
                        fonte = pygame.Rect(src_x, 0, src_width, ALTEZZA_SCHERMO)
                        self.schermo.blit(self.sfondo_studio_primo, (pos_schermo, 0), fonte)
                        pos_schermo += src_width
                    else:
                        if self.sfondo_studio_loop_width == 0:
                            break
                        ciclo_x = (world_x - self.sfondo_studio_primo.get_width()) % self.sfondo_studio_loop_width
                        indice = 0
                        while indice < len(self.sfondo_studio_loop):
                            img = self.sfondo_studio_loop[indice]
                            if ciclo_x < img.get_width():
                                break
                            ciclo_x -= img.get_width()
                            indice += 1
                        if indice == len(self.sfondo_studio_loop):
                            indice = 0
                            ciclo_x = 0
                        img = self.sfondo_studio_loop[indice]
                        src_width = min(img.get_width() - ciclo_x, LARGHEZZA_SCHERMO - pos_schermo)
                        fonte = pygame.Rect(ciclo_x, 0, src_width, ALTEZZA_SCHERMO)
                        self.schermo.blit(img, (pos_schermo, 0), fonte)
                        pos_schermo += src_width
        else:
            start_x = int(self.camera_offset_x // 100 * 100) - 100
            end_x = int(self.camera_offset_x + LARGHEZZA_SCHERMO + 100)
            for x in range(start_x, end_x, 100):
                screen_x = x - int(self.camera_offset_x)
                pygame.draw.line(self.schermo, Colori.GRIGIO, (screen_x, 0), (screen_x, ALTEZZA_SCHERMO), 1)
            for y in range(0, ALTEZZA_SCHERMO, 100):
                pygame.draw.line(self.schermo, Colori.GRIGIO, (0, y), (LARGHEZZA_SCHERMO, y), 1)

        terra_y = ALTEZZA_SCHERMO - 70
        pygame.draw.line(self.schermo, Colori.GRIGIO_CHIARO, (0, terra_y), (LARGHEZZA_SCHERMO, terra_y), 4)

        if int(self.cronometro.ottieni_secondi_totali()) % 2 == 0:
            testo_diretta = self.font_medio.render("DIRETTA", True, Colori.ROSSO_DIRETTA)
            diretta_rect = testo_diretta.get_rect(topright=(LARGHEZZA_SCHERMO - 20, 20))
            self.schermo.blit(testo_diretta, diretta_rect)

    def disegna_pubblicita(self):
        banner = pygame.Surface((LARGHEZZA_SCHERMO, 140), pygame.SRCALPHA)
        banner.fill((0, 0, 0, 180))
        self.schermo.blit(banner, (0, ALTEZZA_SCHERMO // 2 - 70))

        testo_pubblicita = self.font_grande.render("PUBBLICITA' IN DIRETTA", True, Colori.ROSSO_DIRETTA)
        rect_pubblicita = testo_pubblicita.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2 - 30))
        self.schermo.blit(testo_pubblicita, rect_pubblicita)

        rimanente = max(0.0, DURATA_PUBBLICITA - self.timer_pubblicita)
        testo_timer = self.font_medio.render(f"Torna in onda tra {rimanente:.1f}s", True, Colori.GIALLO)
        rect_timer = testo_timer.get_rect(center=(LARGHEZZA_SCHERMO // 2, ALTEZZA_SCHERMO // 2 + 30))
        self.schermo.blit(testo_timer, rect_timer)

    def disegna_fine_gioco(self):

        titolo_testo = "HAI VINTO!" if self.ha_vinto else "GAME OVER"
        colore = Colori.VERDE if self.ha_vinto else Colori.ROSSO_DIRETTA

        titolo = self.font_grande.render(titolo_testo, True, colore)
        titolo_rect = titolo.get_rect(center=(LARGHEZZA_SCHERMO // 2, 150))
        self.schermo.blit(titolo, titolo_rect)

        testo_tempo = self.font_medio.render(
            f"Tempo raggiunto: {self.cronometro.ottieni_secondi_totali():.1f}s",
            True,
            Colori.GIALLO
        )

        tempo_rect = testo_tempo.get_rect(center=(LARGHEZZA_SCHERMO // 2, 300))
        self.schermo.blit(testo_tempo, tempo_rect)

        istruzione = self.font_piccolo.render(
            "Premi INVIO per tornare al menu",
            True,
            Colori.BIANCO
        )

        istruzione_rect = istruzione.get_rect(center=(LARGHEZZA_SCHERMO // 2, 450))
        self.schermo.blit(istruzione, istruzione_rect)

    def disegna_fps(self):
        testo_fps = self.font_piccolissimo.render(f"FPS: {self.cronometro.ottieni_fps():.0f}", True, Colori.VERDE)
        fps_rect = testo_fps.get_rect(bottomright=(LARGHEZZA_SCHERMO - 10, ALTEZZA_SCHERMO - 10))
        self.schermo.blit(testo_fps, fps_rect)

    def inizia_gioco(self):
        self.coppia_scelta = self.lista_coppie[self.indice_coppia_corrente]
        self.stato = StatoGioco.GIOCANDO
        self.reset_gioco()
        self.cronometro.ripristina()
        self.cronometro.riprendi()
        y_terra = ALTEZZA_SCHERMO - 120
        self.protagonista = Giocatore(120, y_terra, Colori.CIANO, self.coppia_scelta.protagonista)
        self.nemico = Giocatore(-120, y_terra, Colori.ROSSO_DIRETTA, self.coppia_scelta.nemico)

    def ritorna_a_menu(self):
        self.stato = StatoGioco.MENU
        self.cronometro.ripristina()
        self.reset_gioco()

    def attiva_pausa(self):
        if self.stato == StatoGioco.GIOCANDO:
            self.stato = StatoGioco.IN_PAUSA
            self.cronometro.pausa()
        elif self.stato == StatoGioco.IN_PAUSA:
            self.stato = StatoGioco.GIOCANDO
            self.cronometro.riprendi()

    def attiva_evento_casuale(self):
        if not self.pubblicita_attiva:
            self.pubblicita_attiva = True
            self.timer_pubblicita = 0

    def cambia_coppia_selezionata(self, direzione: int):
        self.indice_coppia_corrente = (self.indice_coppia_corrente + direzione) % len(self.lista_coppie)
        self.coppia_scelta = self.lista_coppie[self.indice_coppia_corrente]

    def esegui(self):
        while self.in_esecuzione:
            self.gestisci_input()
            self.aggiorna()
            self.disegna()

        pygame.quit()
        sys.exit()


def principale():
    print("=" * 50)
    print("Breaking Point - Lo Studio TV nel Caos")
    print("=" * 50)
    print()
    print("Inizializzazione del gioco...")

    gioco = Gioco()
    
    if gioco.deb_mode():
        print("[OK] Gioco inizializzato correttamente")
        print()
        print("Comandi:")
        print("  SPACE  - Inizia il gioco / Ritorna al menu")
        print("  ESC    - Esci dal gioco")
        print("  P      - Pausa/Riprendi (durante il gioco)")
        print("  D      - Attiva/Disattiva modalità debug")
        print()
    print("Buon divertimento!")
    print("=" * 50)
    print()

    gioco.esegui()


if __name__ == "__main__":
    principale()
