import streamlit as st
from collections import Counter

# Função para normalizar uma sequência trocando 🔴 e 🔵 para um padrão genérico,
# mantendo empates 🟡 fixos. Isso ajuda a identificar padrões que são a mesma estrutura
def normalizar_seq(seq):
    # Mapear cores para 0 e 1 (ex: 🔴=0, 🔵=1), empates fixos (2)
    # para poder comparar inversões
    mapping = {'🔴': 0, '🔵': 1, '🟡': 2}
    normal = [mapping[c] for c in seq]

    # Também criar inverso (troca 0<->1, 2 fica igual)
    inverso = [1 - x if x in (0,1) else x for x in normal]

    return normal, inverso

# Função para verificar se duas sequências são iguais
# considerando normal e inverso
def seq_igual(seq1, seq2):
    n1, i1 = normalizar_seq(seq1)
    n2, i2 = normalizar_seq(seq2)
    return n1 == n2 or n1 == i2

# Função para buscar subpadrões repetidos no histórico
def buscar_subpadroes(historico, min_len=3, max_len=9):
    n = len(historico)
    achados = []

    for tamanho in range(max_len, min_len-1, -1):
        if tamanho > n:
            continue
        # Criar todas as subsequências desse tamanho
        subseqs = []
        for start in range(n - tamanho +1):
            subseq = historico[start:start+tamanho]
            subseqs.append( (start, subseq) )
        # Comparar todas entre si para ver repetições
        for i in range(len(subseqs)):
            start_i, seq_i = subseqs[i]
            for j in range(i+1, len(subseqs)):
                start_j, seq_j = subseqs[j]
                if seq_igual(seq_i, seq_j):
                    achados.append({
                        'tamanho': tamanho,
                        'pos1': start_i,
                        'seq1': seq_i,
                        'pos2': start_j,
                        'seq2': seq_j
                    })
        if achados:
            break
    return achados

# Função para prever próxima jogada com base no padrão encontrado
def prever_proxima(historico, padrao):
    """
    padrao = dict com keys: tamanho, pos1, seq1, pos2, seq2
    A ideia é: 
    - A sequência mais recente é a seq1 em pos1
    - Ver a jogada seguinte após seq2 em pos2 (se existir)
    """
    pos2 = padrao['pos2']
    tamanho = padrao['tamanho']
    historico_len = len(historico)

    prox_pos = pos2 + tamanho
    if prox_pos >= historico_len:
        return None  # Não há próxima jogada conhecida

    jogada_apos = historico[prox_pos]

    # Agora é importante saber se a sequência seq1 foi invertida em relação a seq2,
    # para inverter a jogada_apos também.

    n1, i1 = normalizar_seq(padrao['seq1'])
    n2, i2 = normalizar_seq(padrao['seq2'])

    # Se seq1 é inverso de seq2, inverter jogada_apos
    if n1 == i2:
        # inverter jogada_apos: 🔴 <-> 🔵, 🟡 fica igual
        if jogada_apos == '🔴':
            jogada_apos = '🔵'
        elif jogada_apos == '🔵':
            jogada_apos = '🔴'

    return jogada_apos

# Função principal que roda análise e previsão
def analisar_historico(historico):
    achados = buscar_subpadroes(historico)
    if not achados:
        return None, "Nenhum padrão repetido detectado."

    # Pegar o melhor padrão (maior tamanho)
    melhor = max(achados, key=lambda x: x['tamanho'])
    prox_jogada = prever_proxima(historico, melhor)

    if prox_jogada is None:
        return None, "Padrão encontrado, mas não foi possível prever próxima jogada (limite histórico)."

    texto = (f"Padrão detectado: sequência de tamanho {melhor['tamanho']} "
             f"repetida nas posições {melhor['pos1']+1} e {melhor['pos2']+1}.\n"
             f"Sugestão baseada na repetição estrutural com possível inversão.")
    return prox_jogada, texto

# ---------------- STREAMLIT ------------------

def main():
    st.title("FS Pattern Auto-ID & Prediction")

    st.write("Informe o histórico (máximo 27) na ordem correta: mais recente à esquerda.")
    st.write("Use os emojis 🔴 🔵 🟡 separados por espaço.")

    raw = st.text_input("Histórico:", "")

    if raw:
        historico = raw.strip().split()
        if len(historico) < 9:
            st.warning("Histórico deve conter pelo menos 9 resultados.")
            return
        if len(historico) > 27:
            historico = historico[:27]

        st.write("### Histórico (mais recente → mais antigo):")
        st.write(" ".join(historico))

        jogada, justificativa = analisar_historico(historico)
        if jogada is None:
            st.info(justificativa)
        else:
            st.markdown(f"### Próxima jogada prevista: {jogada}")
            st.info(justificativa)

if __name__ == "__main__":
    main()
