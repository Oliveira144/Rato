import streamlit as st from collections import deque, Counter

Mapeamento de emojis para letras para facilitar processamento

COR_MAP = {"🔴": "R", "🔵": "B", "🟡": "Y"} COR_REV = {v: k for k, v in COR_MAP.items()}

st.set_page_config(page_title="FS Última Ficha AI", layout="wide") st.title("🔮 FS Última Ficha AI – Análise Inteligente Automática")

Histórico (recente à esquerda)

historico = st.session_state.get("historico", deque(maxlen=27))

col1, col2 = st.columns(2)

with col1: st.subheader("Inserir Resultado (⬅️ Recente ➝ Antigo)") col_b1, col_b2, col_b3 = st.columns(3) if col_b1.button("🔴 Red"): historico.appendleft("R") if col_b2.button("🔵 Blue"): historico.appendleft("B") if col_b3.button("🟡 Yellow"): historico.appendleft("Y")

with col2: if st.button("↩️ Desfazer Última Entrada") and historico: historico.popleft()

st.session_state["historico"] = historico

Mostrar histórico na tela com emojis

st.subheader("Histórico (⬅️ Recente | Antigo ➝)") linha_emojis = [COR_REV[c] for c in historico] st.write(" ".join(linha_emojis))

Lógica inteligente de previsão

sugestao = "" confiança = ""

if len(historico) >= 9: janela = list(historico)[:9]  # Pega as 9 jogadas mais recentes sequencia = "".join(janela)

# Procurar se essa sequência já ocorreu antes no restante do histórico
restante = list(historico)[9:]
ocorrencias = []

for i in range(len(restante) - 9):
    bloco = restante[i:i+9]
    if bloco == janela:
        if i > 0:
            prox = restante[i-1]  # entrada que veio depois da repetição anterior
            ocorrencias.append(prox)

if ocorrencias:
    contagem = Counter(ocorrencias)
    mais_comum = contagem.most_common(1)[0][0]
    sugestao = COR_REV[mais_comum]
    confiança = f"{(contagem[mais_comum] / len(ocorrencias)) * 100:.1f}% de confiança"
else:
    sugestao = "⚠️ Nenhum padrão detectado ainda."
    confiança = "Adicione mais resultados."

else: sugestao = "⚠️ Aguarde pelo menos 9 resultados." confiança = "Insira mais dados."

Mostrar sugestão

st.subheader("📈 Sugestão da Próxima Entrada") st.markdown(f"Próxima Jogada Recomendada: {sugestao}") st.markdown(f"Confiança: {confiança}")

