import streamlit as st from collections import deque, Counter import random

Inicialização do histórico

if 'historico' not in st.session_state: st.session_state.historico = deque(maxlen=27)

st.title("FS Auto Predictor – AI de Reescrita")

cores = ["🔴", "🔵", "🟡"]

Função de sugestão baseada em repetição simples de sequência

def sugerir_proxima_jogada(historico): if len(historico) < 9: return "Aguardando mais resultados...", None

ultimos_9 = list(historico)[-9:]
melhor_match = 0
melhor_cor = None
for i in range(len(historico) - 9):
    bloco = list(historico)[i:i+9]
    match = sum([1 for a, b in zip(bloco, ultimos_9) if a == b])
    if match > melhor_match:
        melhor_match = match
        if i + 9 < len(historico):
            melhor_cor = historico[i + 9]

if melhor_cor:
    return melhor_cor, melhor_match / 9
else:
    return random.choice(cores), 0.0

Exibe o histórico no painel (esquerda para direita, mais recente à esquerda)

historico_formatado = list(st.session_state.historico)[::-1] st.markdown("## Histórico") st.write(" ".join(historico_formatado))

Botões de entrada

st.markdown("### Inserir novo resultado") col1, col2, col3 = st.columns(3) with col1: if st.button("🔴 Red"): st.session_state.historico.append("🔴") st.experimental_rerun() with col2: if st.button("🔵 Blue"): st.session_state.historico.append("🔵") st.experimental_rerun() with col3: if st.button("🟡 Yellow"): st.session_state.historico.append("🟡") st.experimental_rerun()

Sugestão automática

if len(st.session_state.historico) >= 9: suggestion, confidence = sugerir_proxima_jogada(st.session_state.historico) st.markdown("### Sugestão Automática") st.success( f"A próxima jogada sugerida é: {suggestion} com confiança de {round(confidence*100, 2)}%." ) else: st.warning("Insira pelo menos 9 resultados para iniciar a previsão.")

