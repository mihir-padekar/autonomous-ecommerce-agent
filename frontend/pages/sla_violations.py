import streamlit as st
import pandas as pd
import random


def render_sla_violations():

    st.title("⚠️ SLA Violations")

    records = []

    for i in range(40):

        records.append(
            {
                "Ticket":
                    f"SLA-{1000+i}",
                "Department":
                    random.choice(
                        [
                            "Support",
                            "Warehouse",
                            "Shipping"
                        ]
                    ),
                "Violation Hours":
                    random.randint(1,72),
                "Status":
                    random.choice(
                        [
                            "Open",
                            "Resolved"
                        ]
                    )
            }
        )

    df = pd.DataFrame(records)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )