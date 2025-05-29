import pygame
import random
import sys
from copy import deepcopy
import math
from heapq import heappush, heappop

# Initialize PyGame
pygame.init()

# Window configuration
WIDTH = 600
HEIGHT = 650
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("8-Puzzle with A* (Manhattan)")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (50, 150, 255)
DARK_BLUE = (30, 100, 200)
FONT = pygame.font.SysFont("Arial", 40)
SMALL_FONT = pygame.font.SysFont("Arial", 25)

# Goal state
GOAL_STATE = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8]
]

def generate_random_state():
    """Generate a random solvable initial state"""
    state = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    random.shuffle(state)
    inversions = 0
    for i in range(9):
        for j in range(i + 1, 9):
            if state[i] != 0 and state[j] != 0 and state[i] > state[j]:
                inversions += 1
    
    if inversions % 2 != 0:
        found_swap = False
        for i_s in range(8):
            for j_s in range(i_s + 1, 9):
                if state[i_s] != 0 and state[j_s] != 0:
                    state[i_s], state[j_s] = state[j_s], state[i_s]
                    found_swap = True
                    break
            if found_swap:
                break
        if not found_swap:
            state[0], state[1] = state[1], state[0]
            
    return [state[i:i+3] for i in range(0, 9, 3)]

def find_empty(board):
    """Find position of empty tile (0)"""
    for i in range(3):
        for j in range(3):
            if board[i][j] == 0:
                return (i, j)
    return None

def generate_moves(board):
    """Generate all valid moves"""
    moves = []
    i, j = find_empty(board)
    for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Up, Down, Left, Right
        ni, nj = i + di, j + dj
        if 0 <= ni < 3 and 0 <= nj < 3:
            new_board = deepcopy(board)
            new_board[i][j], new_board[ni][nj] = new_board[ni][nj], new_board[i][j]
            moves.append(new_board)
    return moves

def manhattan_distance(board):
    """Calculate Manhattan distance heuristic"""
    distance = 0
    for i in range(3):
        for j in range(3):
            if board[i][j] != 0:
                goal_row = board[i][j] // 3
                goal_col = board[i][j] % 3
                distance += abs(i - goal_row) + abs(j - goal_col)
    return distance

def a_star_search(initial_board):
    """A* search algorithm with Manhattan distance heuristic"""
    open_set = []
    # Each element is (f_score, g_score, board, path)
    heappush(open_set, (manhattan_distance(initial_board), 0, initial_board, [initial_board]))
    
    closed_set = set()
    
    while open_set:
        _, g, current_board, path = heappop(open_set)
        
        if current_board == GOAL_STATE:
            return path
        
        board_tuple = tuple(tuple(row) for row in current_board)
        if board_tuple in closed_set:
            continue
            
        closed_set.add(board_tuple)
        
        for move in generate_moves(current_board):
            move_tuple = tuple(tuple(row) for row in move)
            if move_tuple not in closed_set:
                new_g = g + 1
                new_f = new_g + manhattan_distance(move)
                heappush(open_set, (new_f, new_g, move, path + [move]))
    
    return None  # No solution found (shouldn't happen for solvable puzzles)

def solve_puzzle(board):
    """Solve using A* with Manhattan distance"""
    return a_star_search(board)

def draw_board(board, solving_in_progress, current_step=0, solution=None):
    """Draw the puzzle board and animation"""
    WINDOW.fill(WHITE)
    pygame.draw.rect(WINDOW, GRAY, (50, 100, 500, 500))
    for i in range(3):
        for j in range(3):
            if board[i][j] != 0:
                pygame.draw.rect(WINDOW, BLUE, (50 + j * 166, 100 + i * 166, 166, 166))
                number = FONT.render(str(board[i][j]), True, WHITE)
                text_rect = number.get_rect(center=(50 + j * 166 + 166 // 2, 100 + i * 166 + 166 // 2))
                WINDOW.blit(number, text_rect)

    # Solve button
    pygame.draw.rect(WINDOW, BLACK, (50, 30, 200, 50))
    solve_text = FONT.render("Solve", True, WHITE)
    solve_text_rect = solve_text.get_rect(center=(50 + 100, 30 + 25))
    WINDOW.blit(solve_text, solve_text_rect)

    # Restart Board button
    pygame.draw.rect(WINDOW, BLACK, (350, 30, 200, 50))
    restart_text = FONT.render("Restart Board", True, WHITE)
    restart_text_rect = restart_text.get_rect(center=(350 + 100, 30 + 25))
    WINDOW.blit(restart_text, restart_text_rect)

    # Analyzing animation
    if solving_in_progress:
        center_x, center_y = WIDTH // 2, 80
        radius = 15
        thickness = 3
        start_angle = math.radians(pygame.time.get_ticks() * 0.3)
        end_angle = start_angle + math.radians(270)

        pygame.draw.circle(WINDOW, GRAY, (center_x, center_y), radius, thickness)
        pygame.draw.arc(WINDOW, DARK_BLUE, 
                       (center_x - radius, center_y - radius, radius * 2, radius * 2),
                       start_angle, end_angle, thickness)

        analyzing_text = SMALL_FONT.render("Analyzing...", True, BLACK)
        text_rect = analyzing_text.get_rect(center=(center_x, center_y + radius + 15))
        WINDOW.blit(analyzing_text, text_rect)

    # Step counter
    if solution is not None:
        step_text = FONT.render(f"Steps: {current_step}/{len(solution) - 1}", True, BLACK)
        WINDOW.blit(step_text, (200, 600))

def puzzle_game():
    """Main game function"""
    board = generate_random_state()
    solution = None
   