import streamlit as st
import json
import pandas as pd
import polars as pl
from pathlib import Path
from datetime import datetime

# Config
TRACES_FILE = "traces_sample.json"
GRADES_FILE = "trace_grades.csv"

# Functions
def save_grades():
    """Save all grades to CSV"""
    data = []
    for trace in st.session_state.traces:
        trace_id = trace['id']
        grade_info = st.session_state.grades.get(trace_id, {'grade': 'UNGRADED', 'comment': ''})
        data.append({
            'trace_id': trace_id,
            'scenario': trace['scenario'],
            'grade': grade_info.get('grade', 'UNGRADED'),
            'comment': grade_info.get('comment', ''),
            'graded_at': grade_info.get('graded_at', datetime.now().isoformat())
        })
    
    df = pd.DataFrame(data)
    df.to_csv(GRADES_FILE, index=False)


def autosave_grades():
    """Auto-save grades whenever a change is made"""
    for trace_id in st.session_state.grades:
        if 'graded_at' not in st.session_state.grades[trace_id]:
            st.session_state.grades[trace_id]['graded_at'] = datetime.now().isoformat()
    save_grades()

# Page config
st.set_page_config(
    page_title="LLM Trace Grader",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 LLM Trace Grading Dashboard")
st.markdown("Grade e-ink reader sales assistant traces for quality and customer kindness")

# Initialize session state
if "traces" not in st.session_state:
    with open(TRACES_FILE, "r") as f:
        st.session_state.traces = json.load(f)

if "grades" not in st.session_state:
    # Load existing grades if they exist
    if Path(GRADES_FILE).exists():
        st.session_state.grades = {}
        df = pd.read_csv(GRADES_FILE)
        for _, row in df.iterrows():
            st.session_state.grades[row['trace_id']] = {
                'grade': row['grade'],
                'comment': row['comment'] if pd.notna(row['comment']) else ""
            }
    else:
        st.session_state.grades = {}

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

# Sidebar
with st.sidebar:
    st.header("Navigation")
    
    # Stats
    total_traces = len(st.session_state.traces)
    graded_count = sum(1 for t in st.session_state.traces if t['id'] in st.session_state.grades)
    pass_count = sum(1 for t in st.session_state.traces 
                    if t['id'] in st.session_state.grades 
                    and st.session_state.grades[t['id']]['grade'] == 'PASS')
    fail_count = sum(1 for t in st.session_state.traces 
                    if t['id'] in st.session_state.grades 
                    and st.session_state.grades[t['id']]['grade'] == 'FAIL')
    
    st.metric("Total Traces", total_traces)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Graded", graded_count)
    with col2:
        st.metric("✅ Pass", pass_count)
    with col3:
        st.metric("❌ Fail", fail_count)
    
    st.divider()
    
    # Navigation
    st.subheader("Quick Jump")
    trace_options = {}
    for i, trace in enumerate(st.session_state.traces):
        status_icon = "✅" if trace['id'] in st.session_state.grades else "⭕"
        grade_status = st.session_state.grades.get(trace['id'], {}).get('grade', '')
        if grade_status:
            status_icon = "✅" if grade_status == "PASS" else "❌"
        trace_options[f"{status_icon} {trace['id']} - {trace['scenario'][:30]}..."] = i
    
    selected_trace = st.selectbox("Jump to trace:", list(trace_options.keys()))
    st.session_state.current_index = trace_options[selected_trace]
    
    st.divider()
    
    # Save button
    if st.button("💾 Save All Grades", use_container_width=True, type="primary"):
        save_grades()
        st.success("✅ All grades saved successfully!")
    
    st.divider()
    st.markdown("### Export Options")
    if st.button("📥 Download CSV", use_container_width=True):
        if Path(GRADES_FILE).exists():
            with open(GRADES_FILE, "rb") as f:
                st.download_button(
                    label="Click to download",
                    data=f.read(),
                    file_name=f"trace_grades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

# Main content
current_trace = st.session_state.traces[st.session_state.current_index]
trace_id = current_trace['id']

# Header with navigation
col1, col2, col3 = st.columns([1, 8, 1])

with col1:
    if st.session_state.current_index > 0:
        if st.button("⬅️ Previous", use_container_width=True):
            st.session_state.current_index -= 1
            st.rerun()

with col2:
    st.markdown(f"### **{current_trace['id']}** - {current_trace['scenario']}")
    st.markdown(f"*Expected behavior:* {current_trace['expected_behavior']}")

with col3:
    if st.session_state.current_index < len(st.session_state.traces) - 1:
        if st.button("Next ➡️", use_container_width=True):
            st.session_state.current_index += 1
            st.rerun()

st.divider()

# Trace conversation display
st.subheader("Conversation")

for message in current_trace['conversation']:
    role = message['role']
    content = message['message']
    
    if role == "customer":
        with st.chat_message("user"):
            st.write(content)
    else:  # assistant
        with st.chat_message("assistant"):
            st.write(content)

st.divider()

# Grading section
st.subheader("Grade this Trace")

col1, col2 = st.columns(2)

with col1:
    if st.button(
        "✅ PASS - Good customer service",
        use_container_width=True,
        key=f"pass_{trace_id}",
        type="secondary"
    ):
        st.session_state.grades[trace_id] = {
            'grade': 'PASS',
            'comment': st.session_state.grades.get(trace_id, {}).get('comment', '')
        }
        autosave_grades()
        st.rerun()

with col2:
    if st.button(
        "❌ FAIL - Poor customer service",
        use_container_width=True,
        key=f"fail_{trace_id}",
        type="secondary"
    ):
        st.session_state.grades[trace_id] = {
            'grade': 'FAIL',
            'comment': st.session_state.grades.get(trace_id, {}).get('comment', '')
        }
        autosave_grades()
        st.rerun()

st.markdown("---")

# Show current grade
current_grade = st.session_state.grades.get(trace_id, {})
if current_grade:
    col1, col2 = st.columns([1, 3])
    with col1:
        grade_display = "✅ PASS" if current_grade['grade'] == 'PASS' else "❌ FAIL"
        st.success(grade_display) if current_grade['grade'] == 'PASS' else st.error(grade_display)
    with col2:
        st.markdown(f"*Graded on: {current_grade.get('graded_at', 'N/A')}*")

st.markdown("---")

# Comments section
st.subheader("Comments (Optional)")
current_comment = st.session_state.grades.get(trace_id, {}).get('comment', '')

comment = st.text_area(
    "Add notes about this trace:",
    value=current_comment,
    placeholder="e.g., 'Agent was very rude', 'Great discount mention', 'Could have been more helpful'",
    height=100,
    key=f"comment_{trace_id}"
)

if st.button("💬 Save Comment", use_container_width=True):
    if trace_id not in st.session_state.grades:
        st.session_state.grades[trace_id] = {'grade': 'UNGRADED'}
    st.session_state.grades[trace_id]['comment'] = comment
    autosave_grades()
    st.success("✅ Comment saved!")

st.divider()

# Summary table at bottom
st.subheader("Grading Summary")

summary_data = []
for trace in st.session_state.traces:
    tid = trace['id']
    grade_info = st.session_state.grades.get(tid, {})
    summary_data.append({
        'Trace ID': tid,
        'Scenario': trace['scenario'],
        'Grade': grade_info.get('grade', '⭕ Ungraded'),
        'Comment': grade_info.get('comment', '')[:50] + ('...' if len(grade_info.get('comment', '')) > 50 else '')
    })

# Use Polars for efficient data processing
summary_df_pl = pl.DataFrame(summary_data)
summary_df = summary_df_pl.to_pandas()

st.dataframe(
    summary_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Grade": st.column_config.TextColumn(width="small"),
    }
)