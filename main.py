import random
import copy
from typing import List, Tuple, Optional

class MiniSudoku:
    def __init__(self):
        self.size = 6
        self.box_size = 2  # 2x3 boxes for 6x6 grid
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.solution = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.initial_grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
    def print_grid(self, grid: List[List[int]] = None) -> None:
        """Print the Sudoku grid with nice formatting"""
        if grid is None:
            grid = self.grid
            
        print("\n  " + " ".join([str(i+1) for i in range(self.size)]))
        print("  " + "-" * (self.size * 2 - 1))
        
        for i, row in enumerate(grid):
            row_str = f"{chr(65+i)}|"
            for j, cell in enumerate(row):
                if cell == 0:
                    row_str += " ."
                else:
                    row_str += f" {cell}"
                    
                # Add vertical separator for boxes
                if j == 2:
                    row_str += "|"
            print(row_str)
            
            # Add horizontal separator for boxes
            if i == 1 or i == 3:
                print("  " + "-" * (self.size * 2 - 1))
    
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
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.generate_complete_grid()
        self.remove_numbers(difficulty)
    
    def make_move(self, row: int, col: int, num: int) -> bool:
        """Make a move if valid"""
        if self.initial_grid[row][col] != 0:
            return False  # Can't change initial numbers
        
        if num == 0 or self.is_valid_move(row, col, num):
            self.grid[row][col] = num
            return True
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
        print("\n📋 Menu:")
        print("1. New Easy Game")
        print("2. New Medium Game") 
        print("3. New Hard Game")
        print("4. Quit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "4":
            print("Thanks for playing! 👋")
            break
        elif choice in ["1", "2", "3"]:
            difficulty_map = {"1": "easy", "2": "medium", "3": "hard"}
            difficulty = difficulty_map[choice]
            
            print(f"\n🎯 Generating {difficulty} puzzle...")
            game.generate_puzzle(difficulty)
            
            print(f"\n🎮 {difficulty.capitalize()} Mini Sudoku")
            print("💡 Use numbers 1-6. Enter moves as: A1 3 (row, column, number)")
            print("💡 Special commands: 'hint', 'check', 'solution', 'restart', 'menu'")
            
            while True:
                game.print_grid()
                
                # Check if completed
                if game.is_complete():
                    conflicts = game.check_conflicts()
                    if not conflicts:
                        print("\n🎉 Congratulations! Puzzle completed! 🎉")
                        break
                    else:
                        print(f"\n⚠️  Almost there! {len(conflicts)} conflicts remaining.")
                
                user_input = input("\nEnter move (or command): ").strip().lower()
                
                if user_input == "menu":
                    break
                elif user_input == "hint":
                    hint = game.get_hint()
                    if hint:
                        row, col, num = hint
                        print(f"💡 Hint: Try {num} at {chr(65+row)}{col+1}")
                    else:
                        print("💡 No hints available - puzzle is complete!")
                        
                elif user_input == "check":
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
                    print("🔄 Puzzle restarted!")
                    
                else:
                    # Parse move
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
