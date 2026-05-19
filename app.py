import io
from datetime import datetime, timedelta

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Streamlit Migration App",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
    :root {
        --ink: #17202a;
        --muted: #657080;
        --line: #d9dee7;
        --panel: #ffffff;
        --soft: #f5f7fb;
        --accent: #0f766e;
        --accent-2: #eab308;
        --danger: #dc2626;
    }

    .stApp {
        background:
            linear-gradient(180deg, rgba(245, 247, 251, 0.94), rgba(245, 247, 251, 1)),
            radial-gradient(circle at 10% 10%, rgba(15, 118, 110, 0.08), transparent 34%);
        color: var(--ink);
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: var(--muted);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1320px;
    }

    h1, h2, h3 {
        letter-spacing: 0;
    }

    .app-header {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        align-items: flex-start;
        padding: 1.1rem 0 1.25rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.25rem;
    }

    .app-title {
        font-size: 2rem;
        line-height: 1.15;
        font-weight: 760;
        margin: 0;
        color: var(--ink);
    }

    .app-subtitle {
        margin: 0.45rem 0 0;
        color: var(--muted);
        font-size: 0.98rem;
        max-width: 760px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.42rem;
        border: 1px solid var(--line);
        background: #ffffff;
        color: var(--ink);
        padding: 0.48rem 0.68rem;
        border-radius: 999px;
        font-size: 0.88rem;
        white-space: nowrap;
        margin-top: 0.15rem;
    }

    .dot {
        width: 0.52rem;
        height: 0.52rem;
        border-radius: 999px;
        background: var(--accent);
        display: inline-block;
    }

    .metric-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem;
        min-height: 118px;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.82rem;
        font-weight: 650;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    .metric-value {
        font-size: 1.75rem;
        font-weight: 760;
        color: var(--ink);
        line-height: 1.1;
    }

    .metric-delta {
        margin-top: 0.45rem;
        color: var(--accent);
        font-size: 0.86rem;
        font-weight: 650;
    }

    .section-title {
        font-size: 1.05rem;
        font-weight: 760;
        margin: 0 0 0.35rem;
    }

    .section-help {
        color: var(--muted);
        margin: 0 0 0.9rem;
        font-size: 0.92rem;
    }

    .panel {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.9rem 1rem;
    }

    div[data-testid="stTabs"] button {
        font-weight: 650;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 8px;
        border: 1px solid #0f766e;
        background: #0f766e;
        color: #ffffff;
        font-weight: 700;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: #115e59;
        background: #115e59;
        color: #ffffff;
    }

    @media (max-width: 720px) {
        .app-header {
            display: block;
        }

        .status-pill {
            margin-top: 0.85rem;
        }

        .app-title {
            font-size: 1.55rem;
        }
    }
</style>
"""


def inject_css() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def build_sample_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    days = pd.date_range(datetime.today() - timedelta(days=179), periods=180, freq="D")
    channels = ["Organic", "Paid", "Referral", "Email"]
    regions = ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon"]
    products = ["Starter", "Growth", "Enterprise"]

    records = []
    for day in days:
        weekday_boost = 1.18 if day.weekday() < 5 else 0.82
        trend = 1 + ((day - days[0]).days / len(days)) * 0.28
        for channel in channels:
            for product in products:
                base = {
                    "Organic": 820,
                    "Paid": 1050,
                    "Referral": 470,
                    "Email": 390,
                }[channel]
                product_weight = {
                    "Starter": 0.74,
                    "Growth": 1.0,
                    "Enterprise": 1.36,
                }[product]
                sessions = max(40, int(rng.normal(base * product_weight * weekday_boost * trend, 95)))
                conversion_rate = np.clip(
                    rng.normal(
                        {
                            "Organic": 0.052,
                            "Paid": 0.044,
                            "Referral": 0.071,
                            "Email": 0.084,
                        }[channel],
                        0.012,
                    ),
                    0.015,
                    0.14,
                )
                orders = max(1, int(sessions * conversion_rate))
                average_order_value = rng.normal(
                    {
                        "Starter": 64,
                        "Growth": 128,
                        "Enterprise": 310,
                    }[product],
                    14,
                )
                revenue = orders * max(22, average_order_value)
                records.append(
                    {
                        "date": day.date(),
                        "region": rng.choice(regions, p=[0.42, 0.18, 0.16, 0.13, 0.11]),
                        "channel": channel,
                        "product": product,
                        "sessions": sessions,
                        "orders": orders,
                        "revenue": round(float(revenue), 2),
                        "csat": round(float(np.clip(rng.normal(4.33, 0.34), 3.0, 5.0)), 2),
                    }
                )
    return pd.DataFrame.from_records(records)


def read_uploaded_file(uploaded_file: io.BytesIO | None) -> pd.DataFrame:
    if uploaded_file is None:
        return build_sample_data()

    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    if name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    st.error("CSV 또는 Excel 파일만 업로드할 수 있습니다.")
    return build_sample_data()


def normalize_data(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.copy()
    rename_map = {col: col.strip().lower().replace(" ", "_") for col in data.columns}
    data = data.rename(columns=rename_map)

    expected = ["date", "region", "channel", "product", "sessions", "orders", "revenue", "csat"]
    missing = [col for col in expected if col not in data.columns]
    if missing:
        st.warning(
            "업로드 파일에 필요한 컬럼이 없어 샘플 데이터를 사용합니다. "
            f"필요 컬럼: {', '.join(expected)}"
        )
        return build_sample_data()

    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    for col in ["sessions", "orders", "revenue", "csat"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["date", "region", "channel", "product"])
    numeric_defaults = {"sessions": 0, "orders": 0, "revenue": 0.0, "csat": 0.0}
    data = data.fillna(numeric_defaults)
    return data


def format_currency(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:,.0f}"


def pct_change(current: float, previous: float) -> float:
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100


def date_filter(data: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp]:
    min_date = data["date"].min().date()
    max_date = data["date"].max().date()
    default_start = max(min_date, max_date - timedelta(days=60))
    return st.sidebar.date_input(
        "기간",
        value=(default_start, max_date),
        min_value=min_date,
        max_value=max_date,
    )


def filter_data(data: pd.DataFrame) -> pd.DataFrame:
    uploaded_file = st.sidebar.file_uploader("데이터 업로드", type=["csv", "xlsx", "xls"])
    data = normalize_data(read_uploaded_file(uploaded_file))

    selected_dates = date_filter(data)
    if len(selected_dates) != 2:
        start_date, end_date = data["date"].min().date(), data["date"].max().date()
    else:
        start_date, end_date = selected_dates

    regions = sorted(data["region"].dropna().unique())
    channels = sorted(data["channel"].dropna().unique())
    products = sorted(data["product"].dropna().unique())

    selected_regions = st.sidebar.multiselect("지역", regions, default=regions)
    selected_channels = st.sidebar.multiselect("채널", channels, default=channels)
    selected_products = st.sidebar.multiselect("상품", products, default=products)

    mask = (
        (data["date"].dt.date >= start_date)
        & (data["date"].dt.date <= end_date)
        & (data["region"].isin(selected_regions))
        & (data["channel"].isin(selected_channels))
        & (data["product"].isin(selected_products))
    )
    return data.loc[mask].copy()


def metric_card(label: str, value: str, delta: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-delta">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div class="app-header">
            <div>
                <h1 class="app-title">운영 성과 대시보드</h1>
                <p class="app-subtitle">
                    핵심 지표, 추세, 채널별 성과, 원본 데이터 편집까지 한 화면에서 확인합니다.
                </p>
            </div>
            <div class="status-pill"><span class="dot"></span>Live Streamlit App</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    st.sidebar.title("설정")
    st.sidebar.caption("필터를 바꾸면 모든 지표와 차트가 즉시 갱신됩니다.")


def render_kpis(data: pd.DataFrame) -> None:
    if data.empty:
        st.info("선택한 조건에 해당하는 데이터가 없습니다.")
        return

    latest_date = data["date"].max()
    midpoint = latest_date - timedelta(days=30)
    current = data[data["date"] > midpoint]
    previous = data[(data["date"] <= midpoint) & (data["date"] > midpoint - timedelta(days=30))]

    revenue = data["revenue"].sum()
    orders = data["orders"].sum()
    sessions = data["sessions"].sum()
    conversion = orders / sessions if sessions else 0
    csat = data["csat"].mean()

    current_revenue = current["revenue"].sum()
    previous_revenue = previous["revenue"].sum()
    current_orders = current["orders"].sum()
    previous_orders = previous["orders"].sum()
    current_csat = current["csat"].mean() if not current.empty else 0
    previous_csat = previous["csat"].mean() if not previous.empty else 0

    cols = st.columns(4)
    with cols[0]:
        metric_card("Revenue", format_currency(revenue), f"{pct_change(current_revenue, previous_revenue):+.1f}% vs prev")
    with cols[1]:
        metric_card("Orders", f"{orders:,.0f}", f"{pct_change(current_orders, previous_orders):+.1f}% vs prev")
    with cols[2]:
        metric_card("Conversion", f"{conversion:.2%}", f"{sessions:,.0f} sessions")
    with cols[3]:
        metric_card("CSAT", f"{csat:.2f}", f"{current_csat - previous_csat:+.2f} pts vs prev")


def render_trend_chart(data: pd.DataFrame) -> None:
    daily = (
        data.groupby("date", as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("orders", "sum"), sessions=("sessions", "sum"))
        .sort_values("date")
    )
    daily["date"] = pd.to_datetime(daily["date"])

    base = alt.Chart(daily).encode(x=alt.X("date:T", title=None))
    revenue_line = base.mark_line(color="#0f766e", strokeWidth=3).encode(
        y=alt.Y("revenue:Q", title="Revenue"),
        tooltip=[
            alt.Tooltip("date:T", title="Date"),
            alt.Tooltip("revenue:Q", title="Revenue", format="$,.0f"),
            alt.Tooltip("orders:Q", title="Orders", format=","),
        ],
    )
    revenue_area = base.mark_area(color="#0f766e", opacity=0.12).encode(y="revenue:Q")
    st.altair_chart((revenue_area + revenue_line).properties(height=330), use_container_width=True)


def render_channel_chart(data: pd.DataFrame) -> None:
    channel = (
        data.groupby("channel", as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("orders", "sum"), sessions=("sessions", "sum"))
        .sort_values("revenue", ascending=False)
    )
    chart = (
        alt.Chart(channel)
        .mark_bar(cornerRadiusTopRight=4, cornerRadiusBottomRight=4, color="#2563eb")
        .encode(
            x=alt.X("revenue:Q", title="Revenue"),
            y=alt.Y("channel:N", title=None, sort="-x"),
            tooltip=[
                alt.Tooltip("channel:N", title="Channel"),
                alt.Tooltip("revenue:Q", title="Revenue", format="$,.0f"),
                alt.Tooltip("orders:Q", title="Orders", format=","),
                alt.Tooltip("sessions:Q", title="Sessions", format=","),
            ],
        )
        .properties(height=330)
    )
    st.altair_chart(chart, use_container_width=True)


def render_product_mix(data: pd.DataFrame) -> None:
    product = (
        data.groupby("product", as_index=False)
        .agg(revenue=("revenue", "sum"), orders=("orders", "sum"))
        .sort_values("revenue", ascending=False)
    )
    chart = (
        alt.Chart(product)
        .mark_arc(innerRadius=64, outerRadius=126)
        .encode(
            theta=alt.Theta("revenue:Q"),
            color=alt.Color(
                "product:N",
                scale=alt.Scale(range=["#0f766e", "#eab308", "#2563eb", "#dc2626"]),
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("product:N", title="Product"),
                alt.Tooltip("revenue:Q", title="Revenue", format="$,.0f"),
                alt.Tooltip("orders:Q", title="Orders", format=","),
            ],
        )
        .properties(height=320)
    )
    st.altair_chart(chart, use_container_width=True)


def render_region_table(data: pd.DataFrame) -> None:
    region = (
        data.groupby("region", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            orders=("orders", "sum"),
            sessions=("sessions", "sum"),
            csat=("csat", "mean"),
        )
        .sort_values("revenue", ascending=False)
    )
    region["conversion"] = np.where(region["sessions"] > 0, region["orders"] / region["sessions"], 0)
    st.dataframe(
        region,
        use_container_width=True,
        hide_index=True,
        column_config={
            "region": st.column_config.TextColumn("Region"),
            "revenue": st.column_config.NumberColumn("Revenue", format="$%.2f"),
            "orders": st.column_config.NumberColumn("Orders", format="%d"),
            "sessions": st.column_config.NumberColumn("Sessions", format="%d"),
            "csat": st.column_config.NumberColumn("CSAT", format="%.2f"),
            "conversion": st.column_config.ProgressColumn(
                "Conversion",
                min_value=0,
                max_value=max(0.01, float(region["conversion"].max())),
                format="%.2f",
            ),
        },
    )


def render_data_tools(data: pd.DataFrame) -> None:
    st.markdown('<p class="section-title">데이터 편집</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-help">표에서 값을 수정한 뒤 CSV로 내려받을 수 있습니다.</p>',
        unsafe_allow_html=True,
    )
    edited = st.data_editor(
        data.sort_values("date", ascending=False).head(500),
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "date": st.column_config.DateColumn("Date"),
            "region": st.column_config.TextColumn("Region"),
            "channel": st.column_config.TextColumn("Channel"),
            "product": st.column_config.TextColumn("Product"),
            "sessions": st.column_config.NumberColumn("Sessions", min_value=0, step=1),
            "orders": st.column_config.NumberColumn("Orders", min_value=0, step=1),
            "revenue": st.column_config.NumberColumn("Revenue", min_value=0.0, format="$%.2f"),
            "csat": st.column_config.NumberColumn("CSAT", min_value=0.0, max_value=5.0, format="%.2f"),
        },
    )
    csv = edited.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "CSV 다운로드",
        data=csv,
        file_name=f"streamlit_dashboard_export_{datetime.now():%Y%m%d_%H%M}.csv",
        mime="text/csv",
        use_container_width=True,
    )


def render_insights(data: pd.DataFrame) -> None:
    if data.empty:
        return

    by_channel = data.groupby("channel")["revenue"].sum().sort_values(ascending=False)
    by_product = data.groupby("product")["orders"].sum().sort_values(ascending=False)
    by_region = data.groupby("region")["csat"].mean().sort_values(ascending=False)

    best_channel = by_channel.index[0]
    best_product = by_product.index[0]
    best_region = by_region.index[0]

    cols = st.columns(3)
    with cols[0]:
        st.metric("Top Channel", best_channel, format_currency(by_channel.iloc[0]))
    with cols[1]:
        st.metric("Best Seller", best_product, f"{by_product.iloc[0]:,.0f} orders")
    with cols[2]:
        st.metric("Highest CSAT", best_region, f"{by_region.iloc[0]:.2f}")


def main() -> None:
    inject_css()
    render_sidebar()

    raw_data = build_sample_data()
    data = filter_data(raw_data)

    render_header()
    render_kpis(data)

    st.write("")
    tabs = st.tabs(["Overview", "Channels", "Regions", "Data"])

    with tabs[0]:
        st.markdown('<p class="section-title">매출 추세</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-help">선택한 기간의 일별 매출 흐름입니다.</p>', unsafe_allow_html=True)
        render_trend_chart(data)
        render_insights(data)

    with tabs[1]:
        col_left, col_right = st.columns([1.35, 1])
        with col_left:
            st.markdown('<p class="section-title">채널별 매출</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-help">유입 채널별 매출, 주문, 세션을 비교합니다.</p>', unsafe_allow_html=True)
            render_channel_chart(data)
        with col_right:
            st.markdown('<p class="section-title">상품 믹스</p>', unsafe_allow_html=True)
            st.markdown('<p class="section-help">상품군별 매출 기여도를 확인합니다.</p>', unsafe_allow_html=True)
            render_product_mix(data)

    with tabs[2]:
        st.markdown('<p class="section-title">지역별 성과</p>', unsafe_allow_html=True)
        st.markdown('<p class="section-help">지역 단위의 매출, 전환율, 만족도를 비교합니다.</p>', unsafe_allow_html=True)
        render_region_table(data)

    with tabs[3]:
        render_data_tools(data)


if __name__ == "__main__":
    main()
