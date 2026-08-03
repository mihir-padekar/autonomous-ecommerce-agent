import streamlit as st
import pandas as pd
import random


def render_inventory_alerts():

    st.title("📦 Inventory Alerts")

    inventory = []

    for i in range(25):

        inventory.append(
            {
                "SKU":
                    f"SKU-{1000+i}",
                "Product":
                    f"Product {i}",
                "Stock":
                    random.randint(1,20),
                "Threshold":
                    25,
                "Priority":
                    random.choice(
                        [
                            "High",
                            "Medium",
                            "Low"
                        ]
                    )
            }
        )

    df = pd.DataFrame(inventory)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )