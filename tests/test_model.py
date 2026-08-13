"""Tests for the CartilageModel chondrocyte ABM."""
import numpy as np
import pytest

from cartilage import CartilageModel, EARLY_OA_CYTOKINE_LEVEL, HEALTHY_CYTOKINE_LEVEL
from cartilage.agents import Chondrocyte


def test_model_initializes_full_health_matrix_and_correct_agent_count():
    model = CartilageModel(width=15, height=15, num_chondrocytes=30, seed=1)
    assert model.matrix.shape == (15, 15)
    assert np.all(model.matrix == 1.0)
    assert model.schedule.get_agent_count() == 30
    # every agent actually placed on the grid, one per cell (SingleGrid)
    positions = [a.pos for a in model.schedule.agents]
    assert len(positions) == len(set(positions))


def test_healthy_condition_stays_at_homeostasis():
    model = CartilageModel(width=15, height=15, num_chondrocytes=30,
                            cytokine_level=HEALTHY_CYTOKINE_LEVEL, seed=2)
    for _ in range(60):
        model.step()
    df = model.datacollector.get_model_vars_dataframe()
    assert df["MeanMatrixHealth"].iloc[-1] == pytest.approx(1.0)
    assert df["NumChondrocytes"].iloc[-1] == 30


def test_early_oa_condition_shows_progressive_matrix_decline():
    model = CartilageModel(width=15, height=15, num_chondrocytes=30,
                            cytokine_level=EARLY_OA_CYTOKINE_LEVEL, seed=3)
    for _ in range(60):
        model.step()
    df = model.datacollector.get_model_vars_dataframe()
    # matrix health should decline monotonically-ish: end well below start
    assert df["MeanMatrixHealth"].iloc[-1] < df["MeanMatrixHealth"].iloc[0]
    assert df["MeanMatrixHealth"].iloc[-1] < 0.95


def test_early_oa_condition_triggers_clustering():
    model = CartilageModel(width=15, height=15, num_chondrocytes=30,
                            cytokine_level=EARLY_OA_CYTOKINE_LEVEL, seed=4)
    for _ in range(60):
        model.step()
    df = model.datacollector.get_model_vars_dataframe()
    # proliferation into damaged neighborhoods should both grow the population and raise the
    # clustered fraction above the incidental baseline seen with random initial placement
    assert df["NumChondrocytes"].iloc[-1] > df["NumChondrocytes"].iloc[0]
    assert df["ClusterFraction"].iloc[-1] > df["ClusterFraction"].iloc[0]


def test_matrix_values_always_stay_in_unit_interval():
    model = CartilageModel(width=15, height=15, num_chondrocytes=30,
                            cytokine_level=EARLY_OA_CYTOKINE_LEVEL, seed=5)
    for _ in range(60):
        model.step()
        assert model.matrix.min() >= 0.0
        assert model.matrix.max() <= 1.0


def test_apoptosis_removes_agent_from_grid_and_schedule():
    model = CartilageModel(width=10, height=10, num_chondrocytes=1,
                            apoptosis_threshold=0.0, cytokine_level=1.0, seed=6)
    agent = model.schedule.agents[0]
    agent.stress_exposure = 999  # force apoptosis on the next step regardless of dynamics
    model.step()
    assert model.schedule.get_agent_count() == 0
    assert all(model.grid.is_cell_empty((x, y)) for x in range(10) for y in range(10))


def test_proliferation_only_into_empty_cells():
    # A 3x3 grid fully surrounded by chondrocytes: proliferation must not raise or double-place.
    model = CartilageModel(width=3, height=3, num_chondrocytes=0, seed=7)
    for x in range(3):
        for y in range(3):
            c = Chondrocyte(model.next_id(), model)
            model.grid.place_agent(c, (x, y))
            model.schedule.add(c)
    model.matrix[:] = 0.0  # force every cell below cluster_trigger
    model.step()  # should not raise even though no empty neighbor cells exist anywhere
    assert model.schedule.get_agent_count() == 9


def test_is_clustered_true_only_with_a_chondrocyte_neighbor():
    model = CartilageModel(width=5, height=5, num_chondrocytes=0, seed=8)
    a = Chondrocyte(model.next_id(), model)
    model.grid.place_agent(a, (2, 2))
    model.schedule.add(a)
    assert a.is_clustered() is False

    b = Chondrocyte(model.next_id(), model)
    model.grid.place_agent(b, (2, 3))
    model.schedule.add(b)
    assert a.is_clustered() is True
    assert b.is_clustered() is True


def test_seeded_runs_are_reproducible():
    def run():
        model = CartilageModel(width=15, height=15, num_chondrocytes=30,
                                cytokine_level=EARLY_OA_CYTOKINE_LEVEL, seed=123)
        for _ in range(40):
            model.step()
        return model.datacollector.get_model_vars_dataframe()["MeanMatrixHealth"].tolist()

    assert run() == run()
