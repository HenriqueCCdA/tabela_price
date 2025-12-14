from collections import defaultdict

from dateutil.relativedelta import relativedelta
import streamlit as st
import pandas as pd

DIAS_MES_PADRAO = 30

def vfuturo(vp: float, taxa: float, tempo: int) -> float:
    return vp*(1+taxa)**tempo

def taxa_mensal_para_dia(taxa: float) -> float:
    return (1+taxa) ** (1/DIAS_MES_PADRAO) - 1

def gerar_parcelas_sac(
    valor_solicitado: float,
    prazo: int,
    taxa_de_juros_mensal: float,
    data_solicitacao: float,
    juros_exponencial: float,
):

    tabela = defaultdict(list)

    taxa_de_juros_mensal *= 0.01
    principal = valor_solicitado / prazo
    saldo_devedor = valor_solicitado

    if juros_exponencial:
        taxa_juros_dia = taxa_mensal_para_dia(taxa_de_juros_mensal)

    for prestacao in range(1, prazo + 1):

        vencimento_atual = data_solicitacao + relativedelta(months=prestacao)
        if prestacao == 1:
            qtd_dias_periodo = (vencimento_atual - data_solicitacao).days
        else:
            vencimento_anterior = data_solicitacao + relativedelta(months=prestacao-1)
            qtd_dias_periodo = (vencimento_atual - vencimento_anterior).days

        if juros_exponencial:
            juros = vfuturo(saldo_devedor, taxa_juros_dia, qtd_dias_periodo) - saldo_devedor
        else:
            juros = saldo_devedor * taxa_de_juros_mensal

        valor_prestacao = principal + juros
        saldo_devedor -= principal

        tabela["prestacao"].append(prestacao)
        tabela["vencimento"].append(vencimento_atual)
        tabela["qtd_dias_periodo"].append(qtd_dias_periodo)
        tabela["valor_prestacao"].append(valor_prestacao)
        tabela["principal"].append(principal)
        tabela["juros"].append(juros)
        tabela["saldo_devedor"].append(saldo_devedor)

    return pd.DataFrame(tabela)

if __name__ == "__main__":

    valor_solicitado = st.number_input("Valor solicitado", value=1_000.00)
    prazo = st.number_input("Numero de Parcelas", step=1, min_value=1, value=10)
    taxa_de_juros_mensal = st.number_input("Taxa de Juros (%)",value=1.5)
    data_primeiro_vencimento = st.date_input("Data do Primeiro vencimanto")
    sistema_de_calculo = st.radio(
        "Sistema de amortização",
        ["PRICE", "SAC"],
    )
    juros_exponencial = st.checkbox("Juros exponencial")

    if st.sidebar.button("Gerar"):
        print(sistema_de_calculo)

        if sistema_de_calculo == 'SAC':
            tabela_sac = gerar_parcelas_sac(
                valor_solicitado,
                prazo,
                taxa_de_juros_mensal,
                data_primeiro_vencimento,
                juros_exponencial,
            )
            st.dataframe(
                tabela_sac,
                hide_index=True,
                column_config={
                    "prestacao": "Prestação",
                    "vencimento": "Data de Vencimento",
                    "valor_prestacao": "Valor da Prestação",
                    "principal": "Principal",
                    "juros": "Juros",
                    "saldo_devedor": "Sado Devedor",
                }
            )
            st.line_chart(
                tabela_sac,
                x="prestacao",
                y=["saldo_devedor"],
                x_label="Número da Prestação",
                y_label="Saldo Devedor",
            )
            st.line_chart(
                tabela_sac,
                x="prestacao",
                y=["juros"],
                x_label="Número da Prestação",
                y_label="Juros",
            )
            st.line_chart(
                tabela_sac,
                x="prestacao",
                y=["valor_prestacao"],
                x_label="Número da Prestação",
                y_label="Valor da Prestacao",
            )
        elif sistema_de_calculo == 'PRICE':
            print(sistema_de_calculo)
