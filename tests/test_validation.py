from pathlib import Path

import openpyxl
import pytest

from src.validation import ContagemError, count_rows, parse_total_registros


@pytest.mark.parametrize(
    ("texto", "esperado"),
    [
        ("Exibindo registros de 1 a 25 de um total de 1553 encontrados.", 1553),
        ("Exibindo registros de 1 a 25 de um total de 193 encontrados.", 193),
        ("Exibindo registros de 1 a 1 de um total de 1 encontrado.", 1),
        ("Exibindo registros de 0 a 0 de um total de 0 encontrados.", 0),
    ],
)
def test_parse_total_registros_variacoes(texto: str, esperado: int) -> None:
    assert parse_total_registros(texto) == esperado


def test_parse_total_registros_texto_invalido_levanta_erro() -> None:
    with pytest.raises(ContagemError):
        parse_total_registros("Nenhuma informação de contagem aqui.")


def _criar_xlsx_fixture(tmp_path: Path, n_linhas_de_dados: int) -> Path:
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.append(["Nome", "Cidade"])
    for i in range(n_linhas_de_dados):
        sheet.append([f"Paciente {i}", "Manaus"])
    xlsx_path = tmp_path / "fixture.xlsx"
    workbook.save(xlsx_path)
    return xlsx_path


@pytest.mark.parametrize("n_linhas", [0, 1, 25, 193])
def test_count_rows_conta_linhas_de_dados_sem_cabecalho(tmp_path: Path, n_linhas: int) -> None:
    xlsx_path = _criar_xlsx_fixture(tmp_path, n_linhas)
    assert count_rows(xlsx_path) == n_linhas
