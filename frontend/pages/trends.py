import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from services.api_client import APIClient


def render_trends():

    st.title("📈 Delayed Orders Forecast")

    # -----------------------------
    # Get Forecast Data
    # -----------------------------
    data = APIClient.get_delay_forecast()

    history_df = pd.DataFrame(data["history"])
    forecast_df = pd.DataFrame(data["forecast"])

    # Handle empty response
    if history_df.empty or forecast_df.empty:
        st.warning("Forecast data unavailable.")
        return

    # Convert dates
    history_df["ds"] = pd.to_datetime(history_df["ds"])
    forecast_df["ds"] = pd.to_datetime(forecast_df["ds"])

    # -----------------------------
    # Plot
    # -----------------------------
    fig = go.Figure()

    # Historical Orders
    fig.add_trace(
        go.Scatter(
            x=history_df["ds"],
            y=history_df["y"],
            mode="lines+markers",
            name="Historical Orders"
        )
    )

    # Forecast
    fig.add_trace(
        go.Scatter(
            x=forecast_df["ds"],
            y=forecast_df["yhat"],
            mode="lines+markers",
            name="Forecast",
            line=dict(dash="dash")
        )
    )

    # Upper Confidence
    fig.add_trace(
        go.Scatter(
            x=forecast_df["ds"],
            y=forecast_df["yhat_upper"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        )
    )

    # Lower Confidence
    fig.add_trace(
        go.Scatter(
            x=forecast_df["ds"],
            y=forecast_df["yhat_lower"],
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(255,165,0,0.20)",
            line=dict(width=0),
            name="Confidence Interval",
            hoverinfo="skip"
        )
    )

    fig.update_layout(
        title="Monthly Delayed Orders Forecast",
        xaxis_title="Month",
        yaxis_title="Delayed Orders",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        font=dict(color="white"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # -----------------------------
    # Tables
    # -----------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Historical Data")
        st.dataframe(
            history_df,
            use_container_width=True
        )

    with col2:
        st.subheader("Forecast")
        st.dataframe(
            forecast_df,
            use_container_width=True
        )