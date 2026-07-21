import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Ethiopia Financial Inclusion Dashboard", layout="wide")

# ---------- Data Loading ----------
@st.cache_data
def load_data():
    main = pd.read_csv('data/processed/ethiopia_fi_enriched_main.csv')
    main['observation_date'] = pd.to_datetime(main['observation_date'], errors='coerce')
    impact = pd.read_csv('data/processed/ethiopia_fi_enriched_impact.csv')
    try:
        forecast = pd.read_csv('reports/forecast_table.csv')
    except FileNotFoundError:
        forecast = None
    return main, impact, forecast

main, impact, forecast = load_data()
obs = main[main['record_type'] == 'observation']
events = main[main['record_type'] == 'event']

st.title("🇪🇹 Ethiopia Financial Inclusion Dashboard")
st.caption("10 Academy Week 11 — Forecasting Access and Usage, 2025–2027")

page = st.sidebar.radio("Navigate", ["Overview", "Trends", "Forecasts", "Inclusion Projections"])

# ---------- Overview Page ----------
if page == "Overview":
    st.header("Overview")

    acc = obs[(obs['indicator_code']=='ACC_OWNERSHIP') & (obs['gender']=='all')].sort_values('observation_date')
    mm = obs[obs['indicator_code']=='ACC_MM_ACCOUNT'].sort_values('observation_date')
    crossover = obs[obs['indicator_code']=='USG_CROSSOVER'].sort_values('observation_date')

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Account Ownership (Access)", f"{acc['value_numeric'].iloc[-1]:.0f}%",
                f"+{acc['value_numeric'].iloc[-1] - acc['value_numeric'].iloc[-2]:.0f}pp since {acc['observation_date'].dt.year.iloc[-2]}")
    col2.metric("Mobile Money Accounts (Usage)", f"{mm['value_numeric'].iloc[-1]:.1f}%",
                f"+{mm['value_numeric'].iloc[-1] - mm['value_numeric'].iloc[0]:.1f}pp since {mm['observation_date'].dt.year.iloc[0]}")
    col3.metric("P2P / ATM Crossover Ratio", f"{crossover['value_numeric'].iloc[-1]:.2f}",
                "P2P now exceeds ATM cash withdrawals" if crossover['value_numeric'].iloc[-1] > 1 else "ATM still leads")
    recent_growth = acc['value_numeric'].diff().iloc[-1] / (acc['observation_date'].dt.year.diff().iloc[-1])
    col4.metric("Recent Access Growth Rate", f"{recent_growth:.1f} pp/yr", "Down from 2.75pp/yr (2017-21)")

    st.divider()
    st.subheader("Recent Growth Rate Deceleration")
    acc_calc = acc.copy()
    acc_calc['pp_per_year'] = acc_calc['value_numeric'].diff() / acc_calc['observation_date'].dt.year.diff()
    fig = px.bar(acc_calc.dropna(subset=['pp_per_year']), x=acc_calc.dropna(subset=['pp_per_year'])['observation_date'].dt.year.astype(str),
                 y='pp_per_year', labels={'x':'Period ending', 'pp_per_year':'pp growth per year'},
                 title="Account Ownership Growth Rate Has Slowed 4x Since 2017")
    st.plotly_chart(fig, use_container_width=True)

    st.info("Despite Telebirr (54.8M users) and M-Pesa (10.8M users) both scaling rapidly, account ownership grew only +3pp between 2021 and 2024 — the slowest interval on record. See the Trends page for the full pattern.")

# ---------- Trends Page ----------
elif page == "Trends":
    st.header("Trends")

    min_date, max_date = obs['observation_date'].min(), obs['observation_date'].max()
    date_range = st.slider("Date range", min_value=min_date.to_pydatetime(), max_value=max_date.to_pydatetime(),
                            value=(min_date.to_pydatetime(), max_date.to_pydatetime()))

    filtered = obs[(obs['observation_date'] >= date_range[0]) & (obs['observation_date'] <= date_range[1])]

    st.subheader("Access: Account Ownership Over Time")
    acc = filtered[(filtered['indicator_code']=='ACC_OWNERSHIP') & (filtered['gender']=='all')].sort_values('observation_date')
    fig1 = px.line(acc, x='observation_date', y='value_numeric', markers=True,
                    labels={'value_numeric':'% of adults','observation_date':'Date'},
                    title="Account Ownership Rate (Findex Survey Years)")

    events_in_range = events[(events['observation_date'] >= date_range[0]) & (events['observation_date'] <= date_range[1])].dropna(subset=['observation_date'])
    for _, ev in events_in_range.iterrows():
        x_val = ev['observation_date'].strftime('%Y-%m-%d')
        fig1.add_shape(type="line", x0=x_val, x1=x_val, y0=0, y1=1, yref="paper",
                       line=dict(dash="dash", color="gray", width=1), opacity=0.5)
        fig1.add_annotation(x=x_val, y=1, yref="paper", text=ev['indicator'],
                            showarrow=False, textangle=-90, font=dict(size=8), yanchor="bottom")

    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Channel Comparison: P2P vs ATM Transactions")
    channel_codes = ['USG_P2P_COUNT', 'USG_ATM_COUNT']
    channel_data = filtered[filtered['indicator_code'].isin(channel_codes)].sort_values('observation_date')
    if not channel_data.empty:
        fig2 = px.bar(channel_data, x='observation_date', y='value_numeric', color='indicator',
                       barmode='group', labels={'value_numeric':'Transaction count','observation_date':'Date'},
                       title="P2P vs ATM Transaction Volume")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No P2P/ATM data in selected date range.")

    st.subheader("Gender Gap in Account Ownership")
    gender_data = filtered[(filtered['indicator_code']=='ACC_OWNERSHIP') & (filtered['gender'].isin(['male','female']))]
    if not gender_data.empty:
        fig3 = px.bar(gender_data, x='observation_date', y='value_numeric', color='gender',
                       barmode='group', title="Male vs Female Account Ownership")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No gender-disaggregated data in selected date range.")

    st.download_button("Download filtered data (CSV)", filtered.to_csv(index=False), "filtered_data.csv", "text/csv")

# ---------- Forecasts Page ----------
elif page == "Forecasts":
    st.header("Forecasts: Access and Usage, 2025-2027")

    if forecast is None:
        st.error("Forecast table not found. Run notebooks/04_forecasting.ipynb first to generate reports/forecast_table.csv.")
    else:
        scenario = st.selectbox("Scenario", ["base", "optimistic", "pessimistic"])
        target = st.radio("Indicator", ["Access (Account Ownership)", "Usage (Mobile Money Account Rate)"])

        acc_hist = obs[(obs['indicator_code']=='ACC_OWNERSHIP') & (obs['gender']=='all')].sort_values('observation_date')
        mm_hist = obs[obs['indicator_code']=='ACC_MM_ACCOUNT'].sort_values('observation_date')

        fig = go.Figure()
        if target.startswith("Access"):
            fig.add_trace(go.Scatter(x=acc_hist['observation_date'].dt.year, y=acc_hist['value_numeric'],
                                       mode='lines+markers', name='Actual', line=dict(color='black', width=3)))
            for col, color in zip(['pessimistic','base','optimistic'], ['#dc2626','#2563eb','#059669']):
                fig.add_trace(go.Scatter(x=forecast['year'], y=forecast[f'access_{col}'], mode='lines+markers',
                                           name=col.capitalize(), line=dict(dash='dash', color=color)))
            fig.add_hline(y=70, line_dash="dot", line_color="gray", annotation_text="NFIS-II target (70%)")
            fig.update_layout(title="Access Forecast: Account Ownership", yaxis_title="% of adults")
        else:
            fig.add_trace(go.Scatter(x=mm_hist['observation_date'].dt.year, y=mm_hist['value_numeric'],
                                       mode='lines+markers', name='Actual', line=dict(color='black', width=3)))
            for col, color in zip(['pessimistic','base','optimistic'], ['#dc2626','#2563eb','#059669']):
                fig.add_trace(go.Scatter(x=forecast['year'], y=forecast[f'usage_{col}'], mode='lines+markers',
                                           name=col.capitalize(), line=dict(dash='dash', color=color)))
            fig.update_layout(title="Usage Forecast: Mobile Money Account Rate (Digital Payment proxy)", yaxis_title="% of adults")

        st.plotly_chart(fig, use_container_width=True)

        st.subheader(f"Projected values — {scenario} scenario")
        display_cols = ['year'] + [c for c in forecast.columns if scenario in c]
        st.dataframe(forecast[display_cols], use_container_width=True)

        st.markdown("""
        **Key milestones:**
        - Fayda Mandatory Banking Directive (compliance deadline Dec 2026) is the single largest lever for Access in this window.
        - M-Pesa/EthSwitch integration and EthioPay launch are the main Usage-side drivers.
        - The NFIS-II 70% Access target is not reached under any scenario by 2027.
        """)

        st.download_button("Download forecast table (CSV)", forecast.to_csv(index=False), "forecast_table.csv", "text/csv")

# ---------- Inclusion Projections Page ----------
elif page == "Inclusion Projections":
    st.header("Inclusion Projections & Key Questions")

    if forecast is None:
        st.error("Forecast table not found. Run notebooks/04_forecasting.ipynb first.")
    else:
        scenario = st.selectbox("Scenario", ["base", "optimistic", "pessimistic"], key="proj_scenario")

        latest_access = forecast[f'access_{scenario}'].iloc[-1]
        progress_pct = min(latest_access / 70 * 100, 100)

        st.subheader("Progress Toward NFIS-II 70% Access Target (by 2027)")
        st.progress(progress_pct / 100)
        st.write(f"Projected {latest_access:.1f}% by 2027 — {progress_pct:.0f}% of the way to the 70% target ({scenario} scenario).")

        st.divider()
        st.subheader("Answers to the Consortium's Key Questions")

        with st.expander("What drives financial inclusion in Ethiopia?"):
            st.write("Mobile money product launches (Telebirr, M-Pesa) and the Fayda digital ID rollout are the main modeled drivers of Access; infrastructure (4G coverage) and market entry/partnerships drive Usage. However, most of Ethiopia's historical Access growth (2014-2021) predates any of these events, pointing to underlying banking-sector expansion as a major baseline driver too.")

        with st.expander("How do events like product launches and policy changes affect inclusion outcomes?"):
            st.write("See the Event-Indicator Association Matrix (Task 3) — effects are modeled as gradual, lagged ramp-ups rather than instant jumps, typically taking 3-24 months to fully materialize depending on the event type.")

        with st.expander("How did financial inclusion change in 2025, and how will it look in 2026-2027?"):
            st.write(f"Under the {scenario} scenario: Access reaches {forecast[f'access_{scenario}'].iloc[-1]:.1f}% and Usage (mobile money proxy) reaches {forecast[f'usage_{scenario}'].iloc[-1]:.1f}% by 2027. See the Forecasts page for the full scenario range.")

        st.divider()
        st.caption("Note: 'Usage' in this dashboard is proxied by Mobile Money Account Rate (ACC_MM_ACCOUNT) since the dataset does not contain a direct time series for Global Findex's 'made or received a digital payment' metric.")