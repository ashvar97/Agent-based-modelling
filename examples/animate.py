"""Animate one run of the early-OA condition: ECM matrix health as a heatmap, with
chondrocyte positions overlaid, over time.

Run with:
    python examples/animate.py

Produces examples/oa_progression.gif.
"""
import sys
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import animation

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cartilage import CartilageModel, EARLY_OA_CYTOKINE_LEVEL

STEPS = 100
FRAME_EVERY = 2  # keep the gif a manageable size
WIDTH = HEIGHT = 25
NUM_CHONDROCYTES = 50
SEED = 42


def main():
    model = CartilageModel(width=WIDTH, height=HEIGHT, num_chondrocytes=NUM_CHONDROCYTES,
                            cytokine_level=EARLY_OA_CYTOKINE_LEVEL, seed=SEED)

    matrices = [model.matrix.copy()]
    positions = [[a.pos for a in model.schedule.agents]]
    for i in range(STEPS):
        model.step()
        if i % FRAME_EVERY == 0:
            matrices.append(model.matrix.copy())
            positions.append([a.pos for a in model.schedule.agents])

    fig, ax = plt.subplots(figsize=(6, 6))
    im = ax.imshow(matrices[0].T, origin="lower", cmap="RdYlGn", vmin=0, vmax=1)
    scatter = ax.scatter([], [], s=12, color="black", label="chondrocyte")
    ax.set_xticks([])
    ax.set_yticks([])
    title = ax.set_title("step 0")
    fig.colorbar(im, ax=ax, label="ECM matrix health", shrink=0.8)
    ax.legend(loc="upper right", fontsize=8)

    def update(frame_idx):
        im.set_data(matrices[frame_idx].T)
        pos = positions[frame_idx]
        if pos:
            xs, ys = zip(*pos)
        else:
            xs, ys = [], []
        scatter.set_offsets(list(zip(xs, ys)))
        title.set_text(f"step {frame_idx * FRAME_EVERY} (early-OA)")
        return im, scatter, title

    anim = animation.FuncAnimation(fig, update, frames=len(matrices), interval=150, blit=False)

    out_path = Path(__file__).parent / "oa_progression.gif"
    anim.save(out_path, writer="pillow", fps=6)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
