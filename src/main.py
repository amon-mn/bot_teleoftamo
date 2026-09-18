from __future__ import annotations

import sys
import tempfile
import time
from datetime import date
from pathlib import Path

from selenium.common.exceptions import TimeoutException

from src.auth import LoginError, login
from src.browser import build_driver
from src.config import ConfigError, Settings
from src.export import DISEASES, ExportError, export_disease
from src.logger import setup_logger
from src.navigation import FiltroError, apply_location_filter, open_consulta_laudos
from src.storage import move_to_output
from src.validation import ContagemError, count_rows


def run(headless: bool = True, delay: float = 0.0) -> None:
    logger = setup_logger()

    try:
        settings = Settings.from_env_and_file()
    except ConfigError as exc:
        logger.error(f"config: {exc}")
        sys.exit(1)

    data_execucao = date.today()

    with tempfile.TemporaryDirectory(prefix="bot_teleoftamo_staging_") as staging_dir_str:
        staging_dir = Path(staging_dir_str)
        driver = build_driver(headless=headless, download_dir=staging_dir)

        try:
            try:
                login(driver, settings)
                logger.info("login: sucesso")
            except LoginError as exc:
                logger.error(f"login: {exc}")
                sys.exit(1)

            if delay:
                time.sleep(delay)

            try:
                open_consulta_laudos(driver)
                logger.info("navegacao: Consulta de Laudos aberta")
            except TimeoutException as exc:
                logger.error(f"navegacao: {exc}")
                sys.exit(1)

            if delay:
                time.sleep(delay)

            try:
                apply_location_filter(driver, settings.estado, settings.cidade)
                logger.info(f"filtro: estado={settings.estado} cidade={settings.cidade}")
            except FiltroError as exc:
                logger.error(f"filtro: {exc}")
                sys.exit(1)

            if delay:
                time.sleep(delay)

            resumo: list[tuple[str, int]] = []

            for disease in DISEASES:
                etapa = f"export:{disease.nome}"
                try:
                    resultado = export_disease(driver, disease, staging_dir, delay=delay)
                except (ExportError, ContagemError) as exc:
                    logger.error(f"{etapa}: {exc}")
                    continue

                contagem_real = count_rows(resultado.arquivo)
                if contagem_real != resultado.total_esperado:
                    logger.error(
                        f"validacao:{disease.nome}: contagem divergente "
                        f"(esperado={resultado.total_esperado}, arquivo={contagem_real})"
                    )

                destino = move_to_output(resultado.arquivo, data_execucao, disease)
                logger.info(f"{etapa}: {contagem_real} registros salvos em {destino}")
                resumo.append((disease.nome, contagem_real))

                if delay:
                    time.sleep(delay)

            detalhes = ", ".join(f"{nome}={contagem}" for nome, contagem in resumo)
            logger.info(f"resumo: {len(resumo)}/{len(DISEASES)} planilhas geradas — {detalhes}")
        finally:
            driver.quit()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Exportação diária de laudos TeleRetinografia")
    parser.add_argument(
        "--visible",
        action="store_true",
        help="Abre o Chrome visível em vez de headless (útil para acompanhar a automação acontecendo)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Segundos de pausa entre cada etapa/clique, para acompanhar visualmente (padrão: sem pausa)",
    )
    args = parser.parse_args()
    run(headless=not args.visible, delay=args.delay)
