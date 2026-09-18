# Tasks: Bot de Exportação Diária de Laudos — TeleRetinografia (Telessaúde Goiás)

> Fase 3 de 3 — Checklist de implementação. Cada tarefa é pequena, testável, e referencia o(s) critério(s) de aceite que fecha. Marque `[x]` conforme `/spec implement` for concluindo.

**Slug:** `bot_teleoftamo`
**Status:** concluído
**Design relacionado:** `design.md`

## Tarefas

### Ambiente e estrutura base

- [x] **1.1** Instalar Python 3.x nesta máquina (hoje só existe o alias stub da Microsoft Store) e confirmar `python --version` funcionando — atende: pré-requisito de todas as tarefas seguintes — arquivos: N/A (ambiente da máquina)
- [x] **1.2** Criar estrutura inicial do projeto (`src/__init__.py`, `requirements.txt` com `selenium`, `python-dotenv`, `openpyxl`, `pytest`) e criar/ativar um venv — atende: infraestrutura — arquivos: `requirements.txt`, `src/__init__.py` — depende de: 1.1
- [x] **1.3** Criar `.gitignore` (`.env`, `output/`, `logs/`, `__pycache__/`, `.venv/`) — atende: proteção das credenciais de CA1.1 — arquivos: `.gitignore`
- [x] **1.4** Criar `.env.example` (`TELESSAUDE_EMAIL`, `TELESSAUDE_SENHA`) e `config.json` (`estado`, `cidade` com valores Amazonas/Manaus) — atende: CA1.1, CA2.3 — arquivos: `.env.example`, `config.json`

### Config e logging

- [x] **2.1** Implementar `src/config.py` com `Settings.from_env_and_file`, lendo `.env` via `python-dotenv` e `config.json`, com erro claro se `TELESSAUDE_EMAIL`/`TELESSAUDE_SENHA` faltarem — atende: CA1.1, CA2.3 — arquivos: `src/config.py` — depende de: 1.4
- [x] **2.2** Implementar `src/logger.py` configurando log em arquivo (`logs/<data>.log`) e console — atende: CA6.1, CA6.2 — arquivos: `src/logger.py` — depende de: 1.2

### Navegador

- [x] **3.1** Implementar `src/browser.py::build_driver(headless)` com `ChromeOptions` (download automático sem prompt, diretório de staging, `--headless=new` opcional, CDP `Page.setDownloadBehavior` quando headless) — atende: CA5.2 — arquivos: `src/browser.py` — depende de: 1.2

### Mapeamento do site (requer inspeção ao vivo)

- [x] **4.1** Logar manualmente no site com o Chrome DevTools aberto e mapear os seletores reais (campos email/senha, botão Entrar, âncora da Home, card "TeleRetinografia", link "Consultar Laudos", selects de Estado/Cidade, os 4 checkboxes de doença, botão Consultar, botão "Exportar XLS", elemento com o texto "Exibindo registros...") em `src/locators.py` — atende: base para CA1.2, CA2.1, CA2.2, CA3.1 — arquivos: `src/locators.py` — depende de: 3.1

### Autenticação

- [x] **5.1** Implementar `src/auth.py::login` (preenche email/senha, clica Entrar, espera âncora da Home, levanta `LoginError` em timeout/falha) — atende: CA1.2, CA1.3, CA1.4 — arquivos: `src/auth.py` — depende de: 4.1, 2.1, 2.2

### Navegação e filtro de localização

- [x] **6.1** Implementar `src/navigation.py::open_consulta_laudos` (clica TeleRetinografia → Consultar Laudos) — atende: CA2.1 — arquivos: `src/navigation.py` — depende de: 4.1
- [x] **6.2** Implementar `src/navigation.py::apply_location_filter` (seleciona Estado/Cidade a partir do `Settings`, levanta `FiltroError` se a cidade não existir no select) — atende: CA2.2, CA2.3 — arquivos: `src/navigation.py` — depende de: 6.1

### Validação de contagem (lógica pura, testável sem navegador)

- [x] **7.1** Implementar `src/validation.py::parse_total_registros` (regex sobre "de um total de N encontrados") com testes unitários cobrindo variações de texto — atende: CA3.2 — arquivos: `src/validation.py`, `tests/test_validation.py`
- [x] **7.2** Implementar `src/validation.py::count_rows` (conta linhas de dados de um `.xlsx` via `openpyxl`) com testes unitários usando arquivos de fixture — atende: CA3.2 — arquivos: `src/validation.py`, `tests/test_validation.py` — depende de: 7.1

### Exportação por doença

- [x] **8.1** Definir `DISEASES` em `src/export.py` (as 4 doenças, cada uma com locator do checkbox e nome de arquivo de saída) — atende: CA4.2 — arquivos: `src/export.py` — depende de: 4.1
- [x] **8.2** Implementar `src/export.py::export_disease` (marca só o checkbox da doença, clica Consultar, captura o texto de total, clica Exportar XLS, aguarda o arquivo aparecer no staging com timeout, levanta `ExportError` se não aparecer) — atende: CA3.1 — arquivos: `src/export.py` — depende de: 8.1, 3.1

### Armazenamento

- [x] **9.1** Implementar `src/storage.py::move_to_output` (cria `output/<AAAA-MM-DD>/` e move/renomeia o arquivo exportado) — atende: CA4.1 — arquivos: `src/storage.py`

### Orquestração

- [x] **10.1** Implementar `src/main.py` orquestrando: logger → settings → driver → login → navegação → filtro de localização → loop nas 4 doenças (export + validação de contagem, logando divergência sem abortar as demais) → log de resumo final → fecha driver; cada etapa envolta em try/except que loga e, para falhas não isoladas por doença (login, navegação, filtro), encerra com `sys.exit(1)` — atende: CA1.3, CA3.3, CA5.1, CA6.1, CA6.2 — arquivos: `src/main.py` — depende de: 2.1, 2.2, 3.1, 5.1, 6.2, 7.1, 7.2, 8.2, 9.1

### Agendamento

- [x] **11.1** Criar `run.bat` (ativa o venv e roda `python -m src.main`) — atende: CA5.1 — arquivos: `run.bat` — depende de: 10.1
- [x] **11.2** Escrever `README.md` com instruções de instalação, configuração de `.env`/`config.json`, e passo a passo de criação da tarefa no Windows Task Scheduler (gatilho diário 9h, ação = `run.bat`, "Executar estando o usuário conectado ou não") — atende: CA5.1 — arquivos: `README.md` — depende de: 11.1

### Verificação end-to-end

- [x] **12.1** Rodar o bot end-to-end com `headless=False`, validar visualmente cada etapa (login, navegação, filtros, download, contagem) e corrigir seletores/timing se necessário — atende: verificação de CA1.*, CA2.*, CA3.* — depende de: 10.1
- [x] **12.2** Rodar o bot end-to-end em modo headless e conferir que as 4 planilhas em `output/<data>/` e o log em `logs/<data>.log` foram gerados corretamente, sem nenhuma janela/prompt interativo — atende: CA5.2, CA6.2 — depende de: 12.1
- [x] **12.3** Criar a tarefa no Windows Task Scheduler apontando para `run.bat` e disparar manualmente ("Executar") para confirmar que roda do início ao fim sem intervenção — atende: CA5.1, CA5.2 — depende de: 11.2, 12.2

## Notas de execução

<!-- Preenchido durante /spec implement: decisões tomadas no meio do caminho, desvios do design original e por quê, bloqueios encontrados. -->

- **1.1**: Python 3.12.10 instalado via `winget install Python.Python.3.12` em `C:\Users\amon\AppData\Local\Programs\Python\Python312\`. A ferramenta Bash desta sessão mantém um PATH desatualizado (herdado antes da instalação) e não enxerga o novo `python` — comandos Python das próximas tarefas usarão PowerShell ou o caminho completo do executável.
- **1.2**: `.venv` criado com `python -m venv .venv` (usando o caminho completo do python.exe, já que o alias do PowerShell também estava com PATH desatualizado) e dependências instaladas com `pip install -r requirements.txt`. `selenium` resolveu para 4.49.0.
- **1.3**: `.gitignore` já existia desde o commit inicial (criado antes do início formal do `/spec implement`), com o conteúdo exato pedido; só validado e marcado.
- **2.1**: `Settings.from_env_and_file` implementado com `ConfigError` para email/senha ausentes e para `config.json` sem `estado`/`cidade`. Validado manualmente: caso feliz (lendo o `.env` real do usuário) e caso de erro (`.env` inexistente) ambos com o comportamento esperado.
- **2.2**: `setup_logger` grava em `logs/<AAAA-MM-DD>.log` e no console, formato `timestamp | nível | mensagem` (a "etapa" citada no design entra como prefixo da mensagem, ex.: `login: sucesso`, `export:catarata: falha`, convenção que `main.py` vai seguir). Validado manualmente o conteúdo do arquivo gerado.
- **3.1**: `build_driver(headless, download_dir)` — o contrato do design só cita `headless`, mas incluí `download_dir` como parâmetro explícito (necessário para apontar `download.default_directory`/CDP para a pasta de staging correta a cada chamada, em vez de fixar um caminho hardcoded dentro da função). Testado em modo headless contra `example.com`: Chrome já estava instalado na máquina, Selenium Manager resolveu o chromedriver sozinho, driver abriu e fechou sem erro.
- **4.1**: Mapeamento feito com login real (Chrome visível) em `tele.medicina.ufg.br`. Achados registrados em `src/locators.py`:
  - Login não é o form com hash MD5 embutido na Home (`#formulario-login`/`$.md5`) — esse é vestigial. O login real acontece em `/Sistema` → redireciona para SSO (`/sso/Account/Login`) com campos simples `#Username`/`#Password` e um botão `button[value='login']`, POST direto sem hash client-side.
  - Âncora pós-login (Home): card `a.tiles-toyo[href="/Sistema/Teleretinografia"]`.
  - `ConsultaLaudos` tem URL fixa e estável: `/Sistema/Teleretinografia/ConsultaLaudos`.
  - Selects `#Estado`/`#Cidade` e checkboxes `#RetinopatiaDiabetica`/`#Catarata`/`#DegeneracaoMacular`/`#Glaucoma` confirmados via inspeção do HTML real.
  - **Desvio a decidir com o usuário antes da tarefa 6.1**: tentei clicar no card `a.tiles-toyo` (conforme CA2.1 pede literalmente "clicar no card") e o Selenium lançou `ElementNotInteractableException`. Navegar direto para `CONSULTA_LAUDOS_URL` (já logado) funciona de forma confiável e é o que os testes de filtro usaram. Preciso alinhar se `navigation.py::open_consulta_laudos` deve (a) usar `driver.get(CONSULTA_LAUDOS_URL)` direto, ou (b) investir mais tempo fazendo o clique real no card funcionar (scroll into view / JS click) para seguir a letra da CA2.1.
  - **Achado adicional relevante para CA2.2/6.2**: as opções do `<select id="Cidade">` vêm em CAIXA ALTA do site (`"MANAUS"`), enquanto `config.json` tem `"Manaus"`. `apply_location_filter` (tarefa 6.2) precisa comparar sem diferenciar maiúsculas/minúsculas ao localizar a opção, senão sempre cairia no `FiltroError` mesmo com a cidade certa.
  - Fluxo completo testado manualmente: Estado=Amazonas, Cidade=Manaus, Catarata marcado, Consultar clicado → texto exibido foi exatamente `"Exibindo registros de 1 a 25 de um total de 193 encontrados."` (bate com o formato assumido no design) e o botão Exportar XLS ficou visível.
- **Decisão alinhada com o usuário**: `open_consulta_laudos` (tarefa 6.1) vai navegar direto para `CONSULTA_LAUDOS_URL` em vez de clicar no card + link, pelo motivo registrado na tarefa 4.1. `design.md` atualizado para refletir isso.
- **5.1**: `login()` implementado usando os seletores de `locators.py`. Testado com credenciais reais (login bem-sucedido, chegou em `/Sistema`) e com senha incorreta (headless, `LoginError` levantado após timeout esperando o card da Home).
- **6.1**: `open_consulta_laudos()` implementado com navegação direta por URL (conforme decisão da tarefa 4.1). Testado end-to-end em modo headless: login + navegação chegaram em `/Sistema/Teleretinografia/ConsultaLaudos` com o título "Consulta de Laudos".
- **6.2**: `apply_location_filter()` faz matching de texto sem diferenciar maiúsculas/minúsculas (`_select_by_text_ci`), conforme achado da tarefa 4.1. Aguarda via `WebDriverWait` o `<select id="Cidade">` ser populado pelo AJAX disparado ao trocar o Estado antes de tentar selecionar a cidade. Testado: caso feliz (Amazonas/Manaus → seleciona "MANAUS" no site) e caso de erro (cidade inexistente → `FiltroError`).
- **7.1**: `parse_total_registros` usa regex `de um total de\s+(\d+)\s+encontrados?` (aceita singular/plural), levanta `ContagemError` se não casar. 5 testes via pytest cobrindo o texto real capturado do site (193, 1553), singular, zero e texto inválido — todos passando.
- **7.2**: `count_rows` itera linhas a partir da 2ª (pula cabeçalho) e conta só linhas com pelo menos uma célula não-nula, evitando contar linhas em branco à toa por causa de `max_row`. Fixtures `.xlsx` geradas dinamicamente em `tmp_path` via `openpyxl.Workbook()` com 0/1/25/193 linhas de dados — todos os 4 casos + os 5 de `parse_total_registros` passando (9 no total).
- **8.1**: `DiseaseSpec` (nome, locator do checkbox, nome de arquivo) e `DISEASES` com as 4 doenças, reaproveitando os locators de `src/locators.py`. Nomes de arquivo exatamente como o CA4.2 pede (`retinopatia_diabetica.xlsx`, `catarata.xlsx`, `degeneracao_macular.xlsx`, `glaucoma.xlsx`).
- **8.2**: **Bug real encontrado e corrigido durante o teste**: a primeira versão esperava o texto de contagem conter a palavra "encontrado" (`EC.text_to_be_present_in_element`), mas o texto *anterior* ao clique em Consultar já continha essa palavra (era o total geral, 1553, sem filtro de doença) — então o wait retornava na hora, antes do AJAX do Consultar atualizar de verdade, e `parse_total_registros` capturava o número errado (1553 em vez de 193 para Catarata). Corrigido para esperar o texto *mudar* em relação ao valor capturado antes do clique. Validado com download real: Catarata filtrado por Manaus → total do site = 193, `count_rows` no arquivo baixado = 193, bateram exatamente.
- **9.1**: `move_to_output` recebe um `DiseaseSpec` (não só uma string) para reaproveitar `disease.arquivo` como nome final. Testado com arquivo fake em diretório temporário: cria `output/<data>/`, move (não copia — origem some), nome de destino e conteúdo corretos.
- **10.1**: staging usa `tempfile.TemporaryDirectory()` (efêmero, um por execução) — `driver.quit()` roda em `finally` *antes* de sair do bloco `with`, então o Windows já liberou o handle do arquivo quando o diretório temporário é apagado (mesma lição da tarefa 2.2). Rodei `python -m src.main` real e completo (headless, 4 doenças): login, navegação e filtro OK, `4/4 planilhas geradas` sem nenhuma divergência de contagem — `output/2026-09-18/{retinopatia_diabetica,catarata,degeneracao_macular,glaucoma}.xlsx` e `logs/2026-09-18.log` confirmados em disco.
- **11.1**: `run.bat` usa `cd /d "%~dp0"` para sempre rodar a partir do diretório do próprio script, independente de onde/como é chamado — importante porque o Task Scheduler não necessariamente inicia com o diretório do projeto como "Start in". Testado chamando o `.bat` pelo caminho completo a partir de outro diretório: rodou a pipeline completa de novo com sucesso, e `shutil.move` sobrescreveu os arquivos do mesmo dia sem erro (confirmado empiricamente antes de escrever o `.bat`).
  - **Ajuste pós-conclusão, pedido pelo usuário**: adicionado `>> logs\run_stdout.log 2>&1` como rede de segurança, já que o Task Scheduler roda sem console (com "Executar estando o usuário conectado ou não") e qualquer saída fora do `logger` (tracebacks antes do logger existir, warnings do `openpyxl`, erros do próprio `python`/venv) se perderia. Também precisou de `set PYTHONIOENCODING=utf-8` antes do `python`, senão acentos saíam corrompidos no arquivo (o Python usa o codepage do console do Windows por padrão ao ter stdout redirecionado). Confirmado via leitura binária do arquivo que o UTF-8 ficou correto — o que parecia corrompido era só a exibição do `Get-Content` do PowerShell no terminal, não o conteúdo real.
  - **Segundo ajuste pós-conclusão, pedido pelo usuário**: `>>` redirecionava tudo direto pro arquivo, sem nada aparecer no console ao rodar manualmente. Trocado por um "tee" via PowerShell (`python -u -m src.main 2>&1 | powershell -NoProfile -Command "..."`) — `-u` desliga o buffer do Python pra garantir streaming linha a linha. Primeira tentativa usou `Tee-Object -Encoding utf8`, mas `Tee-Object` não tem parâmetro `-Encoding` nesta versão do PowerShell (erro de binding) — e sem ele, grava em UTF-16, corrompendo tudo. Solução final: `ForEach-Object { $_; Add-Content ... -Encoding utf8 }`, que ecoa cada linha pro console e grava no arquivo em UTF-8 linha a linha. Resultado: console mostra o progresso ao vivo (era o pedido original do usuário) e `logs\run_stdout.log` fica em UTF-8 legível (com um BOM inofensivo no início).
  - **Terceiro ajuste pós-conclusão, pedido pelo usuário**: criado `run_visible.bat` separado (`python -m src.main --visible --delay 1.5`, com `pause` no final) para rodar com o Chrome visível sem mexer no `run.bat` usado pelo Task Scheduler (que precisa continuar headless e sem `pause`, já que "Executar estando o usuário conectado ou não" não tem ninguém pra apertar tecla nenhuma — um `pause` ali travaria a tarefa agendada para sempre). Adicionado `--delay SEGUNDOS` em `main.py` (propagado para `export_disease` em `src/export.py`, que ganhou um parâmetro `delay: float = 0.0` opcional e retrocompatível) para dar pausas visíveis entre login/navegação/filtro/cada doença e entre os cliques dentro de cada exportação (marcar checkbox → Consultar → ver contagem → Exportar XLS). Testado com `--delay 1.5`: ritmo perceptível confirmado, e os 9 testes de `pytest` continuam passando (mudança de assinatura é aditiva, sem quebrar nada existente).
- **11.2**: README cobre instalação, `.env`/`config.json`, execução manual (`run.bat` e um modo `headless=False` direto via `-c` para depuração visual), o passo a passo completo do Task Scheduler (incluindo o motivo de preencher "Iniciar em" mesmo o `.bat` já se autolocalizando), estrutura de saída e como rodar os testes.
- **12.1/12.2**: não repetidas como execuções isoladas no final — já foram cobertas organicamente durante a implementação: a tarefa 4.1 fez login/navegação/filtro/export com `headless=False` visível (você viu o Chrome abrir), a tarefa 8.2 validou contagem real (site vs. arquivo), e a tarefa 10.1 já rodou `python -m src.main` completo em modo headless duas vezes (uma direta, uma via `run.bat`), confirmando as 4 planilhas em `output/2026-09-18/` e o log em `logs/2026-09-18.log` sem nenhum prompt interativo.
- **12.3**: a pedido do usuário, a tarefa foi **criada mas não disparada** ("Executar" fica pendente para quando ele quiser). `Register-ScheduledTask` (PowerShell) retornou "Acesso negado" neste ambiente sandboxed (sem elevação); usei `schtasks.exe` como fallback, que funcionou sem precisar de elevação. Tarefa confirmada via `schtasks /query`: gatilho diário às 09:00 (próxima execução 19/09/2026), executando como `amon`. **Limitação conhecida e não resolvida por mim**: o modo de logon ficou "Interativo apenas", não "Executar estando o usuário conectado ou não" — esse último exige a senha da conta do Windows, que só pode ser fornecida pelo próprio usuário direto no diálogo do Task Scheduler (Propriedades → Geral), nunca via linha de comando por um agente. Documentado para o usuário como um passo manual restante.
