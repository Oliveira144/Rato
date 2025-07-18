import streamlit as st
from collections import defaultdict

# ---------- Normalização e comparação ----------
def normalizar_seq(seq):
    mapa = {'🔴': 0, '🔵': 1, '🟡': 2}
    normal = [mapa[c] for c in seq]
    inverso = [1 - x if x in (0,1) else x for x in normal]
    return normal, inverso

def seq_igual(seq1, seq2):
    n1, i1 = normalizar_seq(seq1)
    n2, i2 = normalizar_seq(seq2)
    return n1 == n2 or n1 == i2

# ---------- Buscar subpadrões ----------
def buscar_subpadroes(historico, min_len=3, max_len=9):
    n = len(historico)
    achados = []

    for tamanho in range(max_len, min_len - 1, -1):
        if tamanho > n:
            continue
        subseqs = [(i, historico[i:i+tamanho]) for i in range(n - tamanho + 1)]
        grupos = defaultdict(list)

        for pos, seq in subseqs:
            key, _ = normalizar_seq(seq)
            grupos[tuple(key)].append((pos, seq))

        for key, ocor in grupos.items():
            if len(ocor) >= 2:
                for i in range(len(ocor)):
                    for j in range(i + 1, len(ocor)):
                        achados.append({
                            'tamanho': tamanho,
                            'pos1': ocor[i][0],
                            'seq1': ocor[i][1],
                            'pos2': ocor[j][0],
                            'seq2': ocor[j][1],
                            'key': key
                        })
        if achados:
            break
    return achados

# ---------- Prever próxima jogada ----------
def prever_proxima(historico, padrao):
    pos2 = padrao['pos2']
    tamanho = padrao['tamanho']
    historico_len = len(historico)

    prox_pos = pos2 + tamanho
    if prox_pos >= historico_len:
        return None

    jogada_apos = historico[prox_pos]
    n1, i1 = normalizar_seq(padrao['seq1'])
    n2, i2 = normalizar_seq(padrao['seq2'])

    if n1 == i2:
        # Padrão foi reescrito com inversão
        if jogada_apos == '🔴': jogada_apos = '🔵'
        elif jogada_apos == '🔵': jogada_apos = '🔴'

    return jogada_apos

# ---------- Detectar manipulação ----------
def detectar_manipulacao(historico):
    suspeitas = []
    n = len(historico)
    for i in range(n - 4):
        bloco = historico[i:i+4]
        if bloco == ['🔴', '🔴', '🟡', '🔵']:
            suspeitas.append(i)
    return suspeitas

# ---------- Análise geral ----------
def analisar_historico_avancado(historico):
    achados = buscar_subpadroes(historico)
    manipulos = detectar_manipulacao(historico)

    if not achados:
        return None, "Nenhum padrão relevante foi identificado."

    # Remover padrões que cruzam blocos suspeitos
    achados_filtrados = []
    for pad in achados:
        cruzado = any(
            pad['pos1'] <= m+3 <= pad['pos1']+pad['tamanho'] or 
            pad['pos2'] <= m+3 <= pad['pos2']+pad['tamanho']
            for m in manipulos
        )
        if not cruzado:
            achados_filtrados.append(pad)

    if not achados_filtrados:
        return None, "Padrões detectados, mas todos com possíveis manipulações."

    melhor = max(achados_filtrados, key=lambda x: x['tamanho'])
    prox = prever_proxima(historico, melhor)

    if prox is None:
        return None, "Não foi possível prever a próxima jogada."

    confianca = min(1.0, melhor['tamanho'] / 9)

    explicacao = (f"🔍 Padrão detectado de tamanho {melhor['tamanho']} "
                  f"repetido nas posições {melhor['pos1']+1} e {melhor['pos2']+1']}.\n"
                  f"💡 Previsão baseada em repetição estruturada (com possível inversão).\n"
                  f"📊 Confiança estimada: {confianca*100:.1f}%.")

    if manipulos:
        explicacao += f"\n⚠️ {len(manipulos)} possíveis padrões de manipulação detectados."

    return prox, explicacao

# ---------- Streamlit Interface Automática ----------
def main():
    st.set_page_config(page_title="FS Última Ficha PRO", layout="centered")
    st.title("🧠 FS Última Ficha PRO – AutoDetect v4.1")
    st.markdown("Digite o histórico do painel da **esquerda para direita** (mais recente à esquerda). Use 🔴 🔵 🟡 com espaços.")

    raw = st.text_input("Histórico (mínimo 9, máximo 27):", placeholder="Ex: 🔴 🔴 🔵 🔴 🟡 🔵 🔵 🔴...")

    if raw.strip():
        historico = raw.strip().split()
        if len(historico) < 9:
            st.warning("Insira pelo menos 9 resultados para iniciar a previsão.")
            return
        if len(historico) > 27:
            historico = historico[:27]

        st.markdown("### 🧾 Histórico lido:")
        st.write(" ".join(historico))

        jogada, justificativa = analisar_historico_avancado(historico)

        if jogada:
            st.markdown(f"## 🎯 Próxima jogada sugerida: **{jogada}**")
            st.info(justificativa)
        else:
            st.info(justificativa)

if __name__ == "__main__":
    main()
