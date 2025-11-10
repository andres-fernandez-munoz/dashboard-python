import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import plotly.colors as pc


data = {
    "Name": ["Location 1", "Location 2", "Location 3", "Location 4", "Location 5"],
    "Latitude": [40.0, 40.0, 40.1, 40.1, 40.3],
    "Longitude": [-3.5, -3.55, -3.6, -3.5, -4.2],
    "Moisture": [40, 30, 20, 45, 25],
    "Temperature": [23, 21, 25, 24, 22],
    "Group": ["Farmer A", "Farmer A", "Farmer B", "Farmer B", "Farmer C"]
}
df = pd.DataFrame(data)

app = dash.Dash(__name__)
app.title = "IoT Panel"



def make_figure(selected_group=None):
    if selected_group:
        dff = df[df["Group"] == selected_group]
    else:
        dff = df

    fig = go.Figure()
    
    colors = pc.qualitative.Plotly



    for i, (group, group_df) in enumerate(dff.groupby("Group")):
        color = colors[i % len(colors)]
        
        alert_df = group_df[group_df["Moisture"] < 30]
        normal_df = group_df[group_df["Moisture"] >= 30]

        if len(normal_df) > 0:
            fig.add_trace(go.Scattermapbox(
                lat=normal_df["Latitude"],
                lon=normal_df["Longitude"],
                mode="markers+text",
                text=normal_df["Name"],
                textposition="top center",
                name=group,
                customdata=normal_df[["Temperature","Moisture"]].values,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Group: "+group+"<br>"
                    "Temperature: %{customdata[0]} °C<br>"
                    "Humidity: %{customdata[1]}%"
                ),
                marker=dict(
                    size=15,
                    color=color
                )
            ))

        if len(alert_df) > 0:
            fig.add_trace(go.Scattermapbox(
                lat=alert_df["Latitude"],
                lon=alert_df["Longitude"],
                mode="markers+text",
                text=alert_df["Name"],
                textposition="top center",
                name=group,
                customdata=list(zip(alert_df["Temperature"], alert_df["Moisture"])),
                hovertemplate=(
                    "⚠️ LOW HUMIDITY!!<br>"
                    "<b>%{text}</b><br>"
                    "Group: "+group+"<br>"
                    "Temperature: %{customdata[0]} °C<br>"
                    "Humidity: %{customdata[1]}%"
                ),
                marker=dict(
                    size=18,
                    color="red"
                )
            ))


    if len(dff) > 0:
        center_lat = dff["Latitude"].mean()
        center_lon = dff["Longitude"].mean()
    else:
        center_lat, center_lon = 0, 0

    if selected_group != None:
        zoom_level = 12
    else:
        zoom_level = 8


    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=zoom_level,
        ),
        margin={"r": 10, "t": 10, "l": 10, "b": 10},
        height=600,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )

    return fig



app.layout = html.Div(
    style={
        "fontFamily": "Segoe UI, Roboto, sans-serif",
        "backgroundColor": "#f5f7fa",
        "padding": "5px",
    },
    children=[
        html.Div(
            [
                html.H1(
                    "IoT Device Panel",
                    style={
                        "textAlign": "center",
                        "color": "#1a1a1a",
                        "marginBottom": "5px",
                        "fontWeight": "600",
                    },
                ),
                html.P(
                    "Monitor soil moisture and temperature",
                    style={"textAlign": "center", "color": "#555", "marginBottom": "40px"},
                ),
            ]
        ),

        html.Div(
            style={
                "width": "90%",
                "maxWidth": "2000px",
                "margin": "0 auto",
                "background": "white",
                "borderRadius": "12px",
                "padding": "25px 30px",
                "boxShadow": "0 4px 10px rgba(0,0,0,0.1)",
            },
            children=[
                html.Div(
                    [
                        html.Label(
                            "Select Group:",
                            style={"fontWeight": "bold", "color": "#333"},
                        ),
                        dcc.Dropdown(
                            id="group-dropdown",
                            options=[
                                {"label": "Show All", "value": "ALL"}
                            ] + [{"label": g, "value": g} for g in sorted(set(df["Group"]))],
                            placeholder="Choose a group...",
                            clearable=True,
                            style={"width": "100%", "marginTop": "8px", "marginBottom": "20px"},
                        ),
                    ]
                ),
                html.Div(
                    [
                        dcc.Graph(
                            id="map-graph",
                            style={
                                "width": "100%",
                                "minHeight": "65vh",
                                "borderRadius": "10px",
                                "overflow": "hidden",
                                "flexGrow": "1",
                            },
                            config={"responsive": True},
                            figure=make_figure(),
                        )
                    ]
                ),
            ],
        ),

        html.Footer(
            "ISS - Grupo 1",
            style={
                "textAlign": "center",
                "marginTop": "40px",
                "color": "#888",
                "fontSize": "0.9em",
            },
        ),
    ],
)



@app.callback(
    Output("map-graph", "figure"),
    Input("group-dropdown", "value")
)
def update_map(selected_group):
    if selected_group == "ALL" or selected_group is None:
        return make_figure()
    return make_figure(selected_group)




if __name__ == "__main__":
    app.run(debug=True)

