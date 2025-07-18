import streamlit as st
from datetime import datetime
import pandas as pd

# Configuração da página
st.set_page_config(page_title="FS Pattern Master v1 – AI Estratégica 30x", layout="centered")
st.title("⚡ FS Pattern Master v1 – AI Estratégica 30x")

# Inicialização do estado
if "historico" not in st.session_state:
    st.session_state.historico = []
if "green" not in st.session_state:
    st.session_state.green = 0
if "red" not in st.session_state:
    st.session_state.red = 0
if "modo_g1" not in st.session_state:
    st.session_state.modo_g1 = False
if "ultima_sugestao" not in st.session_state:
    st.session_state.ultima_sugestao = None

# Funções auxiliares

def detectar_horario_de_risco():
    agora = datetime.now()
    dia = agora.weekday()  # segunda=0, domingo=6
    hora = agora.hour
    # Quinta feira 18h em diante, sexta, sabado e domingo todo dia
    return (dia == 3 and hora >= 18) or (dia in [4,5,6])

def inverter_cor(c):
    return {'R':'B','B':'R','T':'T'}.get(c, c)

def verificar_reescrita(col_atual, col_ref):
    # Verifica se col_atual == col_ref ou col_atual invertida == col_ref
    if col_atual == col_ref:
        return True
    invertida = [inverter_cor(c) for c in col_atual]
    if invertida == col_ref:
        return True
    return False

def extrair_linhas(hist):
    # Preenche com ' ' se menos de 27
    hist = ([' '] * (27 - len(hist))) + hist[-27:]
    linha1 = hist[0:9]
    linha2 = hist[9:18]
    linha3 = hist[18:27]
    return [linha1, linha2, linha3]

def gerar_colunas(linhas):
    colunas = []
    for i in range(9):
        colunas.append([linhas[0][i], linhas[1][i], linhas[2][i]])
    return colunas

# 14 padrões básicos - exemplo simplificado (você pode expandir!)
def padroes_basicos(hist):
    ultimos = hist[-9:]
    padrao = ''.join(ultimos[-3:])
    if padrao == 'RRR':
        return 'R', "Padrão básico: sequência de 3 Reds"
    if padrao == 'BBB':
        return 'B', "Padrão básico: sequência de 3 Blues"
    if padrao == 'RBR':
        return 'R', "Padrão básico: padrão alternado RBR"
    if padrao == 'BRB':
        return 'B', "Padrão básico: padrão alternado BRB"
    return None, None

# 16 padrões avançados - exemplo simplificado (expanda conforme necessidade)
def padroes_avancados(hist):
    if len(hist) < 9:
        return None, None
    ultimos = hist[-9:]
    # Padrão 1: 2 Reds e 1 Blue intercalados
    count_r = ultimos.count('R')
    count_b = ultimos.count('B')
    if count_r == 6 and count_b == 3:
        return 'R', "Padrão avançado: predominância Reds com Blues intercalados"
    # Padrão 2: alternância forte (nenhuma repetição de 2)
    for i in range(len(ultimos)-1):
        if ultimos[i] == ultimos[i+1]:
            break
    else:
        # Se não quebrou, alternância pura
        return ultimos[-1], "Padrão avançado: alternância forte detectada"
    return None, None

def detectar_padrao_completo(hist):
    cor, motivo = padroes_basicos(hist)
    if cor:
        return cor, motivo
    cor2, motivo2 = padroes_avancados(hist)
    if cor2:
        return cor2, motivo2
    return None, None

def detectar_reescrita_estrutural(hist):
    if len(hist) < 27:
        return None, "Histórico insuficiente para análise estrutural"
    linhas = extrair_linhas(hist)
    colunas = gerar_colunas(linhas)
    referencia = colunas[-4]  # 4 colunas atrás
    atual = colunas[-1]
    if verificar_reescrita(atual, referencia):
        cor = atual[-1]
        return cor, "Reescrita estrutural detectada, padrão repetido"
    return None, None

def gerar_sugestao(hist):
    if detectar_horario_de_risco():
        return None, "⛔ Horário de alto risco. Sugestão bloqueada."

    cor, motivo = detectar_reescrita_estrutural(hist)
    if cor:
        return cor, motivo

    cor2, motivo2 = detectar_padrao_completo(hist)
    if cor2:
        return cor2, motivo2

    return None, "Nenhum padrão confiável detectado"

# --- INTERFACE ---

st.subheader("🎮 Inserir Resultado")
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("🔴 Red"):
        st.session_state.historico.append('R')
        st.session_state.modo_g1 = False
with col2:
    if st.button("🔵 Blue"):
        st.session_state.historico.append('B')
        st.session_state.modo_g1 = False
with col3:
    if st.button("🟡 Tie"):
        st.session_state.historico.append('T')
        st.session_state.modo_g1 = False

st.subheader("📜 Histórico (formato oficial do jogo)")
linhas = extrair_linhas(st.session_state.historico)
for idx, linha in enumerate(linhas):
    st.write(f"Linha {idx+1}:", " ".join(linha))

st.subheader("🎯 Sugestão Inteligente")
if not st.session_state.modo_g1:
    sugestao, motivo = gerar_sugestao(st.session_state.historico)
    st.session_state.ultima_sugestao = sugestao
    if sugestao:
        cor_map = {'R': "🔴 Red", 'B': "🔵 Blue", 'T': "🟡 Tie"}
        st.success(f"Sugestão: {cor_map[sugestao]}")
        st.info(motivo)
    else:
        st.warning(motivo)
else:
    st.info("🔁 Modo G1 ativo: repita a última sugestão.")

st.subheader("📊 Painel de Desempenho")
colg, colr = st.columns(2)
with colg:
    if st.button("✅ GREEN"):
        st.session_state.green += 1
        st.session_state.modo_g1 = False
with colr:
    if st.button("❌ RED"):
        # Se modo_g1 ligado, desliga mas não conta erro, senão conta
        if st.session_state.modo_g1:
            st.session_state.modo_g1 = False
        else:
            st.session_state.red += 1
        st.session_state.modo_g1 = True

st.metric("Total de GREEN", st.session_state.green)
st.metric("Total de RED", st.session_state.red)

st.subheader("🧾 Exportar Histórico")
if st.button("📥 Exportar histórico CSV"):
    df = pd.DataFrame(st.session_state.historico, columns=["Resultado"])
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Download CSV", data=csv, file_name="historico_fs_pattern_master.csv", mime='text/csv')

st.subheader("🧹 Resetar Tudo")
if st.button("🔄 Resetar Sistema"):
    st.session_state.historico = []
    st.session_state.green = 0
    st.session_state.red = 0
    st.session_state.modo_g1 = False
    st.session_state.ultima_sugestao = None
    st.success("Sistema resetado.")
