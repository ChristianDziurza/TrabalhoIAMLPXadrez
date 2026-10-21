import random
import math
from gerador import carregar_dataset

TAXA_APRENDIZADO = 0.1
EPOCAS = 80
TAM_OCULTA = 15
TAM_SAIDA = 2
MIN_PESO = -1.0
MAX_PESO = 1.0
SEMENTE = 42
ARQUIVO_DATASET = "dataset_xadrez.txt"


def sigmoid(x):
    if x < -500:
        return 0.0
    if x > 500:
        return 1.0
    return 1.0 / (1.0 + math.exp(-x))


def sigmoid_derivada(saida):
    return saida * (1.0 - saida)


def matriz_para_vetor(tabuleiro):
    vetor = []
    for linha in tabuleiro:
        for elemento in linha:
            vetor.append(float(elemento))
    return vetor


class MLP:
    def __init__(self, tam_entrada, tam_oculta, tam_saida):
        self.tam_entrada = tam_entrada
        self.tam_oculta = tam_oculta
        self.tam_saida = tam_saida
        self.pesos_entrada_oculta = self._criar_pesos(tam_entrada, tam_oculta)
        self.bias_oculta = self._criar_bias(tam_oculta)
        self.pesos_oculta_saida = self._criar_pesos(tam_oculta, tam_saida)
        self.bias_saida = self._criar_bias(tam_saida)

    def _criar_pesos(self, linhas, colunas):
        return [[random.uniform(MIN_PESO, MAX_PESO) for _ in range(colunas)] for _ in range(linhas)]

    def _criar_bias(self, tamanho):
        return [random.uniform(MIN_PESO, MAX_PESO) for _ in range(tamanho)]

    def _propagar(self, entrada):
        oculta = []
        for j in range(self.tam_oculta):
            soma = self.bias_oculta[j]
            for i in range(self.tam_entrada):
                soma += entrada[i] * self.pesos_entrada_oculta[i][j]
            oculta.append(sigmoid(soma))
        saida = []
        for k in range(self.tam_saida):
            soma = self.bias_saida[k]
            for j in range(self.tam_oculta):
                soma += oculta[j] * self.pesos_oculta_saida[j][k]
            saida.append(sigmoid(soma))
        return oculta, saida

    def _retropropagar(self, entrada, oculta, saida, alvo):
        delta_saida = [(alvo[k] - saida[k]) * sigmoid_derivada(saida[k]) for k in range(self.tam_saida)]
        erro_oculta = []
        for j in range(self.tam_oculta):
            soma = 0.0
            for k in range(self.tam_saida):
                soma += delta_saida[k] * self.pesos_oculta_saida[j][k]
            erro_oculta.append(soma)
        delta_oculta = [erro_oculta[j] * sigmoid_derivada(oculta[j]) for j in range(self.tam_oculta)]
        for j in range(self.tam_oculta):
            for k in range(self.tam_saida):
                self.pesos_oculta_saida[j][k] += TAXA_APRENDIZADO * delta_saida[k] * oculta[j]
        for k in range(self.tam_saida):
            self.bias_saida[k] += TAXA_APRENDIZADO * delta_saida[k]
        for i in range(self.tam_entrada):
            for j in range(self.tam_oculta):
                self.pesos_entrada_oculta[i][j] += TAXA_APRENDIZADO * delta_oculta[j] * entrada[i]
        for j in range(self.tam_oculta):
            self.bias_oculta[j] += TAXA_APRENDIZADO * delta_oculta[j]

    def treinar(self, dados):
        for epoca in range(EPOCAS):
            erro_total = 0.0
            random.shuffle(dados)
            for tab, alvo in dados:
                entrada = matriz_para_vetor(tab)
                oculta, saida = self._propagar(entrada)
                for k in range(self.tam_saida):
                    erro_total += (alvo[k] - saida[k]) ** 2
                self._retropropagar(entrada, oculta, saida, alvo)
            if (epoca + 1) % 10 == 0:
                print(f"Epoca {epoca + 1}/{EPOCAS} - Erro: {erro_total / len(dados):.4f}")

    def prever(self, entrada):
        _, saida = self._propagar(entrada)
        return saida


def dividir_dados(dados, proporcao_treino=0.7):
    random.shuffle(dados)
    corte = int(len(dados) * proporcao_treino)
    return dados[:corte], dados[corte:]


def classe_de(saida):
    if saida[1] >= 0.5:
        return 2
    if saida[0] >= 0.5:
        return 1
    return 0


def rotulo_para_texto(c):
    if c == 0:
        return "Rei seguro"
    if c == 1:
        return "Rei em cheque"
    return "Rei em cheque-mate"


def imprimir_tabuleiro(tab):
    simbolos = {
        0: ".",
        1: "R", -1: "r",
        2: "Q", -2: "q",
        3: "T", -3: "t",
        4: "B", -4: "b",
        5: "C", -5: "c",
        6: "P", -6: "p",
    }
    print("  " + " ".join(str(j) for j in range(8)))
    for i in range(8):
        print(f"{i} " + " ".join(simbolos.get(tab[i][j], "?") for j in range(8)))


def escolher_caso_teste(teste):
    print(f"\nCasos de teste disponiveis: 1 a {len(teste)}")
    while True:
        try:
            escolha = int(input("Escolha o caso de teste : "))
            if escolha == 0:
                return None
            if 1 <= escolha <= len(teste):
                return teste[escolha - 1]
        except ValueError:
            print("Erro")


def main():
    random.seed(SEMENTE)
    dados = carregar_dataset(ARQUIVO_DATASET)
    print(f"Total: {len(dados)} exemplos")

    treino, teste = dividir_dados(dados, 0.7)
    print(f"Treino: {len(treino)} | Teste: {len(teste)}")

    rede = MLP(64, TAM_OCULTA, TAM_SAIDA)
    rede.treinar(treino)

    acertos = 0
    matriz_confusao = [[0, 0, 0] for _ in range(3)]
    for tab, alvo in teste:
        entrada = matriz_para_vetor(tab)
        saida = rede.prever(entrada)
        previsto = classe_de(saida)
        real = classe_de(alvo)
        matriz_confusao[real][previsto] += 1
        if previsto == real:
            acertos += 1

    print(f"\nAcuracia: {acertos / len(teste) * 100:.2f}%")
    print("\nMatriz de confusao (linha=real, coluna=previsto):")
    nomes = ["Seguro", "Cheque", "Mate"]
    print(f"{'':>10}" + "".join(f"{n:>10}" for n in nomes))
    for i, nome in enumerate(nomes):
        print(f"{nome:>10}" + "".join(f"{matriz_confusao[i][j]:>10}" for j in range(3)))

    while True:
        caso = escolher_caso_teste(teste)
        if caso is None:
            break
        tab, alvo = caso
        entrada = matriz_para_vetor(tab)
        saida = rede.prever(entrada)
        previsto = classe_de(saida)
        real = classe_de(alvo)
        print("\nTabuleiro:")
        imprimir_tabuleiro(tab)
        print(f"\nSaida da rede: [{saida[0]:.3f}, {saida[1]:.3f}]")
        print(f"Previsto: {rotulo_para_texto(previsto)}")
        print(f"Real: {rotulo_para_texto(real)}")
        print(f"{'ACERTOU' if previsto == real else 'ERROU'}\n")


if __name__ == "__main__":
    main()