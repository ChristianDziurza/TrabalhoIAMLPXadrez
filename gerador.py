import random

REI = 1
RAINHA = 2
TORRE = 3
BISPO = 4
CAVALO = 5
PEAO = 6

SEMENTE = 42
QTD_DADOS = 1500
ARQUIVO_SAIDA = "dataset_xadrez.txt"


def copiar_tabuleiro(tab):
    return [linha[:] for linha in tab]


def tabuleiro_vazio():
    return [[0 for _ in range(8)] for _ in range(8)]


def encontrar_rei(tabuleiro, cor):
    for i in range(8):
        for j in range(8):
            if tabuleiro[i][j] == REI * cor:
                return (i, j)
    return None


def dentro_tabuleiro(i, j):
    return 0 <= i < 8 and 0 <= j < 8


def movimentos_cavalo(tab, i, j, cor):
    destinos = []
    movs = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
    for di, dj in movs:
        ni, nj = i + di, j + dj
        if dentro_tabuleiro(ni, nj):
            destino = tab[ni][nj]
            if destino == 0 or destino * cor < 0:
                destinos.append((ni, nj))
    return destinos


def movimentos_peao(tab, i, j, cor):
    destinos = []
    direcao = -1 if cor > 0 else 1
    ni, nj = i + direcao, j
    if dentro_tabuleiro(ni, nj) and tab[ni][nj] == 0:
        destinos.append((ni, nj))
    for dj in (-1, 1):
        ni, nj = i + direcao, j + dj
        if dentro_tabuleiro(ni, nj) and tab[ni][nj] * cor < 0:
            destinos.append((ni, nj))
    return destinos


def movimentos_deslizantes(tab, i, j, cor, direcoes):
    destinos = []
    for di, dj in direcoes:
        ni, nj = i + di, j + dj
        while dentro_tabuleiro(ni, nj):
            alvo = tab[ni][nj]
            if alvo == 0:
                destinos.append((ni, nj))
            elif alvo * cor < 0:
                destinos.append((ni, nj))
                break
            else:
                break
            ni += di
            nj += dj
    return destinos


def movimentos_bispo(tab, i, j, cor):
    return movimentos_deslizantes(tab, i, j, cor, [(-1, -1), (-1, 1), (1, -1), (1, 1)])


def movimentos_torre(tab, i, j, cor):
    return movimentos_deslizantes(tab, i, j, cor, [(-1, 0), (1, 0), (0, -1), (0, 1)])


def movimentos_rainha(tab, i, j, cor):
    return movimentos_bispo(tab, i, j, cor) + movimentos_torre(tab, i, j, cor)


def movimentos_rei(tab, i, j, cor):
    destinos = []
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if di == 0 and dj == 0:
                continue
            ni, nj = i + di, j + dj
            if dentro_tabuleiro(ni, nj):
                alvo = tab[ni][nj]
                if alvo == 0 or alvo * cor < 0:
                    destinos.append((ni, nj))
    return destinos


def movimentos_peca(tab, i, j):
    peca = tab[i][j]
    if peca == 0:
        return []
    cor = 1 if peca > 0 else -1
    tipo = abs(peca)
    if tipo == CAVALO:
        return movimentos_cavalo(tab, i, j, cor)
    if tipo == PEAO:
        return movimentos_peao(tab, i, j, cor)
    if tipo == BISPO:
        return movimentos_bispo(tab, i, j, cor)
    if tipo == TORRE:
        return movimentos_torre(tab, i, j, cor)
    if tipo == RAINHA:
        return movimentos_rainha(tab, i, j, cor)
    if tipo == REI:
        return movimentos_rei(tab, i, j, cor)
    return []


def rei_em_cheque(tab, cor_rei):
    pos_rei = encontrar_rei(tab, cor_rei)
    if pos_rei is None:
        return False
    ri, rj = pos_rei
    cor_atacante = -cor_rei
    for i in range(8):
        for j in range(8):
            peca = tab[i][j]
            if peca == 0 or peca * cor_atacante <= 0:
                continue
            if (ri, rj) in movimentos_peca(tab, i, j):
                return True
    return False


def aplicar_movimento(tab, origem, destino):
    novo = copiar_tabuleiro(tab)
    peca = novo[origem[0]][origem[1]]
    novo[origem[0]][origem[1]] = 0
    novo[destino[0]][destino[1]] = peca
    return novo


def tem_movimento_legal(tab, cor):
    for i in range(8):
        for j in range(8):
            peca = tab[i][j]
            if peca == 0 or peca * cor <= 0:
                continue
            for destino in movimentos_peca(tab, i, j):
                novo = aplicar_movimento(tab, (i, j), destino)
                if not rei_em_cheque(novo, cor):
                    return True
    return False


def posicionar_aleatorio(tab, tipo, cor):
    for _ in range(200):
        i = random.randint(0, 7)
        j = random.randint(0, 7)
        if tab[i][j] == 0:
            tab[i][j] = tipo * cor
            return True
    return False


def posicionar_adjacente_rei(tab, cor_peca, tipo_peca, cor_rei):
    pos_rei = encontrar_rei(tab, cor_rei)
    if pos_rei is None:
        return False
    ri, rj = pos_rei
    candidatos = []
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if di == 0 and dj == 0:
                continue
            ni, nj = ri + di, rj + dj
            if dentro_tabuleiro(ni, nj) and tab[ni][nj] == 0:
                if tipo_peca != PEAO:
                    candidatos.append((ni, nj))
                else:
                    direcao = -1 if cor_peca > 0 else 1
                    if ni - ri == direcao:
                        candidatos.append((ni, nj))
    if not candidatos:
        return False
    i, j = random.choice(candidatos)
    tab[i][j] = tipo_peca * cor_peca
    return True


def gerar_tabuleiro_cheque():
    for _ in range(200):
        tab = tabuleiro_vazio()
        cor_rei = random.choice([1, -1])
        posicionar_aleatorio(tab, REI, cor_rei)
        atacantes = [RAINHA, TORRE, BISPO, CAVALO, PEAO]
        tipo = random.choice(atacantes)
        if not posicionar_adjacente_rei(tab, -cor_rei, tipo, cor_rei):
            continue
        if not rei_em_cheque(tab, cor_rei):
            continue
        if not tem_movimento_legal(tab, cor_rei):
            continue
        return tab, cor_rei
    return None, None


def gerar_tabuleiro_cheque_mate():
    for _ in range(300):
        tab = tabuleiro_vazio()
        cor_rei = random.choice([1, -1])
        i = random.choice([0, 7])
        j = random.randint(0, 7)
        tab[i][j] = REI * cor_rei
        ca = -cor_rei

        rainha_pos = None
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if dentro_tabuleiro(ni, nj) and tab[ni][nj] == 0:
                    rainha_pos = (ni, nj)
                    break
            if rainha_pos:
                break
        if not rainha_pos:
            continue
        tab[rainha_pos[0]][rainha_pos[1]] = RAINHA * ca

        linha_torre = 7 if i == 0 else 0
        col_torre = random.randint(0, 7)
        if tab[linha_torre][col_torre] != 0:
            continue
        tab[linha_torre][col_torre] = TORRE * ca

        if rei_em_cheque(tab, cor_rei) and not tem_movimento_legal(tab, cor_rei):
            return tab, cor_rei
    return None, None


def gerar_tabuleiro_seguro():
    for _ in range(200):
        tab = tabuleiro_vazio()
        cor_rei = random.choice([1, -1])
        posicionar_aleatorio(tab, REI, cor_rei)
        qtd = random.randint(1, 3)
        tipos = [RAINHA, TORRE, BISPO, CAVALO, PEAO]
        for _ in range(qtd):
            tipo = random.choice(tipos)
            posicionar_aleatorio(tab, tipo, -cor_rei)
        if rei_em_cheque(tab, cor_rei):
            continue
        return tab, cor_rei
    return None, None


def rotulo_para_indice(rotulo):
    if rotulo == [0.0, 0.0]:
        return 0
    if rotulo == [1.0, 0.0]:
        return 1
    return 2


def gerar_conjunto_dados(qtd_total):
    dados = []
    alvo_por_classe = qtd_total // 3
    contadores = {"seguro": 0, "cheque": 0, "mate": 0}
    tentativas = 0
    max_tentativas = qtd_total * 50

    geradores = {
        "seguro": (gerar_tabuleiro_seguro, [0.0, 0.0]),
        "cheque": (gerar_tabuleiro_cheque, [1.0, 0.0]),
        "mate": (gerar_tabuleiro_cheque_mate, [0.0, 1.0]),
    }

    while len(dados) < qtd_total and tentativas < max_tentativas:
        tentativas += 1
        escolha = min(contadores, key=lambda k: contadores[k])
        if contadores[escolha] >= alvo_por_classe:
            escolha = random.choice(list(geradores.keys()))
        gerador, rotulo = geradores[escolha]
        tab, cor = gerador()
        if tab is None:
            continue
        dados.append((tab, rotulo))
        contadores[escolha] += 1
        if len(dados) % 200 == 0:
            print(f"Gerados: {len(dados)} | S={contadores['seguro']} C={contadores['cheque']} M={contadores['mate']}")

    print(f"Finalizado: {len(dados)} exemplos")
    return dados


def salvar_dataset(dados, caminho):
    with open(caminho, "w") as f:
        f.write(f"{len(dados)}\n")
        for tab, rotulo in dados:
            classe = rotulo_para_indice(rotulo)
            f.write(f"{classe}\n")
            for linha in tab:
                f.write(" ".join(str(v) for v in linha) + "\n")


def carregar_dataset(caminho):
    dados = []
    with open(caminho, "r") as f:
        n = int(f.readline().strip())
        for _ in range(n):
            classe = int(f.readline().strip())
            tab = []
            for _ in range(8):
                linha = [int(x) for x in f.readline().strip().split()]
                tab.append(linha)
            if classe == 0:
                rotulo = [0.0, 0.0]
            elif classe == 1:
                rotulo = [1.0, 0.0]
            else:
                rotulo = [0.0, 1.0]
            dados.append((tab, rotulo))
    return dados


def main():
    random.seed(SEMENTE)
    dados = gerar_conjunto_dados(QTD_DADOS)
    salvar_dataset(dados, ARQUIVO_SAIDA)
    print(f"Dataset salvo em '{ARQUIVO_SAIDA}' com {len(dados)} exemplos.")


if __name__ == "__main__":
    main()