# Genetic Algorithm Dino Evolution 🧬🦖

![Preview](/preview.png)

## 🎯 Main Feature: Genetic Algorithm Implementation

This project implements a **Genetic Algorithm (GA)** to evolve AI-controlled dinosaurs that learn to play the Chrome Dinosaur Game. Watch as 100 dinos evolve over generations, developing better strategies through natural selection, crossover, and mutation!

### Key Features:

- **Population-based evolution**: 100 dinos per generation compete simultaneously
- **Gene-based decision making**: Each dino has 3 genes (`gap_threshold`, `duck_threshold`, `base_duck_duration`) that control its behavior
- **Sexual reproduction**: Children inherit averaged traits from two parent dinos
- **Mutation**: 25% mutation rate with ±12% magnitude for exploration
- **Elitism**: Top 2 performers are preserved unchanged each generation
- **Real-time stats panel**: Separate window showing all 100 dinos' fitness and genes
- **Evolution tracking**: Watch generations improve over time with history display

---

## 🎮 Original Game Code Credits

**Base Game Implementation**: The Chrome Dinosaur Game code is based on the original implementation by [maxrohowsky](https://twitter.com/maxrohowsky).

The original game is a simple infinite runner where the player jumps over cacti and avoids birds. This project uses that game as the environment for testing evolved AI strategies.

**Original Game Tutorial Videos**:

1. [Python/Pygame Chrome Dino (Part 1) - Setup & Dino Animation](https://youtu.be/wnBGG7JLrkg?feature=shared)
2. [Python/Pygame Chrome Dino (Part 2) - JUMPING & DUCKING Motion](https://youtu.be/aAkO8Pketkg?feature=shared)
3. [Python/Pygame Chrome Dino (Part 3) - Score & Background](https://youtu.be/KbKMqxVw8x0?feature=shared)
4. [Python/Pygame Chrome Dino (Part 4) - Obstacles and Collisions](https://youtu.be/LYvrb-1ntIE?feature=shared)
5. [Python/Pygame Chrome Dino (Part 5) - Menu and Final Touches](https://youtu.be/xQ5UCzFKR58?feature=shared)

---

## 🧬 Genetic Algorithm Implementation

### How It Works:

1. **Initialization**: Create 100 random dinos with random gene values
2. **Evaluation**: All dinos run the same obstacle course simultaneously
3. **Selection**: Top 35% (35 dinos) become parents based on fitness (score)
4. **Reproduction**:
   - Top 2 dinos are kept unchanged (elitism)
   - Remaining 98 slots filled by children created from:
     - **Crossover**: Average of two randomly selected parents' genes
     - **Mutation**: 25% chance, ±12% change per gene
5. **Next Generation**: Repeat with evolved population

### Gene Structure:

Each dino has 3 genes that control behavior:

- **`gap_threshold`**: Distance (pixels) at which to make jump/duck decision
- **`duck_threshold`**: Y-position threshold - if obstacle Y ≤ threshold → duck, else → jump
- **`base_duck_duration`**: How long (frames) to stay ducked

### Decision Logic:

When an obstacle is at `gap_threshold` distance:

- Check obstacle's Y position
- If `obstacle.rect.y ≤ duck_threshold` → **Duck**
- Otherwise → **Jump**

---

## 📋 Table of Contents

- [Installation](#installation)
- [How to Run](#how-to-run)
- [Understanding the Display](#understanding-the-display)
- [Genetic Algorithm Details](#genetic-algorithm-details)
- [Controls](#controls)
- [Libraries](#libraries)

---

## 🚀 Installation

**Requirements**: Python 3.x and pygame

1. Clone the repository
2. Navigate to the project directory
3. Create and activate a virtual environment:

   **Linux / macOS**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   python -m pip install -U pip
   pip install pygame
   ```

   **Windows (PowerShell / CMD)**

   ```bash
   python -m venv venv
   venv\Scripts\activate
   python -m pip install -U pip
   pip install pygame
   ```

4. Run the game:
   ```bash
   python main.py
   ```

---

## 🎮 How to Run

Simply run `python main.py` and watch the evolution unfold!

- **Left Panel**: The game with all 100 dinos running simultaneously
- **Right Panel**: Real-time stats showing all dinos sorted by fitness
  - **E** prefix (Gold): Top 2 elites (kept unchanged)
  - **P** prefix (Blue): Top 35 parents (used for breeding)
  - Normal (Green/Gray): Rest of population

---

## 📊 Understanding the Display

### Game Window (Left):

- **Points**: Current score (shared by all dinos)
- **Gen**: Current generation number
- **History**: Average fitness of recent generations
- **Alive/Dead**: Count of living vs dead dinos

### Stats Panel (Right):

- All 100 dinos sorted by fitness
- Format: `E1. f:850 g:180 d:260 t:35`
  - `E/P`: Elite or Parent marker
  - `f`: Fitness (score)
  - `g`: gap_threshold
  - `d`: duck_threshold
  - `t`: base_duck_duration

---

## 🧬 Genetic Algorithm Details

### Parameters:

- **Population Size**: 100 dinos
- **Parent Selection**: Top 35% (35 dinos)
- **Elitism**: Top 2 dinos preserved unchanged
- **Mutation Rate**: 25% per gene
- **Mutation Magnitude**: ±12% change
- **Crossover**: Arithmetic mean of two parents

### Evolution Process:

1. All 100 dinos compete in the same scenario (fair comparison)
2. Fitness = points survived (higher is better)
3. Top performers become parents
4. Children inherit averaged genes + random mutations
5. Process repeats, improving over generations

### Expected Behavior:

- **Early generations**: Random behavior, many collisions
- **Mid generations**: Dinos start learning patterns
- **Late generations**: Evolved strategies emerge
- **Convergence**: Population fitness improves over time

---

## 🎮 Controls

- **Up Arrow / Spacebar**: Jump (for manual testing)
- **Down Arrow**: Duck (for manual testing)
- **Any Key**: Start/Restart game
- **Close Window**: Exit

---

## 📚 Libraries

- **[pygame](https://www.pygame.org/news)**: Cross-platform Python modules for game development

---

## 📝 Notes

- The genetic algorithm implementation is the main contribution of this project
- Original game mechanics and assets are from the base Chrome Dino implementation
- Evolution parameters can be adjusted in `main.py` (POP_SIZE, mutation rate, etc.)
- Deterministic evaluation ensures fair fitness comparison across generations

---

## 🙏 Credits

- **Base Game Code**: [maxrohowsky](https://twitter.com/maxrohowsky)
- **Genetic Algorithm Implementation**: This project

---

Enjoy watching evolution in action! 🧬✨
