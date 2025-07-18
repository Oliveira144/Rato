import streamlit as st
from collections import defaultdict

# Configuração da interface
st.set_page_config(page_title="FS AutoTracker", layout="wide")

st.title("🔮 Football Studio – Previsão Pós-Padrão (Auto Aprendizagem)")

# Inicialização de variáveis na sessão
if "historico" not in st.session_state:
    st.session_state.historico = []

if "ocorrencias" not in st.session_state:
    st.session_state.ocorrencias = defaultdict(lambda: defaultdict(int))

# Função para atualizar a base de dados de sequências
def registrar_sequencia(historico):
    if len(historico) < 5:
        return
    padrao = tuple(historico[1:5])  # os 4 anteriores
    proximo = historico[0]          # o mais recente
    st.session_state.ocorrencias[padrao][proximo] += 1

# Função para gerar sugestão com base em sequências anteriores
def sugerir_proxima(historico):
    if len(historico) < 4:
        return None, 0.0
    padrao = tuple(historico[:4])
    if padrao not in st.session_state.ocorrencias:
        return None, 0.0
    futuros = st.session_state.ocorrencias[padrao]
    sugestao = max(futuros, key=futuros.get)
    total = sum(futuros.values())
    confianca = futuros[sugestao] / total
    return sugestao, confianca

# Botões de inserção de resultado
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔴 RED"):
        st.session_state.historico.insert(0, "🔴")
        registrar_sequencia(st.session_state.historico)
with col2:
    if st.button("🔵 BLUE"):
        st.session_state.historico.insert(0, "🔵")
        registrar_sequencia(st.session_state.historico)
with col3:
    if st.button("🟡 TIE"):
        st.session_state.historico.insert(0, "🟡")
        registrar_sequencia(st.session_state.historico)

# Mostrar histórico atual (mais recente à esquerda)
st.subheader("📊 Histórico (mais recente à esquerda)")
st.markdown(" ".join(st.session_state.historico[:27]))

# Exibir sugestão baseada no que já ocorreu antes
sugestao, confianca = sugerir_proxima(st.session_state.historico)
if sugestao:
    st.success(f"🎯 Sugestão: **{sugestao}** com confiança de **{confianca:.2%}**")
else:
    st.info("⚠️ Sem dados suficientes para sugestão ainda.")

# Botão para limpar histórico (opcional)
if st.button("🧹 Limpar Histórico"):
    st.session_state.historico.clear()
    st.session_state.ocorrencias.clear()
    st.success("Histórico e dados limpos.")
