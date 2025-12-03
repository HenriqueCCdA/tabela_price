# UTF-8
from pprint import pprint
from datetime import datetime, timedelta
# import arrow
from decimal import Decimal


# getcontext().prec = 6


class calcular:
    def xirr(transactions):
        # Este array é preenchido da seguinte forma:
        # [ (data_solicitacao, -(valor_liberado + valor_tarifa)) ]
        # [ (vencimento_em (1 recebivel), valor_recebivel) ]
        # [ (vencimento_em (2 recebivel), valor_recebivel) ]

        print("Transaction", transactions)
        years = [(ta[0] - transactions[0][0]).days / 365 for ta in transactions]
        residual = 1
        step = 0.05
        guess = 0.05
        epsilon = 0.0001
        limit = transactions[0][1] * -1
        while abs(residual) > epsilon and limit > 0:
            limit -= 1
            residual = 0.0
            for i, ta in enumerate(transactions):
                residual += ta[1] / pow(guess, years[i])
            if abs(residual) > epsilon:
                if residual > 0:
                    guess += step
                else:
                    guess -= step
                    step /= 2.0

        return Decimal(guess) - Decimal(1)

    def calcula_valor_recebivel_sac(
        valor_liberado,
        data_solicitacao,
        primeiro_vencimento,
        taxa_contrato,
        taxa_iof_ano,
        taxa_iof_adicional,
        numero_de_recebiveis,
        valor_tarifa,
        valor_seguro,
        tipo,
    ):
        # A TAXA DO CONTRATO É SEMPRE MENSAL
        _ = (
            ((Decimal(1) + taxa_contrato / Decimal(100)) ** (Decimal(1) / Decimal(30)))
            - Decimal(1)
        ) * Decimal(100)

        # A TAXA DO IOF É SEMPRE ANUAL

        # taxa_iof_dia      = round(Decimal(taxa_iof_ano/365),4)

        taxa_iof_dia = Decimal(0.0082)  # PESSOAL FISICA

        if tipo == "PF":
            taxa_iof_dia = Decimal(0.0082)
        else:
            taxa_iof_dia = Decimal(0.0041)

        # PASSO 1: CALCULO DO RECEBIVEL SEM IOF

        data_solicitacao = datetime.strptime(data_solicitacao, "%Y-%m-%d")

        primeiro_vencimento = datetime.strptime(primeiro_vencimento, "%Y-%m-%d")

        vencimento = primeiro_vencimento

        vencimento_anterior = data_solicitacao

        dia_do_vencimento = primeiro_vencimento.day

        mes_do_vencimento = primeiro_vencimento.month

        ano_do_vencimento = primeiro_vencimento.year

        dias_para_vencimento = {}
        data_de_vencimento = []
        valor_recebivel = {}

        # VALOR PRINCIPAL DA PARCELA (TODAS ELAS)

        valor_principal = valor_liberado / numero_de_recebiveis

        valor_iof = Decimal(0)

        valor_iof_total = Decimal(0)

        for recebivel in range(0, numero_de_recebiveis):
            dias = vencimento - data_solicitacao
            dias_para_vencimento[recebivel] = dias.days

            data_de_vencimento.append(str(vencimento.date()))
            #
            dias = vencimento - vencimento_anterior

            vencimento_anterior = vencimento
            #
            if mes_do_vencimento == 2:
                if dia_do_vencimento > 28:
                    vencimento = vencimento.replace(day=28)
                else:
                    vencimento = vencimento.replace(day=dia_do_vencimento)
            else:
                vencimento = vencimento.replace(day=dia_do_vencimento)
            #
            mes_do_vencimento = mes_do_vencimento + 1

            if mes_do_vencimento > 12:
                mes_do_vencimento = 1
                ano_do_vencimento = ano_do_vencimento + 1
                vencimento = vencimento.replace(year=ano_do_vencimento)

            vencimento = vencimento.replace(month=mes_do_vencimento)

        # CALCULO DO IOF - TAXA_CONTRATO TEM QUE SER DIFERENTE DE ZERO

        saldo_devedor = valor_liberado + valor_tarifa

        # if taxa_contrato != Decimal(0) and taxa_iof_dia != Decimal(0):

        if taxa_iof_dia != Decimal(0):
            for recebivel in range(0, numero_de_recebiveis):
                if (
                    dias_para_vencimento[recebivel] > 365
                ):  # Após 365 dias o IOF continua sendo calculado em cima de 365 dias
                    valor_iof = (
                        valor_principal
                        * (
                            (Decimal(365) * taxa_iof_dia / Decimal(100.00))
                            + taxa_iof_adicional / Decimal(100)
                        )
                    ) * Decimal(1)
                else:
                    valor_iof = (
                        valor_principal
                        * (
                            (
                                dias_para_vencimento[recebivel]
                                * taxa_iof_dia
                                / Decimal(100.00)
                            )
                            + taxa_iof_adicional / Decimal(100)
                        )
                    ) * Decimal(1)
                valor_iof = 0
                valor_recebivel[recebivel] = (
                    (saldo_devedor + valor_iof) * (taxa_contrato / Decimal(100.00))
                ) + valor_principal

                saldo_devedor -= valor_principal

                valor_iof_total += valor_iof

        resultado["valor_iof"] = valor_iof_total
        resultado["valor_liberado"] = valor_liberado
        resultado["valor_recebivel"] = valor_recebivel[0]
        resultado["data_solicitacao"] = data_solicitacao
        resultado["primeiro_vencimento_em"] = primeiro_vencimento
        resultado["data_vencimento"] = data_de_vencimento
        resultado["dias_para_vencimento"] = dias_para_vencimento
        resultado["taxa_contrato"] = taxa_contrato
        resultado["taxa_iof_ano"] = taxa_iof_ano
        resultado["taxa_iof_adicional"] = taxa_iof_adicional
        resultado["numero_de_recebiveis"] = numero_de_recebiveis
        resultado["valor_tarifa"] = valor_tarifa
        resultado["valor_seguro"] = valor_seguro
        resultado["valor_financiado"] = valor_liberado + valor_tarifa + valor_iof_total

        return (resultado, valor_recebivel)

    def calcula_valor_recebivel_price(
        valor_liberado,
        data_solicitacao,
        primeiro_vencimento,
        taxa_contrato,
        taxa_iof_ano,
        taxa_iof_adicional,
        numero_de_recebiveis,
        valor_tarifa,
        valor_seguro,
        tipo,
    ):
        # A TAXA DO CONTRATO É SEMPRE MENSAL
        taxa_contrato_dia = (
            ((Decimal(1) + taxa_contrato / Decimal(100)) ** (Decimal(1) / Decimal(30)))
            - Decimal(1)
        ) * Decimal(100)

        # A TAXA DO IOF É SEMPRE ANUAL

        # taxa_iof_dia      = round(Decimal(taxa_iof_ano/365),4)

        taxa_iof_dia = Decimal(0.0082)  # PESSOAL FISICA

        if tipo == "PF":
            taxa_iof_dia = Decimal(0.0082)
        else:
            taxa_iof_dia = Decimal(0.0041)
            # taxa_iof_dia = ((taxa_iof_dia)/2)

        resultado = {}

        # PASSO 1: CALCULO DO RECEBIVEL SEM IOF

        data_solicitacao = datetime.strptime(data_solicitacao, "%Y-%m-%d")

        primeiro_vencimento = datetime.strptime(primeiro_vencimento, "%Y-%m-%d")

        vencimento = primeiro_vencimento

        vencimento_anterior = data_solicitacao

        dia_do_vencimento = primeiro_vencimento.day

        mes_do_vencimento = primeiro_vencimento.month

        ano_do_vencimento = primeiro_vencimento.year

        dias_para_vencimento = {}
        dias_entre_vencimento = {}
        data_de_vencimento = []

        # data_de_vencimento.append('2024-05-15')
        # data_de_vencimento.append('2024-06-17')
        # data_de_vencimento.append('2024-07-15')
        # data_de_vencimento.append('2024-08-15')
        # data_de_vencimento.append('2024-09-16')
        # data_de_vencimento.append('2024-10-15')
        # data_de_vencimento.append('2024-11-18')
        # data_de_vencimento.append('2024-12-16')
        # data_de_vencimento.append('2025-01-15')
        # data_de_vencimento.append('2025-02-17')

        valor_iof = Decimal(0)
        fator_recebivel_sem_iof = Decimal(0)

        for recebivel in range(0, numero_de_recebiveis):
            dias = vencimento - data_solicitacao
            dias_para_vencimento[recebivel] = dias.days

            data_de_vencimento.append(str(vencimento.date()))
            #
            dias = vencimento - vencimento_anterior
            dias_entre_vencimento[recebivel] = dias.days
            #
            vencimento_anterior = vencimento
            #
            if mes_do_vencimento == 2:
                if dia_do_vencimento > 28:
                    vencimento = vencimento.replace(day=28)
                else:
                    vencimento = vencimento.replace(day=dia_do_vencimento)
            else:
                vencimento = vencimento.replace(day=dia_do_vencimento)
            #
            mes_do_vencimento = mes_do_vencimento + 1

            if mes_do_vencimento > 12:
                mes_do_vencimento = 1
                ano_do_vencimento = ano_do_vencimento + 1
                vencimento = vencimento.replace(year=ano_do_vencimento)

            vencimento = vencimento.replace(month=mes_do_vencimento)

            fator_recebivel_sem_iof += (
                Decimal(1) + taxa_contrato_dia / Decimal(100)
            ) ** -Decimal((dias_para_vencimento[recebivel]))

        valor_recebivel_sem_iof = (
            valor_liberado + valor_tarifa
        ) / fator_recebivel_sem_iof

        # CALCULO DO IOF - TAXA_CONTRATO TEM QUE SER DIFERENTE DE ZERO

        saldo_devedor = valor_liberado + valor_tarifa

        # if taxa_contrato != Decimal(0) and taxa_iof_dia != Decimal(0):

        if taxa_iof_dia != Decimal(0):
            for recebivel in range(0, numero_de_recebiveis):
                valor_recebivel_presente_sem_iof = valor_recebivel_sem_iof - (
                    saldo_devedor
                ) * (
                    (
                        (Decimal(1) + taxa_contrato_dia / Decimal(100.00))
                        ** (dias_entre_vencimento[recebivel])
                    )
                    - Decimal(1)
                )

                if (
                    dias_para_vencimento[recebivel] > 365
                ):  # Após 365 dias o IOF continua sendo calculado em cima de 365 dias
                    valor_iof += (
                        valor_recebivel_presente_sem_iof
                        * (
                            (Decimal(365) * taxa_iof_dia / Decimal(100.00))
                            + taxa_iof_adicional / Decimal(100)
                        )
                    ) * Decimal(1)
                else:
                    valor_iof += (
                        valor_recebivel_presente_sem_iof
                        * (
                            (
                                dias_para_vencimento[recebivel]
                                * taxa_iof_dia
                                / Decimal(100.00)
                            )
                            + taxa_iof_adicional / Decimal(100)
                        )
                    ) * Decimal(1)

                saldo_devedor -= valor_recebivel_presente_sem_iof

            # Valor do iof financiado
            valor_iof = ((valor_liberado + valor_tarifa) * valor_iof) / (
                (valor_liberado + valor_tarifa) - valor_iof
            )

            # Valor do iof não financiado
            # valor_iof = valor_iof

        valor_recebivel = (
            valor_liberado + valor_tarifa + valor_iof
        ) / fator_recebivel_sem_iof

        resultado["valor_iof"] = valor_iof
        resultado["valor_liberado"] = valor_liberado
        resultado["valor_recebivel"] = valor_recebivel
        resultado["data_solicitacao"] = data_solicitacao
        resultado["primeiro_vencimento_em"] = primeiro_vencimento
        resultado["data_vencimento"] = data_de_vencimento
        resultado["dias_para_vencimento"] = dias_para_vencimento
        resultado["taxa_contrato"] = taxa_contrato
        resultado["taxa_iof_ano"] = taxa_iof_ano
        resultado["taxa_iof_adicional"] = taxa_iof_adicional
        resultado["numero_de_recebiveis"] = numero_de_recebiveis
        resultado["valor_tarifa"] = valor_tarifa
        resultado["valor_seguro"] = valor_seguro
        resultado["valor_financiado"] = valor_liberado + valor_tarifa + valor_iof

        return resultado

    def calcula_valor_liberado_price(
        valor_recebivel,
        data_solicitacao,
        primeiro_vencimento,
        taxa_contrato,
        taxa_iof_ano,
        taxa_iof_adicional,
        numero_de_recebiveis,
        valor_tarifa,
        valor_seguro,
    ):
        # A TAXA DO CONTRATO É SEMPRE MENSAL

        taxa_contrato_dia = (
            ((Decimal(1) + taxa_contrato / Decimal(100)) ** (Decimal(1) / Decimal(30)))
            - Decimal(1)
        ) * Decimal(100)

        # A TAXA DO IOF É SEMPRE ANUAL
        taxa_iof_dia = (
            ((Decimal(1) + taxa_iof_ano / Decimal(100)) ** (Decimal(1) / Decimal(360)))
            - Decimal(1)
        ) * Decimal(100)

        resultado = {}

        # PASSO 1: CALCULO DO RECEBIVEL SEM IOF

        data_solicitacao = datetime.strptime(data_solicitacao, "%Y-%m-%d")

        primeiro_vencimento = datetime.strptime(primeiro_vencimento, "%Y-%m-%d")

        vencimento = primeiro_vencimento

        vencimento_anterior = data_solicitacao

        dia_do_vencimento = primeiro_vencimento.day

        dias_para_vencimento = {}
        dias_entre_vencimento = {}
        data_de_vencimento = []

        fator_recebivel_sem_iof = Decimal(0)

        valor_iof = Decimal(0)

        for recebivel in range(0, numero_de_recebiveis):
            dias_para_vencimento[recebivel] = vencimento - data_solicitacao

            data_de_vencimento.append(str(vencimento.date()))

            dias_entre_vencimento[recebivel] = (vencimento - vencimento_anterior).days

            vencimento_anterior = vencimento

            # vencimento = arrow.get(vencimento).replace(day=dia_do_vencimento)

            # vencimento = arrow.get(vencimento).replace(month=1)

            vencimento = calcular.vencimentodiautil(vencimento)

            fator_recebivel_sem_iof += (
                Decimal(1) + taxa_contrato_dia / Decimal(100)
            ) ** -Decimal((dias_para_vencimento[recebivel]))

        valor_financiado = Decimal(valor_recebivel) * Decimal(fator_recebivel_sem_iof)

        # PARA ACHAR O VALOR LIBERADO TEMOS QUE INTERPOLAR USANDO COMO BASE O VALOR FINANCIADO (LIBERADO+TAC+IOF)

        valor_recebivel_referencia = valor_recebivel
        residual = Decimal(1)
        step = Decimal(1)
        guess = valor_financiado
        epsilon = Decimal(0.001)
        limit = 100
        while abs(residual) > epsilon and Decimal(limit) > 0:
            limit -= Decimal(1)
            residual = Decimal(0.0)
            valor_iof = Decimal(0.00)

            # COLOCCAR O CALCULO DO RECEBVEL

            saldo_devedor = guess

            valor_recebivel = guess / fator_recebivel_sem_iof

            if taxa_contrato != Decimal(0) and taxa_iof_dia != Decimal(0):
                for recebivel in range(0, numero_de_recebiveis):
                    valor_recebivel_presente_sem_iof = valor_recebivel - (
                        saldo_devedor
                    ) * (
                        (
                            (Decimal(1) + taxa_contrato_dia / Decimal(100.00))
                            ** (dias_entre_vencimento[recebivel])
                        )
                        - Decimal(1)
                    )

                    if (
                        dias_para_vencimento[recebivel] > 365
                    ):  # Após 365 dias o IOF continua sendo calculado em cima de 365 dias
                        valor_iof += valor_recebivel_presente_sem_iof * (
                            (Decimal(365) * taxa_iof_dia / Decimal(100.00))
                            + taxa_iof_adicional / Decimal(100)
                        )
                    else:
                        valor_iof += valor_recebivel_presente_sem_iof * (
                            (
                                dias_para_vencimento[recebivel]
                                * taxa_iof_dia
                                / Decimal(100.00)
                            )
                            + taxa_iof_adicional / Decimal(100)
                        )

                    saldo_devedor -= valor_recebivel_presente_sem_iof

            valor_recebivel = (guess) / fator_recebivel_sem_iof

            residual = valor_recebivel_referencia - valor_recebivel
            if residual == Decimal(0.00):
                limit = Decimal(0.00)
                if abs(residual) > epsilon:
                    if residual > Decimal(0):
                        guess += step
                    else:
                        guess -= step
                        step /= Decimal(2.0)

        valor_liberado = guess - valor_iof - valor_tarifa

        resultado["valor_iof"] = valor_iof
        resultado["valor_liberado"] = valor_liberado
        resultado["valor_recebivel"] = valor_recebivel
        resultado["data_solicitacao"] = data_solicitacao
        resultado["primeiro_vencimento_em"] = primeiro_vencimento
        resultado["data_vencimento"] = data_de_vencimento
        resultado["dias_para_vencimento"] = dias_para_vencimento
        resultado["taxa_contrato"] = taxa_contrato
        resultado["taxa_iof_ano"] = taxa_iof_ano
        resultado["taxa_iof_adicional"] = taxa_iof_adicional
        resultado["numero_de_recebiveis"] = numero_de_recebiveis
        resultado["valor_tarifa"] = valor_tarifa
        resultado["valor_seguro"] = valor_seguro

        return resultado


class gera_valores_do_financiamento:
    recebivel_detalhe = {}

    def __init__(self, resultado):
        self.resultado = resultado

        self.calcular_irr()

        self.calcular_recebivel_detalhe()

    def calcular_irr(self):
        #  Para calculara a taxa interna de retorno
        # Este array é preenchido da seguinte forma:
        # [ (data_solicitacao, -(valor_liberado + valor_tarifa)) ]
        # [ (vencimento_em (1 recebivel), valor_recebivel) ]
        # [ (vencimento_em (2 recebivel), valor_recebivel) ]

        data_solictacao = self.resultado["data_solicitacao"].date()

        valor_financiado_com_iof = (
            float(self.resultado["valor_liberado"])
            + float(self.resultado["valor_tarifa"])
            + float(self.resultado["valor_iof"])
        )

        # valor_financiado_sem_iof = float(self.resultado["valor_liberado"]) + float(self.resultado["valor_tarifa"]) + float(self.resultado["valor_iof"])

        irr_array = [(data_solictacao, -valor_financiado_com_iof)]

        valor_recebivel = float(self.resultado["valor_recebivel"])

        for numeroderecebiveis in range(0, self.resultado["numero_de_recebiveis"]):
            data_vencimento = self.resultado["data_vencimento"][numeroderecebiveis]
            data_vencimento = datetime.strptime(data_vencimento, "%Y-%m-%d").date()

            irr_array.append((data_vencimento, valor_recebivel))

        irr_ano = calcular.xirr(irr_array) * Decimal(100)

        irr_mes = (Decimal(1) + irr_ano / Decimal(100)) ** (
            Decimal(30.0) / Decimal(365.0)
        )

        irr_dia = (Decimal(1) + irr_ano / Decimal(100)) ** (
            Decimal(1.0) / Decimal(365.0)
        )

        irr_mes = (irr_mes - Decimal(1)) * Decimal(100)

        irr_dia = (irr_dia - Decimal(1)) * Decimal(100)

        self.resultado["irr_ano"] = irr_ano
        self.resultado["irr_mes"] = irr_mes
        self.resultado["irr_dia"] = irr_dia

        # PARA CALCULAR O CET ALTERA PARA VALOR LIBERADO

        irr_array[0] = data_solictacao, -float(self.resultado["valor_liberado"])

        cet_ano = calcular.xirr(irr_array) * Decimal(100)

        cet_mes = (Decimal(1) + cet_ano / Decimal(100)) ** (
            Decimal(30.0) / Decimal(365.0)
        )

        cet_mes = (cet_mes - Decimal(1)) * Decimal(100)

        self.resultado["cet_ano"] = cet_ano
        self.resultado["cet_mes"] = cet_mes

    def calcular_recebivel_detalhe(self):
        valor_recebivel = Decimal(self.resultado["valor_recebivel"])

        irr_dia = Decimal(self.resultado["irr_dia"])

        nro_recebiveis = self.resultado["numero_de_recebiveis"]

        for numeroderecebiveis in range(0, nro_recebiveis):
            # CALCULAR O VALOR PRINCIPAL TEM QUE USAR A FORMULA ABAIXO
            dias_para_calculo_principal = -self.resultado["dias_para_vencimento"][
                nro_recebiveis - 1 - numeroderecebiveis
            ]
            valor_principal = (
                valor_recebivel
                * (Decimal(1) + irr_dia / Decimal(100)) ** dias_para_calculo_principal
            )

            # CALCULAR O VALOR PRESNETEL TEM QUE USAR A FORMULA ABAIXO
            dias_para_vencimento = -self.resultado["dias_para_vencimento"][
                numeroderecebiveis
            ]
            valor_presente = (
                valor_recebivel
                * (Decimal(1) + irr_dia / Decimal(100)) ** dias_para_vencimento
            )

            valor_juros = valor_recebivel - valor_presente
            data_vencimento = self.resultado["data_vencimento"][numeroderecebiveis]

            self.recebivel_detalhe[numeroderecebiveis] = {
                "vencimento_em": data_vencimento,
                "pagmento_previsto_em": data_vencimento,
                "valor_presente": valor_presente,
                "valor_juros": valor_juros,
                "valor_principal": valor_principal,
                "dias_para_vencimento": -self.resultado["dias_para_vencimento"][
                    numeroderecebiveis
                ],
                "valor": Decimal(valor_recebivel)
                + Decimal(self.resultado["valor_seguro"]),
                "valor_contabil": Decimal(valor_recebivel),
            }

        self.resultado["recebivel_detalhe"] = self.recebivel_detalhe


cal = calcular

# valor_liberado,
# data_solicitacao,
# primeiro_vencimento,
# taxa_contrato,
# taxa_iof_ano,
# taxa_iof_adicional,
# numero_de_recebiveis,
# valor_tarifa,
# valor_seguro):

# cal.calcula_valor_recebivel(Decimal(1172.15),"2022-08-19","2022-10-03", Decimal(17.00), Decimal(3.00), Decimal(0.38),
#                               24,Decimal(0.00),Decimal(0.00))

# Tipo Calculo
# P = Pagamento
# S = Solictação

dias_pagamento = 0

data_solicitacao = "2025-10-07"

data_solicitacao = datetime.strptime(data_solicitacao, "%Y-%m-%d")

tipo_calculo = "S"

if tipo_calculo == "N":
    datacalculo = data_solicitacao + timedelta(days=dias_pagamento)
else:
    datacalculo = data_solicitacao

# data_primeiro_vct=datacalculo+ timedelta(days=30)


# data_primeiro_vct = data_primeiro_vct.strftime("%Y-%m-%d")

data_primeiro_vct = "2025-11-07"

# data_primeiro_vct = data_primeiro_vct.strftime("%Y-%m-%d")

datacalculo = datacalculo.strftime("%Y-%m-%d")


resultado = cal.calcula_valor_recebivel_price(
    Decimal(100000.00),
    datacalculo,
    data_primeiro_vct,
    Decimal(1.50),
    Decimal(3.00),
    Decimal(0.38),
    12,
    Decimal(0),
    Decimal(0.00),
    "PF",
)

valor = Decimal(resultado["valor_recebivel"])


contrato = {}

recebivel = {}

data_de_vencimento = []


gera = gera_valores_do_financiamento(
    cal.calcula_valor_recebivel_price(
        Decimal(100_000.00),
        datacalculo,
        data_primeiro_vct,
        Decimal(1.50),
        Decimal(3.00),
        Decimal(0.38),
        12,
        Decimal(0),
        Decimal(0.00),
        "PF",
    )
)

# # DADOS FINANCEIROS PARA GRAVAR EM CONTRATO:
#
# contrato["taxa_cet_ano"]             = gera.resultado["cet_ano"]
# contrato["taxa_cet_mes"]             = gera.resultado["cet_mes"]
# contrato["taxa_contrato"]            = gera.resultado["taxa_contrato"]
# contrato["taxa_iof_ano"]             = gera.resultado["taxa_iof_ano"]
# contrato["taxa_iof_mes"]             = ((Decimal(1)+Decimal(gera.resultado["taxa_iof_ano"])/Decimal(100))**(Decimal(30.0)/Decimal(365.0))-Decimal(1))*Decimal(100)
# contrato["taxa_iof_complementar"]    = gera.resultado["taxa_iof_adicional"]
# contrato["taxa_irr"]                 = gera.resultado["irr_dia"]
# contrato["data_solicitacao"]         = gera.resultado["data_solicitacao"].date()
# contrato["plano"]                    = gera.resultado["numero_de_recebiveis"]
# contrato["primeiro_vencimento_em"]   = gera.resultado["primeiro_vencimento_em"].date()
# contrato["ultimo_vencimento_em"]     = datetime.strptime(gera.resultado["data_vencimento"][gera.resultado["numero_de_recebiveis"]-1],"%Y-%m-%d").date()
# contrato["valor_iof"]                = gera.resultado["valor_iof"]
# contrato["valor_liberado"]           = gera.resultado["valor_liberado"]
# contrato["valor_recebivel"]          = gera.resultado["valor_recebivel"] + gera.resultado["valor_seguro"]
# contrato["valor_seguro"]             = gera.resultado["valor_seguro"]
# contrato["valor_solicitado"]         = gera.resultado["valor_liberado"]
# contrato["valor_tarifa"]             = gera.resultado["valor_tarifa"]
# contrato["valor_total_devido"]       = gera.resultado["valor_recebivel"]*gera.resultado["numero_de_recebiveis"]
# contrato["valor_recebivel_contabil"] = gera.resultado["valor_recebivel"]
#

print("************************* DADOS CONTRATO **********************************")

print(f"cet_ano: {gera.resultado['cet_ano']}")
print(f"cet_mes: {gera.resultado['cet_mes']}")
print(f"taxa_contrato: {gera.resultado['taxa_contrato']}")
print(f"irr_dia: {gera.resultado['irr_dia']}")
print(f"data_solicitacao: {gera.resultado['data_solicitacao'].date()}")
print(f"numero_de_recebiveis: {gera.resultado['numero_de_recebiveis']}")
print(f"primeiro_vencimento_em: {gera.resultado['primeiro_vencimento_em'].date()}")
print(f"valor_iof: {gera.resultado['valor_iof']}")
print(f"valor_liberado: {gera.resultado['valor_liberado']}")
print(f"valor_financiado: {gera.resultado['valor_financiado']}")
print(
    f"valor_recebivel + valor_seguro: {gera.resultado['valor_recebivel'] + gera.resultado['valor_seguro']}"
)
print(f"valor_seguro: {gera.resultado['valor_seguro']}")
print(f"valor_liberado: {gera.resultado['valor_liberado']}")
print(f"valor_tarifa: {gera.resultado['valor_tarifa']}")

print("************************* DADOS DO RECEBIVEL **********************************")
# resultado["numero_de_recebiveis"]):

for numeroderecebiveis in range(0, resultado["numero_de_recebiveis"]):
    print("Recebivel Numero-> ", numeroderecebiveis)
    print(f"vencimento_em: {resultado['data_vencimento'][numeroderecebiveis]}")
    print(f"valor: {resultado['valor_recebivel']}")


recebivel = gera.resultado["recebivel_detalhe"]


print("\n")
print("\n")
print(recebivel)
print("\n")
print("\n")
print("Fator", resultado["valor_recebivel"] / resultado["valor_liberado"])

resultado_recebivel = {}


print("\n")

print("SAC")

resultado, resultado_recebivel = cal.calcula_valor_recebivel_sac(
    Decimal(100_000.00),
    datacalculo,
    data_primeiro_vct,
    Decimal(1.5),
    Decimal(0.0),
    Decimal(0.0),
    12,
    Decimal(0),
    Decimal(0.00),
    "PF",
)


pprint(resultado)
print("\n")
print("\n")
pprint(resultado_recebivel)
