from __future__ import annotations

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from src import locators


class FiltroError(Exception):
    pass


def open_consulta_laudos(driver: WebDriver, timeout: int = 20) -> None:
    driver.get(locators.CONSULTA_LAUDOS_URL)
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locators.SELECT_ESTADO))


def _select_by_text_ci(select: Select, texto: str, campo: str) -> None:
    alvo = texto.strip().lower()
    for opcao in select.options:
        if opcao.text.strip().lower() == alvo:
            select.select_by_value(opcao.get_attribute("value"))
            return
    raise FiltroError(f"Opção '{texto}' não encontrada no campo {campo}")


def apply_location_filter(driver: WebDriver, estado: str, cidade: str, timeout: int = 20) -> None:
    estado_select = Select(driver.find_element(*locators.SELECT_ESTADO))
    _select_by_text_ci(estado_select, estado, "Estado")

    WebDriverWait(driver, timeout).until(
        lambda d: len(Select(d.find_element(*locators.SELECT_CIDADE)).options) > 1
    )
    cidade_select = Select(driver.find_element(*locators.SELECT_CIDADE))
    _select_by_text_ci(cidade_select, cidade, "Cidade")
