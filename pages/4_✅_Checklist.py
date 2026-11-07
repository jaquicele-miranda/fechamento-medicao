import streamlit as st
import pandas as pd
from pathlib import Path

# =====================================================
# CONFIGURAÇÃO
# =====================================================

st.title("✅ Conferência de Checklist")

st.divider()

# =====================================================
# CACHE
# =====================================================

@st.cache_data
def carregar_medicao():

    arquivo = (
        Path(__file__).parent.parent /
        "medição.xlsx"
    )

    return pd.read_excel(arquivo)


@st.cache_data
def carregar_checklist(upload):

    return pd.read_excel(upload)

# =====================================================
# MEDIÇÃO
# =====================================================

medicao = carregar_medicao()

# =====================================================
# CHECKLIST
# =====================================================

arquivo_checklist = st.file_uploader(
    "📂 Selecione a Planilha de Ordens de Serviço",
    type=["xlsx"]
)

if arquivo_checklist is None:

    st.info(
        "Selecione a planilha de Ordens de Serviço."
    )

    st.stop()

checklist = carregar_checklist(
    arquivo_checklist
)
# =====================================================
# FUNÇÃO MOEDA
# =====================================================

def moeda_br(valor):

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

# =====================================================
# FILTROS
# =====================================================

st.sidebar.header("Filtros")

# =====================================================
# MÊS
# =====================================================

if "Data Início Planejado" in medicao.columns:

    medicao["Data Início Planejado"] = pd.to_datetime(
        medicao["Data Início Planejado"],
        errors="coerce"
    )

    medicao["Mês"] = (
        medicao["Data Início Planejado"]
        .dt.strftime("%m/%Y")
    )

    filtro_mes = st.sidebar.multiselect(
        "📅 Mês",
        sorted(
            medicao["Mês"]
            .dropna()
            .unique()
        )
    )

    if filtro_mes:

        medicao = medicao[
            medicao["Mês"].isin(
                filtro_mes
            )
        ]

# =====================================================
# CAB
# =====================================================

if "Centro de Trabalho CAB." in medicao.columns:

    filtro_cab = st.sidebar.multiselect(
        "🏭 Centro de Trabalho CAB.",
        sorted(
            medicao[
                "Centro de Trabalho CAB."
            ]
            .dropna()
            .astype(str)
            .unique()
        )
    )

    if filtro_cab:

        medicao = medicao[
            medicao[
                "Centro de Trabalho CAB."
            ]
            .astype(str)
            .isin(filtro_cab)
        ]

# =====================================================
# OPERAÇÃO
# =====================================================

if "Centro de Trabalho Operação" in medicao.columns:

    filtro_operacao = st.sidebar.multiselect(
        "👷 Centro de Trabalho Operação",
        sorted(
            medicao[
                "Centro de Trabalho Operação"
            ]
            .dropna()
            .astype(str)
            .unique()
        )
    )

    if filtro_operacao:

        medicao = medicao[
            medicao[
                "Centro de Trabalho Operação"
            ]
            .astype(str)
            .isin(filtro_operacao)
        ]

# =====================================================
# APROVAÇÃO
# =====================================================

if "Aprovação" in medicao.columns:

    aprovacoes = sorted(
        medicao["Aprovação"]
        .dropna()
        .astype(str)
        .unique()
    )

    aprovacoes.append("(Vazio)")

    filtro_aprovacao = st.sidebar.multiselect(
        "✅ Aprovação",
        aprovacoes
    )

    if filtro_aprovacao:

        filtro_vazio = (
            "(Vazio)"
            in filtro_aprovacao
        )

        valores = [
            x
            for x in filtro_aprovacao
            if x != "(Vazio)"
        ]

        mascara = (
            medicao["Aprovação"]
            .astype(str)
            .isin(valores)
        )

        if filtro_vazio:

            mascara = (
                mascara
                |
                medicao["Aprovação"].isna()
                |
                (
                    medicao["Aprovação"]
                    .astype(str)
                    .str.strip()
                    == ""
                )
            )

        medicao = medicao[
            mascara
        ]

# =====================================================
# VALIDAÇÕES
# =====================================================

if "Nº Ordem" not in medicao.columns:

    st.error(
        "Coluna 'Nº Ordem' não encontrada na medição."
    )

    st.stop()

if "Ordem" not in checklist.columns:

    st.error(
        "Coluna 'Ordem' não encontrada na planilha de OS."
    )

    st.stop()

if "Com Checklist ?" not in checklist.columns:

    st.error(
        "Coluna 'Com Checklist ?' não encontrada."
    )

    st.stop()

# =====================================================
# PADRONIZAÇÃO
# =====================================================

medicao["Nº Ordem"] = (
    pd.to_numeric(
        medicao["Nº Ordem"],
        errors="coerce"
    )
    .fillna(0)
    .astype(int)
    .astype(str)
)

checklist["Ordem"] = (
    pd.to_numeric(
        checklist["Ordem"],
        errors="coerce"
    )
    .fillna(0)
    .astype(int)
    .astype(str)
)

checklist["Com Checklist ?"] = (
    checklist["Com Checklist ?"]
    .fillna("")
    .astype(str)
    .str.upper()
    .str.strip()
)
# =====================================================
# CHECKLIST COM ALERTA
# =====================================================

checklist_alerta = checklist[
    checklist["Com Checklist ?"]
    .isin(
        [
            "SEM CHECKLIST",
            "CHECKLIST COM ERRO"
        ]
    )
].copy()
# =====================================================
# CRUZAMENTO
# =====================================================

alerta = medicao.merge(
    checklist_alerta[
        [
            "Ordem",
            "Com Checklist ?"
        ]
    ],
    left_on="Nº Ordem",
    right_on="Ordem",
    how="inner"
)
# =====================================================
# SEPARAÇÃO DOS ALERTAS
# =====================================================

sem_checklist = alerta[
    alerta["Com Checklist ?"] == "SEM CHECKLIST"
].copy()

checklist_erro = alerta[
    alerta["Com Checklist ?"] == "CHECKLIST COM ERRO"
].copy()
# =====================================================
# CÁLCULOS
# =====================================================

total_ordens = (
    medicao["Nº Ordem"]
    .nunique()
)

qtd_sem_checklist = (
    sem_checklist["Nº Ordem"]
    .nunique()
)

qtd_checklist_erro = (
    checklist_erro["Nº Ordem"]
    .nunique()
)

total_alertas = (
    qtd_sem_checklist +
    qtd_checklist_erro
)

ordens_ok = (
    total_ordens -
    total_alertas
)

valor_sem_checklist = (
    pd.to_numeric(
        sem_checklist["Preço na Aprovação"],
        errors="coerce"
    ).fillna(0).sum()
    if "Preço na Aprovação" in sem_checklist.columns
    else 0
)

valor_checklist_erro = (
    pd.to_numeric(
        checklist_erro["Preço na Aprovação"],
        errors="coerce"
    ).fillna(0).sum()
    if "Preço na Aprovação" in checklist_erro.columns
    else 0
)

valor_alerta = (
    valor_sem_checklist +
    valor_checklist_erro
)

cobertura = (
    (ordens_ok / total_ordens) * 100
    if total_ordens > 0
    else 0
)
# =====================================================
# KPIs
# =====================================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Ordens Medição",
        total_ordens
    )

with col2:
    st.metric(
        "Ordens OK",
        ordens_ok
    )

with col3:
    st.metric(
        "Sem Checklist",
        qtd_sem_checklist
    )

with col4:
    st.metric(
        "Checklist com Erro",
        qtd_checklist_erro
    )

with col5:
    st.metric(
        "% Cobertura",
        f"{cobertura:.1f}%"
    )

# =====================================================
# KPIs FINANCEIROS
# =====================================================

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Valor Sem Checklist",
        moeda_br(valor_sem_checklist)
    )

with col2:
    st.metric(
        "Valor Checklist com Erro",
        moeda_br(valor_checklist_erro)
    )

with col3:
    st.metric(
        "Valor Total em Alerta",
        moeda_br(valor_alerta)
    )

# =====================================================
# COBERTURA
# =====================================================

st.subheader(
    "📊 Cobertura de Checklist"
)

st.progress(
    cobertura / 100
)

# =====================================================
# ORDENS SEM CHECKLIST
# =====================================================

st.subheader(
    "🚨 Ordens Sem Checklist"
)

if len(sem_checklist) == 0:

    st.success(
        "Nenhuma ordem sem checklist."
    )

else:

    colunas_alerta = [
        "Nº Ordem",
        "Texto Breve",
        "Centro de Trabalho CAB.",
        "Centro de Trabalho Operação",
        "Aprovação",
        "Preço na Aprovação",
        "Com Checklist ?"
    ]

    colunas_alerta = [
        c for c in colunas_alerta
        if c in sem_checklist.columns
    ]

    st.dataframe(
        sem_checklist[colunas_alerta],
        use_container_width=True
    )

# =====================================================
# ORDENS COM CHECKLIST COM ERRO
# =====================================================

st.subheader(
    "⚠️ Ordens com Checklist com Erro"
)

if len(checklist_erro) == 0:

    st.success(
        "Nenhum checklist com erro."
    )

else:

    colunas_alerta = [
        "Nº Ordem",
        "Texto Breve",
        "Centro de Trabalho CAB.",
        "Centro de Trabalho Operação",
        "Aprovação",
        "Preço na Aprovação",
        "Com Checklist ?"
    ]

    colunas_alerta = [
        c for c in colunas_alerta
        if c in checklist_erro.columns
    ]

    st.dataframe(
        checklist_erro[colunas_alerta],
        use_container_width=True
    )

# =====================================================
# EXPORTAÇÃO
# =====================================================

exportar = pd.concat(
    [
        sem_checklist,
        checklist_erro
    ],
    ignore_index=True
)

csv = exportar.to_csv(
    index=False,
    sep=";"
).encode("utf-8-sig")

st.download_button(
    "📥 Baixar Planilha de Alerta",
    data=csv,
    file_name="Checklist_Alerta.csv",
    mime="text/csv"
)