import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="Dashboard",
    layout="wide"
)

st.title("📊 Dashboard")

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
# FILTROS
# =====================================================

st.sidebar.header("Filtros")

# =====================================================
# FILTRO MÊS
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
            df["Mês"]
            .isin(filtro_mes)
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
# =====================================================
# STATUS DE USUÁRIO DA ORDEM
# =====================================================

if "Status de usuário da ordem" in df.columns:

    status = sorted(
        df["Status de usuário da ordem"]
        .dropna()
        .astype(str)
        .unique()
    )

    status.append("(Vazio)")

    filtro_status = st.sidebar.multiselect(
        "📌 Status da Ordem",
        status
    )

    if filtro_status:

        filtro_vazio = (
            "(Vazio)"
            in filtro_status
        )

        valores = [
            x
            for x in filtro_status
            if x != "(Vazio)"
        ]

        mascara = (
            df["Status de usuário da ordem"]
            .astype(str)
            .isin(valores)
        )

        if filtro_vazio:

            mascara = (
                mascara
                |
                df["Status de usuário da ordem"].isna()
                |
                (
                    df["Status de usuário da ordem"]
                    .astype(str)
                    .str.strip()
                    == ""
                )
            )

        df = df[
            mascara
        ]
# =====================================================
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
# =====================================================
# IDENTIFICAR INDIRETOS
# =====================================================

if "Descrição do Material" not in df.columns:
    st.error("Coluna 'Descrição do Material' não encontrada.")
    st.stop()

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
# INDICADORES
# =====================================================

valor_total = pd.to_numeric(
    df["Preço na Aprovação"],
    errors="coerce"
).fillna(0).sum()

valor_indiretos = pd.to_numeric(
    indiretos["Preço na Aprovação"],
    errors="coerce"
).fillna(0).sum()

percentual_indiretos = (
    (valor_indiretos / valor_total) * 100
    if valor_total > 0
    else 0
)

col1, col2, col3, col4, col5 = st.columns(5)

with col5:
    st.metric(
        "Ordens",
        df["Nº Ordem"].nunique()
    )

with col1:
    st.metric("Total Registros", len(df))

with col2:
    st.metric(
        "Valor Total",
        f"R$ {valor_total:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

with col3:
    st.metric(
        "Valor Indiretos",
        f"R$ {valor_indiretos:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
# =====================================================
# TOP 10 EQUIPES
# =====================================================

st.subheader("🏆 Top 10 Equipes")

top10 = (
    indiretos
    .groupby("Centro de Trabalho Operação")
    ["Preço na Aprovação"]
    .sum()
    .reset_index()
    .sort_values(
        "Preço na Aprovação",
        ascending=False
    )
    .head(10)
)

top10_exibir = top10.copy()

top10_exibir["Preço na Aprovação"] = (
    top10_exibir["Preço na Aprovação"]
    .map(
        lambda x: f"R$ {x:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
)

st.dataframe(
    top10_exibir,
    use_container_width=True
)
# =====================================================
# RESUMO EQUIPES
# =====================================================

resumo_equipes = (
    indiretos
    .groupby("Centro de Trabalho Operação")
    ["Preço na Aprovação"]
    .sum()
    .reset_index()
)

resumo_equipes["% Participação"] = (
    resumo_equipes["Preço na Aprovação"]
    /
    resumo_equipes["Preço na Aprovação"].sum()
) * 100

# =====================================================
# MAIOR EQUIPE
# =====================================================

maior_equipe = (
    resumo_equipes
    .sort_values(
        "Preço na Aprovação",
        ascending=False
    )
    .iloc[0]
)

participacao_top3 = (
    resumo_equipes
    .sort_values(
        "Preço na Aprovação",
        ascending=False
    )
    .head(3)["% Participação"]
    .sum()
)
# =====================================================
# RESUMO EXECUTIVO
# =====================================================

st.subheader("📋 Resumo Executivo")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.metric(
        "Maior Equipe",
        maior_equipe["Centro de Trabalho Operação"]
    )

with col_b:
    st.metric(
        "Valor Maior Equipe",
       f"R$ {maior_equipe['Preço na Aprovação']:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

with col_c:
    st.metric(
        "Concentração Top 3",
        f"{participacao_top3:.2f}%"
    )
if participacao_top3 > 60:

    st.warning(
        f"""
        ⚠️ Concentração elevada

        As 3 maiores equipes representam
        {participacao_top3:.2f}% dos indiretos.
        """
    )
# =====================================================
# PARTICIPAÇÃO DOS INDIRETOS
# =====================================================

resumo_equipes_exibir = resumo_equipes.copy()

resumo_equipes_exibir["Preço na Aprovação"] = (
    resumo_equipes_exibir["Preço na Aprovação"]
    .map(
        lambda x: f"R$ {x:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
)

resumo_equipes_exibir["% Participação"] = (
    resumo_equipes_exibir["% Participação"]
    .map(lambda x: f"{x:.2f}%")
)

st.subheader("📊 Participação dos Indiretos")

resumo_equipes_exibir = (
    resumo_equipes
    .sort_values(
        "Preço na Aprovação",
        ascending=False
    )
    .head(10)
    .copy()
)

resumo_equipes_exibir["Preço na Aprovação"] = (
    resumo_equipes_exibir["Preço na Aprovação"]
    .map(lambda x: f"R$ {x:,.2f}")
)

resumo_equipes_exibir["% Participação"] = (
    resumo_equipes_exibir["% Participação"]
    .map(lambda x: f"{x:.2f}%")
)

st.dataframe(
    resumo_equipes_exibir,
    use_container_width=True
)
# =====================================================
# PIZZA TOP 5
# =====================================================

fig_pizza = px.pie(
    resumo_equipes
    .sort_values(
        "Preço na Aprovação",
        ascending=False
    )
    .head(5),
    values="Preço na Aprovação",
    names="Centro de Trabalho Operação",
    title="Top 5 Equipes"
)

fig_pizza.update_layout(
    height=600
)

st.plotly_chart(
    fig_pizza,
    use_container_width=True
)
# =====================================================
# HEATMAP
# =====================================================

if (
    len(indiretos) > 0
    and "Data Início Planejado" in indiretos.columns
    and "Centro de Trabalho Operação" in indiretos.columns
):

    heatmap = (
        indiretos
        .groupby(
            [
                "Data Início Planejado",
                "Centro de Trabalho Operação"
            ]
        )["Preço na Aprovação"]
        .sum()
        .reset_index()
    )

    heatmap["Competência"] = pd.to_datetime(
        heatmap["Data Início Planejado"]
    ).dt.strftime("%m/%Y")

    fig_heatmap = px.density_heatmap(
        heatmap,
        x="Competência",
        y="Centro de Trabalho Operação",
        z="Preço na Aprovação",
        title="Indiretos por Equipe x Competência",
        color_continuous_scale="Blues"
    )

    st.subheader("🔥 Heatmap de Indiretos")

    st.plotly_chart(
        fig_heatmap,
        use_container_width=True
    )


# =====================================================
# ALERTA
# =====================================================

if percentual_indiretos > 35:

    st.error(
        f"⚠️ Percentual de indiretos elevado: {percentual_indiretos:.2f}%"
    )

elif percentual_indiretos > 25:

    st.warning(
        f"Percentual de indiretos em atenção: {percentual_indiretos:.2f}%"
    )

else:

    st.success(
        f"Percentual de indiretos controlado: {percentual_indiretos:.2f}%"
    )