"""
Sistema em Python para Análise de Rentabilidade, Benchmark e Projeção de Carteira de Renda Fixa (Perfil Moderado)
Autor: Kaique Oliveira Teles
Curso: Análise e Desenvolvimento de Sistemas - Universidade Santo Amaro (UNISA)
"""

import csv
import os


def criar_csv_exemplo(arquivo_csv):
    """Gera automaticamente uma base de carteira exemplo em CSV caso o arquivo não exista."""
    dados_iniciais = [
        {"ativo": "Tesouro Selic 2029", "aporte": "25000.00", "taxa_anual": "0.1075", "isento_ir": "N"},
        {"ativo": "CDB Banco Inter", "aporte": "30000.00", "taxa_anual": "0.1256", "isento_ir": "N"},
        {"ativo": "LCI Caixa 93% CDI", "aporte": "25000.00", "taxa_anual": "0.0990", "isento_ir": "S"},
        {"ativo": "Tesouro IPCA+ 2035", "aporte": "20000.00", "taxa_anual": "0.1150", "isento_ir": "N"},
    ]
    with open(arquivo_csv, mode="w", newline="", encoding="utf-8") as f:
        campos = ["ativo", "aporte", "taxa_anual", "isento_ir"]
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        writer.writerows(dados_iniciais)


def cadastrar_ativo(arquivo_csv):
    """Permite ao usuário cadastrar um novo título de renda fixa no arquivo CSV."""
    print("\n--- CADASTRO DE NOVO ATIVO DE RENDA FIXA ---")
    ativo = input("Nome do Ativo (ex: CDB Banco XP 110% CDI): ").strip()
    if not ativo:
        print("Erro: O nome do ativo não pode ficar vazio.")
        return

    try:
        aporte = float(input("Valor do Aporte Inicial (R$): ").replace(",", "."))
        taxa_perc = float(input("Taxa de Rentabilidade Anual (% a.a., ex: 12.5): ").replace(",", "."))
        if aporte <= 0 or taxa_perc < 0:
            raise ValueError("Valores devem ser positivos.")
    except ValueError:
        print("Erro: Informe valores numéricos válidos para aporte e taxa.")
        return

    isento = input("Ativo isento de Imposto de Renda (LCI/LCA/CRI/CRA)? [S/N]: ").strip().upper()
    if isento not in ("S", "N"):
        isento = "N"

    arquivo_existe = os.path.exists(arquivo_csv)
    with open(arquivo_csv, mode="a", newline="", encoding="utf-8") as f:
        campos = ["ativo", "aporte", "taxa_anual", "isento_ir"]
        writer = csv.DictWriter(f, fieldnames=campos)
        if not arquivo_existe:
            writer.writeheader()
        writer.writerow({
            "ativo": ativo,
            "aporte": f"{aporte:.2f}",
            "taxa_anual": f"{taxa_perc / 100:.4f}",
            "isento_ir": isento,
        })
    print(f"Ativo '{ativo}' cadastrado com sucesso em '{arquivo_csv}'!")


def consultar_rentabilidade_anual(arquivo_csv):
    """Lê a carteira do CSV, calcula rendimentos brutos e líquidos e exibe a tabela consolidada."""
    total_investido, total_bruto, total_liquido = 0.0, 0.0, 0.0
    print(f"\n{'Ativo':<20} | {'Aporte':<12} | {'Taxa Nom.':<10} | {'Bruto Ano':<12} | {'Líquido Ano'}")
    print("-" * 72)

    with open(arquivo_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            valor = float(row["aporte"])
            taxa = float(row["taxa_anual"])  # Ex.: 0.12 para 12% a.a.
            isento_ir = row["isento_ir"].strip().upper() == "S"

            rend_bruto = valor * taxa
            aliq_ir = 0.0 if isento_ir else 0.175  # Alíquota média regressiva de 17,5% (361 a 720 dias)
            rend_liq = rend_bruto * (1 - aliq_ir)

            total_investido += valor
            total_bruto += rend_bruto
            total_liquido += rend_liq

            print(f"{row['ativo']:<20} | R${valor:<10.2f} | {taxa * 100:>7.2f}% | R${rend_bruto:<10.2f} | R${rend_liq:.2f}")

    print("=" * 72)
    taxa_media = (total_bruto / total_investido) * 100 if total_investido > 0 else 0.0
    print(f"Patrimônio: R${total_investido:.2f} | Rentabilidade Ponderada: {taxa_media:.2f}% a.a.")
    return total_investido, total_bruto, total_liquido


def comparativo_benchmark_e_projecao(investido, bruto_ano, cdi_ano, selic_ano):
    """Compara a rentabilidade ponderada frente a Selic/CDI e projeta o patrimônio para N+1."""
    if investido <= 0:
        print("Nenhum capital investido encontrado para análise.")
        return

    rentab_carteira = (bruto_ano / investido) * 100
    perc_cdi = (rentab_carteira / cdi_ano) * 100
    perc_selic = (rentab_carteira / selic_ano) * 100

    print("\n========== RELATÓRIO DE BENCHMARK COM OS JUROS ATUAIS ==========")
    print(f"Taxa Selic Vigente: {selic_ano:.2f}% a.a. | Taxa CDI Vigente: {cdi_ano:.2f}% a.a.")
    print(f"Rentabilidade Bruta da Carteira: {rentab_carteira:.2f}% a.a.")
    print(f"-> Desempenho relativo ao CDI:   {perc_cdi:.2f}% do CDI")
    print(f"-> Desempenho relativo à Selic: {perc_selic:.2f}% da Selic")

    status = "SUPEROU O BENCHMARK" if rentab_carteira >= cdi_ano else "ABAIXO DO BENCHMARK"
    print(f"Diagnóstico de Eficiência: [{status}]")

    # Projeção para o próximo ano (N+1) considerando juros compostos pela taxa ponderada
    saldo_atual = investido + bruto_ano
    taxa_proj = rentab_carteira / 100
    projecao_futura = saldo_atual * (1 + taxa_proj)
    ganho_projetado = projecao_futura - saldo_atual

    print("\n----------- PROJEÇÃO PATRIMONIAL PARA O PRÓXIMO ANO (N+1) -----------")
    print(f"Capital Consolidado Atual: R$ {saldo_atual:,.2f}")
    print(f"Patrimônio Estimado (T+12m): R$ {projecao_futura:,.2f}")
    print(f"Rendimento Nominal Estimado: R$ {ganho_projetado:,.2f}")


def main():
    arquivo_csv = "carteira_renda_fixa.csv"
    selic_vigente = 10.75
    cdi_vigente = 10.65

    if not os.path.exists(arquivo_csv):
        criar_csv_exemplo(arquivo_csv)

    while True:
        print("\n========================================================================")
        print("   SISTEMA DE ANÁLISE DE CARTEIRA DE RENDA FIXA (PERFIL MODERADO)       ")
        print("========================================================================")
        print("1 - Executar Análise Completa (Rentabilidade, Benchmark e Projeção N+1)")
        print("2 - Cadastrar Novo Ativo na Carteira")
        print("3 - Atualizar Taxas de Benchmark (Selic / CDI Vigentes)")
        print("0 - Sair")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            investido, bruto, _ = consultar_rentabilidade_anual(arquivo_csv)
            comparativo_benchmark_e_projecao(investido, bruto, cdi_vigente, selic_vigente)
        elif opcao == "2":
            cadastrar_ativo(arquivo_csv)
        elif opcao == "3":
            try:
                selic_vigente = float(input("Informe a Taxa Selic vigente (% a.a.): ").replace(",", "."))
                cdi_vigente = float(input("Informe a Taxa CDI vigente (% a.a.): ").replace(",", "."))
                print("Taxas atualizadas com sucesso!")
            except ValueError:
                print("Erro: Valor numérico inválido.")
        elif opcao == "0":
            print("Encerrando o sistema. Até logo!")
            break
        else:
            print("Opção inválida. Tente novamente.")


if __name__ == "__main__":
    main()
