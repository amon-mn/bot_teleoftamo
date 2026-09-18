from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from src import locators
from src.validation import parse_total_registros


class ExportError(Exception):
    pass


@dataclass(frozen=True)
class DiseaseSpec:
    nome: str
    checkbox: tuple
    arquivo: str


DISEASES: list[DiseaseSpec] = [
    DiseaseSpec("Retinopatia diabética", locators.CHECKBOX_RETINOPATIA_DIABETICA, "retinopatia_diabetica.xlsx"),
    DiseaseSpec("Catarata", locators.CHECKBOX_CATARATA, "catarata.xlsx"),
    DiseaseSpec("Degeneração Macular", locators.CHECKBOX_DEGENERACAO_MACULAR, "degeneracao_macular.xlsx"),
    DiseaseSpec("Glaucoma", locators.CHECKBOX_GLAUCOMA, "glaucoma.xlsx"),
]


@dataclass(frozen=True)
class ExportResult:
    arquivo: Path
    total_esperado: int


def _marcar_apenas(driver: WebDriver, disease: DiseaseSpec) -> None:
    for outra in DISEASES:
        checkbox = driver.find_element(*outra.checkbox)
        deve_marcar = outra.nome == disease.nome
        if checkbox.is_selected() != deve_marcar:
            checkbox.click()


def export_disease(
    driver: WebDriver,
    disease: DiseaseSpec,
    staging_dir: Path,
    timeout: int = 60,
    delay: float = 0.0,
) -> ExportResult:
    _marcar_apenas(driver, disease)
    if delay:
        time.sleep(delay)

    texto_anterior = driver.find_element(*locators.TEXTO_CONTAGEM_REGISTROS).text
    driver.find_element(*locators.BOTAO_CONSULTAR).click()

    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.find_element(*locators.TEXTO_CONTAGEM_REGISTROS).text != texto_anterior
        )
    except TimeoutException as exc:
        raise ExportError(
            f"Contagem de registros não atualizou após 'Consultar' para '{disease.nome}'"
        ) from exc

    if delay:
        time.sleep(delay)

    texto = driver.find_element(*locators.TEXTO_CONTAGEM_REGISTROS).text
    total_esperado = parse_total_registros(texto)

    arquivos_antes = set(staging_dir.glob("*.xlsx"))

    driver.find_element(*locators.BOTAO_EXPORTAR_XLS).click()
    if delay:
        time.sleep(delay)

    inicio = time.monotonic()
    novo_arquivo: Path | None = None
    while time.monotonic() - inicio < timeout:
        novos = set(staging_dir.glob("*.xlsx")) - arquivos_antes
        if novos:
            novo_arquivo = novos.pop()
            break
        time.sleep(0.5)

    if novo_arquivo is None:
        raise ExportError(
            f"Download não apareceu em {staging_dir} dentro de {timeout}s para '{disease.nome}'"
        )

    return ExportResult(arquivo=novo_arquivo, total_esperado=total_esperado)
