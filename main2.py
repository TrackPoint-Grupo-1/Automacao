import time
import streamlit as st
import requests
from PIL import Image
import pytesseract
import os
import json

# Caminho para simular persistência da sessão
SESSION_FILE = "session.json"

# Configuração do Tesseract (caso necessário no Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Configuração da página
st.set_page_config(page_title="Atendimento ao Cliente", page_icon=":clipboard:", layout="wide")

# Base URL da API
API_URL = "http://127.0.0.1:5000"

# Estilo CSS
st.markdown("""
    <style>
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #0078D4;
            text-align: center;
            margin-top: 20px;
        }
        .subtitle {
            font-size: 18px;
            color: #666666;
            text-align: center;
            margin-bottom: 40px;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            font-size: 14px;
            color: #999999;
        }
    </style>
""", unsafe_allow_html=True)

# ---------------------- Sessão ----------------------
def salvar_sessao(email, cargo):
    with open(SESSION_FILE, "w") as f:
        json.dump({"logged_in": True, "email": email, "cargo": cargo}, f)

def carregar_sessao():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            dados = json.load(f)
            return dados.get("logged_in", False), dados.get("email"), dados.get("cargo")
    return False, None, None

def limpar_sessao():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)

# ---------------------- Login API ----------------------
def fazer_login(email, senha):
    try:
        resposta = requests.patch(
            f"{API_URL}/usuarios/login",
            json={"email": email, "senha": senha}
        )
        if resposta.status_code == 200:
            return True, resposta.json()
        else:
            return False, resposta.json()
    except Exception as e:
        return False, {"error": str(e)}

# ---------------------- Login Page ----------------------
def login_page():
    st.markdown('<p class="title">Página de Login</p>', unsafe_allow_html=True)

    email = st.text_input("E-mail")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        sucesso, resposta = fazer_login(email, senha)
        if sucesso:
            salvar_sessao(email, resposta["cargo"])
            st.success("Login realizado com sucesso! Redirecionando...")
            time.sleep(2)
            st.rerun()
        else:
            st.error(resposta.get("error", "Falha ao realizar login."))

# ---------------------- Página Principal ----------------------
def pagina_principal():
    st.sidebar.title("Boas vindas!")
    st.sidebar.subheader("O que você deseja fazer?")

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = True
    if "email" not in st.session_state:
        st.session_state["email"] = "junior@gmail.com"
    if "cargo_usuario" not in st.session_state:
        st.session_state["cargo_usuario"] = "Recursos Humanos"

    if st.session_state["cargo_usuario"] == "Recursos Humanos":
        sidebar_option = st.sidebar.radio("Escolha uma opção:", ("Enviar Atestado", "Informações", "Analisar Atestados"))
    else:
        sidebar_option = st.sidebar.radio("Escolha uma opção:", ("Enviar Atestado", "Informações"))

    if sidebar_option == "Enviar Atestado":
        enviar_atestado()
    elif sidebar_option == "Informações":
        mostrar_informacoes()
    elif sidebar_option == "Analisar Atestados":
        analisar_atestados()

    st.markdown('<div class="footer">© 2025 Trackpoint | Todos os direitos reservados</div>', unsafe_allow_html=True)

# ---------------------- Enviar Atestado ----------------------
def enviar_atestado():
    st.markdown('<p class="title">Atendimento ao Cliente</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Envie o seu atestado médico em formato de imagem para análise.</p>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Escolha um arquivo (JPEG, PNG, JPG)", type=["jpg", "jpeg", "png"])
    cid_input = st.text_input("Informe o CID, se houver (opcional)")

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Atestado Enviado", use_container_width=True)

        text = pytesseract.image_to_string(image)

        if text:
            st.subheader("Texto Detectado na Imagem:")
            st.write(text)
        else:
            st.warning("Nenhum texto foi detectado na imagem.")

        if st.button("📤 Enviar Atestado"):
            try:
                payload = {
                    "email": st.session_state["email"],
                    "cid": cid_input,
                    "texto_capturado": text
                }
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "insomnia/11.0.2"
                }
                response = requests.post(f"{API_URL}/atestados/criar", json=payload, headers=headers)
                response.raise_for_status()
                st.success("✅ Atestado enviado com sucesso!")
            except requests.RequestException as e:
                st.error("Erro ao enviar atestado: " + str(e))

# ---------------------- Informações ----------------------
def mostrar_informacoes():
    st.markdown('<p class="title">Informações</p>', unsafe_allow_html=True)
    st.write(
        "Aqui você pode enviar seu atestado médico para análise. O atestado será verificado por nossa equipe e você será "
        "contatado em breve para um retorno. Se tiver dúvidas, entre em contato conosco através da nossa central de "
        "atendimentos."
    )

# ---------------------- Analisar Atestados (RH) ----------------------

def analisar_atestados():
    st.markdown("""
        <h2 style='color:#4F8BF9; margin-bottom: 30px; text-align:center;'>📄 Analisar Atestados</h2>
    """, unsafe_allow_html=True)

    status_filtro = st.selectbox("🔍 Filtrar por status:", ["Pendente", "Todos", "Aprovado", "Rejeitado"], index=0)
    limite_por_pagina = st.selectbox("📦 Quantos atestados por página?", [5, 10, 15, 20], index=1)
    pagina = st.number_input("📄 Página:", min_value=1, value=1, step=1)

    params = {"page": pagina, "limit": limite_por_pagina}
    if status_filtro != "Todos":
        params["status"] = status_filtro

    try:
        resposta = requests.get(f"{API_URL}/atestados/paginado", params=params)
        resposta.raise_for_status()
        dados = resposta.json()

        st.markdown(f"""
            <p style='font-size:16px; color:#BBBBBB;'>
                🔢 <strong>Total de atestados:</strong> {dados['total']}
            </p>
        """, unsafe_allow_html=True)

        email_usuario_logado = st.session_state.get("email")
        atestados_visiveis = [a for a in dados["results"] if a["email"] != email_usuario_logado]

        if not atestados_visiveis:
            st.info("⚠️ Nenhum atestado disponível para análise. "
                    "Se você enviou um atestado, ele não será exibido aqui. "
                    "Outro colaborador deve avaliá-lo.")
        else:
            for atestado in atestados_visiveis:
                with st.container():
                    st.markdown(f"""
                        <div style="
                            background-color: #1e1e1e;
                            padding: 25px 30px;
                            margin: 20px 0;
                            border-radius: 12px;
                            box-shadow: 0 0 12px rgba(0, 0, 0, 0.4);
                            border: 1px solid #333333;
                            color: #f0f0f0;
                        ">
                            <h4 style='margin-bottom: 10px;'>🆔 Atestado #{atestado['id']}</h4>
                            <p><strong>📧 Email:</strong> {atestado['email']}</p>
                            <p><strong>📅 Data de Envio:</strong> {atestado['data_envio']}</p>
                            <p><strong>📌 Status:</strong> {atestado['status']}</p>
                            <p><strong>🧬 CID:</strong> {atestado['cid'] or "Não informado"}</p>
                            <p><strong>📝 Texto Capturado:</strong><br>
                            <span style="display:block; background-color:#2e2e2e; padding:10px; border-radius:8px; color:#e0e0e0; margin-top:5px;">
                                {atestado['texto_capturado']}
                            </span></p>
                    """, unsafe_allow_html=True)

                    if atestado['status'] == "Pendente":
                        col1, col2 = st.columns([1, 1])
                        with col1:
                            if st.button(f"✅ Aprovar", key=f"aprovar_{atestado['id']}"):
                                try:
                                    resposta_aprovar = requests.patch(
                                        f"{API_URL}/atestados/{atestado['id']}/aprovar",
                                        json={"email_usuario_logado": email_usuario_logado}
                                    )
                                    if resposta_aprovar.status_code == 200:
                                        st.success("✅ Atestado aprovado com sucesso!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Erro ao aprovar: {resposta_aprovar.text}")
                                except Exception as e:
                                    st.error(f"❌ Erro ao aprovar atestado: {e}")
                        with col2:
                            if st.button(f"❌ Rejeitar", key=f"rejeitar_{atestado['id']}"):
                                try:
                                    resposta_rejeitar = requests.patch(
                                        f"{API_URL}/atestados/{atestado['id']}/rejeitar",
                                        json={"email_usuario_logado": email_usuario_logado}
                                    )
                                    if resposta_rejeitar.status_code == 200:
                                        st.success("🚫 Atestado rejeitado com sucesso!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ Erro ao rejeitar: {resposta_rejeitar.text}")
                                except Exception as e:
                                    st.error(f"❌ Erro ao rejeitar atestado: {e}")

                    st.markdown("</div>", unsafe_allow_html=True)

    except requests.RequestException as e:
        st.error(f"🚨 Erro ao buscar atestados: {e}")

# ---------------------- Atualizar Status ----------------------
def atualizar_status(id_atestado, novo_status):
    try:
        url = f"{API_URL}/atestados/{id_atestado}/status"
        payload = {"status": novo_status}
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "insomnia/11.0.2"
        }
        response = requests.patch(url, json=payload, headers=headers)
        response.raise_for_status()
        st.success(f"Status do atestado {id_atestado} atualizado para '{novo_status}' com sucesso!")
        st.rerun()
    except requests.RequestException as e:
        st.error("Erro ao atualizar o status: " + str(e))

# ---------------------- Roteamento ----------------------
logado, email, cargo = carregar_sessao()
if logado:
    st.session_state["logged_in"] = True
    st.session_state["email"] = email
    st.session_state["cargo_usuario"] = cargo
    pagina_principal()
else:
    login_page()
