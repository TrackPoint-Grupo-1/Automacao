import streamlit as st
from PIL import Image
import pytesseract


# Função para autenticar o usuário
def check_login(username, password):
    # Dados de login simples (usuário: MABASIL, senha: 181004)
    if username == "MABASIL" and password == "181004":
        return True
    return False


# Configuração do caminho do Tesseract (caso necessário, no Windows)
# Tente descomentar a linha abaixo e forneça o caminho correto do tesseract no seu sistema
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Configuração da página
st.set_page_config(page_title="Atendimento ao Cliente", page_icon=":clipboard:", layout="wide")

# Função para adicionar estilo CSS
st.markdown("""
    <style>
        /* Estilo para o título */
        .title {
            font-size: 36px;
            font-weight: bold;
            color: #0078D4;
            text-align: center;
            margin-top: 20px;
        }

        /* Estilo para o subtítulo */
        .subtitle {
            font-size: 18px;
            color: #666666;
            text-align: center;
            margin-bottom: 40px;
        }

        /* Estilo para o container do upload */
        .upload-container {
            background-color: #f7f7f7;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
            margin: 0 auto;
            width: 70%;
        }

        /* Estilo para a imagem do atestado */
        .uploaded-image {
            border: 2px solid #ddd;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            width: 100%;
        }

        /* Estilo para mensagens de sucesso */
        .success-message {
            color: #28a745;
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            margin-top: 20px;
        }

        /* Rodapé */
        .footer {
            text-align: center;
            margin-top: 40px;
            font-size: 14px;
            color: #999999;
        }
    </style>
""", unsafe_allow_html=True)


# Página de login
def login_page():
    st.markdown('<p class="title">Página de Login</p>', unsafe_allow_html=True)

    # Campos de login
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    # Botão de login
    if st.button("Entrar"):
        if check_login(username, password):
            st.session_state.logged_in = True  # Marca como logado
        else:
            st.error("Credenciais inválidas. Tente novamente.")


# Verifica se o usuário está logado
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Exibe a tela de login se o usuário não estiver logado
if not st.session_state.logged_in:
    login_page()

else:
    # Tela após login
    # Sidebar
    st.sidebar.title("Boas vindas!")
    st.sidebar.subheader("O que você deseja fazer?")
    sidebar_option = st.sidebar.radio("Escolha uma opção:", ("Enviar Atestado", "Informações"))

    # Lógica para cada opção da sidebar
    if sidebar_option == "Enviar Atestado":
        # Título e subtítulo
        st.markdown('<p class="title">Atendimento ao Cliente</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Envie o seu atestado médico em formato de imagem para análise.</p>',
                    unsafe_allow_html=True)

        # Caixa de upload de arquivo
        uploaded_file = st.file_uploader("Escolha um arquivo (JPEG, PNG, JPG)", type=["jpg", "jpeg", "png"])

        if uploaded_file is not None:
            # Exibe a imagem enviada
            image = Image.open(uploaded_file)
            st.image(image, caption="Atestado Enviado", output_format="PNG", channels="RGB")

            # Exibe mensagem de sucesso
            st.markdown('<p class="success-message">Arquivo enviado com sucesso!</p>', unsafe_allow_html=True)

            # Tenta ler o texto da imagem utilizando o pytesseract (OCR)
            text = pytesseract.image_to_string(image)

            if text:
                st.subheader("Texto Detectado na Imagem:")
                st.write(text)
            else:
                st.warning("Nenhum texto foi detectado na imagem.")

            # Salva o arquivo em disco
            with open("atestado_enviado.jpg", "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.write("O seu atestado foi salvo com sucesso.")

    elif sidebar_option == "Informações":
        # Exibe informações na área principal
        st.markdown('<p class="title">Informações</p>', unsafe_allow_html=True)
        st.write(
            "Aqui você pode enviar seu atestado médico para análise. O atestado será verificado por nossa equipe e você será "
            "contatado em breve para um retorno. Se tiver dúvidas, entre em contato conosco através da nossa central de "
            "atendimentos."
        )

    # Rodapé
    st.markdown('<div class="footer">© 2025 Trackpoint | Todos os direitos reservados</div>', unsafe_allow_html=True)