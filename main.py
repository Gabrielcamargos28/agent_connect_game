import numpy as np
import pygame
import sys
import math
import random
import time

# Configurações gerais do Conecta 4
ROWS = 6
COLUMNS = 7
PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4

# Cores para a interface gráfica
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

SQUARESIZE = 100
width = COLUMNS * SQUARESIZE
height = (ROWS + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)


# Crie a janela
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Connect 4")

# Inicializa o Pygame
pygame.init()
font = pygame.font.SysFont("monospace", 75)
small_font = pygame.font.SysFont("monospace", 30)

# Funções de jogo
def create_board():
    return np.zeros((ROWS, COLUMNS))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROWS - 1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROWS):
        if board[r][col] == 0:
            return r

def print_board(board):
    print(np.flip(board, 0))

def winning_move(board, piece):
    # Verificar todas as possíveis sequências de 4 em linha
    for c in range(COLUMNS - 3):
        for r in range(ROWS):
            if all([board[r][c + i] == piece for i in range(WINDOW_LENGTH)]):
                return [(r, c + i) for i in range(WINDOW_LENGTH)]  # Retorna as posições vencedoras
    for c in range(COLUMNS):
        for r in range(ROWS - 3):
            if all([board[r + i][c] == piece for i in range(WINDOW_LENGTH)]):
                return [(r + i, c) for i in range(WINDOW_LENGTH)]  # Retorna as posições vencedoras
    for c in range(COLUMNS - 3):
        for r in range(ROWS - 3):
            if all([board[r + i][c + i] == piece for i in range(WINDOW_LENGTH)]):
                return [(r + i, c + i) for i in range(WINDOW_LENGTH)]  # Retorna as posições vencedoras
    for c in range(COLUMNS - 3):
        for r in range(3, ROWS):
            if all([board[r - i][c + i] == piece for i in range(WINDOW_LENGTH)]):
                return [(r - i, c + i) for i in range(WINDOW_LENGTH)]  # Retorna as posições vencedoras
    return None

def draw_board(board, winning_positions=None):
    for c in range(COLUMNS):
        for r in range(ROWS):
            pygame.draw.rect(screen, BLUE, (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c * SQUARESIZE + SQUARESIZE / 2), int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    for c in range(COLUMNS):
        for r in range(ROWS):
            if board[r][c] == PLAYER_PIECE:
                pygame.draw.circle(screen, RED, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)
            elif board[r][c] == AI_PIECE:
                pygame.draw.circle(screen, YELLOW, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    # Desenha a linha vencedora em verde
    if winning_positions:
        for r, c in winning_positions:
            pygame.draw.circle(screen, (0, 255, 0), (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    pygame.display.update()

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMNS):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def display_winner(winner_text):
    label = font.render(winner_text, 1, (255, 255, 255))  # Cor branca para o texto
    screen.blit(label, (width // 2 - label.get_width() // 2, height // 2 - label.get_height() // 2))
    pygame.display.update()
    
    # Pausar até o jogador clicar ou pressionar uma tecla
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False  # Termina a pausa quando o usuário clica
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # Permite sair com a tecla ESC
                    pygame.quit()
                    sys.exit()
                waiting = False  # Termina a pausa quando o usuário pressiona qualquer tecla
        pygame.display.update()

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def score_position(board, piece):
    score = 0
    for row in range(ROWS):
        for col in range(COLUMNS):
            if board[row][col] == piece:
                score += 1
    return score

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def choose_algorithm_input():
    font = pygame.font.SysFont("monospace", 30)
    text = "Escolha o Algoritmo (1: Minimax, 2: Poda Alfa-Beta)"
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, (width // 2 - label.get_width() // 2, height // 2 - 100))

    button_minimax = pygame.Rect(width // 2 - 150, height // 2 + 50, 100, 50)
    button_alpha_beta = pygame.Rect(width // 2 + 50, height // 2 + 50, 100, 50)

    pygame.draw.rect(screen, pygame.Color('dodgerblue2'), button_minimax)
    pygame.draw.rect(screen, pygame.Color('dodgerblue2'), button_alpha_beta)

    text_minimax = font.render("Minimax", True, (255, 255, 255))
    text_alpha_beta = font.render("Poda Alfa-Beta", True, (255, 255, 255))

    screen.blit(text_minimax, (button_minimax.x + 10, button_minimax.y + 10))
    screen.blit(text_alpha_beta, (button_alpha_beta.x + 10, button_alpha_beta.y + 10))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_minimax.collidepoint(event.pos):
                    return 'minimax'
                elif button_alpha_beta.collidepoint(event.pos):
                    return 'alpha-beta'

# Passando width e height como parâmetros para a função get_depth_input
def get_depth_input(width, height):
    input_box = pygame.Rect(width // 2 - 100, height // 2 - 50, 200, 40)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    font = pygame.font.Font(None, 32)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return int(text)  # Retorna a profundidade definida pelo jogador
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode
        
        # Desenhando o fundo da tela e o menu
        screen.fill(BLACK)  # Altere para a cor que deseja no fundo
        pygame.draw.rect(screen, BLUE, (0, 0, width, SQUARESIZE))  # Mantém a parte superior com a barra de menu
        pygame.draw.rect(screen, color, input_box, 2)  # Desenha a caixa de entrada

        # Atualiza a tela com o texto
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.display.flip()

def play_game():
    board = create_board()
    game_over = False
    turn = PLAYER
    algorithm = choose_algorithm_input()
    
    # Passando width e height para get_depth_input
    ply = get_depth_input(width, height)
    
    while not game_over:
        draw_board(board)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                if turn == PLAYER:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)
                    if winning_move(board, PLAYER_PIECE):
                        display_winner("PLAYER WINS!!")
                        game_over = True
                    turn = AI
                    break

        if turn == AI and not game_over:
            if algorithm == 'minimax':
                col, minimax_score = minimax(board, ply, -math.inf, math.inf, True)
            elif algorithm == 'alpha-beta':
                col, minimax_score = minimax(board, ply, -math.inf, math.inf, True)
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)
                if winning_move(board, AI_PIECE):
                    display_winner("AI WINS!!")
                    game_over = True
                turn = PLAYER

if __name__ == '__main__':
    play_game()
    pygame.quit()
