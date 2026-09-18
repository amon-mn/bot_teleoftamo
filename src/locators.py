from selenium.webdriver.common.by import By

LOGIN_URL = "https://tele.medicina.ufg.br/Sistema"
CONSULTA_LAUDOS_URL = "https://tele.medicina.ufg.br/Sistema/Teleretinografia/ConsultaLaudos"

# --- Login ---
CAMPO_EMAIL = (By.ID, "Username")
CAMPO_SENHA = (By.ID, "Password")
BOTAO_ENTRAR = (By.CSS_SELECTOR, "button[value='login']")

# --- Home (âncora pós-login) ---
CARD_TELERETINOGRAFIA = (By.CSS_SELECTOR, "a.tiles-toyo[href='/Sistema/Teleretinografia']")

# --- Consulta de Laudos: filtro de localização ---
SELECT_ESTADO = (By.ID, "Estado")
SELECT_CIDADE = (By.ID, "Cidade")

# --- Consulta de Laudos: checkboxes de doença ---
CHECKBOX_RETINOPATIA_DIABETICA = (By.ID, "RetinopatiaDiabetica")
CHECKBOX_CATARATA = (By.ID, "Catarata")
CHECKBOX_DEGENERACAO_MACULAR = (By.ID, "DegeneracaoMacular")
CHECKBOX_GLAUCOMA = (By.ID, "Glaucoma")

# --- Consulta de Laudos: ações ---
BOTAO_CONSULTAR = (By.CSS_SELECTOR, "button[onclick='Consultar()']")
BOTAO_EXPORTAR_XLS = (By.ID, "btn-imprimir-xls")

# --- Consulta de Laudos: contagem de resultados ---
TEXTO_CONTAGEM_REGISTROS = (By.CSS_SELECTOR, "div.grid-topo-detalhes")
