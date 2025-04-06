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
        .upload-container {
            background-color: #f7f7f7;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            margin: 0 auto;
            width: 70%;
        }
        .uploaded-image {
            border: 2px solid #ddd;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 100%;
        }
        .success-message {
            color: #28a745;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            margin-top: 20px;
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

def salvar_sessao(email):
    with open(SESSION_FILE, "w") as f:
        json.dump({"logged_in": True, "email": email}, f)

def carregar_sessao():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            dados = json.load(f)
            return dados.get("logged_in", False), dados.get("email")
    return False, None

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
            salvar_sessao(email)
            st.success("Login realizado com sucesso! Redirecionando...")
            time.sleep(2)
            st.rerun()
        else:
            st.error(resposta.get("error", "Falha ao realizar login."))


# ---------------------- Página Principal ----------------------

def pagina_principal():
    st.sidebar.title("Boas vindas!")
    st.sidebar.subheader("O que você deseja fazer?")
    sidebar_option = st.sidebar.radio("Escolha uma opção:", ("Enviar Atestado", "Informações"))

    # Inicializa estados
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "email" not in st.session_state:
        st.session_state["email"] = ""

    if sidebar_option == "Enviar Atestado":
        st.markdown('<p class="title">Atendimento ao Cliente</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Envie o seu atestado médico em formato de imagem para análise.</p>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Escolha um arquivo (JPEG, PNG, JPG)", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Atestado Enviado", output_format="PNG", channels="RGB")
            st.markdown('<p class="success-message">Arquivo enviado com sucesso!</p>', unsafe_allow_html=True)

            text = pytesseract.image_to_string(image)

            if text:
                st.subheader("Texto Detectado na Imagem:")
                st.write(text)
            else:
                st.warning("Nenhum texto foi detectado na imagem.")

            with open("atestado_enviado.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.write("O seu atestado foi salvo com sucesso.")

    elif sidebar_option == "Informações":
        st.markdown('<p class="title">Informações</p>', unsafe_allow_html=True)
        st.write(
            "Aqui você pode enviar seu atestado médico para análise. O atestado será verificado por nossa equipe e você será "
            "contatado em breve para um retorno. Se tiver dúvidas, entre em contato conosco através da nossa central de "
            "atendimentos."
        )

    st.markdown('<div class="footer">© 2025 Trackpoint | Todos os direitos reservados</div>', unsafe_allow_html=True)


# ---------------------- Roteamento ----------------------

logado, email = carregar_sessao()
if logado:
    st.session_state["logged_in"] = True
    st.session_state["email_usuario"] = email
    pagina_principal()
else:
    login_page()
