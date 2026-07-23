# student-dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(page_title="Student Performance Dashboard", layout="wide")

# --- Custom CSS ---
st.markdown(
    """
    <style>
    .header {background-color:#0b5cff; padding:12px; border-radius:8px;}
    .big-title {color: white; font-size:30px; font-weight:700; margin:0;}
    .subtitle {color: #e6f0ff; margin-top:4px;}
    .card {background:#f8f9fb; padding:12px; border-radius:8px; margin-bottom:12px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and description
st.markdown('<div class="header"><p class="big-title">Student Performance Analytics Dashboard</p><p class="subtitle">Interactive analysis of marks and attendance</p></div>', unsafe_allow_html=True)
st.write("Use the sidebar to filter data and download filtered results.")

# Load dataset
@st.cache_data
def load_data(path="student_performance.csv"):
    df = pd.read_csv(path)
    # Basic cleaning & ensure numeric types
    df['Marks'] = pd.to_numeric(df['Marks'], errors='coerce')
    df['Attendance'] = pd.to_numeric(df['Attendance'], errors='coerce')
    df['Semester'] = pd.to_numeric(df['Semester'], errors='coerce')
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load dataset: {e}")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
departments = ["All"] + sorted(df['Department'].dropna().unique().tolist())
dept_sel = st.sidebar.selectbox("Department", departments, index=0)
semesters = ["All"] + sorted(df['Semester'].dropna().unique().astype(int).tolist())
sem_sel = st.sidebar.selectbox("Semester", semesters, index=0)

min_att = int(df['Attendance'].min(skipna=True))
max_att = int(df['Attendance'].max(skipna=True))
att_range = st.sidebar.slider("Attendance range (%)", min_att, max_att, (min_att, max_att))

# Apply filters
filtered = df.copy()
if dept_sel != "All":
    filtered = filtered[filtered['Department'] == dept_sel]
if sem_sel != "All":
    filtered = filtered[filtered['Semester'] == int(sem_sel)]
filtered = filtered[(filtered['Attendance'] >= att_range[0]) & (filtered['Attendance'] <= att_range[1])]

# Display filtered data
st.markdown("<div class='card'><strong>Filtered Data</strong></div>", unsafe_allow_html=True)
st.dataframe(filtered.reset_index(drop=True))

# Summary statistics
st.markdown("<div class='card'><strong>Summary Statistics</strong></div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Records shown", len(filtered))
with col2:
    st.metric("Average Marks", f"{filtered['Marks'].mean():.2f}" if not filtered.empty else "N/A")
with col3:
    st.metric("Average Attendance", f"{filtered['Attendance'].mean():.2f}" if not filtered.empty else "N/A")

st.markdown("#### Descriptive stats (Marks & Attendance)")
st.write(filtered[['Marks', 'Attendance']].describe().transpose())

# Visualizations
st.markdown("<div class='card'><strong>Visualizations</strong></div>", unsafe_allow_html=True)

# Bar chart: average marks by department
st.markdown("**Average Marks by Department**")
avg_by_dept = filtered.groupby('Department', dropna=False)['Marks'].mean().sort_values(ascending=False)
fig1, ax1 = plt.subplots(figsize=(6,3))
sns.barplot(x=avg_by_dept.index, y=avg_by_dept.values, palette="Blues_d", ax=ax1)
ax1.set_ylabel("Average Marks")
ax1.set_xlabel("")
ax1.set_ylim(0, 100)
plt.xticks(rotation=30)
st.pyplot(fig1)

# Pie chart: semester distribution
st.markdown("**Semester Distribution**")
sem_counts = filtered['Semester'].value_counts().sort_index()
fig2, ax2 = plt.subplots(figsize=(5,4))
ax2.pie(sem_counts.values, labels=sem_counts.index.astype(int), autopct="%1.1f%%", startangle=140)
ax2.axis('equal')
st.pyplot(fig2)

# Histogram: marks distribution
st.markdown("**Marks Distribution**")
fig3, ax3 = plt.subplots(figsize=(6,3))
sns.histplot(filtered['Marks'].dropna(), bins=10, kde=True, color='green', ax=ax3)
ax3.set_xlabel("Marks")
st.pyplot(fig3)

# Scatter plot: Attendance vs Marks
st.markdown("**Attendance vs Marks**")
fig4, ax4 = plt.subplots(figsize=(6,4))
sns.scatterplot(data=filtered, x='Attendance', y='Marks', hue='Department', palette='tab10', ax=ax4)
ax4.set_xlim(min_att - 5, max_att + 5)
ax4.set_ylim(0, 100)
st.pyplot(fig4)

# Download filtered data as CSV
st.markdown("<div class='card'><strong>Download</strong></div>", unsafe_allow_html=True)
def convert_df_to_csv_bytes(df_in):
    return df_in.to_csv(index=False).encode('utf-8')

csv_bytes = convert_df_to_csv_bytes(filtered)
st.download_button(
    label="Download filtered data as CSV",
    data=csv_bytes,
    file_name="filtered_student_performance.csv",
    mime="text/csv",
)

# Small example: show top 5 students by marks
st.markdown("<div class='card'><strong>Top Students</strong></div>", unsafe_allow_html=True)
if not filtered.empty:
    top5 = filtered.sort_values(by='Marks', ascending=False).head(5)
    st.table(top5[['Student_ID', 'Name', 'Department', 'Semester', 'Marks', 'Attendance']].reset_index(drop=True))
else:
    st.write("No data after filtering.")

# Footer / note
st.markdown("<hr>")
st.caption("This is a simple Streamlit dashboard for student performance analytics. Customize as needed.")
