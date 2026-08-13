"""Chondrocyte agent: a cartilage cell embedded in the extracellular matrix (ECM).

Behavior grounded in the osteoarthritis (OA) chondrocyte literature (see README):
- Segarra-Queralt et al. 2023, "Network-based modelling of mechano-inflammatory chondrocyte
  regulation in early osteoarthritis" -- inflammatory cytokines and local mechanical/matrix
  damage push chondrocytes from an anabolic (matrix-synthesizing) to a catabolic
  (matrix-degrading) state.
- Chondrocyte cluster formation ("chondrocyte cloning"): a well-documented histological hallmark
  of early OA cartilage, where chondrocytes proliferate near damaged matrix in an attempted (and
  ultimately often insufficient) repair response.

The exact thresholds/rates here are illustrative, not fitted to real assay data -- see the
"Model parameters are illustrative" note in the README.
"""
from mesa import Agent


class Chondrocyte(Agent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.stress_exposure = 0.0  # accumulated catabolic-signal exposure; drives apoptosis
        self.age = 0

    def step(self):
        x, y = self.pos
        matrix_health = self.model.matrix[x, y]

        # Catabolic drive = ambient inflammatory cytokine level + locally sensed matrix damage.
        # Damaged matrix itself contributes to the catabolic signal, which is a simplified stand
        # in for the DAMP/cytokine feedback loop described in Segarra-Queralt et al. 2023: matrix
        # breakdown products further activate surrounding chondrocytes toward degradation.
        catabolic_signal = self.model.cytokine_level + (1.0 - matrix_health) * self.model.damage_feedback

        if catabolic_signal > self.model.catabolic_threshold:
            # Catabolic state: degrade the local matrix, accumulate stress.
            self.model.matrix[x, y] = max(0.0, matrix_health - self.model.degradation_rate)
            self.stress_exposure += catabolic_signal
        else:
            # Anabolic state: synthesize/repair the local matrix, recover from stress.
            self.model.matrix[x, y] = min(1.0, matrix_health + self.model.synthesis_rate)
            self.stress_exposure = max(0.0, self.stress_exposure - self.model.recovery_rate)

        # Cluster-forming repair response: proliferate into a damaged neighboring lacuna. This
        # is what produces the chondrocyte clusters seen histologically in early OA cartilage.
        if matrix_health < self.model.cluster_trigger:
            if self.random.random() < self.model.proliferation_prob:
                self._attempt_proliferate()

        # Apoptosis under sustained severe stress exposure.
        self.age += 1
        if self.stress_exposure > self.model.apoptosis_threshold:
            self.model.remove_chondrocyte(self)

    def is_clustered(self):
        """True if at least one Moore neighbor cell is also occupied by a chondrocyte."""
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        return any(not self.model.grid.is_cell_empty(n) for n in neighbors)

    def _attempt_proliferate(self):
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True, include_center=False)
        empty = [n for n in neighbors if self.model.grid.is_cell_empty(n)]
        if not empty:
            return
        pos = self.random.choice(empty)
        daughter = Chondrocyte(self.model.next_id(), self.model)
        self.model.grid.place_agent(daughter, pos)
        self.model.schedule.add(daughter)
