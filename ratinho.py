import streamlit as st
from collections import Counter, defaultdict

# ---------- Normalização e comparação ----------

def normalizar_seq(seq):
    mapping = {'🔴': 0, '🔵': 1, '🟡': 2}
    normal = [mapping[c] for c in seq]
    inverso = [1 - x if x in (0,1) else x for x in normal]
    return normal, inverso

def seq_igual(seq1, seq2):
    n1, i1 = normalizar_seq(seq1)
    n2, i2 = normalizar_seq(seq2)
    return n1 == n2 or n1 == i2

# ---------- Busca de subpadrões com estatística ----------

def buscar_subpadroes(historico, min_len=3, max_len=9):
    n = len(historico)
    achados = []

    for tamanho in range(max_len, min_len-1, -1):
        if tamanho > n:
            continue
        subseqs = []
        for start in range(n - tamanho +1):
            subseq = historico[start:start+tamanho]
            subseqs.append( (start, subseq) )

        rep_contagem = defaultdict(list)

        for idx, (start_pos, seq) in enumerate(subseqs):
            nseq, _ = normalizar_seq(seq)
            key = tuple(nseq)
            rep_contagem[key].append((start_pos, seq))

        for key, ocor in rep_contagem.items():
            if len(ocor) >= 2:
                for i in range(len(ocor)):
                    for j in range(i+1, len(ocor)):
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

# ---------- Previsão da próxima jogada com análise ----------

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
        if jogada_apos == '🔴':
            jogada_apos = '🔵'
        elif jogada_apos == '🔵':
            jogada_apos = '🔴'

    return jogada_apos

# ---------- Sistema Anti-Manipulação ----------

def detectar_manipulacao(historico):
    manipulos = []
    n = len(historico)
    for i in range(n-4):
        seq = historico[i:i+4]
        if seq == ['🔴','🔴','🟡','🔵']:
            manipulos.append(i)
    return manipulos

# ---------- Análise final com ranking ----------

def analisar_historico_avancado(historico):
    achados = buscar_subpadroes(historico)
    manipulos = detectar_manipulacao(historico)

    if not achados:
        return None, "Nenhum padrão repetido detectado."

    achados_filtrados = []
    for pad in achados:
        overlap = False
        for m in manipulos:
            if (pad['pos1'] <= m+3 and pad['pos1'] >= m) or (pad['pos2'] <= m+3 and pad['pos2'] >= m):
                overlap = True
                break
        if not overlap:
            achados_filtrados.append(pad)

    if not achados_filtrados:
        return None, "Padrões encontrados, mas todos suspeitos de manipulação."

    melhor = max(achados_filtrados, key=lambda x: x['tamanho'])
    prox_jogada = prever_proxima(historico, melhor)
    if prox_jogada is None:
        return None, "Padrão encontrado, mas não foi possível prever próxima jogada (limite histórico)."

    confianca = min(1.0, melhor['tamanho'] / 9)

    texto = (f"Padrão detectado: sequência de tamanho {melhor['tamanho']} "
             f"repetida nas posições {melhor['pos1']+1} e {melhor['pos2']+1}.\n"
             f"Sugestão baseada na repetição estrutural com possível inversão.\n"
             f"Confiança estimada: {confianca*100:.1f}%.\n")

    if manipulos:
        texto += f"Atenção: detectadas possíveis manipulações em {len(manipulos)} blocos."

    return prox_jogada, texto

# ---------- Interface Streamlit ----------

def main():
    st.title("FS Última Ficha v4.1 - Análise Avançada com Anti-Manipulação e Confiança")

    st.write("Informe o histórico (máximo 27) na ordem correta: mais recente à esquerda.")
    st.write("Use os emojis 🔴 🔵 🟡 separados por espaço.")

    raw = st.text_input("Histórico:")

    if st.button("Analisar"):
        if not raw.strip():
            st.warning("Informe o histórico antes de analisar.")
            return

        historico = raw.strip().split()
        if len(historico) < 9:
            st.warning("Histórico deve conter pelo menos 9 resultados.")
            return
        if len(historico) > 27:
            historico = historico[:27]

        st.write("### Histórico (mais recente → mais antigo):")
        st.write(" ".join(historico))

        jogada, justificativa = analisar_historico_avancado(historico)
        if jogada is None:
            st.info(justificativa)
        else:
            st.markdown(f"### Próxima jogada prevista: {jogada}")
            st.info(justificativa)

if __name__ == "__main__":
    main()
