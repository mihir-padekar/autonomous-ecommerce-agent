import plotly.graph_objects as go
import streamlit as st


PLOT_BG = "#111827"
GRID = "#1F2937"
TEXT = "#CBD5E1"


def _base_layout(fig):

    fig.update_layout(
        paper_bgcolor=PLOT_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(color=TEXT),
        margin=dict(
            l=20,
            r=20,
            t=40,
            b=20
        ),
        height=320
    )

    return fig


def delayed_orders_chart(data):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["days"],
            y=data["values"],
            mode="lines+markers",
            line=dict(
                color="#6366F1",
                width=4
            ),
            marker=dict(
                size=8
            ),
            fill="tozeroy"
        )
    )

    fig.update_xaxes(
        showgrid=False
    )

    fig.update_yaxes(
        gridcolor=GRID
    )

    fig = _base_layout(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )


def complaints_donut(data):

    fig = go.Figure()

    fig.add_trace(
        go.Pie(
            labels=data["labels"],
            values=data["values"],
            hole=.72,
            marker=dict(
                colors=[
                    "#6366F1",
                    "#10B981",
                    "#F59E0B",
                    "#EF4444"
                ]
            )
        )
    )

    fig = _base_layout(fig)

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={"displayModeBar": False}
    )


# def sla_chart(data):

#     fig = go.Figure()

#     fig.add_trace(
#         go.Bar(
#             x=data["days"],
#             y=data["values"],
#             marker_color="#8B5CF6"
#         )
#     )

#     fig.update_yaxes(
#         gridcolor=GRID
#     )

#     fig.update_xaxes(
#         showgrid=False
#     )

#     fig = _base_layout(fig)

#     st.plotly_chart(
#         fig,
#         use_container_width=True,
#         config={"displayModeBar": False}
#     )


def render_charts(mock_data):

    c1, c2 = st.columns(2)

    with c1:

        st.markdown(
            """
            <div class="chart-card">
            <h5>Delayed Orders Trend</h5>
            </div>
            """,
            unsafe_allow_html=True
        )

        delayed_orders_chart(
            mock_data["delayed_orders"]
        )

    with c2:

        st.markdown(
            """
            <div class="chart-card">
            <h5>Complaints by Category</h5>
            </div>
            """,
            unsafe_allow_html=True
        )

        complaints_donut(
            mock_data["complaints"]
        )

    # with c3:

    #     st.markdown(
    #         """
    #         <div class="chart-card">
    #         <h5>SLA Violations</h5>
    #         </div>
    #         """,
    #         unsafe_allow_html=True
    #     )

    #     sla_chart(
    #         mock_data["sla"]
    #     )