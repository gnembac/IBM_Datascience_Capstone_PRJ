# ============================================================
# SpaceX Launch Records Dashboard - Plotly Dash
# IBM Data Science Capstone | TASK 1-4 Complete
# ============================================================
# Setup:
#   pip install pandas dash plotly
#   wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/
#        IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv
# Run:
#   python spacex_dash_app.py  → http://localhost:8050
# ============================================================

import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# ── Data ────────────────────────────────────────────────────
spacex_df = pd.read_csv("spacex_launch_dash.csv")
min_payload = spacex_df["Payload Mass (kg)"].min()
max_payload = spacex_df["Payload Mass (kg)"].max()

# Dynamically extract unique launch sites for dropdown
launch_sites = sorted(spacex_df["Launch Site"].unique())

# ── App Instance ─────────────────────────────────────────────
app = dash.Dash(__name__)

# ── Layout ───────────────────────────────────────────────────
app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "maxWidth": "1200px", "margin": "0 auto"},
    children=[
        # Header
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "fontSize": 40}
        ),
        html.Hr(),

        # TASK 1: Launch Site Dropdown
        html.Label("Select Launch Site:", style={"fontWeight": "bold"}),
        dcc.Dropdown(
            id="site-dropdown",
            options=[{"label": "All Sites", "value": "ALL"}]
                  + [{"label": site, "value": site} for site in launch_sites],
            value="ALL",
            placeholder="Select a Launch Site here",
            searchable=True,
            clearable=False,
            style={"marginBottom": "20px"}
        ),

        # TASK 2: Pie Chart
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),

        # TASK 3: Payload Range Slider
        html.Label("Payload Range (kg):", style={"fontWeight": "bold"}),
        dcc.RangeSlider(
            id="payload-slider",
            min=0,
            max=10000,
            step=1000,
            value=[min_payload, max_payload],
            marks={i: f"{i:,}" for i in range(0, 10001, 1000)},
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        html.Br(),

        # TASK 4: Scatter Chart
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


# ── TASK 2: Pie Chart Callback ────────────────────────────────
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value")
)
def get_pie_chart(entered_site):
    label_map = {0: "Failed", 1: "Success"}

    if entered_site == "ALL":
        # Sum of successful launches per site
        fig = px.pie(
            spacex_df,
            values="class",
            names="Launch Site",
            title="Total Successful Launches by Site",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
    else:
        site_df = (
            spacex_df[spacex_df["Launch Site"] == entered_site]
            .groupby("class")
            .size()
            .reset_index(name="count")
        )
        site_df["Outcome"] = site_df["class"].map(label_map)
        fig = px.pie(
            site_df,
            values="count",
            names="Outcome",
            title=f"Success vs Failed Launches — {entered_site}",
            color="Outcome",
            color_discrete_map={"Success": "#00CC96", "Failed": "#EF553B"}
        )

    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(margin=dict(t=50, l=20, r=20, b=20))
    return fig


# ── TASK 4: Scatter Chart Callback ───────────────────────────
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value")
    ]
)
def get_scatter_chart(entered_site, payload_range):
    # Apply payload range filter first
    mask = spacex_df["Payload Mass (kg)"].between(payload_range[0], payload_range[1])
    payload_df = spacex_df[mask]

    # Optionally filter by site
    if entered_site != "ALL":
        payload_df = payload_df[payload_df["Launch Site"] == entered_site]
        title = f"Payload vs. Launch Outcome — {entered_site}"
    else:
        title = "Payload vs. Launch Outcome — All Sites"

    fig = px.scatter(
        payload_df,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        hover_data=["Launch Site", "Payload Mass (kg)", "class"],
        title=title,
        labels={"class": "Launch Outcome (0=Fail, 1=Success)"},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig.update_layout(
        yaxis=dict(tickvals=[0, 1], ticktext=["Failed", "Success"]),
        margin=dict(t=50, l=20, r=20, b=20)
    )
    return fig


# ── Entry Point ───────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)