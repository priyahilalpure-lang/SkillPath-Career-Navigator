
import streamlit as st
import plotly.graph_objects as go
import networkx as nx
import csv
import io
import math

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="SkillPath Career Navigator",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 SkillPath Career Navigator")
st.caption("Explore your skills. Discover your career path.")

# ---------------- CAREER DATA ----------------
CAREERS = {
    "Data Scientist": {
        "Python": 5,
        "Statistics": 5,
        "SQL": 4,
        "Machine Learning": 5,
        "Data Visualization": 4
    },
    "AI Engineer": {
        "Python": 5,
        "Statistics": 4,
        "SQL": 3,
        "Machine Learning": 5,
        "Deep Learning": 5
    },
    "Data Analyst": {
        "Python": 3,
        "Statistics": 4,
        "SQL": 5,
        "Data Visualization": 5,
        "Excel": 4
    },
    "Full Stack Developer": {
        "HTML/CSS": 5,
        "JavaScript": 5,
        "Python": 3,
        "SQL": 4,
        "Git": 4
    }
}

LEARNING_RESOURCES = {
    "Python": "Practise Python basics, functions, and projects.",
    "Statistics": "Study probability, averages, distributions, and hypothesis testing.",
    "SQL": "Practise SELECT, JOIN, GROUP BY, and subqueries.",
    "Machine Learning": "Learn regression, classification, and model evaluation.",
    "Data Visualization": "Build charts and dashboards with Plotly.",
    "Deep Learning": "Study neural networks and deep-learning fundamentals.",
    "Excel": "Practise formulas, pivot tables, and charts.",
    "HTML/CSS": "Build responsive web pages.",
    "JavaScript": "Practise DOM manipulation and interactive web apps.",
    "Git": "Learn commits, branches, and GitHub workflows."
}

# ---------------- SIDEBAR ----------------
st.sidebar.header("Your Career Profile")
name = st.sidebar.text_input("Your name", "Learner")

career = st.sidebar.selectbox(
    "Choose your target career",
    list(CAREERS.keys())
)

st.sidebar.info(
    "Select your current skill levels on the dashboard. "
    "SkillPath will calculate your readiness."
)

targets = CAREERS[career]

# ---------------- SKILL INPUTS ----------------
st.header("🎯 Your Skill Assessment")
st.write(f"Rate your current skills for **{career}** from 0 (beginner) to 5 (advanced).")

current = {}

skill_names = list(targets.keys())
columns = st.columns(2)

for i, skill in enumerate(skill_names):
    with columns[i % 2]:
        current[skill] = st.slider(
            f"{skill}",
            min_value=0,
            max_value=5,
            value=0,
            key=f"{career}_{skill}"
        )

# ---------------- CALCULATIONS ----------------
total_target = sum(targets.values())
total_current = sum(current.values())

readiness = round((total_current / total_target) * 100) if total_target else 0

matched = sum(
    1 for skill in targets
    if current[skill] >= targets[skill]
)

to_improve = len(targets) - matched

# ---------------- METRICS ----------------
st.divider()
st.header("📊 Your Skill Gap Analysis")

m1, m2, m3 = st.columns(3)
m1.metric("Career readiness", f"{readiness}%")
m2.metric("Skills matched", f"{matched}/{len(targets)}")
m3.metric("Skills to improve", to_improve)

st.progress(readiness / 100)

# ---------------- BAR CHART ----------------
st.subheader("Current Skills vs Career Requirements")

fig = go.Figure()

fig.add_trace(go.Bar(
    name="Your current level",
    x=skill_names,
    y=[current[s] for s in skill_names],
    marker_color="#0875D1"
))

fig.add_trace(go.Bar(
    name="Target level",
    x=skill_names,
    y=[targets[s] for s in skill_names],
    marker_color="#83C7F8"
))

fig.update_layout(
    barmode="group",
    yaxis=dict(title="Skill level (0–5)", range=[0, 5.5], dtick=1),
    xaxis_title="Skills",
    height=430,
    legend_title="Skill level",
    margin=dict(t=30, b=50)
)

st.plotly_chart(fig, use_container_width=True)

# ---------------- SKILL GAP TABLE ----------------
st.subheader("🔍 Your Skill Gaps")

for skill in skill_names:
    gap = max(0, targets[skill] - current[skill])
    if gap == 0:
        st.success(f"**{skill}** — Target achieved! 🎉")
    else:
        st.warning(
            f"**{skill}** — Current: {current[skill]}/5 | "
            f"Target: {targets[skill]}/5 | Gap: {gap}"
        )

# ---------------- LEARNING ROADMAP ----------------
st.divider()
st.header("🗺️ Your Personal Learning Roadmap")

gaps = sorted(
    [
        (skill, targets[skill] - current[skill])
        for skill in skill_names
        if current[skill] < targets[skill]
    ],
    key=lambda item: item[1],
    reverse=True
)

if gaps:
    st.write("Focus on these skills first, starting with the largest gap.")

    for number, (skill, gap) in enumerate(gaps, start=1):
        with st.expander(f"Step {number}: Improve {skill} (gap: {gap})"):
            st.write(LEARNING_RESOURCES.get(
                skill, f"Find a beginner-to-intermediate course in {skill}."
            ))
            st.write(f"Suggested target: reach level {targets[skill]}/5.")
else:
    st.success("Excellent! You have met all the skill targets for this career.")

# ---------------- NETWORK GRAPH ----------------
st.divider()
st.header("🕸️ Career Skill Network")
st.caption("Explore how your target career connects to its required skills.")

graph = nx.Graph()
career_node = career

graph.add_node(career_node, kind="career")

for skill in skill_names:
    graph.add_node(skill, kind="skill")
    graph.add_edge(career_node, skill)

# Add connections between skills in the displayed learning sequence
for i in range(len(skill_names) - 1):
    graph.add_edge(skill_names[i], skill_names[i + 1])

# Manually calculate positions; no NumPy-based layout is used.
positions = {career_node: (0, 0)}
radius = 2.2

for i, skill in enumerate(skill_names):
    angle = (2 * math.pi * i / len(skill_names)) - math.pi / 2
    positions[skill] = (
        radius * math.cos(angle),
        radius * math.sin(angle)
    )

edge_x = []
edge_y = []

for start, end in graph.edges():
    x0, y0 = positions[start]
    x1, y1 = positions[end]
    edge_x.extend([x0, x1, None])
    edge_y.extend([y0, y1, None])

network_fig = go.Figure()

network_fig.add_trace(go.Scatter(
    x=edge_x,
    y=edge_y,
    mode="lines",
    line=dict(width=1.5, color="#AAB7C4"),
    hoverinfo="none"
))

node_x = [positions[node][0] for node in graph.nodes()]
node_y = [positions[node][1] for node in graph.nodes()]
node_labels = list(graph.nodes())

node_colors = [
    "#0875D1" if node == career_node
    else "#16A085" if current[node] >= targets[node]
    else "#F39C12"
    for node in node_labels
]

network_fig.add_trace(go.Scatter(
    x=node_x,
    y=node_y,
    mode="markers+text",
    text=node_labels,
    textposition="bottom center",
    marker=dict(size=24, color=node_colors, line=dict(width=1, color="white")),
    hovertext=[
        f"{node}: {current[node]}/5 current, {targets[node]}/5 target"
        if node != career_node else node
        for node in node_labels
    ],
    hoverinfo="text"
))

network_fig.update_layout(
    showlegend=False,
    height=500,
    xaxis=dict(visible=False),
    yaxis=dict(visible=False),
    margin=dict(l=20, r=20, t=20, b=40)
)

st.plotly_chart(network_fig, use_container_width=True)

# ---------------- DOWNLOAD REPORT ----------------
st.divider()
st.header("📥 Download Your Skill Report")

csv_buffer = io.StringIO()
writer = csv.writer(csv_buffer)

writer.writerow([
    "Name", "Career", "Skill",
    "Current Level", "Target Level", "Gap"
])

for skill in skill_names:
    writer.writerow([
        name,
        career,
        skill,
        current[skill],
        targets[skill],
        max(0, targets[skill] - current[skill])
    ])

st.download_button(
    label="⬇️ Download Skill Report (CSV)",
    data=csv_buffer.getvalue(),
    file_name="skillpath_report.csv",
    mime="text/csv"
)

st.divider()
st.caption("SkillPath Career Navigator | Built with Python, Streamlit, Plotly and NetworkX")
