# Spec: Bot de Exportação Diária de Laudos — TeleRetinografia (Telessaúde Goiás)

> Fase 1 de 3 — Requisitos. Este documento é a fonte da verdade sobre O QUÊ construir e PARA QUEM. Não descreve como implementar (isso é `design.md`) nem em que ordem (isso é `tasks.md`).

**Slug:** `bot_teleoftamo`
**Status:** aprovado
**Criado em:** 2026-09-18

## Contexto

O usuário precisa acompanhar diariamente a quantidade de laudos de TeleRetinografia cadastrados no sistema Telessaúde Goiás (`tele.medicina.ufg.br`), filtrados por doença, para a campanha de Manaus/AM. Hoje esse processo é manual: fazer login, navegar até o módulo TeleRetinografia, aplicar filtros de estado/cidade e de cada doença, e exportar cada resultado em planilha. Um bot em Python com Selenium deve automatizar login e a extração diária dessas 4 planilhas (uma por doença), rodando sem intervenção humana todos os dias às 9h.

## Histórias de usuário

1. Como usuário do sistema Telessaúde Goiás, quero que o bot faça login automaticamente com minhas credenciais, para não precisar logar manualmente todos os dias.
2. Como usuário, quero que o bot navegue até TeleRetinografia > Consultar Laudos e aplique o filtro de Estado = Amazonas e Cidade = Manaus, para consultar os laudos da campanha correta.
3. Como usuário, quero que o bot filtre os laudos por cada uma das 4 doenças (Retinopatia diabética, Catarata, Degeneração Macular, Glaucoma) individualmente e exporte cada resultado em uma planilha XLS separada, para ter os dados organizados por doença.
4. Como usuário, quero que os arquivos exportados sejam salvos em uma pasta local organizada por data, para manter histórico das exportações diárias.
5. Como usuário, quero que o bot rode automaticamente todos os dias às 9h via Windows Task Scheduler, sem exigir interação manual.
6. Como usuário, quero que falhas de execução (login, site fora do ar, exportação, divergência de contagem) sejam registradas em um arquivo de log, para eu poder diagnosticar problemas depois.

## Critérios de aceite

### Login automático (história 1)

- **CA1.1** — QUANDO o bot for executado ENTÃO O SISTEMA DEVE ler as credenciais (email e senha) de um arquivo `.env` local, nunca hardcoded no código.
- **CA1.2** — QUANDO o bot acessar a URL de login do Telessaúde Goiás ENTÃO O SISTEMA DEVE preencher os campos Email e Senha e clicar em "Entrar".
- **CA1.3** — SE o login falhar (credenciais inválidas, timeout, erro de rede) ENTÃO O SISTEMA DEVE registrar o erro no log e encerrar a execução sem tentar as etapas seguintes.
- **CA1.4** — QUANDO o login for bem-sucedido ENTÃO O SISTEMA DEVE confirmar que a página Home foi carregada antes de prosseguir.

### Navegação e filtro de localização (história 2)

- **CA2.1** — QUANDO o login for concluído ENTÃO O SISTEMA DEVE clicar no módulo "TeleRetinografia" e em seguida em "Consultar Laudos".
- **CA2.2** — QUANDO a tela de Consulta de Laudos for carregada ENTÃO O SISTEMA DEVE selecionar "Amazonas" no campo Estado e "Manaus" no campo Cidade.
- **CA2.3** — O SISTEMA DEVE ler Estado/Cidade de um arquivo de configuração (não hardcoded no código Selenium), para permitir trocar a cidade-alvo no futuro sem alterar lógica.

### Exportação por doença (história 3)

- **CA3.1** — QUANDO o filtro de Estado/Cidade estiver aplicado ENTÃO O SISTEMA DEVE, para cada uma das 4 doenças (Retinopatia diabética, Catarata, Degeneração Macular, Glaucoma), marcar apenas o checkbox daquela doença, clicar em "Consultar" e depois em "Exportar XLS".
- **CA3.2** — QUANDO uma exportação for concluída ENTÃO O SISTEMA DEVE conferir que o número de linhas de dados no arquivo XLS baixado corresponde ao número de registros exibido pelo site (ex.: "Exibindo registros de X a Y de Z encontrados") para aquele filtro.
- **CA3.3** — SE o número de linhas no arquivo não corresponder ao número de registros do site ENTÃO O SISTEMA DEVE registrar essa divergência no log como erro.

### Armazenamento dos arquivos (história 4)

- **CA4.1** — QUANDO uma planilha for exportada ENTÃO O SISTEMA DEVE salvá-la em `output/<AAAA-MM-DD>/<nome-da-doenca>.xlsx`, onde `<AAAA-MM-DD>` é a data da execução.
- **CA4.2** — O SISTEMA DEVE gerar 4 arquivos por execução, um por doença, com nomes identificáveis (ex.: `retinopatia_diabetica.xlsx`, `catarata.xlsx`, `degeneracao_macular.xlsx`, `glaucoma.xlsx`).

### Execução agendada (história 5)

- **CA5.1** — O SISTEMA DEVE ser executável como um único script Python (ponto de entrada), sem loop interno, compatível com ser disparado pelo Windows Task Scheduler.
- **CA5.2** — QUANDO executado sem interação humana ENTÃO O SISTEMA DEVE completar login, navegação e as 4 exportações sem exigir nenhum input manual.

### Log e tratamento de erro (história 6)

- **CA6.1** — QUANDO qualquer etapa falhar (login, navegação, filtro, exportação, validação de contagem) ENTÃO O SISTEMA DEVE registrar data/hora, etapa e mensagem de erro em um arquivo de log local.
- **CA6.2** — QUANDO a execução for concluída com sucesso ENTÃO O SISTEMA DEVE registrar no log um resumo (quantas planilhas geradas e a contagem de registros por doença).

## Fora de escopo

- Notificação por email/Slack/outro canal em caso de erro — fica só no log por enquanto, é uma possível iteração futura.
- Suporte a cidades/estados além de Manaus/Amazonas nesta primeira versão — o mecanismo de configuração é previsto (CA2.3), mas só será usado com Manaus por ora.
- Tratamento de captcha ou autenticação multifator — o sistema atual não exige nenhum dos dois; se isso mudar no futuro, não está coberto por esta spec.
- Qualquer funcionalidade dos módulos "Campanhas" ou "Exames" (cadastro) do TeleRetinografia — o escopo é exclusivamente "Consultar Laudos".
- Dashboard, interface gráfica ou relatórios agregados além das 4 planilhas brutas exportadas.
- Execução em servidor/nuvem — assume-se execução local, na máquina do próprio usuário, via Windows Task Scheduler.
- Retenção/limpeza automática de pastas antigas em `output/` — o histórico por data se acumula sem rotina de expurgo nesta versão.

## Dúvidas resolvidas

- **Site e autorização**: sistema institucional Telessaúde Goiás (UFG), conta própria do usuário — uso autorizado.
- **Mecanismo de login**: apenas email e senha, sem captcha nem 2FA.
- **Tarefas pós-login**: navegar TeleRetinografia → Consultar Laudos, filtrar Estado=Amazonas/Cidade=Manaus, e para cada uma das 4 doenças aplicar o filtro e exportar via botão nativo "Exportar XLS" do site.
- **Critério de sucesso**: contagem de linhas nas planilhas exportadas deve bater com o número de registros retornado pelo site para aquele filtro.
- **Frequência de execução**: diariamente às 9h.
- **Local/nome dos arquivos de saída**: pasta local `output/<data>/`, um arquivo por doença, mantendo histórico por dia (sem sobrescrever execuções anteriores).
- **Armazenamento de credenciais**: arquivo `.env` local, fora do controle de versão.
- **Agendamento**: Windows Task Scheduler chama o script Python uma vez; o script não mantém loop/agendamento interno.
- **Tratamento de erro**: registrar em arquivo de log local; sem notificação externa nesta versão.
