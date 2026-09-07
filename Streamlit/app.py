# ============================================================
# Customer Churn Risk Dashboard — MVP (Streamlit)
# Ejecutar con:  streamlit run app.py
# Datos: df_test.csv y model_metrics.csv en el mismo directorio.
# ============================================================

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

CUSTOMERS_PATH = BASE_DIR / "df_test.csv"
METRICS_PATH = BASE_DIR / "model_metrics.csv"

# ============================================================
# CONFIGURACIÓN
# ============================================================

st.set_page_config(
    page_title="Customer Churn Risk Dashboard",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# COLORES
# ============================================================

RISK_COLORS = {
    "Low": "#2E9E5B",
    "Medium": "#E8912D",
    "High": "#D64545",
}


# ============================================================
# ESTILOS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #F7F8FA;
    }

    [data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E6E8EB;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        color: #6B7280;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.9rem;
        font-weight: 700;
        color: #111827;
    }

    .card {
        background: #FFFFFF;
        border: 1px solid #E6E8EB;
        border-radius: 12px;
        padding: 22px 26px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }

    .section-title {
        font-size: 1.15rem;
        font-weight: 650;
        color: #111827;
        margin-bottom: 4px;
    }

    .section-sub {
        font-size: 0.85rem;
        color: #6B7280;
        margin-bottom: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CARGAR DATOS
# ============================================================

@st.cache_data
def load_customers():

    df = pd.read_csv(CUSTOMERS_PATH)

    # Customer ID
    df["customerid"] = df["customerid"].astype(str)

    # Asegurar nombre correcto de contract
    df = df.rename(columns={"type": "contract"})

    # Convertir tipos numéricos
    df["Probabilidad_Churn"] = pd.to_numeric(
        df["Probabilidad_Churn"],
        errors="coerce"
    )

    df["monthlycharges"] = pd.to_numeric(
        df["monthlycharges"],
        errors="coerce"
    )

    df["totalcharges"] = pd.to_numeric(
        df["totalcharges"],
        errors="coerce"
    )

    df["tenure_days"] = pd.to_numeric(
        df["tenure_days"],
        errors="coerce"
    )

    # Tenure en meses
    df["tenure_months"] = (
        df["tenure_days"] / 30.44
    ).round(0)

    # ========================================================
    # NIVEL DE RIESGO
    # ========================================================

    def riesgo(probabilidad):

        if probabilidad > 0.70:
            return "High"

        elif probabilidad > 0.30:
            return "Medium"

        else:
            return "Low"

    df["Nivel_Riesgo"] = df["Probabilidad_Churn"].apply(riesgo)

    return df


@st.cache_data
def load_metrics():

    m = pd.read_csv(METRICS_PATH)

    return dict(
        zip(
            m["Metric"],
            m["Value"]
        )
    )


# ============================================================
# CARGAR DATASETS
# ============================================================

customers = load_customers()
metrics = load_metrics()


# ============================================================
# SESSION STATE
# ============================================================

if "selected_customer" not in st.session_state:

    st.session_state.selected_customer = (
        customers["customerid"].iloc[0]
    )


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def risk_badge(level):

    color = RISK_COLORS[level]

    return (
        f'<span style="'
        f'background:{color}1A;'
        f'color:{color};'
        f'border:1px solid {color};'
        f'padding:4px 14px;'
        f'border-radius:999px;'
        f'font-weight:700;'
        f'font-size:0.85rem;">'
        f'{level.upper()} RISK'
        f'</span>'
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📉 Churn Analytics")
st.sidebar.caption("B2B SaaS · Customer Churn Risk Dashboard")

page = st.sidebar.radio(
    "Select Page",
    [
        "Overview",
        "Customer Detail",
        "Model Performance"
    ]
)

st.sidebar.markdown("---")




# ============================================================
# 1. OVERVIEW
# ============================================================

if page == "Overview":

    st.title("Customer Churn Risk Overview")

    st.caption(
        "Select a customer to view their details."
    )

    # ========================================================
    # FILTROS
    # ========================================================

    with st.sidebar:

        st.subheader("Filters")

        f_risk = st.multiselect(
            "Risk Level",
            ["High", "Medium", "Low"],
            default=["High", "Medium", "Low"]
        )

        contract_options = sorted(
            customers["contract"]
            .dropna()
            .unique()
        )

        f_contract = st.multiselect(
            "Contract",
            contract_options,
            default=contract_options
        )

        f_prob = st.slider(
            "Churn Probability",
            0.0,
            1.0,
            (0.0, 1.0),
            0.01,
            help="Filter customers by predicted churn probability."
        )

    # ========================================================
    # DATAFRAME FILTRADO
    # ========================================================

    dff = customers[
        customers["Nivel_Riesgo"].isin(f_risk)
        &
        customers["contract"].isin(f_contract)
        &
        customers["Probabilidad_Churn"].between(
            f_prob[0],
            f_prob[1]
        )
    ]

    # ========================================================
    # KPIs
    # ========================================================

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total Customers",
        f"{len(dff):,}"
    )

    c2.metric(
        "🔴 High Risk",
        f"{(dff['Nivel_Riesgo'] == 'High').sum():,}"
    )

    c3.metric(
        "🟠 Medium Risk",
        f"{(dff['Nivel_Riesgo'] == 'Medium').sum():,}"
    )

    c4.metric(
        "🟢 Low Risk",
        f"{(dff['Nivel_Riesgo'] == 'Low').sum():,}"
    )

    st.markdown("")

    # ========================================================
    # DISTRIBUCIÓN DE RIESGO
    # ========================================================

    dist = (
        dff["Nivel_Riesgo"]
        .value_counts()
        .reindex(
            ["Low", "Medium", "High"],
            fill_value=0
        )
        .rename_axis("Risk")
        .reset_index(name="Customers")
    )

    dist["Share"] = (
        dist["Customers"]
        /
        max(dist["Customers"].sum(), 1)
    )

    col_chart, col_gap = st.columns([1, 2])

    # --------------------------------------------------------
    # GRÁFICO
    # --------------------------------------------------------

    with col_chart:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            'Risk Distribution'
            '</div>',
            unsafe_allow_html=True
        )

        fig = go.Figure(
            go.Bar(
                y=dist["Risk"][::-1],
                x=dist["Customers"][::-1],
                orientation="h",
                marker_color=[
                    RISK_COLORS[r]
                    for r in dist["Risk"][::-1]
                ],
                text=[
                    f"{n:,} ({s:.0%})"
                    for n, s in zip(
                        dist["Customers"][::-1],
                        dist["Share"][::-1]
                    )
                ],
                textposition="outside"
            )
        )

        fig.update_layout(
            height=230,
            margin=dict(
                l=10,
                r=60,
                t=10,
                b=10
            ),
            plot_bgcolor="white",
            xaxis=dict(
                showgrid=False,
                showticklabels=False,
                title=""
            ),
            yaxis=dict(
                title=""
            ),
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # CLIENTES EN RIESGO
    # --------------------------------------------------------

    with col_gap:

        st.markdown(
            '<div class="section-title">'
            'Customers at Risk'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-sub">'
            'Ordered by churn probability '
            '(highest first). Select a row '
            'to view the details.'
            '</div>',
            unsafe_allow_html=True  
        )

        table = (
            dff
            .sort_values(
                "Probabilidad_Churn",
                ascending=False
            )[
                [
                    "customerid",
                    "Probabilidad_Churn",
                    "Nivel_Riesgo",
                    "contract",
                    "tenure_months",
                    "monthlycharges"
                ]
            ]
            .rename(
                columns={
                    "customerid": "Customer ID",
                    "Probabilidad_Churn": "Churn Probability",
                    "Nivel_Riesgo": "Risk Level",
                    "contract": "Contract",
                    "tenure_months": "Tenure (months)",
                    "monthlycharges": "Monthly Charges"
                }
            )
        )

        # Convertir probabilidad a porcentaje visible
        table["Churn Probability"] = (
        table["Churn Probability"] * 100
        ).round(1).astype(str) + "%"

        event = st.dataframe(
            table,
            use_container_width=True,
            height=430,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config={

        

                "Monthly Charges":
                    st.column_config.NumberColumn(
                        "Monthly Charges",
                        format="$%.2f"
                    )
            }
        )

        if event.selection.rows:

            chosen = (
                table
                .iloc[
                    event.selection.rows[0]
                ]["Customer ID"]
            )

            st.session_state.selected_customer = chosen

            st.info(
                f"Customer **{chosen}** selected. "
                f"Go to **Customer Detail** to view their profile."
            )


# ============================================================
# 2. CUSTOMER DETAIL
# ============================================================


elif page == "Customer Detail":

    st.title("Customer Detail")

    st.caption(
        "Individual customer profile and their churn risk level"
    )

    # ========================================================
    # SELECTOR DE CLIENTE
    # ========================================================

    sorted_ids = (
        customers
        .sort_values(
            "Probabilidad_Churn",
            ascending=False
        )["customerid"]
        .tolist()
    )

    current_customer = (
        st.session_state.selected_customer
    )

    if current_customer in sorted_ids:

        idx = sorted_ids.index(
            current_customer
        )

    else:

        idx = 0

    selected = st.selectbox(
        "Select Customer",
        sorted_ids,
        index=idx
    )

    st.session_state.selected_customer = selected

    # ========================================================
    # CLIENTE SELECCIONADO
    # ========================================================

    cust = (
        customers.loc[
            customers["customerid"] == selected
        ]
        .iloc[0]
    )

    prob = float(
        cust["Probabilidad_Churn"]
    )

    level = cust["Nivel_Riesgo"]

    color = RISK_COLORS[level]

    st.markdown("")

    # ========================================================
    # RIESGO + INFORMACIÓN
    # ========================================================

    col_risk, col_info = st.columns(
        [1, 2]
    )

    # --------------------------------------------------------
    # GAUGE
    # --------------------------------------------------------

    with col_risk:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=prob * 100,

                number={
                    "suffix": "%",
                    "font": {
                        "size": 44
                    }
                },

                title={
                    "text": "CHURN PROBABILITY",
                    "font": {
                        "size": 13
                    }
                },

                gauge={

                    "axis": {
                        "range": [0, 100],
                        "tickwidth": 1,
                        "ticksuffix": "%"
                    },

                    "bar": {
                        "color": color,
                        "thickness": 0.28
                    },

                    "bgcolor": "#F1F2F4",

                    "steps": [

                        {
                            "range": [0, 30],
                            "color": "rgba(46, 158, 91, 0.12)"
                        },

                        {
                            "range": [30, 70],
                            "color": "rgba(232, 145, 45, 0.12)"
                        },

                        {
                            "range": [70, 100],
                            "color": "rgba(214, 69, 69, 0.12)"
                        }
                    ]
                }
            )
        )

        fig.update_layout(
            height=280,
            margin=dict(
                l=20,
                r=20,
                t=40,
                b=10
            ),
            paper_bgcolor="white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.markdown(
            f"""
            <div style="text-align:center;margin-top:-8px;">
                {risk_badge(level)}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # CUSTOMER INFORMATION
    # --------------------------------------------------------

    with col_info:

        st.markdown(
            '<div class="card">',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="section-title">'
            'Customer Information'
            '</div>',
            unsafe_allow_html=True
        )

        i1, i2 = st.columns(2)

        i1.markdown(
            f"**Customer ID**\n\n"
            f"{cust['customerid']}"
        )

        i2.markdown(
            f"**Contract**\n\n"
            f"{str(cust['contract']).title()}"
        )

        i1.markdown(
            f"**Tenure**\n\n"
            f"{int(cust['tenure_months'])} months"
        )

        i2.markdown(
            f"**Monthly Charges**\n\n"
            f"${cust['monthlycharges']:,.2f}"
        )

        st.markdown("---")

        st.markdown(
            '<div class="section-title">'
            'Recommended Action'
            '</div>',
            unsafe_allow_html=True
        )

        if level == "High":

            st.error(
                "**High churn risk**\n\n"
                "Contact the customer proactively. "
                "Consider a retention offer, contract review, "
                "service improvement or personalized incentive."
            )

        elif level == "Medium":

            st.warning(
                "**Moderate churn risk**\n\n"
                "Monitor the customer closely and consider "
                "an engagement campaign or personalized offer "
                "before the risk increases."
            )

        else:

            st.success(
                "**Low churn risk**\n\n"
                "Customer appears stable. Maintain service quality "
                "and consider upselling or cross-selling opportunities."
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

    # ========================================================
    # CUSTOMER PROFILE
    # ========================================================

    st.markdown("")

    st.markdown(
        '<div class="section-title">'
        'Customer Profile'
        '</div>',
        unsafe_allow_html=True
    )

    p1, p2, p3, p4 = st.columns(4)

    p1.metric(
        "Internet Service",
        str(cust["internetservice"]).title()
    )

    p2.metric(
        "Payment Method",
        str(cust["paymentmethod"])
        .replace("_", " ")
        .title()
    )

    p3.metric(
        "Paperless Billing",
        str(cust["paperlessbilling"]).title()
    )

    p4.metric(
        "Total Charges",
        f"${cust['totalcharges']:,.2f}"
    )

    # ========================================================
    # SUBSCRIBED SERVICES
    # ========================================================

    st.markdown("")

    st.markdown(
        '<div class="section-title">'
        'Subscribed Services'
        '</div>',
        unsafe_allow_html=True
    )

    services = {

        "Online Security":
            cust["onlinesecurity"],

        "Online Backup":
            cust["onlinebackup"],

        "Device Protection":
            cust["deviceprotection"],

        "Tech Support":
            cust["techsupport"],

        "Streaming TV":
            cust["streamingtv"],

        "Streaming Movies":
            cust["streamingmovies"],

        "Multiple Lines":
            cust["multiplelines"]
    }

    service_cols = st.columns(4)

    for i, (service, value) in enumerate(
        services.items()
    ):

        with service_cols[i % 4]:

            if str(value).lower() == "yes":

                st.success(
                    f"✓ {service}"
                )

            else:

                st.markdown(
                    f"""
                    <div style="
                        padding:10px;
                        margin-bottom:8px;
                        border-radius:8px;
                        background:#F7F7F8;
                        color:#6B7280;
                    ">
                        — {service}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    # ========================================================
    # CUSTOMER CHARACTERISTICS
    # ========================================================

    st.markdown("")

    st.markdown(
        '<div class="section-title">'
        'Customer Characteristics'
        '</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Gender",
        str(cust["gender"]).title()
    )

    c2.metric(
        "Senior Citizen",
        "Yes"
        if cust["seniorcitizen"] == 1
        else "No"
    )

    c3.metric(
        "Partner",
        str(cust["partner"]).title()
    )

    c4.metric(
        "Dependents",
        str(cust["dependents"]).title()
    )

    # ========================================================
    # MODEL ASSESSMENT
    # ========================================================

    st.markdown("")

    st.markdown(
        '<div class="section-title">'
        'Model Assessment'
        '</div>',
        unsafe_allow_html=True
    )

    m1, m2, m3 = st.columns(3)

    m1.metric(
        "Churn Probability",
        f"{prob:.1%}"
    )

    m2.metric(
        "Risk Level",
        level
    )

    m3.metric(
        "Probability Range",
        str(cust["Rango_Probabilidad"])
    )

    # ========================================================
    # BUSINESS INTERPRETATION
    # ========================================================

    st.markdown("")

    st.markdown(
        '<div class="section-title">'
        'Business Interpretation'
        '</div>',
        unsafe_allow_html=True
    )

    if level == "High":

        st.markdown(
            f"""
            ### ⚠️ Immediate attention required

            This customer has an estimated **{prob:.1%} probability
            of churn**, placing the account in the
            **High Risk** category.

            The retention team should prioritize this customer for
            **proactive contact and retention actions**.
            """
        )

    elif level == "Medium":

        st.markdown(
            f"""
            ### 🔍 Customer requires monitoring

            This customer has an estimated **{prob:.1%} probability
            of churn**, placing the account in the
            **Medium Risk** category.

            The customer should be monitored and considered for
            **engagement or retention campaigns**.
            """
        )

    else:

        st.markdown(
            f"""
            ### ✅ Customer appears stable

            This customer has an estimated **{prob:.1%} probability
            of churn**, placing the account in the
            **Low Risk** category.

            The focus should remain on **service quality,
            customer satisfaction and potential upselling
            opportunities**.
            """
        )


# ============================================================
# 3. MODEL PERFORMANCE
# ============================================================

else:

    st.title("Model Performance")

    st.caption(
        "This section provides an overview of the model's performance metrics and their interpretation."
    )

    # ========================================================
    # KPIs DEL MODELO
    # ========================================================

    m1, m2, m3, m4 = st.columns(4)

    m1.metric(
        "AUC-ROC",
        f"{metrics.get('AUC-ROC', 0):.3f}"
    )

    m2.metric(
        "Accuracy",
        f"{metrics.get('Accuracy', 0):.0%}"
    )

    m3.metric(
        "Churn Recall",
        f"{metrics.get('Recall - Churn', 0):.0%}"
    )

    m4.metric(
        "Churn F1-score",
        f"{metrics.get('F1-Score - Churn', 0):.3f}"
    )

    st.markdown("")

    # ========================================================
    # EXPLICACIÓN
    # ========================================================

    st.info(
        "💡 **How to interpret this??** "
        "The model estimates the probability of each customer"
        "  churning. Customers are classified into Low (≤30%), Medium (30–70%), and High (>70%) based on their predicted probability."
    )

    # ========================================================
    # DETALLE DE MÉTRICAS
    # ========================================================

    with st.expander("Metric details"):

        st.markdown(
            f"""
            | Metric | Value | What it means |
            |---|---:|---|
            | **AUC-ROC** | {metrics.get('AUC-ROC', 0):.3f} | Ability to distinguish between customers who churn and those who stay. |
            | **Accuracy** | {metrics.get('Accuracy', 0):.0%} | Total percentage of correct predictions. |
            | **Churn Recall** | {metrics.get('Recall - Churn', 0):.0%} | Of the customers who actually churned, how many the model detected. |
            | **Churn Precision** | {metrics.get('Precision - Churn', 0):.0%} | Of the customers flagged as churned, how many actually left. |
            | **Churn F1-score** | {metrics.get('F1-Score - Churn', 0):.2f} | Balance between precision and recall. |
            """
        )

        st.markdown("---")

        st.markdown(
            "**Referencia visual AUC-ROC**"
        )

        # ====================================================
        # CURVA ROC VISUAL
        # ====================================================

        fpr = np.linspace(
            0,
            1,
            100
        )

        auc = float(
            metrics.get(
                "AUC-ROC",
                0.9
            )
        )

        # Evitar división por cero
        auc = min(
            max(auc, 0.01),
            0.99
        )

        k = auc / (1 - auc)

        tpr = (
            fpr ** (1 / k)
        )

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=fpr,
                y=tpr,
                mode="lines",
                name="ROC",
                line=dict(
                    color="#2563EB",
                    width=2.5
                )
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode="lines",
                name="Aleatorio",
                line=dict(
                    color="#9CA3AF",
                    dash="dash"
                )
            )
        )

        fig.update_layout(
            height=300,
            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10
            ),
            xaxis_title="False Positive Rate",
            yaxis_title="True Positive Rate",
            plot_bgcolor="white",
            showlegend=True,
            legend=dict(
                orientation="h",
                y=1.1
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )