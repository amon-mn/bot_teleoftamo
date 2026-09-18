# Tasks: Bot de Exportação Diária de Laudos — TeleRetinografia (Telessaúde Goiás)

> Fase 3 de 3 — Checklist de implementação. Cada tarefa é pequena, testável, e referencia o(s) critério(s) de aceite que fecha. Marque `[x]` conforme `/spec implement` for concluindo.

**Slug:** `bot_teleoftamo`
**Status:** rascunho
**Design relacionado:** `design.md`

## Tarefas

### Ambiente e estrutura base

- [ ] **1.1** Instalar Python 3.x nesta máquina (hoje só existe o alias stub da Microsoft Store) e confirmar `python --version` funcionando — atende: pré-requisito de todas as tarefas seguintes — arquivos: N/A (ambiente da máquina)
- [ ] **1.2** Criar estrutura inicial do projeto (`src/__init__.py`, `requirements.txt` com `selenium`, `python-dotenv`, `openpyxl`, `pytest`) e criar/ativar um venv — atende: infraestrutura — arquivos: `requirements.txt`, `src/__init__.py` — depende de: 1.1
- [ ] **1.3** Criar `.gitignore` (`.env`, `output/`, `logs/`, `__pycache__/`, `.venv/`) — atende: proteção das credenciais de CA1.1 — arquivos: `.gitignore`
- [ ] **1.4** Criar `.env.example` (`TELESSAUDE_EMAIL`, `TELESSAUDE_SENHA`) e `config.json` (`estado`, `cidade` com valores Amazonas/Manaus) — atende: CA1.1, CA2.3 — arquivos: `.env.example`, `config.json`

### Config e logging

- [ ] **2.1** Implementar `src/config.py` com `Settings.from_env_and_file`, lendo `.env` via `python-dotenv` e `config.json`, com erro claro se `TELESSAUDE_EMAIL`/`TELESSAUDE_SENHA` faltarem — atende: CA1.1, CA2.3 — arquivos: `src/config.py` — depende de: 1.4
- [ ] **2.2** Implementar `src/logger.py` configurando log em arquivo (`logs/<data>.log`) e console — atende: CA6.1, CA6.2 — arquivos: `src/logger.py` — depende de: 1.2

### Navegador

- [ ] **3.1** Implementar `src/browser.py::build_driver(headless)` com `ChromeOptions` (download automático sem prompt, diretório de staging, `--headless=new` opcional, CDP `Page.setDownloadBehavior` quando headless) — atende: CA5.2 — arquivos: `src/browser.py` — depende de: 1.2

### Mapeamento do site (requer inspeção ao vivo)

- [ ] **4.1** Logar manualmente no site com o Chrome DevTools aberto e mapear os seletores reais (campos email/senha, botão Entrar, âncora da Home, card "TeleRetinografia", link "Consultar Laudos", selects de Estado/Cidade, os 4 checkboxes de doença, botão Consultar, botão "Exportar XLS", elemento com o texto "Exibindo registros...") em `src/locators.py` — atende: base para CA1.2, CA2.1, CA2.2, CA3.1 — arquivos: `src/locators.py` — depende de: 3.1

### Autenticação

- [ ] **5.1** Implementar `src/auth.py::login` (preenche email/senha, clica Entrar, espera âncora da Home, levanta `LoginError` em timeout/falha) — atende: CA1.2, CA1.3, CA1.4 — arquivos: `src/auth.py` — depende de: 4.1, 2.1, 2.2

### Navegação e filtro de localização

- [ ] **6.1** Implementar `src/navigation.py::open_consulta_laudos` (clica TeleRetinografia → Consultar Laudos) — atende: CA2.1 — arquivos: `src/navigation.py` — depende de: 4.1
- [ ] **6.2** Implementar `src/navigation.py::apply_location_filter` (seleciona Estado/Cidade a partir do `Settings`, levanta `FiltroError` se a cidade não existir no select) — atende: CA2.2, CA2.3 — arquivos: `src/navigation.py` — depende de: 6.1

### Validação de contagem (lógica pura, testável sem navegador)

- [ ] **7.1** Implementar `src/validation.py::parse_total_registros` (regex sobre "de um total de N encontrados") com testes unitários cobrindo variações de texto — atende: CA3.2 — arquivos: `src/validation.py`, `tests/test_validation.py`
- [ ] **7.2** Implementar `src/validation.py::count_rows` (conta linhas de dados de um `.xlsx` via `openpyxl`) com testes unitários usando arquivos de fixture — atende: CA3.2 — arquivos: `src/validation.py`, `tests/test_validation.py` — depende de: 7.1

### Exportação por doença

- [ ] **8.1** Definir `DISEASES` em `src/export.py` (as 4 doenças, cada uma com locator do checkbox e nome de arquivo de saída) — atende: CA4.2 — arquivos: `src/export.py` — depende de: 4.1
- [ ] **8.2** Implementar `src/export.py::export_disease` (marca só o checkbox da doença, clica Consultar, captura o texto de total, clica Exportar XLS, aguarda o arquivo aparecer no staging com timeout, levanta `ExportError` se não aparecer) — atende: CA3.1 — arquivos: `src/export.py` — depende de: 8.1, 3.1

### Armazenamento

- [ ] **9.1** Implementar `src/storage.py::move_to_output` (cria `output/<AAAA-MM-DD>/` e move/renomeia o arquivo exportado) — atende: CA4.1 — arquivos: `src/storage.py`

### Orquestração

- [ ] **10.1** Implementar `src/main.py` orquestrando: logger → settings → driver → login → navegação → filtro de localização → loop nas 4 doenças (export + validação de contagem, logando divergência sem abortar as demais) → log de resumo final → fecha driver; cada etapa envolta em try/except que loga e, para falhas não isoladas por doença (login, navegação, filtro), encerra com `sys.exit(1)` — atende: CA1.3, CA3.3, CA5.1, CA6.1, CA6.2 — arquivos: `src/main.py` — depende de: 2.1, 2.2, 3.1, 5.1, 6.2, 7.1, 7.2, 8.2, 9.1

### Agendamento

- [ ] **11.1** Criar `run.bat` (ativa o venv e roda `python -m src.main`) — atende: CA5.1 — arquivos: `run.bat` — depende de: 10.1
- [ ] **11.2** Escrever `README.md` com instruções de instalação, configuração de `.env`/`config.json`, e passo a passo de criação da tarefa no Windows Task Scheduler (gatilho diário 9h, ação = `run.bat`, "Executar estando o usuário conectado ou não") — atende: CA5.1 — arquivos: `README.md` — depende de: 11.1

### Verificação end-to-end

- [ ] **12.1** Rodar o bot end-to-end com `headless=False`, validar visualmente cada etapa (login, navegação, filtros, download, contagem) e corrigir seletores/timing se necessário — atende: verificação de CA1.*, CA2.*, CA3.* — depende de: 10.1
- [ ] **12.2** Rodar o bot end-to-end em modo headless e conferir que as 4 planilhas em `output/<data>/` e o log em `logs/<data>.log` foram gerados corretamente, sem nenhuma janela/prompt interativo — atende: CA5.2, CA6.2 — depende de: 12.1
- [ ] **12.3** Criar a tarefa no Windows Task Scheduler apontando para `run.bat` e disparar manualmente ("Executar") para confirmar que roda do início ao fim sem intervenção — atende: CA5.1, CA5.2 — depende de: 11.2, 12.2

## Notas de execução

<!-- Preenchido durante /spec implement: decisões tomadas no meio do caminho, desvios do design original e por quê, bloqueios encontrados. -->
