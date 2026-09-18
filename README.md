# bot_teleoftamo

Bot de exportação diária de laudos de TeleRetinografia (Telessaúde Goiás) para a campanha de Manaus/AM. Loga automaticamente no sistema, aplica os filtros de localização e doença, e exporta 4 planilhas (uma por doença) em `output/<data>/`.

Detalhes de requisitos e design técnico em [specs/bot_teleoftamo/](specs/bot_teleoftamo/).

## Pré-requisitos

- Python 3.x instalado (não o alias stub da Microsoft Store — confirme com `python --version`).
- Google Chrome instalado (o Selenium Manager resolve o chromedriver automaticamente).
- Uma conta válida no Telessaúde Goiás (`tele.medicina.ufg.br`).

## Instalação

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuração

1. Copie `.env.example` para `.env` e preencha com suas credenciais reais:

   ```
   TELESSAUDE_EMAIL=seu.email@exemplo.com
   TELESSAUDE_SENHA=sua-senha-aqui
   ```

   O `.env` está no `.gitignore` — nunca é versionado.

2. Ajuste `config.json` se precisar trocar o Estado/Cidade filtrados (hoje fixo em Amazonas/Manaus):

   ```json
   {
     "estado": "Amazonas",
     "cidade": "Manaus"
   }
   ```

## Rodando manualmente

```bat
run.bat
```

Isso ativa o venv e roda `python -m src.main`. As planilhas saem em `output/<AAAA-MM-DD>/` e o log da execução em `logs/<AAAA-MM-DD>.log`. Tudo que passa pelo terminal (incluindo eventuais erros fora do log estruturado) também é gravado em `logs/run_stdout.log`, como rede de segurança para quando não há console visível (caso do Task Scheduler).

Para acompanhar a automação acontecendo (ver o Chrome abrindo, logando e clicando pelas telas), rode:

```bat
run_visible.bat
```

Isso roda `python -m src.main --visible`, que sobe o Chrome com janela visível em vez de headless, e mantém o console aberto no final (`pause`) para você ler o resultado. Útil para depurar ou simplesmente ver o fluxo funcionando; o `run.bat` (usado pelo Task Scheduler) continua headless por padrão.

## Agendamento diário via Windows Task Scheduler

1. Abra o **Agendador de Tarefas** (Task Scheduler).
2. **Ação** → **Criar Tarefa...** (não "Tarefa Básica", para ter acesso a todas as opções).
3. Aba **Geral**:
   - Nome: `bot_teleoftamo`.
   - Marque **Executar estando o usuário conectado ou não**.
   - Marque **Executar com privilégios mais altos** (opcional, só se necessário no seu ambiente).
4. Aba **Gatilhos** → **Novo...**:
   - Iniciar a tarefa: **Diariamente**.
   - Horário: **09:00**.
   - Habilitado: marcado.
5. Aba **Ações** → **Novo...**:
   - Ação: **Iniciar um programa**.
   - Programa/script: caminho completo para `run.bat` (ex.: `C:\Users\amon\projects\bot_teleoftamo\run.bat`).
   - Iniciar em (opcional): `C:\Users\amon\projects\bot_teleoftamo` (o `run.bat` já se posiciona sozinho no diretório correto, mas preencher esse campo evita ambiguidade).
6. Aba **Condições**: desmarque "Iniciar a tarefa somente se o computador estiver com energia CA" se o agendamento precisar rodar mesmo em notebook na bateria.
7. Salve. O Windows vai pedir a senha da conta do usuário (necessário para "Executar estando o usuário conectado ou não").
8. Para testar sem esperar o horário: clique com o botão direito na tarefa → **Executar**. Confirme em `logs/<data>.log` e em `output/<data>/` que as 4 planilhas foram geradas.

## Estrutura de saída

```
output/
  2026-09-18/
    retinopatia_diabetica.xlsx
    catarata.xlsx
    degeneracao_macular.xlsx
    glaucoma.xlsx
logs/
  2026-09-18.log
  run_stdout.log
```

## Testes

```bat
.venv\Scripts\python.exe -m pytest
```

Cobre a lógica pura (parsing de contagem de registros e leitura de `.xlsx`), sem depender do navegador.
