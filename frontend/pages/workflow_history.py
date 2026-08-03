import streamlit as st
import pandas as pd
import re
from services.workflow_service import WorkflowService
from components.loader import loading


def clear_search_box():
    """Callback function to clear the search input field in session state."""
    st.session_state["workflow_search_input"] = ""


def render_workflow_history():
    st.title("📜 Workflow History")

    # Fetch global live history list
    with loading("Fetching Workflows..."):
        data = WorkflowService.get_real_workflow_history()

    if data and "Error" in data[0]:
        st.error(f"⚠️ {data[0]['Error']}")
        st.info("Make sure your backend API service is running on http://127.0.0.1:8000")
        return

    df = pd.DataFrame(data)

    # Smart Search input linked to session_state key
    search = st.text_input(
        "Search or Inspect", 
        placeholder="Search Workflow ID (e.g., 15cb28bd...)",
        key="workflow_search_input"
    ).strip()

    # Regex rule to identify a UUID/Workflow ID structure
    is_uuid = bool(re.match(r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$", search))

    # --- SCENARIO A: User Pasted a Specific Workflow ID ---
    if is_uuid:
        st.subheader(f"🔍 Inspecting Workflow: `{search}`")
        
        with st.spinner("Fetching execution logs from agents..."):
            details = WorkflowService.get_workflow_details(search)

        if isinstance(details, dict) and details.get("NotFound"):
            st.warning("No live trace found for this Workflow ID. Please check the identifier.")
        elif details and "Error" in details[0]:
            st.error(f"Could not load details: {details[0]['Details']}")
        else:
            details_df = pd.DataFrame(details)
            
            # Display step-by-step trace metrics
            st.write("### ⚙️ Agent Execution Timeline")
            st.dataframe(
                details_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Fixed Back button that calls the clearing callback function
            st.button(
                "⬅️ Clear inspection and return to main list", 
                on_click=clear_search_box
            )
            
        return  # Stop execution here so we don't render the global list below

    # --- SCENARIO B: Normal workflow table view / general text filtering ---
    if search and not df.empty:
        df = df[df["Workflow Name"].str.contains(search, case=False, na=False)]

    if not df.empty:
        st.write("### 📋 Recent Workflows")
        st.caption("💡 Tip: Copy any Workflow ID from this table and paste it above to inspect agent internals.")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=500
        )
    else:
        st.warning("No workflow records found.")