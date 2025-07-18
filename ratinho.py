import streamlit as st from collections import deque, Counter

st.set_page_config(page_title="FS Auto Predictor", layout="wide")

st.title("📊 Football Studio - Auto Predictor")

Histórico de resultados (deque com tamanho máximo de 27)

history = st.session_state.get("history", deque(maxlen=27))

Função para adicionar novo resultado

def add_result(color): history.appendleft(color) st.session_state.history = history

Exibir os resultados da direita (mais antigo) para a esquerda (mais recente)

st.markdown("### Histórico (mais recente à esquerda):") if history: st.markdown( """<div style='display: flex; gap: 5px;'>""" + """"".join([f"<div style='padding:10px; border-radius:5px; background:{'red' if r=='🔴' else 'blue' if r=='🔵' else 'gold'};'>{r}</div>" for r in history]) + "</div>"", unsafe_allow_html=True )

Botões para inserir novo resultado

col1, col2, col3 = st.columns(3) with col1: if st.button("🔴 Vermelho"): add_result("🔴") with col2: if st.button("🔵 Azul"): add_result("🔵") with col3: if st.button("🟡 Empate"): add_result("🟡")

Análise automática de padrão

suggestion = "" confidence = "" if len(history) >= 9: bloco = list(history)[:9]

# Exemplo simples: detectar 5 ou mais azuis consecutivos
azul_consec = 0
for cor in bloco:
    if cor == "🔵":
        azul_consec += 1
    else:
        azul_consec = 0
    if azul_consec >= 5:
        suggestion = "🔴 (quebra provável de sequência azul)"
        confidence = "Alta"
        break

# Se não pegou sequência azul, verificar sequência vermelha
if not suggestion:
    red_consec = 0
    for cor in bloco:
        if cor == "🔴":
            red_consec += 1
        else:
            red_consec = 0
        if red_consec >= 5:
            suggestion = "🔵 (quebra provável de sequência vermelha)"
            confidence = "Alta"
            break

# Se ainda não detectou nada
if not suggestion:
    mais_freq = Counter(bloco).most_common(1)[0][0]
    if mais_freq == "🔵":
        suggestion = "🔵 (continuidade dominante)"
        confidence = "Média"
    elif mais_freq == "🔴":
        suggestion = "🔴 (continuidade dominante)"
        confidence = "Média"
    else:
        suggestion = "🔴 ou 🔵 (após empate, instável)"
        confidence = "Baixa"

Mostrar sugestão

if suggestion: st.markdown(""" ### 🎯 Sugestão de Entrada: Jogada Sugerida: {sugestao}

**Confiabilidade:** {conf}
""".format(sugestao=suggestion, conf=confidence))

