from __future__ import annotations

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src import locators
from src.config import Settings


class LoginError(Exception):
    pass


def login(driver: WebDriver, settings: Settings, timeout: int = 20) -> None:
    driver.get(locators.LOGIN_URL)

    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locators.CAMPO_EMAIL))
    except TimeoutException as exc:
        raise LoginError("Campo de email não apareceu na página de login") from exc

    driver.find_element(*locators.CAMPO_EMAIL).send_keys(settings.email)
    driver.find_element(*locators.CAMPO_SENHA).send_keys(settings.senha)
    driver.find_element(*locators.BOTAO_ENTRAR).click()

    try:
        WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locators.CARD_TELERETINOGRAFIA))
    except TimeoutException as exc:
        raise LoginError("Home não carregou após o login — verifique as credenciais") from exc
