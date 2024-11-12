import numpy as np
import pygame
import sys
import math
import random

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
GREEN = (0, 255, 0)

SQUARESIZE = 100
width = COLUMNS * SQUARESIZE
height = (ROWS + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)

# Inicializa o Pygame
pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Connect 4")
font = pygame.font.SysFont("monospace", 75)
small_font = pygame.font.SysFont("monospace", 30)

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

def winning_move(board, piece):
    for c in range(COLUMNS - 3):
        for r in range(ROWS):
            if all([board[r][c + i] == piece for i in range(WINDOW_LENGTH)]):
                return [(r, c + i) for i in range(WINDOW_LENGTH)]
    for c in range(COLUMNS):
        for r in range(ROWS - 3):
            if all([board[r + i][c] == piece for i in range(WINDOW_LENGTH)]):
                return [(r + i, c) for i in range(WINDOW_LENGTH)]
    for c in range(COLUMNS - 3):
        for r in range(ROWS - 3):
            if all([board[r + i][c + i] == piece for i in range(WINDOW_LENGTH)]):
                return [(r + i, c + i) for i in range(WINDOW_LENGTH)]
    for c in range(COLUMNS - 3):
        for r in range(3, ROWS):
            if all([board[r - i][c + i] == piece for i in range(WINDOW_LENGTH)]):
                return [(r - i, c + i) for i in range(WINDOW_LENGTH)]
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

    if winning_positions:
        for r, c in winning_positions:
            pygame.draw.circle(screen, GREEN, (int(c * SQUARESIZE + SQUARESIZE / 2), height - int(r * SQUARESIZE + SQUARESIZE / 2)), RADIUS)

    pygame.display.update()

def display_winner(winner_text):
    label = font.render(winner_text, 1, (255, 255, 255))
    screen.blit(label, (width // 2 - label.get_width() // 2, height // 2 - label.get_height() // 2))
    pygame.display.update()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type in {pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN}:
                waiting = False
        pygame.display.update()

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def get_valid_locations(board):
    return [col for col in range(COLUMNS) if is_valid_location(board, col)]

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 1e14)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -1e14)
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

def play_game():
    board = create_board()
    game_over = False
    turn = PLAYER
    draw_board(board)

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION and turn == PLAYER:
                pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
                posx = event.pos[0]
                pygame.draw.circle(screen, RED, (posx, SQUARESIZE // 2), RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN and turn == PLAYER:
                posx = event.pos[0]
                col = int(math.floor(posx / SQUARESIZE))
                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)
                    if winning_move(board, PLAYER_PIECE):
                        draw_board(board, winning_move(board, PLAYER_PIECE))
                        display_winner("Player Wins!")
                        game_over = True
                    turn = AI
                    draw_board(board)

        if turn == AI and not game_over:
            col, _ = minimax(board, 5, -math.inf, math.inf, True)
            if col is not None and is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)
                if winning_move(board, AI_PIECE):
                    draw_board(board, winning_move(board, AI_PIECE))
                    display_winner("AI Wins!")
                    game_over = True
                turn = PLAYER
                draw_board(board)

if __name__ == "__main__":
    play_game()
