import streamlit as st
import pandas as pd
import random


def render_custom_query():

    st.title("🔍 Custom Query")

    query = st.text_area(
        "Enter Business Query"
    )

    if st.button("Run Query"):

        results = []

        for i in range(10):

            results.append(
                {
                    "Order":
                        f"ORD-{1000+i}",
                    "Value":
                        random.randint(
                            100,
                            1000
                        ),
                    "Status":
                        random.choice(
                            [
                                "Completed",
                                "Pending"
                            ]
                        )
                }
            )

        st.dataframe(
            pd.DataFrame(results),
            use_container_width=True
        )