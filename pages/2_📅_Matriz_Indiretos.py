import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Matriz de Indiretos",
    layout="wide"
)

st.title("📅 Matriz de Recursos Indiretos")
st.markdown("""
<style>
[data-testid="stDataFrame"] {
    color: black !important;
    font-weight: 500;
}
</style>
""", unsafe_allow_html=True)
# =====================================================
# CARREGAR PLANILHA
# =====================================================

@st.cache_data
def carregar_dados():

    arquivo = (
        Path(__file__).parent.parent /
        "medição.xlsx"
    )

    return pd.read_excel(arquivo)

df = carregar_dados()
# =====================================================
# PREPARAÇÃO DOS DADOS
# =====================================================

if "Preço na Aprovação" in df.columns:

    df["Preço na Aprovação"] = pd.to_numeric(
        df["Preço na Aprovação"],
        errors="coerce"
    ).fillna(0)

if "Data Início Planejado" in df.columns:

    df["Data Início Planejado"] = pd.to_datetime(
        df["Data Início Planejado"],
        errors="coerce"
    )

    df["Mês"] = (
        df["Data Início Planejado"]
        .dt.strftime("%m/%Y")
    )

for coluna in [
    "Município",
    "Centro de Trabalho CAB.",
    "Centro de Trabalho Operação",
    "Aprovação",
    "Descrição do Material"
]:

    if coluna in df.columns:

        df[coluna] = (
            df[coluna]
            .fillna("")
            .astype(str)
        )
# =====================================================
# FILTROS
# =====================================================

st.sidebar.header("Filtros")
# =====================================================
# MÊS
# =====================================================

if "Data Início Planejado" in df.columns:

    df["Data Início Planejado"] = pd.to_datetime(
        df["Data Início Planejado"],
        errors="coerce"
    )

    df["Mês"] = (
        df["Data Início Planejado"]
        .dt.strftime("%m/%Y")
    )

    filtro_mes = st.sidebar.multiselect(
        "📅 Mês",
        sorted(
            df["Mês"]
            .dropna()
            .unique()
        )
    )

    if filtro_mes:

        df = df[
            df["Mês"].isin(filtro_mes)
        ]

# =====================================================
# MUNICÍPIO
# =====================================================

if "Município" in df.columns:

    filtro_municipio = st.sidebar.multiselect(
        "🏙 Município",
        sorted(
            df["Município"]
            .dropna()
            .astype(str)
            .unique()
        )
    )

    if filtro_municipio:

        df = df[
            df["Município"]
            .astype(str)
            .isin(filtro_municipio)
        ]
# =====================================================
# CENTRO DE TRABALHO CAB.
# =====================================================

if "Centro de Trabalho CAB." in df.columns:

    filtro_cab = st.sidebar.multiselect(
        "🏭 Centro de Trabalho CAB.",
        sorted(
            df["Centro de Trabalho CAB."]
            .dropna()
            .astype(str)
            .unique()
        )
    )

    if filtro_cab:

        df = df[
            df["Centro de Trabalho CAB."]
            .astype(str)
            .isin(filtro_cab)
        ]

# =====================================================
# CENTRO DE TRABALHO OPERAÇÃO
# =====================================================

if "Centro de Trabalho Operação" in df.columns:

    filtro_operacao = st.sidebar.multiselect(
        "👷 Centro de Trabalho Operação",
        sorted(
            df["Centro de Trabalho Operação"]
            .dropna()
            .astype(str)
            .unique()
        )
    )

    if filtro_operacao:

        df = df[
            df["Centro de Trabalho Operação"]
            .astype(str)
            .isin(filtro_operacao)
        ]

# =====================================================
# APROVAÇÃO
# =====================================================

if "Aprovação" in df.columns:

    aprovacoes = sorted(
        df["Aprovação"]
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

        filtro_vazio = "(Vazio)" in filtro_aprovacao

        valores_selecionados = [
            x for x in filtro_aprovacao
            if x != "(Vazio)"
        ]

        mascara = (
            df["Aprovação"]
            .astype(str)
            .isin(valores_selecionados)
        )

        if filtro_vazio:

            mascara = (
                mascara
                |
                df["Aprovação"].isna()
                |
                (
                    df["Aprovação"]
                    .astype(str)
                    .str.strip()
                    == ""
                )
            )

        df = df[mascara]
# ====================================================
# ITEM
# =====================================================

if "Descrição do Material" in df.columns:

    filtro_item = st.sidebar.multiselect(
        "📦 Item",
        sorted(
            df["Descrição do Material"]
            .dropna()
            .astype(str)
            .unique()
        )
    )

    if filtro_item:

        df = df[
            df["Descrição do Material"]
            .astype(str)
            .isin(filtro_item)
        ]
indiretos = df[
    df["Descrição do Material"]
    .astype(str)
    .str.contains(
        "INDIRETO|ALOJAMENTO|ENCARREGADO|CAMINHÃO|VAN|DESLOCAMENTO|BANDEIRA",
        case=False,
        na=False
    )
].copy()

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

indiretos = df[
    df["Descrição do Material"]
    .astype(str)
    .str.contains(
        "INDIRETO|ALOJAMENTO|ENCARREGADO|CAMINHÃO|VAN|DESLOCAMENTO|BANDEIRA",
        case=False,
        na=False
    )
].copy()

diretos = df[
    ~df["Descrição do Material"]
    .astype(str)
    .str.contains(
        "INDIRETO|ALOJAMENTO|ENCARREGADO|CAMINHÃO|VAN|DESLOCAMENTO|BANDEIRA",
        case=False,
        na=False
    )
].copy()
# =====================================================
# KPI INDIRETOS
# =====================================================
st.subheader("📈 Indicadores dos Recursos Indiretos")
valor_diretos = pd.to_numeric(
    diretos["Preço na Aprovação"],
    errors="coerce"
).fillna(0).sum()

valor_indiretos = pd.to_numeric(
    indiretos["Preço na Aprovação"],
    errors="coerce"
).fillna(0).sum()

total_geral = valor_indiretos + valor_diretos

percentual_indiretos = (
    (valor_indiretos / total_geral) * 100
    if total_geral > 0
    else 0
)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Qtd. Indiretos", len(indiretos))

with col2:
    st.metric(
        "Valor Indiretos",
        moeda_br(valor_indiretos)
    )

with col3:
    st.metric(
        "Itens Distintos",
        indiretos["Descrição do Material"].nunique()
    )

with col4:
    st.metric(
        "Equipes",
        indiretos["Centro de Trabalho Operação"].nunique()
    )

with col5:
    st.metric(
        "% Indiretos",
        f"{percentual_indiretos:.2f}%"
    )
# =====================================================
# PREPARAÇÃO DATA
# =====================================================

indiretos["Data Início Planejado"] = pd.to_datetime(
    indiretos["Data Início Planejado"],
    errors="coerce"
)

indiretos["Dia"] = (
    indiretos["Data Início Planejado"]
    .dt.day
)
# =====================================================
# MATRIZ OPERACIONAL INDIRETOS
# =====================================================

matriz_qtd = pd.pivot_table(
    indiretos,
    index="Descrição do Material",
    columns="Dia",
    values="Quantidade Real",
    aggfunc="sum",
    fill_value=0
)

matriz_qtd["TOTAL"] = matriz_qtd.sum(axis=1)

matriz_qtd = matriz_qtd.sort_values(
    "TOTAL",
    ascending=False
)

st.subheader("📊 Matriz Operacional dos Indiretos")

st.dataframe(
    matriz_qtd,
    use_container_width=True
)
# =====================================================
# MATRIZ FINANCEIRA INDIRETOS
# =====================================================

matriz_valor = pd.pivot_table(
    indiretos,
    index="Descrição do Material",
    columns="Dia",
    values="Preço na Aprovação",
    aggfunc="sum",
    fill_value=0
)

matriz_valor["TOTAL"] = matriz_valor.sum(axis=1)
matriz_valor = matriz_valor.sort_values(
    "TOTAL",
    ascending=False
)
st.subheader("💰 Matriz Financeira dos Indiretos")

st.dataframe(
    matriz_valor.style.format(
        lambda x: moeda_br(x)
    ),
    use_container_width=True
)
# =====================================================
# HEATMAP INDIRETOS
# =====================================================

heatmap_matriz = (
    indiretos
    .groupby(
        [
            "Dia",
            "Centro de Trabalho Operação"
        ]
    )["Preço na Aprovação"]
    .sum()
    .reset_index()
)

fig = px.density_heatmap(
    heatmap_matriz,
    x="Dia",
    y="Centro de Trabalho Operação",
    z="Preço na Aprovação",
    title="Utilização dos Indiretos"
)

st.subheader("🔥 Heatmap dos Indiretos")

st.plotly_chart(
    fig,
    use_container_width=True
)
st.divider()

st.header("📦 Demais Itens da Medição")
st.subheader("📈 Indicadores dos Demais Itens")
# =====================================================
# KPI DIRETOS
# =====================================================

valor_diretos = pd.to_numeric(
    diretos["Preço na Aprovação"],
    errors="coerce"
).fillna(0).sum()

col5, col6, col7 = st.columns(3)

with col5:
    st.metric(
        "Qtd. Diretos",
        len(diretos)
    )

with col6:
    st.metric(
        "Valor Diretos",
        moeda_br(valor_diretos)
    )

with col7:
    st.metric(
        "Itens Diretos",
        diretos["Descrição do Material"].nunique()
    )

diretos["Data Início Planejado"] = pd.to_datetime(
    diretos["Data Início Planejado"],
    errors="coerce"
)

diretos["Dia"] = (
    diretos["Data Início Planejado"]
    .dt.day
)
# =====================================================
# MATRIZ OPERACIONAL DIRETOS
# =====================================================

matriz_diretos = pd.pivot_table(
    diretos,
    index="Descrição do Material",
    columns="Dia",
    values="Quantidade Real",
    aggfunc="sum",
    fill_value=0
)

matriz_diretos["TOTAL"] = matriz_diretos.sum(axis=1)

matriz_diretos = matriz_diretos.sort_values(
    "TOTAL",
    ascending=False
)
st.subheader("📊 Matriz Operacional dos Demais Itens")
st.dataframe(
    matriz_diretos,
    use_container_width=True
)
# =====================================================
# MATRIZ FINANCEIRA DIRETOS
# =====================================================

matriz_financeira_diretos = pd.pivot_table(
    diretos,
    index="Descrição do Material",
    columns="Dia",
    values="Preço na Aprovação",
    aggfunc="sum",
    fill_value=0
)

matriz_financeira_diretos["TOTAL"] = (
    matriz_financeira_diretos.sum(axis=1)
)
matriz_financeira_diretos = (
    matriz_financeira_diretos
    .sort_values(
        "TOTAL",
        ascending=False
    )
)
st.subheader("💰 Matriz Financeira dos Demais Itens")

st.dataframe(
    matriz_financeira_diretos.style.format(
        lambda x: moeda_br(x)
    ),
    use_container_width=True
)
# =====================================================
# HEATMAP DIRETOS
# =====================================================

heatmap_diretos = (
    diretos
    .groupby(
        [
            "Dia",
            "Centro de Trabalho Operação"
        ]
    )["Preço na Aprovação"]
    .sum()
    .reset_index()
)

fig_diretos = px.density_heatmap(
    heatmap_diretos,
    x="Dia",
    y="Centro de Trabalho Operação",
    z="Preço na Aprovação",
    title="Utilização dos Demais Itens"
)

st.subheader("🔥 Heatmap dos Demais Itens")

st.plotly_chart(
    fig_diretos,
    use_container_width=True
)
# =====================================================
# TOP 20 SERVIÇOS
# =====================================================

top_diretos = (
    diretos
    .groupby("Descrição do Material")
    ["Preço na Aprovação"]
    .sum()
    .reset_index()
    .sort_values(
        "Preço na Aprovação",
        ascending=False
    )
    .head(20)
)
top_diretos_exibir = top_diretos.copy()

top_diretos_exibir.index = (
    range(1, len(top_diretos_exibir) + 1)
)

top_diretos_exibir["Preço na Aprovação"] = (
    top_diretos_exibir["Preço na Aprovação"]
    .apply(moeda_br)
)

st.subheader("🏆 Top 20 Serviços da Medição")

st.dataframe(
    top_diretos_exibir,
    use_container_width=True
)