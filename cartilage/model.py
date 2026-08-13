"""CartilageModel: a grid of extracellular matrix (ECM) populated with Chondrocyte agents.

Two conditions are meant to be compared (see examples/run_comparison.py):
- cytokine_level=0.0   -- healthy/physiological baseline
- cytokine_level>0     -- an early-osteoarthritic inflammatory milieu (e.g. elevated IL-1beta/
                          TNF-alpha), which pushes chondrocytes toward the catabolic (matrix
                          degrading) state and triggers cluster-forming proliferation.
"""
import numpy as np
from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from mesa.time import RandomActivation

from .agents import Chondrocyte


def mean_matrix_health(model):
    return float(model.matrix.mean())


def count_chondrocytes(model):
    return model.schedule.get_agent_count()


def cluster_fraction(model):
    """Fraction of living chondrocytes that are part of a multi-cell cluster (i.e. have at
    least one chondrocyte neighbor) -- a simple proxy for the "chondrocyte cloning" clusters
    seen histologically in early OA cartilage."""
    agents = model.schedule.agents
    if not agents:
        return 0.0
    return sum(1 for a in agents if a.is_clustered()) / len(agents)


def matrix_snapshot(model):
    return model.matrix.copy()


# Suggested cytokine_level values for the two conditions the model is meant to compare
# (see examples/run_comparison.py). With the model's other default parameters, the healthy
# level sits comfortably below catabolic_threshold and never triggers matrix degradation, while
# the early-OA level sits above it from the first step, which is what gets the catabolic /
# clustering feedback loop going.
HEALTHY_CYTOKINE_LEVEL = 0.0
EARLY_OA_CYTOKINE_LEVEL = 0.4


class CartilageModel(Model):

    def __init__(self, width=30, height=30, num_chondrocytes=60, cytokine_level=0.0,
                 catabolic_threshold=0.3, degradation_rate=0.02, synthesis_rate=0.03,
                 damage_feedback=0.6, recovery_rate=0.1, cluster_trigger=0.7,
                 proliferation_prob=0.15, apoptosis_threshold=12.0, seed=None):
        super().__init__()
        if seed is not None:
            self.random.seed(seed)

        self.grid = SingleGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)

        # ECM matrix health per cell, 1.0 = fully healthy, 0.0 = fully degraded.
        self.matrix = np.ones((width, height))

        # Condition / rate parameters -- illustrative, not fitted to assay data (see README).
        self.cytokine_level = cytokine_level
        self.catabolic_threshold = catabolic_threshold
        self.degradation_rate = degradation_rate
        self.synthesis_rate = synthesis_rate
        self.damage_feedback = damage_feedback
        self.recovery_rate = recovery_rate
        self.cluster_trigger = cluster_trigger
        self.proliferation_prob = proliferation_prob
        self.apoptosis_threshold = apoptosis_threshold

        self.steps = 0

        self.datacollector = DataCollector(
            model_reporters={
                "MeanMatrixHealth": mean_matrix_health,
                "NumChondrocytes": count_chondrocytes,
                "ClusterFraction": cluster_fraction,
                "Matrix": matrix_snapshot,
            }
        )

        for i in range(num_chondrocytes):
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            while not self.grid.is_cell_empty((x, y)):
                x = self.random.randrange(width)
                y = self.random.randrange(height)
            chondrocyte = Chondrocyte(self.next_id(), self)
            self.grid.place_agent(chondrocyte, (x, y))
            self.schedule.add(chondrocyte)

        self.datacollector.collect(self)

    def remove_chondrocyte(self, agent):
        self.grid.remove_agent(agent)
        self.schedule.remove(agent)

    def step(self):
        self.steps += 1
        self.schedule.step()
        self.datacollector.collect(self)
