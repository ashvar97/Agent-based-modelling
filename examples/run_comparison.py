"""Compare the healthy vs. early-OA condition and plot the three tracked metrics over time.

Run with:
    python examples/run_comparison.py

Produces examples/healthy_vs_oa.png.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cartilage import CartilageModel, EARLY_OA_CYTOKINE_LEVEL, HEALTHY_CYTOKINE_LEVEL

STEPS = 100
WIDTH = HEIGHT = 25
NUM_CHONDROCYTES = 50
SEED = 42


def run(cytokine_level):
    model = CartilageModel(width=WIDTH, height=HEIGHT, num_chondrocytes=NUM_CHONDROCYTES,
                            cytokine_level=cytokine_level, seed=SEED)
    for _ in range(STEPS):
        model.step()
    return model.datacollector.get_model_vars_dataframe()


def main():
    healthy = run(HEALTHY_CYTOKINE_LEVEL)
    early_oa = run(EARLY_OA_CYTOKINE_LEVEL)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    metrics = [
        ("MeanMatrixHealth", "Mean ECM matrix health"),
        ("NumChondrocytes", "Chondrocyte count"),
        ("ClusterFraction", "Fraction of chondrocytes in a cluster"),
    ]
    for ax, (col, title) in zip(axes, metrics):
        ax.plot(healthy.index, healthy[col], label=f"healthy (cytokine={HEALTHY_CYTOKINE_LEVEL})", color="tab:green")
        ax.plot(early_oa.index, early_oa[col], label=f"early-OA (cytokine={EARLY_OA_CYTOKINE_LEVEL})", color="tab:red")
        ax.set_title(title)
        ax.set_xlabel("step")
        ax.legend(fontsize=8)

    fig.suptitle("Chondrocyte ABM: healthy homeostasis vs. early-OA progression")
    fig.tight_layout()
    out_path = Path(__file__).parent / "healthy_vs_oa.png"
    fig.savefig(out_path, dpi=150)
    print(f"Saved {out_path}")

    print(f"\nAfter {STEPS} steps:")
    print(f"  healthy:  matrix health={healthy['MeanMatrixHealth'].iloc[-1]:.3f}, "
          f"chondrocytes={healthy['NumChondrocytes'].iloc[-1]}, "
          f"clustered={healthy['ClusterFraction'].iloc[-1]:.2f}")
    print(f"  early-OA: matrix health={early_oa['MeanMatrixHealth'].iloc[-1]:.3f}, "
          f"chondrocytes={early_oa['NumChondrocytes'].iloc[-1]}, "
          f"clustered={early_oa['ClusterFraction'].iloc[-1]:.2f}")


if __name__ == "__main__":
    main()
