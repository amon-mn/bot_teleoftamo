from __future__ import annotations

import re
from pathlib import Path

import openpyxl

_PADRAO_TOTAL = re.compile(r"de um total de\s+(\d+)\s+encontrados?", re.IGNORECASE)


class ContagemError(Exception):
    pass


def parse_total_registros(texto: str) -> int:
    match = _PADRAO_TOTAL.search(texto)
    if not match:
        raise ContagemError(f"Não foi possível extrair o total de registros de: {texto!r}")
    return int(match.group(1))


def count_rows(xlsx_path: Path) -> int:
    workbook = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    try:
        sheet = workbook.active
        linhas = sheet.iter_rows(min_row=2, values_only=True)
        return sum(1 for linha in linhas if any(celula is not None for celula in linha))
    finally:
        workbook.close()
