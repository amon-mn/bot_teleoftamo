from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Settings:
    email: str
    senha: str
    estado: str
    cidade: str
    output_dir: Path
    logs_dir: Path

    @classmethod
    def from_env_and_file(
        cls,
        env_path: Path = Path(".env"),
        config_path: Path = Path("config.json"),
        output_dir: Path = Path("output"),
        logs_dir: Path = Path("logs"),
    ) -> "Settings":
        load_dotenv(dotenv_path=env_path)

        email = os.getenv("TELESSAUDE_EMAIL")
        senha = os.getenv("TELESSAUDE_SENHA")
        if not email or not senha:
            raise ConfigError(
                f"TELESSAUDE_EMAIL e TELESSAUDE_SENHA devem estar definidos em {env_path}"
            )

        if not config_path.exists():
            raise ConfigError(f"Arquivo de configuração não encontrado: {config_path}")

        config = json.loads(config_path.read_text(encoding="utf-8"))
        estado = config.get("estado")
        cidade = config.get("cidade")
        if not estado or not cidade:
            raise ConfigError(f"'estado' e 'cidade' devem estar definidos em {config_path}")

        return cls(
            email=email,
            senha=senha,
            estado=estado,
            cidade=cidade,
            output_dir=output_dir,
            logs_dir=logs_dir,
        )
