import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import holidays

st.title("🚨 Auditoria")
st.divider()
@st.cache_data
def carregar_dados():

    arquivo = (
        Path(__file__).parent.parent /
        "medição.xlsx"
    )

    return pd.read_excel(arquivo)

df = carregar_dados()
if "Preço na Aprovação" in df.columns:

    df["Preço na Aprovação"] = pd.to_numeric(
        df["Preço na Aprovação"],
        errors="coerce"
    ).fillna(0)

if "Quantidade Real" in df.columns:

    df["Quantidade Real"] = pd.to_numeric(
        df["Quantidade Real"],
        errors="coerce"
    )

if "Qtd. Req. Compra" in df.columns:

    df["Qtd. Req. Compra"] = pd.to_numeric(
        df["Qtd. Req. Compra"],
        errors="coerce"
    )

def moeda_br(valor):

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
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
# KPI DA AUDITORIA
# =====================================================
st.subheader("📈 Indicadores")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Registros",
        len(df)
    )

with col2:
    st.metric(
        "Ordens",
        df["Nº Ordem"].nunique()
        if "Nº Ordem" in df.columns
        else 0
    )

with col3:

   valor_total = (
    pd.to_numeric(
        df["Preço na Aprovação"],
        errors="coerce"
    ).fillna(0).sum()
    if "Preço na Aprovação" in df.columns
    else 0
)

   st.metric(
    "Valor Total",
    moeda_br(valor_total)
)
# =====================================================
# AUDITORIA DE QUANTIDADES
# =====================================================

if (
    "Quantidade Real" in df.columns
    and "Qtd. Req. Compra" in df.columns
):

    qtd_real = pd.to_numeric(
        df["Quantidade Real"],
        errors="coerce"
    )

    qtd_req = pd.to_numeric(
        df["Qtd. Req. Compra"],
        errors="coerce"
    )

    auditoria = df[qtd_real > qtd_req]

    st.subheader(
        "⚠️ Quantidade Real Maior que Quantidade Solicitada"
    )

    st.metric(
        "Ocorrências",
        len(auditoria)
    )

    st.dataframe(
        auditoria,
        use_container_width=True
    )

# =====================================================
# TOP 20 ORDENS
# =====================================================

if (
    "Valor Total Item Pedido" in df.columns
    and "Nº Ordem" in df.columns
):

    top_ordens = (
        df.groupby("Nº Ordem")["Valor Total Item Pedido"]
        .sum()
        .reset_index()
        .sort_values(
            "Valor Total Item Pedido",
            ascending=False
        )
        .head(20)
    )

    st.subheader("🏆 Top 20 Ordens por Valor")

    fig = px.bar(
        top_ordens,
        x="Nº Ordem",
        y="Valor Total Item Pedido"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
# =====================================================
# MAPEAMENTO MUNICÍPIOS
# =====================================================

MAPEAMENTO = {
    "PEDERNEIRAS": "CFSP",
    "CUBATÃO": "CFSP",
    "JUNDIAÍ": "CFSP",
    "VALINHOS": "CFSP",
    "LOUVEIRA": "CFSP",
    "SANTO ANDRÉ": "CFSP",
    "TAUBATÉ": "CFSP",
    "SUZANO": "CFSP",
    "SANTOS": "SSAN",
    "CAMPINAS": "CFSP",
    "RIBEIRÃO PIRES": "CFSP",
    "RIO GRANDE DA SERRA": "CFSP",
    "SÃO PAULO": "CFSP",
    "SÃO CAETANO DO SUL": "CFSP",
    "ITAQUAQUECETUBA": "SITA",
    "VINHEDO": "CFSP",
    "JUIZ DE FORA": "CFSP",
    "CAMPO LIMPO PAULISTA": "CFSP",
    "GUARUJÁ": "SGUA",
    "MONTE MOR": "CFSP",
    "RIBEIRÃO PRETO": "CFSP",
    "APARECIDA": "CFSP",
    "CONGONHAS": "CEJF",
    "CACHOEIRA PAULISTA": "CFSP",
    "PINDAMONHANGABA": "CFSP",
    "GUARÁ": "CFSP",
    "LORENA": "CFSP",
    "RESENDE": "CFBA",
    "BARRA MANSA": "CFBA",
    "CRUZEIRO": "CFSP",
    "PORTO REAL": "CFBA",
    "QUELUZ": "CFSP",
    "JACAREÍ": "CFSP",
    "SÃO JOSÉ DOS CAMPOS": "CFSP",
    "GUARAREMA": "CFSP",
    "CAÇAPAVA": "CFSP",
    "MOGI DAS CRUZES": "CFSP",
    "ROSEIRA": "CFSP",
    "SARZEDO": "CFJF",
}

# =====================================================
# IDENTIFICAÇÃO DAS COLUNAS
# =====================================================

col_municipio = None
col_centro = None

for c in df.columns:

    texto = str(c).upper()

    if "MUNIC" in texto:
        col_municipio = c

    if "CENTRO" in texto and "REQUISI" in texto:
        col_centro = c

if col_municipio is None:
    st.error("Coluna Município não encontrada.")
    st.stop()

if col_centro is None:
    st.error("Coluna Centro Requisição não encontrada.")
    st.stop()

# =====================================================
# VALIDAÇÃO
# =====================================================

def validar(row):

    municipio = str(row[col_municipio]).strip().upper()
    centro = str(row[col_centro]).strip().upper()

    # Município vazio assume CFSP
    if municipio in ["", "NAN"]:
        esperado = "CFSP"
    else:
        esperado = MAPEAMENTO.get(municipio)

    if esperado is None:
        return "VALIDAR MUNICÍPIO"

    if esperado != centro:
        return f"ERRO - CORRETO: {esperado}"

    return "OK"
df["Validação"] = df.apply(validar, axis=1)

erros = df[
    df["Validação"] != "OK"
].copy()

# Remover registros RN1 e RN2 das divergências
if "Aprovação" in erros.columns:

    erros = erros[
        ~erros["Aprovação"]
        .astype(str)
        .str.strip()
        .str.upper()
        .isin(["RN1", "RN2"])
    ]

# =====================================================
# DIVERGÊNCIAS
# =====================================================

valor_divergencias = pd.to_numeric(
    erros["Preço na Aprovação"],
    errors="coerce"
).fillna(0).sum()

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Municípios com Divergência",
        len(erros)
    )

with col2:
    st.metric(
        "Valor das Divergências",
        moeda_br(valor_divergencias)
    )

st.subheader("🏙 Municípios com Divergência")

colunas_exibir = [
    "Nº Ordem",
    "Texto Breve",
    "Centro de Trabalho Operação",
    "Nome do município",
    "Centro requisição",
    "Aprovação",
    "Preço na Aprovação",
    "Validação"
]

colunas_existentes = [
    c for c in colunas_exibir
    if c in erros.columns
]

st.dataframe(
    erros[colunas_existentes],
    use_container_width=True
)
# =====================================================
# ITENS SEM APROVAÇÃO
# =====================================================

if "Aprovação" in df.columns:

    sem_aprovacao = df[
        df["Aprovação"].isna()
        |
        (
            df["Aprovação"]
            .astype(str)
            .str.strip()
            == ""
        )
    ]

    valor_sem_aprovacao = pd.to_numeric(
        sem_aprovacao["Preço na Aprovação"],
        errors="coerce"
    ).fillna(0).sum()

    st.subheader("⚠️ Itens sem Aprovação")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Itens sem Aprovação",
            len(sem_aprovacao)
        )

    with col2:
        st.metric(
            "Valor sem Aprovação",
            moeda_br(valor_sem_aprovacao)
        )

    st.dataframe(
        sem_aprovacao,
        use_container_width=True
    )
# =====================================================
# STATUS EXECUÇÃO X PROGRAMAÇÃO
# =====================================================
# =====================================================
# MATRIZ DE LANÇAMENTOS
# =====================================================
import pandas as pd
import streamlit as st

st.subheader("📅 Lançamentos por Equipe")

matriz = df.copy()

# Excluir RN1 e RN2
if "Aprovação" in matriz.columns:
    matriz = matriz[
        ~matriz["Aprovação"]
        .astype(str)
        .str.strip()
        .str.upper()
        .isin(["RN1", "RN2"])
    ]

# Converter data
matriz["Data"] = pd.to_datetime(
    matriz["Data Início Planejado"],
    errors="coerce"
)

matriz["Dia"] = matriz["Data"].dt.day

# Identificar atividades indiretas
PADRAO_INDIRETO = (
    "INDIRETO|ALOJAMENTO|ENCARREGADO|"
    "CAMINHÃO|VAN|DESLOCAMENTO|BANDEIRA"
)

matriz["Tipo"] = (
    matriz["Descrição do Material"]
    .astype(str)
    .str.contains(
        PADRAO_INDIRETO,
        case=False,
        na=False
    )
)

matriz["Tipo"] = matriz["Tipo"].map(
    {
        True: "🟦",
        False: "🟩"
    }
)

# Criar painel
painel = pd.pivot_table(
    matriz,
    index="Centro de Trabalho Operação",
    columns="Dia",
    values="Tipo",
    aggfunc=lambda x: (
        "🟪"
        if len(set(x)) > 1
        else list(x)[0]
    )
)

data_base = (
    matriz["Data"]
    .dropna()
    .min()
)

ano = data_base.year
mes = data_base.month

# Preencher sem lançamento
painel = painel.fillna("🔴")

# Trocar por ⬜ nos finais de semana
for coluna in painel.columns:

    try:
        data = pd.Timestamp(
            year=ano,
            month=mes,
            day=int(coluna)
        )

        if data.weekday() >= 5:  # sábado ou domingo
            painel[coluna] = painel[coluna].replace(
                "🔴",
                "⬜"
            )

    except:
        pass

dias_semana = {
    "Mon": "Seg",
    "Tue": "Ter",
    "Wed": "Qua",
    "Thu": "Qui",
    "Fri": "Sex",
    "Sat": "Sáb",
    "Sun": "Dom"
}

novos_nomes = {}

for dia in painel.columns:

    try:
        data = pd.Timestamp(
            year=ano,
            month=mes,
            day=int(dia)
        )

        novos_nomes[dia] = (
            f"{dia:02d} "
            f"({dias_semana[data.strftime('%a')]})"
        )

    except:
        novos_nomes[dia] = dia

painel.rename(
    columns=novos_nomes,
    inplace=True
)

# Destacar colunas de final de semana
def destacar_fds(col):

    nome = str(col.name)

    if "(Sáb)" in nome or "(Dom)" in nome:
        return ["background-color:#EAF4FF"] * len(col)

    return [""] * len(col)

# Formatação dos símbolos
# NÃO aplica background-color para não sobrescrever o azul do FDS
def destacar_status(val):

    if val in ["🔴", "⬜"]:
        return (
            "font-size:22px;"
            "font-weight:bold;"
            "text-align:center;"
        )

    return (
        "font-size:18px;"
        "font-weight:bold;"
        "text-align:center;"
    )

# Estilo da tabela
st.markdown("""
<style>
[data-testid="stDataFrame"] table {
    font-size: 18px !important;
}

[data-testid="stDataFrame"] td {
    font-size: 18px !important;
    font-weight: bold !important;
    text-align: center !important;
}

[data-testid="stDataFrame"] th {
    font-size: 16px !important;
    font-weight: bold !important;
    text-align: center !important;
}
</style>
""", unsafe_allow_html=True)

# Exibir painel
st.dataframe(
    painel.style
          .apply(destacar_fds, axis=0)
          .map(destacar_status),
    use_container_width=True
)

# Legenda
st.caption("""
🟩 Direto

🟦 Indireto

🟪 Direto + Indireto

🔴 Sem lançamento em dia útil

⬜ Sem lançamento em final de semana

🟦 Coluna destacada = Final de Semana
""")
# =====================================================
# ORDENS COM QUANTIDADE REAL ZERO
# =====================================================

if "Quantidade Real" in df.columns:

    qtd_zero = df[
        (
            df["Quantidade Real"]
            .fillna(0)
            == 0
        )
    ].copy()

    st.subheader(
        "🚨 Ordens com Quantidade Real = 0"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Registros",
            len(qtd_zero)
        )

    with col2:

        st.metric(
            "Ordens Distintas",
            qtd_zero["Nº Ordem"].nunique()
            if "Nº Ordem" in qtd_zero.columns
            else 0
        )

    colunas_exibir = [
        "Nº Ordem",
        "Texto Breve",
        "Centro de Trabalho CAB.",
        "Centro de Trabalho Operação",
        "Quantidade Real",
        "Qtd. Req. Compra",
        "Preço na Aprovação",
        "Aprovação"
    ]

    colunas_exibir = [
        c
        for c in colunas_exibir
        if c in qtd_zero.columns
    ]

    st.dataframe(
        qtd_zero[colunas_exibir],
        use_container_width=True
    )
    qtd_zero = df[
    (
        df["Quantidade Real"]
        .fillna(0)
        == 0
    )
].copy()

if "Aprovação" in qtd_zero.columns:

    qtd_zero = qtd_zero[
        ~qtd_zero["Aprovação"]
        .astype(str)
        .str.strip()
        .str.upper()
        .isin(
            [
                "RN1",
                "RN2"
            ]
        )
    ]
    valor_qtd_zero = (
    qtd_zero["Preço na Aprovação"]
    .sum()
)

st.metric(
    "Valor Quantidade Real = 0",
    moeda_br(valor_qtd_zero)
)