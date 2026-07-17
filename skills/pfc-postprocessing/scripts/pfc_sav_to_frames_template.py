from __future__ import annotations

'''
This template must run inside a PFC Python environment, not plain CPython.

Purpose:
restore a list of save states and export one bitmap per state.

Public rewrite of the chapter-22 `outfig.py` idea:

    model restore "jieguo1"
    plot export bitmap filename "jieguo_1"
'''

try:
    import itasca as it
except Exception as exc:  # pragma: no cover
    raise SystemExit("This template must run inside PFC Python where `itasca` is available.") from exc


SAVE_STEMS = [f"jieguo{i}" for i in range(1, 21)]
PLOT_NAME = "main"
FRAME_PREFIX = "frame"


def export_frames(save_stems: list[str], plot_name: str = PLOT_NAME, frame_prefix: str = FRAME_PREFIX) -> None:
    it.command("python-reset-state false")
    for index, stem in enumerate(save_stems, start=1):
        it.command(f'model restore "{stem}"')
        it.command(f'plot export bitmap filename "{frame_prefix}_{index:04d}"')


if __name__ == "__main__":
    export_frames(SAVE_STEMS)
