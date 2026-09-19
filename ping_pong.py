import pygame, sys, json, os

pygame.init()

#Musica de fondo
pygame.mixer.init()

fire_sound = pygame.mixer.Sound('hit.ogg')
sonido_fondo = pygame.mixer.Sound('fallen_down.ogg')
musica_juego = pygame.mixer.Sound('hope_and_dream.ogg')

sonido_fondo.set_volume(0.2)
musica_juego.set_volume(0.2)
sonido_fondo.play(-1)


class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        
        if self.image is None:
            self.image = self.text
            
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False

    def changeColor(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

# --- AJUSTES VENTANA ---
ventana_ancho = 1280
ventana_alto = 720
pygame.display.set_caption("Ping Pong")
SCREEN = pygame.display.set_mode((ventana_ancho, ventana_alto))

BG = pygame.image.load("Background.png")
BG = pygame.transform.scale(BG, (ventana_ancho, ventana_alto))

def get_font(size):
    return pygame.font.Font("font.ttf", size)

# --- ASSETS ---
img_Players = "racket.png"
img_ball = "tenis_ball.png"
img_fondo = "Fondo.png"

font1 = pygame.font.Font(None, 80)
font2 = pygame.font.Font(None, 35)

P1_Win = font1.render('PLAYER 1 WIN', True, (0, 0, 0))
P2_Win = font1.render('PLAYER 2 WIN', True, (0, 0, 0))

bg_color = (47, 222, 184)
color_texto = (0, 0, 0)

Fondo_Juego = pygame.transform.scale(pygame.image.load(img_fondo), (ventana_ancho, ventana_alto))

# --- GESTIÓN DE PUNTAJES ---
SCORES_FILE = "scores.json"

def load_scores():
    if not os.path.exists(SCORES_FILE):
        return []
    try:
        with open(SCORES_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_score(name, score):
    if not name.strip():
        name = "Jugador"
    scores = load_scores()
    scores.append({"name": name, "score": score})
    # Ordenar de mayor a menor y guardar solo los 8 mejores
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:8]
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f)

# --- CLASES Y ESTRUCTURAS ---
class GameSprite(pygame.sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update_r(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[pygame.K_s] and self.rect.y < ventana_alto - 180:
            self.rect.y += self.speed

    def update_l(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.y < ventana_alto - 180:
            self.rect.y += self.speed

class Ball(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, speed_x, speed_y):
        super().__init__(player_image, player_x, player_y, size_x, size_y, 0)
        self.speed_x = speed_x
        self.speed_y = speed_y
        
        self.original_speed_x = speed_x
        self.original_speed_y = speed_y

    def update(self): 
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.y <= 0 or self.rect.y >= ventana_alto - self.rect.height:
            self.speed_y *= -1

    def increase_speed(self):
        incremento = 1
        if self.speed_x > 0:
            self.speed_x += incremento
        else:
            self.speed_x -= incremento

        if self.speed_y > 0:
            self.speed_y += incremento
        else:
            self.speed_y -= incremento
            
        max_speed = 25
        if abs(self.speed_x) > max_speed:
            self.speed_x = max_speed if self.speed_x > 0 else -max_speed
        if abs(self.speed_y) > max_speed:
            self.speed_y = max_speed if self.speed_y > 0 else -max_speed

    def reset_position(self):
        self.rect.x = ventana_ancho // 2 - 20
        self.rect.y = ventana_alto // 2 - 20
        
        self.speed_x = self.original_speed_x
        self.speed_y = self.original_speed_y
        
        self.speed_x *= -1

# --- ELEMENTOS DEL JUEGO ---

def pause():
    fondo_pausa = SCREEN.copy()
    capa_oscura = pygame.Surface((ventana_ancho, ventana_alto))
    capa_oscura.set_alpha(150)
    capa_oscura.fill((0, 0, 0))
    fondo_pausa.blit(capa_oscura, (0, 0))

    pausado = True
    while pausado:
        SCREEN.blit(fondo_pausa, (0, 0))
        MOUSE_POS = pygame.mouse.get_pos()

        TEXTO_PAUSA = get_font(80).render("PAUSE", True, "#b68f40")
        RECT_PAUSA = TEXTO_PAUSA.get_rect(center=(ventana_ancho // 2, 150))
        SCREEN.blit(TEXTO_PAUSA, RECT_PAUSA)

        BTN_CONTINUAR = Button(image=None, pos=(ventana_ancho // 2, 350), 
                            text_input="CONTINUE", font=get_font(60), base_color="#8a8a8a", hovering_color="White")
        BTN_MENU = Button(image=None, pos=(ventana_ancho // 2, 500), 
                            text_input="EXIT TO MENU", font=get_font(60), base_color="#8a8a8a", hovering_color="White")

        for boton in [BTN_CONTINUAR, BTN_MENU]:
            boton.changeColor(MOUSE_POS)
            boton.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    return True 
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BTN_CONTINUAR.checkForInput(MOUSE_POS):
                    return True 
                if BTN_MENU.checkForInput(MOUSE_POS):
                    return False 

        pygame.display.update()

def input_name_screen(score):
    fondo_pausa = SCREEN.copy()
    capa_oscura = pygame.Surface((ventana_ancho, ventana_alto))
    capa_oscura.set_alpha(200)
    capa_oscura.fill((0, 0, 0))
    fondo_pausa.blit(capa_oscura, (0, 0))

    name = ""
    ingresando = True

    while ingresando:
        SCREEN.blit(fondo_pausa, (0, 0))
        
        titulo = get_font(50).render(f"GAME OVER - SCORE: {score}", True, "White")
        instruccion = font2.render("Type your name and press ENTER to save.", True, (200, 200, 200))
        instruccion2 = font2.render("Press ESC to exit without saving.", True, (150, 150, 150))
        
        nombre_surface = get_font(70).render(name + "_", True, "#b68f40")

        SCREEN.blit(titulo, titulo.get_rect(center=(ventana_ancho//2, 150)))
        SCREEN.blit(instruccion, instruccion.get_rect(center=(ventana_ancho//2, 250)))
        SCREEN.blit(instruccion2, instruccion2.get_rect(center=(ventana_ancho//2, 300)))
        SCREEN.blit(nombre_surface, nombre_surface.get_rect(center=(ventana_ancho//2, 450)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    save_score(name, score)
                    return 
                elif event.key == pygame.K_ESCAPE:
                    return 
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    # Limitar tamaño del nombre y asegurar que sea un carácter imprimible
                    if len(name) < 12 and event.unicode.isprintable():
                        name += event.unicode
                        
        pygame.display.update()

def scoreboard_screen():
    while True:
        SCREEN.blit(BG, (0, 0))
        MOUSE_POS = pygame.mouse.get_pos()

        TITULO = get_font(60).render("TOP SCORES", True, "#b68f40")
        SCREEN.blit(TITULO, TITULO.get_rect(center=(ventana_ancho//2, 100)))

        scores = load_scores()
        y_offset = 220
        
        if not scores:
            txt = get_font(20).render("There are no saved scores yet.", True, "White")
            SCREEN.blit(txt, txt.get_rect(center=(ventana_ancho//2, y_offset)))
        else:
            for i, s in enumerate(scores):
                texto = f"{i+1}. {s['name']} - {s['score']} streak"
                txt_surface = get_font(20).render(texto, True, "White")
                SCREEN.blit(txt_surface, txt_surface.get_rect(center=(ventana_ancho//2, y_offset)))
                y_offset += 45
                
        BTN_VOLVER = Button(image=None, pos=(ventana_ancho//2, ventana_alto - 80), 
                            text_input="BACK", font=get_font(50), base_color="#8a8a8a", hovering_color="White")
        
        BTN_VOLVER.changeColor(MOUSE_POS)
        BTN_VOLVER.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BTN_VOLVER.checkForInput(MOUSE_POS):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                    
        pygame.display.update()

def play():
    sonido_fondo.stop()
    musica_juego.play(-1)
    
    P1 = Player(img_Players, 40 , ventana_alto // 2 - 90, 50, 180, 10)
    P2 = Player(img_Players, ventana_ancho - 100, ventana_alto // 2 - 90, 50, 180, 10)
    tenis_ball = Ball(img_ball, ventana_ancho // 2 - 20, ventana_alto // 2 - 20, 50, 50, 7, 7)

    score_p1 = 0
    score_p2 = 0
    rebotes = 0
    max_puntos = 10

    x = 0
    clock = pygame.time.Clock()
    finish = False
    playing = True
    winner_text = None

    while playing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not finish:
                        if not pause(): 
                            playing = False
                    else:
                        playing = False
                elif finish and event.key == pygame.K_m:
                    playing = False 

        if not finish:
            x -= 5
            P1.update_r()
            P2.update_l()
            tenis_ball.update()

            if pygame.sprite.collide_rect(P1, tenis_ball):
                tenis_ball.rect.left = P1.rect.right
                tenis_ball.speed_x *= -1
                tenis_ball.increase_speed()
                rebotes += 1
                fire_sound.play()

            if pygame.sprite.collide_rect(P2, tenis_ball):
                tenis_ball.rect.right = P2.rect.left
                tenis_ball.speed_x *= -1
                tenis_ball.increase_speed()
                rebotes += 1
                fire_sound.play()

            if tenis_ball.rect.x < 0:
                score_p2 += 1
                rebotes = 0
                tenis_ball.reset_position()
                if score_p2 >= max_puntos:
                    finish = True
                    winner_text = P2_Win

            if tenis_ball.rect.x > ventana_ancho - tenis_ball.rect.width:
                score_p1 += 1
                rebotes = 0
                tenis_ball.reset_position()
                if score_p1 >= max_puntos:
                    finish = True
                    winner_text = P1_Win

        x_relativa = x % Fondo_Juego.get_rect().width
        SCREEN.blit(Fondo_Juego, (x_relativa - Fondo_Juego.get_rect().width, 0))
        if x_relativa < ventana_ancho:
            SCREEN.blit(Fondo_Juego, (x_relativa, 0))

        P1.reset()
        P2.reset()
        tenis_ball.reset()

        texto_marcador = font2.render(f"P1: {score_p1}  |  P2: {score_p2}", True, color_texto)
        texto_rebotes = font2.render(f"Streak: {rebotes}", True, color_texto)
        SCREEN.blit(texto_marcador, (ventana_ancho // 2 - 80, 20))
        SCREEN.blit(texto_rebotes, (ventana_ancho // 2 - 50, 50))

        if finish and winner_text:
            SCREEN.blit(winner_text, (ventana_ancho // 2 - 200, ventana_alto // 2 - 50))
            msg_salida = font2.render("Press ESC to pause", True, color_texto)
            SCREEN.blit(msg_salida, (ventana_ancho // 2 - 220, ventana_alto // 2 + 30))

        pygame.display.update()
        clock.tick(60)

    musica_juego.stop()

def Practice_mode():
    sonido_fondo.stop()
    musica_juego.play(-1)

    P1 = Player(img_Players, 40 , ventana_alto // 2 - 90, 50, 180, 10)
    Muro = GameSprite(img_Players, ventana_ancho - 50, 0, 100, ventana_alto + 60, 0)
    tenis_ball = Ball(img_ball, ventana_ancho // 2 - 20, ventana_alto // 2 - 20, 50, 50, 7, 7)

    rebotes = 0
    x = 0
    clock = pygame.time.Clock()
    playing = True 

    while playing:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if not pause():
                        playing = False

        if playing:
            x -= 5
            P1.update_r()
            tenis_ball.update()

            if pygame.sprite.collide_rect(P1, tenis_ball):
                tenis_ball.rect.left = P1.rect.right
                tenis_ball.speed_x *= -1
                tenis_ball.increase_speed() 
                rebotes += 1                
                fire_sound.play()

            if pygame.sprite.collide_rect(Muro, tenis_ball):
                tenis_ball.rect.right = Muro.rect.left
                tenis_ball.speed_x *= -1
                fire_sound.play()

            # SI EL JUGADOR FALLA (PIERDE EN PRÁCTICA)
            if tenis_ball.rect.x < 0:
                # Lanzamos la pantalla para guardar el puntaje
                input_name_screen(rebotes)
                # Al terminar de escribir, salimos directamente al menú
                playing = False

            # Renderizado
            x_relativa = x % Fondo_Juego.get_rect().width
            SCREEN.blit(Fondo_Juego, (x_relativa - Fondo_Juego.get_rect().width, 0))
            if x_relativa < ventana_ancho:
                SCREEN.blit(Fondo_Juego, (x_relativa, 0))

            if playing: # Solo redibujamos si no hemos perdido esta misma iteración
                P1.reset()
                Muro.reset()
                tenis_ball.reset()

                texto_rebotes = font2.render(f"Streak: {rebotes}", True, color_texto)
                msg_salida = font2.render("Press ESC to pause", True, color_texto)
                
                SCREEN.blit(texto_rebotes, (ventana_ancho // 2 - 100, 20))
                SCREEN.blit(msg_salida, (20, 20))

        pygame.display.update() 
        clock.tick(60)
        
    musica_juego.stop()

def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        # CREAMOS EL TÍTULO
        MENU_TEXT = get_font(90).render("Ping Pong", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(ventana_ancho // 2, 120))
        
        # ¡AQUÍ ESTABA EL ERROR! Faltaba esta línea para dibujar el título en pantalla
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        # BOTONES REORGANIZADOS (ajusté un poco el tamaño de fuente y la altura)
        PLAY_BUTTON = Button(image=None, pos=(ventana_ancho // 2, 280), 
                            text_input="Multiplayer", font=get_font(55), base_color="#8a8a8a", hovering_color="White")
        PRACTICE_BUTTON = Button(image=None, pos=(ventana_ancho // 2, 390), 
                            text_input="Practice mode", font=get_font(55), base_color="#8a8a8a", hovering_color="White")
        SCORES_BUTTON = Button(image=None, pos=(ventana_ancho // 2, 500), 
                            text_input="Score list", font=get_font(55), base_color="#8a8a8a", hovering_color="White")
        QUIT_BUTTON = Button(image=None, pos=(ventana_ancho // 2, 610), 
                            text_input="Exit", font=get_font(55), base_color="#8a8a8a", hovering_color="White")

        # Dibujar y actualizar los botones
        for button in [PLAY_BUTTON, PRACTICE_BUTTON, SCORES_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                    sonido_fondo.play(-1) 
                if PRACTICE_BUTTON.checkForInput(MENU_MOUSE_POS):
                    Practice_mode()
                    sonido_fondo.play(-1) 
                if SCORES_BUTTON.checkForInput(MENU_MOUSE_POS):
                    scoreboard_screen()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()
