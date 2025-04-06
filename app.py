import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Team Effort Dashboard", layout="wide")

# --- Sidebar Help ---
with st.sidebar:
    st.title("ℹ️ Instructions")
    st.markdown("""
    - Add team members and tasks
    - Enter effort (in hours)
    - Click 'Create Dashboard' to visualize & analyze
    - Use suggestions to balance workload
    """)

# --- Title ---
st.title("🛠️ Team Effort Dashboard")
st.markdown("Track and analyze team workload based on JIRA task assignments and effort in hours.")

st.divider()

# --- Session State ---
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# --- Form to Add Task ---
with st.form("task_form", clear_on_submit=True):
    st.subheader("➕ Add New Task")
    col1, col2, col3 = st.columns(3)
    with col1:
        member = st.text_input("👤 Team Member")
    with col2:
        task_id = st.text_input("📝 JIRA Task ID")
    with col3:
        hours = st.number_input("⏱️ Effort (Hours)", min_value=0.0, step=0.5)

    submitted = st.form_submit_button("✅ Add Task")
    if submitted and member and task_id and hours > 0:
        st.session_state.tasks.append({
            "Member": member.strip().title(),
            "Task ID": task_id.strip().upper(),
            "Hours": hours
        })
        st.success("Task added!")

# --- Task Table ---
st.subheader("📋 Current Tasks")
if st.session_state.tasks:
    task_df = pd.DataFrame(st.session_state.tasks)
    edited_df = st.data_editor(task_df, num_rows="dynamic", key="editor", use_container_width=True)
    st.session_state.tasks = edited_df.to_dict("records")
else:
    st.info("No tasks added yet. Use the form above to begin.")

st.divider()

# --- Dashboard ---
if st.button("📊 Create Dashboard"):
    if st.session_state.tasks:
        st.subheader("📈 Effort Dashboard")
        df = pd.DataFrame(st.session_state.tasks)
        effort_summary = df.groupby("Member")["Hours"].sum().reset_index().sort_values(by="Hours", ascending=False)
        total_effort = df["Hours"].sum()
        avg_effort = effort_summary["Hours"].mean()

        # 🔹 METRIC
        st.metric("🔢 Total Team Effort", f"{total_effort:.1f} hours")

        col1, col2 = st.columns(2)

        # 🔹 Bar Chart
        with col1:
            st.markdown("#### 📊 Hours per Member")
            bar_chart = alt.Chart(effort_summary).mark_bar(color="#4B8BBE").encode(
                x=alt.X("Member:N", title="Team Member"),
                y=alt.Y("Hours:Q", title="Total Hours"),
                tooltip=["Member", "Hours"]
            ).properties(height=400)
            st.altair_chart(bar_chart, use_container_width=True)

        # 🔹 Pie Chart
        with col2:
            st.markdown("#### 🥧 Contribution Percentage")
            pie_chart = px.pie(effort_summary, names='Member', values='Hours',
                               title='Effort Distribution', hole=0.4)
            st.plotly_chart(pie_chart, use_container_width=True)

        # 🔹 Suggestion Field
        st.markdown("### 💡 Suggestions for Task Assignment")
        underloaded = effort_summary[effort_summary["Hours"] < avg_effort]
        if not underloaded.empty:
            for _, row in underloaded.iterrows():
                st.info(f"✅ **{row['Member']}** has only **{row['Hours']} hours**, which is below the team average. Consider assigning more tasks.")
        else:
            st.success("Workload is evenly distributed! 🎉")

        # 🔹 Colored Effort Table
        st.markdown("### 🧾 Member Workload Table")
        colored_df = effort_summary.style.background_gradient(cmap='Blues').format({'Hours': '{:.1f}'})
        st.dataframe(colored_df, use_container_width=True)
    else:
        st.warning("⚠️ Please add some tasks to generate the dashboard.")
