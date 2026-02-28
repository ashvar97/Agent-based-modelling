# Sheep-Shepherd-Simulation

This project implements a multi-agent simulation using the Mesa framework to model the behavior of shepherd agents interacting with sheeps and the environment. The simulation includes collecting and moving sheep within a grid environment.

## Overview

- **Functionality:** The simulation models shepherd agents that move within a grid to collect sheep and deposit them in specified locations. The environment uses a grid representation to track the positions of agents and sheep in real time.
- **Objective:** To study agent-based modeling techniques and understand decision-making and resource management within a simulated environment.

## Key Learning Areas
### 1. Agent-Based Modeling

- **Agent Behavior:** Implementation of autonomous agents with unique behaviors, such as moving randomly or based on environmental conditions.
- **Environment Interaction:** Agents interact with a grid environment, collecting and depositing sheep based on specific rules.

### 2. Mesa Framework

- **SingleGrid:** Used to represent the environment where agents interact, ensuring only one agent per cell.
- **RandomActivation:** Implements simultaneous activation of all agents in each simulation step.
- **Data Collection:** Utilizes Mesa’s DataCollector to track simulation progress and gather metrics.

### 3. Real-Time Visualization

- **Matplotlib Integration:** Visualizes agent movements and environment changes with animations using Matplotlib.
- **Interactive Visualization:** Enables analysis of simulation dynamics through graphical representations.

## Languages and Tools Used

### Python

- **Mesa:** Framework for agent-based modeling.
- **Matplotlib:** For creating animations and visualizing the simulation.
- **NumPy & Pandas:** For numerical operations and data analysis.

## Installation and Usage

### Requirements
- **Python 3.x** to run the script.
- **Required Libraries:**
```bash
pip install mesa matplotlib numpy pandas
```

## Instructions
1. Clone the repository
  ```bash
  git clone https://github.com/carlosagalicia/Sheep-Shepherd-Simulation.git
  ```

2. Navigate to the project directory and run the notebook:
  ```bash
  jupyter notebook sheep-shepherd.ipynb
  ```

3. Follow the instructions in the notebook to execute the simulation.

## Operation

- The shepherd agents move within the grid, collecting sheep from one location and depositing them in another.
- Agents make decisions based on their surroundings, including whether to move, pick up, or drop off sheep.
- The simulation updates the grid environment in real time and visualizes the process.

## Usage

- Adjust simulation parameters in the notebook to explore different scenarios.
- Run all cells in the notebook to start the simulation.

## Visual Representation
<table>
<tr>
  <td width="50%">
    <h3 align="center">Ungrouped Sheep (initial state)</h3>
    <div align="center">
      <img src="https://github.com/user-attachments/assets/58d51067-4112-4252-b9f9-623decd62690">
    </div>
  </td>
</tr>
</table>

<table>
<tr>
  <td width="50%">
    <h3 align="center">Grouped Sheep (final state)</h3>
    <div align="center">
      <img src="https://github.com/user-attachments/assets/c39ba0b0-6c1a-471a-9147-f24fa0ecb051">
    </div>
  </td>
</tr>
</table>
