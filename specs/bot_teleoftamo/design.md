# Design: Bot de Exportação Diária de Laudos — TeleRetinografia (Telessaúde Goiás)

> Fase 2 de 3 — Design técnico. Descreve COMO atender `spec.md`. Toda decisão aqui deve rastrear até um ou mais critérios de aceite da spec.

**Slug:** `bot_teleoftamo`
**Status:** aprovado
**Spec relacionada:** `spec.md`

## Resumo da abordagem

Script Python único (sem daemon/loop interno) que usa Selenium + Chrome para logar no Telessaúde Goiás, navegar até TeleRetinografia → Consultar Laudos, aplicar o filtro de localização e, para cada uma das 4 doenças, aplicar o filtro e acionar o botão nativo "Exportar XLS" do próprio site (evita parsing de HTML/paginação — o site já gera a planilha). O bot aguarda o download, valida a contagem de linhas contra o texto "Exibindo registros de X a Y de Z encontrados", move o arquivo para `output/<data>/<doenca>.xlsx`, e registra tudo em log. Selenium 4.6+ resolve o chromedriver automaticamente via Selenium Manager, sem instalação manual de driver. O agendamento diário às 9h fica a cargo do Windows Task Scheduler chamando um `.bat` que ativa o venv e roda `python -m src.main`.

## Arquivos e componentes afetados

Projeto novo (`C:\Users\amon\projects\bot_teleoftamo`), estrutura proposta:

- `requirements.txt` — `selenium`, `python-dotenv`, `openpyxl`.
- `.env.example` / `.env` (gitignored) — `TELESSAUDE_EMAIL`, `TELESSAUDE_SENHA`.
- `config.json` — `{"estado": "Amazonas", "cidade": "Manaus"}`; ponto único de configuração de localização (atende CA2.3).
- `.gitignore` — ignora `.env`, `output/`, `logs/`, `__pycache__/`, `.venv/`.
- `src/__init__.py`
- `src/config.py` — carrega `.env` (via `python-dotenv`) e `config.json`; expõe um objeto `Settings` (email, senha, estado, cidade, paths de output/logs).
- `src/logger.py` — configura `logging` para gravar em `logs/<data>.log` (formato timestamp, nível, etapa, mensagem) e também no console.
- `src/browser.py` — `build_driver(headless: bool) -> WebDriver`: monta `ChromeOptions` (prefs de download automático sem prompt, `download.default_directory` apontando para uma pasta de staging temporária, `--headless=new` quando aplicável) e, se headless, habilita download via CDP (`Page.setDownloadBehavior`).
- `src/locators.py` — centraliza todos os seletores CSS/XPath usados (campos de login, botão Entrar, card "TeleRetinografia", link "Consultar Laudos", selects de Estado/Cidade, checkboxes de doença, botão Consultar, botão Exportar XLS, texto "Exibindo registros..."). Ponto único de manutenção se o site mudar o HTML.
- `src/auth.py` — `login(driver, settings)`: navega até a URL de login, preenche email/senha, clica em Entrar, espera a Home carregar (elemento âncora pós-login) ou lança `LoginError`.
- `src/navigation.py` — `open_consulta_laudos(driver)`: clica no card TeleRetinografia → Consultar Laudos; `apply_location_filter(driver, estado, cidade)`: seleciona Estado e Cidade nos `<select>`.
- `src/export.py` — `DISEASES` (lista fixa das 4 doenças → locator do checkbox + nome de arquivo de saída); `export_disease(driver, disease, staging_dir) -> ExportResult`: desmarca outros checkboxes, marca o da doença, clica Consultar, lê o texto de contagem total, clica Exportar XLS, aguarda o arquivo aparecer na pasta de staging (polling com timeout), retorna caminho do arquivo + contagem esperada.
- `src/validation.py` — `count_rows(xlsx_path) -> int` (via `openpyxl`, conta linhas de dados desconsiderando cabeçalho); `parse_total_registros(texto) -> int` (regex sobre "de um total de N encontrados").
- `src/storage.py` — `move_to_output(staging_path, data_execucao, disease) -> Path`: cria `output/<AAAA-MM-DD>/` se não existir e move/renomeia o arquivo.
- `src/main.py` — orquestra: configura logger → carrega settings → sobe driver → login → navega → aplica filtro de localização → para cada doença: exporta, valida contagem, move para output, loga resultado → loga resumo final → fecha driver. Envolve cada etapa em try/except que loga a etapa+erro (CA6.1) e interrompe a execução (CA1.3); usa `sys.exit(1)` em caso de falha para o Task Scheduler refletir status via código de saída.
- `run.bat` — ativa `.venv` e roda `python -m src.main`; é o alvo configurado no Windows Task Scheduler.
- `README.md` — instruções de instalação (Python, `pip install -r requirements.txt`), configuração do `.env`/`config.json`, e passo a passo de criação da tarefa agendada no Task Scheduler (gatilho diário 9h, ação = `run.bat`, "Executar estando o usuário conectado ou não").

## Modelo de dados

Não há banco de dados. Único "esquema" é o arquivo `config.json`:

```json
{
  "estado": "Amazonas",
  "cidade": "Manaus"
}
```

E a estrutura de saída em disco: `output/<AAAA-MM-DD>/{retinopatia_diabetica,catarata,degeneracao_macular,glaucoma}.xlsx`.

## Contratos de interface

- `Settings.from_env_and_file(env_path, config_path) -> Settings` — falha rápido (exceção clara) se `TELESSAUDE_EMAIL`/`TELESSAUDE_SENHA` não estiverem definidos.
- `login(driver: WebDriver, settings: Settings) -> None` — levanta `LoginError` se a Home não carregar dentro do timeout.
- `apply_location_filter(driver: WebDriver, estado: str, cidade: str) -> None` — levanta `FiltroError` se a opção `cidade` não existir no `<select>` (ex.: cidade digitada errado no `config.json`).
- `export_disease(driver: WebDriver, disease: DiseaseSpec, staging_dir: Path, timeout: int) -> ExportResult` onde `ExportResult = {arquivo: Path, total_esperado: int}`. Levanta `ExportError` se o download não aparecer dentro do timeout.
- `count_rows(xlsx_path: Path) -> int`.
- Contrato de validação em `main.py`: `if count_rows(arquivo) != total_esperado: log.error(...)` (CA3.3) — não aborta as demais doenças, só registra a divergência daquela doença e segue para a próxima (falha isolada por doença, não devem gerar erro total ao ponto de gerar as outras 3 planilhas).

## Alternativas consideradas

- **Fazer scraping da tabela HTML em vez de usar "Exportar XLS"**: descartado — o site já oferece exportação nativa, reimplementar isso à mão seria mais trabalho e mais frágil a mudanças de layout, sem ganho real.
- **webdriver-manager para gerenciar o ChromeDriver**: descartado em favor do Selenium Manager embutido (Selenium ≥ 4.6), que já resolve a versão do driver automaticamente e elimina uma dependência extra.
- **pandas para ler o XLSX e contar linhas**: descartado — `openpyxl` sozinho já conta linhas sem precisar da dependência pesada do pandas.
- **YAML para `config.json`**: descartado — JSON via `json` da stdlib evita depender de `pyyaml` para uma config de 2 campos.
- **Bot com loop interno + `schedule`/`APScheduler`**: descartado conforme decisão do usuário — Windows Task Scheduler é mais simples e confiável, e o script não precisa ficar residente em memória o dia todo.

## Rastreabilidade

| Critério de aceite (spec.md) | Como este design atende |
|---|---|
| CA1.1 | `src/config.py` lê `TELESSAUDE_EMAIL`/`TELESSAUDE_SENHA` de `.env` via `python-dotenv`; nunca hardcoded. |
| CA1.2 | `src/auth.py::login` preenche os campos via `src/locators.py` e clica em Entrar. |
| CA1.3 | `login` levanta `LoginError`; `main.py` captura, loga a etapa "login" e encerra (`sys.exit(1)`) sem prosseguir. |
| CA1.4 | `login` espera um elemento âncora da Home (ex.: o card "TeleRetinografia") antes de retornar com sucesso. |
| CA2.1 | `src/navigation.py::open_consulta_laudos` clica no card TeleRetinografia e no link Consultar Laudos. |
| CA2.2 | `src/navigation.py::apply_location_filter` seleciona Estado/Cidade nos `<select>`. |
| CA2.3 | Estado/Cidade vêm de `config.json`, lido por `src/config.py` — trocar cidade é editar um valor, sem tocar código. |
| CA3.1 | `src/export.py::export_disease`, chamado em loop sobre `DISEASES` em `main.py`, marca só o checkbox da doença, clica Consultar e Exportar XLS. |
| CA3.2 | `export_disease` captura o texto de contagem (via `parse_total_registros`); `main.py` compara com `count_rows(arquivo)` após o download. |
| CA3.3 | Divergência entre `total_esperado` e `count_rows` é logada como erro em `main.py`, identificando a doença. |
| CA4.1 | `src/storage.py::move_to_output` grava em `output/<AAAA-MM-DD>/<doenca>.xlsx`. |
| CA4.2 | `DISEASES` tem exatamente 4 entradas com nomes de arquivo fixos; `main.py` itera todas. |
| CA5.1 | `src/main.py` é um script único chamável via `python -m src.main`; `run.bat` é o alvo do Task Scheduler. Sem loop/agendador interno. |
| CA5.2 | `src/browser.py` sobe o Chrome em modo headless com download habilitado via CDP; todo o fluxo (login → export) roda sem input manual. |
| CA6.1 | `src/logger.py` configura log em arquivo; cada etapa (`login`, `navegação`, `filtro`, `export:<doença>`, `validação:<doença>`) loga erro com contexto ao falhar. |
| CA6.2 | Ao final de `main.py`, um log de nível INFO resume quantas planilhas foram geradas e a contagem por doença. |

## Estratégia de verificação

- **Manual, ambiente real (principal forma de verificação aqui — não há como mockar o SSO da UFG de forma confiável)**: rodar `python -m src.main` primeiro com `headless=False` para inspecionar visualmente cada etapa (login, navegação, filtros, download) durante a implementação, depois validar novamente em modo headless antes de considerar pronto para o Task Scheduler.
- **Testes unitários (com `pytest`) para a lógica pura, sem depender do navegador**:
  - `parse_total_registros`: casos com texto real capturado do site ("Exibindo registros de 1 a 25 de um total de 1553 encontrados.") e variações de plural/zero registros.
  - `count_rows`: contra arquivos `.xlsx` de fixture com N linhas conhecidas.
  - `Settings.from_env_and_file`: erro claro quando `.env` está incompleto.
- **Verificação de CA3.2/CA3.3 em execução real**: comparar manualmente, numa primeira rodada supervisionada, o total mostrado na tela para cada doença com o total logado pelo bot, confirmando que a extração dos dois números bate.
- **Verificação de CA5.1/CA5.2**: criar a tarefa no Task Scheduler, disparar manualmente uma vez ("Executar" no Task Scheduler) e confirmar que roda do início ao fim sem nenhuma janela interativa/prompt, gerando as 4 planilhas e o log.
