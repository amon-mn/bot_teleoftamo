from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

from src.export import DiseaseSpec


def move_to_output(
    staging_path: Path,
    data_execucao: date,
    disease: DiseaseSpec,
    output_dir: Path = Path("output"),
) -> Path:
    destino_dir = output_dir / data_execucao.isoformat()
    destino_dir.mkdir(parents=True, exist_ok=True)
    destino = destino_dir / disease.arquivo
    shutil.move(str(staging_path), str(destino))
    return destino
