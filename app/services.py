import folium

def get_earthquake_view(latitude: int, longitude: int):
    m = folium.Map(
        location=[latitude, longitude],
        zoom_start=6
    )

    folium.Marker(
        location=[latitude, longitude],
        popup="Epicenter",
        tooltip=f"{latitude}, {longitude}",
        icon=folium.Icon(color="orange")
    ).add_to(m)

    m.get_root().width = "800px"
    m.get_root().height = "600px"
    iframe = m.get_root()._repr_html_()

    return iframe