import sys
import winsound
import os

class PuliMeka:
    """
    Puli Meka (Tigers vs Goats) - A traditional South Indian board game.
    3 Tigers vs 15 Goats.
    Rules:
    - Goats start by placing 15 pieces one by one.
    - Tigers move and can capture Goats by jumping over them to an empty spot in a straight line.
    - Goats move only after all 15 are placed.
    - Goats win if all Tigers are trapped (no legal moves).
    - Tigers win if they capture enough Goats (usually 5-6) such that Goats cannot trap them.
    """
    def __init__(self) -> None:
        # Board state: 23 positions. None = Empty, 'T' = Tiger, 'G' = Goat
        self.board: list[str | None] = [None] * 23
        
        # 3 Tigers start at positions 0, 1, 2
        self.board[0] = 'T'
        self.board[1] = 'T'
        self.board[2] = 'T'
        
        self.goats_to_place = 15
        self.goats_captured = 0
        self.turn = 'G'  # Goats start by placing
        self.game_over = False
        self.winner = None

        # Adjacency List for the 23-point board
        # Board Structure (Triangular Grid):
        #      0
        #    1---2
        #   3--4--5
        #  6-7-8-9-10
        # 11-12-13-14-15
        # 16-17-18-19-20-21-22 (approximate expansion)
        self.adjacency = {
            0: [1, 2],
            1: [0, 2, 3, 4],
            2: [0, 1, 4, 5],
            3: [1, 4, 6, 7],
            4: [1, 2, 3, 5, 7, 8],
            5: [2, 4, 8, 9],
            6: [3, 7, 10, 11],
            7: [3, 4, 6, 8, 11, 12],
            8: [4, 5, 7, 9, 12, 13],
            9: [5, 8, 13, 14],
            10: [6, 11, 15], # Placeholder for 10
            11: [6, 7, 12, 16],
            12: [7, 8, 11, 13, 16, 17],
            13: [8, 9, 12, 14, 17, 18],
            14: [9, 13, 18],
            15: [10], # Placeholder for 15
            16: [11, 12, 17, 19],
            17: [12, 13, 16, 18, 19, 20],
            18: [13, 14, 17, 20, 21],
            19: [16, 17, 20],
            20: [17, 18, 19, 21],
            21: [18, 20, 22],
            22: [21]
        }
        
        # Valid Linear Jumps (Start, Mid, End)
        # These are pre-calculated to ensure Tigers can only jump in straight lines.
        self.linear_jumps = [
            (0, 1, 3), (0, 2, 5), (1, 4, 8), (2, 4, 7),
            (3, 4, 5), (6, 7, 8), (7, 8, 9), (11, 12, 13), (12, 13, 14),
            (16, 17, 18), (17, 18, 19), (0, 4, 12), (1, 3, 6), (2, 5, 9),
            (6, 11, 16), (7, 12, 17), (8, 13, 18), (9, 14, 18), # Approximated
            (3, 7, 12), (5, 8, 12) # Cross diagonals
        ]

    def _play_sound(self, sound_type: str) -> None:
        try:
            if sound_type == 'goat':
                if os.path.exists('goat.wav'):
                    winsound.PlaySound('goat.wav', winsound.SND_ASYNC)
            elif sound_type == 'tiger':
                if os.path.exists('tiger.wav'):
                    winsound.PlaySound('tiger.wav', winsound.SND_ASYNC)
        except Exception:
            pass # Silent fail if audio issue

    def print_board(self) -> None:
        b = [' ' if x is None else x for x in self.board]
        # Improved ASCII board display for 23 points
        print(f"""
              {b[0]} (0)
             / \\
          (1) {b[1]}---{b[2]} (2)
           / \\ / \\
        (3){b[3]}---{b[4]}---{b[5]}(5)
         / \\ / \\ / \\
      (6){b[6]}---{b[7]}---{b[8]}---{b[9]}(9)
       / \\ / \\ / \\ / \\
    (11){b[11]}--{b[12]}--{b[13]}--{b[14]}(14)
     / \\ / \\ / \\ / \\
    (16){b[16]}--{b[17]}--{b[18]}--{b[21]}(21)
        """)
        print(f"Goats Placed: {15 - self.goats_to_place}/15 | Captured: {self.goats_captured}")
        print(f"Turn: {'Goat' if self.turn == 'G' else 'Tiger'}")

    def play(self) -> None:
        print("Welcome to Puli Meka (Tigers vs Goats)")
        print("Objective: Goats trap 3 Tigers. Tigers eat 5 Goats.")
        
        while not self.game_over:
            self.print_board()
            
            if self.turn == 'G':
                if self.goats_to_place > 0:
                    self._phase_place_goat()
                else:
                    self._phase_move_piece('G')
            else:
                self._phase_move_piece('T')
                
            self._check_win_condition()
            
        self.print_board()
        print(f"GAME OVER! Winner: {self.winner}")

    def _phase_place_goat(self) -> None:
        while True:
            try:
                pos_input = input("Place Goat at (0-22) or 'q' to quit: ")
                if pos_input.lower() == 'q': sys.exit()
                pos = int(pos_input)
                if 0 <= pos <= 22 and self.board[pos] is None:
                    self.board[pos] = 'G'
                    self.goats_to_place -= 1
                    self._play_sound('goat')
                    self.turn = 'T'
                    break
                print("Invalid position. Must be empty 0-22.")
            except (ValueError, IndexError):
                print("Please enter a valid position (0-22).")

    def _phase_move_piece(self, player: str) -> None:
        while True:
            try:
                prompt = "Tiger Move" if player == 'T' else "Goat Move"
                cmd = input(f"{prompt} (from to) or 'q' to quit: ").split()
                if not cmd: continue
                if cmd[0].lower() == 'q': sys.exit()
                if len(cmd) != 2:
                    print("Format: from to (e.g., '3 7')")
                    continue
                
                start, end = int(cmd[0]), int(cmd[1])
                
                if self._validate_and_execute_move(player, start, end):
                    if player == 'G': self._play_sound('goat')
                    self.turn = 'T' if player == 'G' else 'G'
                    break
                print("Invalid move. Pieces must be adjacent, or Tigers can jump Goats.")
            except (ValueError, IndexError):
                print("Enter valid positions (0-22).")

    def _validate_and_execute_move(self, player, start: int, end: int) -> bool:
        if not (0 <= start <= 22 and 0 <= end <= 22): return False
        if self.board[start] != player: return False
        if self.board[end] is not None: return False
        
        # 1. Normal Move (Adjacent)
        if end in self.adjacency.get(start, []):
            self.board[start] = None
            self.board[end] = player
            return True
            
        # 2. Jump Move (Tiger Only)
        if player == 'T':
            for s, m, e in self.linear_jumps:
                if (start == s and end == e) or (start == e and end == s):
                    mid = m
                    if self.board[mid] == 'G':
                        # Valid capture!
                        self.board[start] = None
                        self.board[mid] = None # Eat Goat
                        self.board[end] = 'T'
                        self.goats_captured += 1
                        self._play_sound('tiger')
                        print(f"Tiger captured Goat at {mid}!")
                        return True
                    
        return False

    def _check_win_condition(self) -> None:
        # Tiger Win: Captured 5 Goats
        if self.goats_captured >= 5:
            self.game_over = True
            self.winner = "Tigers (Traditional Win: 5 Goats Captured)"
            return
            
        # Goat Win: Tigers have no legal moves (anywhere)
        # We check all Tigers on the board
        all_tigers_blocked = True
        for i, p in enumerate(self.board):
            if p == 'T':
                if self._has_moves_at_pos('T', i):
                    all_tigers_blocked = False
                    break
        
        if all_tigers_blocked:
            self.game_over = True
            self.winner = "Goats (Strategic Win: All Tigers Blocked)"

    def _has_moves_at_pos(self, player: str, pos: int) -> bool:
        # Check adjacent
        for neighbor in self.adjacency.get(pos, []):
            if self.board[neighbor] is None: return True
        # Check jumps (if Tiger)
        if player == 'T':
            for s, m, e in self.linear_jumps:
                if pos == s and self.board[m] == 'G' and self.board[e] is None: return True
                if pos == e and self.board[m] == 'G' and self.board[s] is None: return True
        return False

if __name__ == "__main__":
    game = PuliMeka()
    game.play()
