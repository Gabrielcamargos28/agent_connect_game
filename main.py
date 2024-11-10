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

SQUARESIZE = 100
width = COLUMNS * SQUARESIZE
height = (ROWS + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)

# Inicializa o Pygame
pygame.init()
font = pygame.font.SysFont("monospace", 75)

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
                return True
    for c in range(COLUMNS):
        for r in range(ROWS - 3):
            if all([board[r + i][c] == piece for i in range(WINDOW_LENGTH)]):
                return True
    for c in range(COLUMNS - 3):
        for r in range(ROWS - 3):
            if all([board[r + i][c + i] == piece for i in range(WINDOW_LENGTH)]):
                return True
    for c in range(COLUMNS - 3):
        for r in range(3, ROWS):
            if all([board[r - i][c + i] == piece for i in range(WINDOW_LENGTH)]):
                return True
    return False

def draw_board(board):
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
    pygame.display.update()

# Configuração inicial
board = create_board()
game_over = False
turn = random.randint(PLAYER, AI)
screen = pygame.display.set_mode(size)
draw_board(board)

# Funções Minimax e Poda Alfa-Beta adaptadas para a jogabilidade
def minimax(board, depth, maximizingPlayer):
    valid_locations = [c for c in range(COLUMNS) if is_valid_location(board, c)]
    is_terminal = winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(valid_locations) == 0
    if depth == 0 or is_terminal:
        return (None, random.randint(-10, 10))  # Função de avaliação simulada

    if maximizingPlayer:
        value = -math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
        return best_col, value
    else:
        value = math.inf
        best_col = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
        return best_col, value

# Função para obter profundidade da busca (ply)
def get_depth():
    while True:
        try:
            depth = int(input("Digite a profundidade da busca (ply) (1-4): "))
            if depth < 1 or depth > 4:
                print("Por favor, digite um valor entre 1 e 4.")
            else:
                return depth
        except ValueError:
            print("Entrada inválida! Por favor, insira um número.")

# Loop principal do jogo
ply = get_depth()  # Obter profundidade definida pelo jogador


def display_winner(winner_text):
    label = font.render(winner_text, 1, (255, 255, 255))  # Cor branca para o texto
    screen.blit(label, (width // 2 - label.get_width() // 2, height // 2 - label.get_height() // 2))
    pygame.display.update()

# Loop principal do jogo
ply = get_depth()  # Obter profundidade definida pelo jogador


while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE / 2)), RADIUS)

        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            if turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)
                    if winning_move(board, PLAYER_PIECE):
                        print("PLAYER 1 WINS!")
                        game_over = True

                    turn = AI
                    print_board(board)
                    draw_board(board)

    if turn == AI and not game_over:
        col, minimax_score = minimax(board, ply, True)  # Usando o valor de profundidade definido pelo jogador

        if is_valid_location(board, col):
            pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)
            if winning_move(board, AI_PIECE):
                print("PLAYER 2 WINS!")
                game_over = True

            print_board(board)
            draw_board(board)
            turn = PLAYER

    if game_over:
        pygame.time.wait(3000)
