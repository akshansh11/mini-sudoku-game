import random
import copy
import time
import json
import os
from typing import List, Tuple, Optional, Dict
from datetime import datetime, timedelta

class MiniSudoku:
    def __init__(self):
        self.size = 6
        self.box_size = 2  # 2x3 boxes for 6x6 grid
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.solution = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.initial_grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        # Timer and scoring
        self.start_time = None
        self.pause_time = 0
        self.is_paused = False
        self.moves_made = 0
        self.hints_used = 0
        self.wrong_moves = 0
        self.difficulty = "medium"
        
        # Game statistics
        self.stats_file = "sudoku_stats.json"
        self.save_file = "sudoku_save.json"
        self.stats = self.load_stats()
        
    def load_stats(self) -> Dict:
        """Load game statistics from file"""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "games_played": 0,
            "games_won": 0,
            "best_times": {"easy": None, "medium": None, "hard": None},
            "total_time_played": 0,
            "best_scores": {"easy": 0, "medium": 0, "hard": 0},
            "hints_used_total": 0,
            "perfect_games": 0  # Games won without hints or wrong moves
        }
    
    def save_stats(self):
        """Save game statistics to file"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not save stats: {e}")
    
    def start_timer(self):
        """Start the game timer"""
        self.start_time = time.time()
        self.pause_time = 0
        self.is_paused = False
    
    def pause_timer(self):
        """Pause the timer"""
        if not self.is_paused and self.start_time:
            self.pause_time += time.time() - self.start_time
            self.is_paused = True
    
    def resume_timer(self):
        """Resume the timer"""
        if self.is_paused:
            self.start_time = time.time()
            self.is_paused = False
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time in seconds"""
        if not self.start_time:
            return 0
        
        if self.is_paused:
            return self.pause_time
        else:
            return self.pause_time + (time.time() - self.start_time)
    
    def format_time(self, seconds: float) -> str:
        """Format time as MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def calculate_score(self) -> int:
        """Calculate final score based on performance"""
        if not self.start_time:
            return 0
        
        elapsed_time = self.get_elapsed_time()
        
        # Base score by difficulty
        base_scores = {"easy": 1000, "medium": 1500, "hard": 2000}
        base_score = base_scores.get(self.difficulty, 1500)
        
        # Time bonus (faster = higher score)
        time_bonus = max(0, base_score - (elapsed_time * 2))
        
        # Penalties
        hint_penalty = self.hints_used * 50
        wrong_move_penalty = self.wrong_moves * 25
        
        final_score = max(100, int(base_score + time_bonus - hint_penalty - wrong_move_penalty))
        return final_score
    
    def save_game(self) -> bool:
        """Save current game state"""
        try:
            game_state = {
                "grid": self.grid,
                "solution": self.solution,
                "initial_grid": self.initial_grid,
                "difficulty": self.difficulty,
                "start_time": self.start_time,
                "pause_time": self.pause_time,
                "moves_made": self.moves_made,
                "hints_used": self.hints_used,
                "wrong_moves": self.wrong_moves,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(self.save_file, 'w') as f:
                json.dump(game_state, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️  Could not save game: {e}")
            return False
    
    def load_game(self) -> bool:
        """Load saved game state"""
        if not os.path.exists(self.save_file):
            return False
        
        try:
            with open(self.save_file, 'r') as f:
                game_state = json.load(f)
            
            self.grid = game_state["grid"]
            self.solution = game_state["solution"]
            self.initial_grid = game_state["initial_grid"]
            self.difficulty = game_state["difficulty"]
            self.start_time = game_state["start_time"]
            self.pause_time = game_state["pause_time"]
            self.moves_made = game_state["moves_made"]
            self.hints_used = game_state["hints_used"]
            self.wrong_moves = game_state["wrong_moves"]
            
            # Resume timer
            if self.start_time:
                self.start_time = time.time() - self.pause_time
                self.pause_time = 0
            
            return True
        except Exception as e:
            print(f"⚠️  Could not load game: {e}")
            return False
    
    def update_stats_on_win(self):
        """Update statistics when player wins"""
        elapsed_time = self.get_elapsed_time()
        score = self.calculate_score()
        
        self.stats["games_played"] += 1
        self.stats["games_won"] += 1
        self.stats["total_time_played"] += elapsed_time
        self.stats["hints_used_total"] += self.hints_used
        
        # Update best time
        if (self.stats["best_times"][self.difficulty] is None or 
            elapsed_time < self.stats["best_times"][self.difficulty]):
            self.stats["best_times"][self.difficulty] = elapsed_time
        
        # Update best score
        if score > self.stats["best_scores"][self.difficulty]:
            self.stats["best_scores"][self.difficulty] = score
        
        # Perfect game (no hints, no wrong moves)
        if self.hints_used == 0 and self.wrong_moves == 0:
            self.stats["perfect_games"] += 1
        
        self.save_stats()
    
    def print_grid(self, grid: List[List[int]] = None, show_conflicts: bool = False) -> None:
        """Print the Sudoku grid with nice formatting"""
        if grid is None:
            grid = self.grid
        
        # Print timer and stats
        if self.start_time:
            elapsed = self.format_time(self.get_elapsed_time())
            status = "⏸️  PAUSED" if self.is_paused else "⏱️ "
            print(f"\n{status} Time: {elapsed} | Moves: {self.moves_made} | Hints: {self.hints_used} | Errors: {self.wrong_moves}")
        
        print("\n  " + " ".join([str(i+1) for i in range(self.size)]))
        print("  " + "-" * (self.size * 2 - 1))
        
        conflicts = self.check_conflicts() if show_conflicts else []
        
        for i, row in enumerate(grid):
            row_str = f"{chr(65+i)}|"
            for j, cell in enumerate(row):
                if cell == 0:
                    row_str += " ."
                else:
                    # Highlight conflicts
                    if (i, j) in conflicts:
                        row_str += f" {cell}❌"
                    # Highlight initial numbers
                    elif self.initial_grid[i][j] != 0:
                        row_str += f" {cell}"
                    else:
                        row_str += f" {cell}"
                    
                # Add vertical separator for boxes
                if j == 2:
                    row_str += "|"
            print(row_str)
            
            # Add horizontal separator for boxes
            if i == 1 or i == 3:
                print("  " + "-" * (self.size * 2 - 1))
    
    def print_stats(self):
        """Print game statistics"""
        print("\n📊 Your Sudoku Statistics")
        print("=" * 40)
        print(f"🎮 Games Played: {self.stats['games_played']}")
        print(f"🏆 Games Won: {self.stats['games_won']}")
        
        if self.stats['games_played'] > 0:
            win_rate = (self.stats['games_won'] / self.stats['games_played']) * 100
            print(f"📈 Win Rate: {win_rate:.1f}%")
        
        print(f"⭐ Perfect Games: {self.stats['perfect_games']}")
        
        total_hours = self.stats['total_time_played'] / 3600
        print(f"⏱️  Total Play Time: {total_hours:.1f} hours")
        
        print(f"💡 Total Hints Used: {self.stats['hints_used_total']}")
        
        print("\n🏅 Best Times:")
        for difficulty in ["easy", "medium", "hard"]:
            best_time = self.stats['best_times'][difficulty]
            if best_time:
                print(f"   {difficulty.capitalize()}: {self.format_time(best_time)}")
            else:
                print(f"   {difficulty.capitalize()}: Not set")
        
        print("\n🎯 Best Scores:")
        for difficulty in ["easy", "medium", "hard"]:
            best_score = self.stats['best_scores'][difficulty]
            print(f"   {difficulty.capitalize()}: {best_score}")
    
    def is_valid_move(self, row: int, col: int, num: int, grid: List[List[int]] = None) -> bool:
        """Check if placing num at (row, col) is valid"""
        if grid is None:
            grid = self.grid
            
        # Check row
        for j in range(self.size):
            if grid[row][j] == num:
                return False
        
        # Check column
        for i in range(self.size):
            if grid[i][col] == num:
                return False
        
        # Check 2x3 box
        box_row = (row // 2) * 2
        box_col = (col // 3) * 3
        
        for i in range(box_row, box_row + 2):
            for j in range(box_col, box_col + 3):
                if grid[i][j] == num:
                    return False
        
        return True
    
    def solve(self, grid: List[List[int]]) -> bool:
        """Solve the Sudoku using backtracking"""
        for i in range(self.size):
            for j in range(self.size):
                if grid[i][j] == 0:
                    for num in range(1, self.size + 1):
                        if self.is_valid_move(i, j, num, grid):
                            grid[i][j] = num
                            if self.solve(grid):
                                return True
                            grid[i][j] = 0
                    return False
        return True
    
    def generate_complete_grid(self) -> None:
        """Generate a complete valid Sudoku grid"""
        # Fill diagonal boxes first (they don't interfere with each other)
        self.fill_diagonal_boxes()
        
        # Solve the rest
        self.solve(self.grid)
        
        # Store the complete solution
        self.solution = copy.deepcopy(self.grid)
    
    def fill_diagonal_boxes(self) -> None:
        """Fill the diagonal 2x3 boxes"""
        for box in range(0, self.size, 3):  # boxes at (0,0), (0,3), (2,0), (2,3), etc.
            if box < 3:
                self.fill_box(0, box)
            else:
                self.fill_box(2, box - 3)
    
    def fill_box(self, start_row: int, start_col: int) -> None:
        """Fill a 2x3 box with random valid numbers"""
        nums = list(range(1, self.size + 1))
        random.shuffle(nums)
        
        idx = 0
        for i in range(start_row, start_row + 2):
            for j in range(start_col, start_col + 3):
                self.grid[i][j] = nums[idx]
                idx += 1
    
    def remove_numbers(self, difficulty: str = "medium") -> None:
        """Remove numbers to create puzzle"""
        difficulty_settings = {
            "easy": 15,      # Remove 15 numbers (leave 21)
            "medium": 20,    # Remove 20 numbers (leave 16)  
            "hard": 25       # Remove 25 numbers (leave 11)
        }
        
        cells_to_remove = difficulty_settings.get(difficulty, 20)
        cells = [(i, j) for i in range(self.size) for j in range(self.size)]
        random.shuffle(cells)
        
        removed = 0
        for row, col in cells:
            if removed >= cells_to_remove:
                break
                
            # Temporarily remove the number
            backup = self.grid[row][col]
            self.grid[row][col] = 0
            
            # Check if puzzle still has unique solution
            test_grid = copy.deepcopy(self.grid)
            if self.count_solutions(test_grid) == 1:
                removed += 1
            else:
                # Restore the number if removing it makes puzzle invalid
                self.grid[row][col] = backup
        
        # Store the initial puzzle state
        self.initial_grid = copy.deepcopy(self.grid)
    
    def count_solutions(self, grid: List[List[int]], limit: int = 2) -> int:
        """Count number of solutions (up to limit)"""
        def backtrack(g: List[List[int]]) -> int:
            for i in range(self.size):
                for j in range(self.size):
                    if g[i][j] == 0:
                        solutions = 0
                        for num in range(1, self.size + 1):
                            if self.is_valid_move(i, j, num, g):
                                g[i][j] = num
                                solutions += backtrack(g)
                                g[i][j] = 0
                                if solutions >= limit:
                                    return solutions
                        return solutions
            return 1
        
        return backtrack(copy.deepcopy(grid))
    
    def generate_puzzle(self, difficulty: str = "medium") -> None:
        """Generate a new puzzle"""
        self.difficulty = difficulty
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.generate_complete_grid()
        self.remove_numbers(difficulty)
        
        # Reset game stats
        self.moves_made = 0
        self.hints_used = 0
        self.wrong_moves = 0
        self.start_timer()
    
    def make_move(self, row: int, col: int, num: int) -> bool:
        """Make a move if valid"""
        if self.initial_grid[row][col] != 0:
            return False  # Can't change initial numbers
        
        # Count as a move
        self.moves_made += 1
        
        if num == 0 or self.is_valid_move(row, col, num):
            self.grid[row][col] = num
            return True
        else:
            self.wrong_moves += 1
            return False
    
    def is_complete(self) -> bool:
        """Check if puzzle is completed"""
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] == 0:
                    return False
        return True
    
    def get_hint(self) -> Optional[Tuple[int, int, int]]:
        """Get a hint for next move"""
        empty_cells = [(i, j) for i in range(self.size) 
                      for j in range(self.size) if self.grid[i][j] == 0]
        
        if not empty_cells:
            return None
        
        self.hints_used += 1
        row, col = random.choice(empty_cells)
        return (row, col, self.solution[row][col])
    
    def check_conflicts(self) -> List[Tuple[int, int]]:
        """Return list of cells with conflicts"""
        conflicts = []
        for i in range(self.size):
            for j in range(self.size):
                if self.grid[i][j] != 0:
                    num = self.grid[i][j]
                    self.grid[i][j] = 0  # Temporarily remove to check
                    if not self.is_valid_move(i, j, num):
                        conflicts.append((i, j))
                    self.grid[i][j] = num  # Restore
        return conflicts


def play_mini_sudoku():
    """Main game loop"""
    print("🧩 Welcome to Mini Sudoku! (6x6)")
    print("=" * 40)
    
    game = MiniSudoku()
    
    while True:
        print(f"\n📋 Menu:")
        print("1. New Easy Game")
        print("2. New Medium Game") 
        print("3. New Hard Game")
        print("4. Load Saved Game")
        print("5. View Statistics")
        print("6. Quit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "6":
            print("Thanks for playing! 👋")
            break
        elif choice == "5":
            game.print_stats()
            continue
        elif choice == "4":
            if game.load_game():
                print(f"✅ Game loaded! Resuming {game.difficulty} puzzle...")
            else:
                print("❌ No saved game found.")
                continue
        elif choice in ["1", "2", "3"]:
            difficulty_map = {"1": "easy", "2": "medium", "3": "hard"}
            difficulty = difficulty_map[choice]
            
            print(f"\n🎯 Generating {difficulty} puzzle...")
            game.generate_puzzle(difficulty)
        else:
            print("❌ Invalid choice. Please try again.")
            continue
        
        # Game loop
        print(f"\n🎮 {game.difficulty.capitalize()} Mini Sudoku")
        print("💡 Commands: move (A1 3), hint, check, solution, pause, save, restart, menu")
        
        while True:
            if not game.is_paused:
                game.print_grid()
            else:
                print("\n⏸️  Game Paused")
                print("💡 Type 'resume' to continue playing")
            
            # Check if completed
            if game.is_complete() and not game.is_paused:
                conflicts = game.check_conflicts()
                if not conflicts:
                    game.pause_timer()
                    elapsed_time = game.format_time(game.get_elapsed_time())
                    score = game.calculate_score()
                    
                    print("\n🎉 Congratulations! Puzzle completed! 🎉")
                    print(f"⏱️  Time: {elapsed_time}")
                    print(f"🎯 Score: {score}")
                    print(f"📊 Moves: {game.moves_made} | Hints: {game.hints_used} | Errors: {game.wrong_moves}")
                    
                    # Check for perfect game
                    if game.hints_used == 0 and game.wrong_moves == 0:
                        print("⭐ PERFECT GAME! No hints or errors!")
                    
                    game.update_stats_on_win()
                    
                    # Clean up save file
                    if os.path.exists(game.save_file):
                        os.remove(game.save_file)
                    
                    break
                else:
                    print(f"\n⚠️  Almost there! {len(conflicts)} conflicts remaining.")
            
            user_input = input("\nEnter command: ").strip().lower()
            
            if user_input == "menu":
                break
            elif user_input == "pause":
                if game.is_paused:
                    print("⚠️  Game is already paused.")
                else:
                    game.pause_timer()
                    print("⏸️  Game paused.")
            elif user_input == "resume":
                if game.is_paused:
                    game.resume_timer()
                    print("▶️  Game resumed.")
                else:
                    print("⚠️  Game is not paused.")
            elif user_input == "save":
                if game.save_game():
                    print("💾 Game saved successfully!")
                else:
                    print("❌ Failed to save game.")
            elif user_input == "hint":
                if game.is_paused:
                    print("⚠️  Resume game to get hints.")
                    continue
                    
                hint = game.get_hint()
                if hint:
                    row, col, num = hint
                    print(f"💡 Hint: Try {num} at {chr(65+row)}{col+1}")
                else:
                    print("💡 No hints available - puzzle is complete!")
                    
            elif user_input == "check":
                if game.is_paused:
                    print("⚠️  Resume game to check conflicts.")
                    continue
                    
                conflicts = game.check_conflicts()
                if conflicts:
                    print(f"⚠️  Found {len(conflicts)} conflicts:")
                    for row, col in conflicts:
                        print(f"   - {chr(65+row)}{col+1}: {game.grid[row][col]}")
                else:
                    print("✅ No conflicts found!")
                    
            elif user_input == "solution":
                print("\n🔍 Solution:")
                game.print_grid(game.solution)
                
            elif user_input == "restart":
                game.grid = copy.deepcopy(game.initial_grid)
                game.moves_made = 0
                game.hints_used = 0
                game.wrong_moves = 0
                game.start_timer()
                print("🔄 Puzzle restarted!")
                
            else:
                # Parse move
                if game.is_paused:
                    print("⚠️  Resume game to make moves.")
                    continue
                    
                try:
                    parts = user_input.upper().replace(",", " ").split()
                    if len(parts) != 2:
                        print("❌ Invalid format. Use: A1 3")
                        continue
                        
                    pos = parts[0]
                    num = int(parts[1])
                    
                    if len(pos) != 2:
                        print("❌ Invalid position. Use format: A1")
                        continue
                        
                    row = ord(pos[0]) - ord('A')
                    col = int(pos[1]) - 1
                    
                    if not (0 <= row < 6 and 0 <= col < 6):
                        print("❌ Position out of range. Use A-F and 1-6")
                        continue
                        
                    if not (0 <= num <= 6):
                        print("❌ Number must be 0-6 (0 to clear)")
                        continue
                    
                    if game.make_move(row, col, num):
                        if num == 0:
                            print(f"✅ Cleared {pos}")
                        else:
                            print(f"✅ Placed {num} at {pos}")
                    else:
                        if game.initial_grid[row][col] != 0:
                            print("❌ Cannot modify initial numbers!")
                        else:
                            print(f"❌ Invalid move: {num} at {pos}")
                
                except (ValueError, IndexError):
                    print("❌ Invalid input. Use format: A1 3")


if __name__ == "__main__":
    play_mini_sudoku()
