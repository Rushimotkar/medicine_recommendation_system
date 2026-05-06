import folium

def build_doctor_map(doctors: list):
    """
    Build map using Folium
    """

    if not doctors:
        return "<h3>No doctors found</h3>"

    avg_lat = sum(d["latitude"] for d in doctors) / len(doctors)
    avg_lon = sum(d["longitude"] for d in doctors) / len(doctors)

    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=13)

    for doc in doctors:
        maps_url = f"https://www.google.com/maps?q={doc['latitude']},{doc['longitude']}"

        popup_html = f"""
        <b>{doc['name']}</b><br>
        {doc['full_address']}<br>
        <a href="{maps_url}" target="_blank">Open in Maps</a>
        """

        folium.Marker(
            [doc["latitude"], doc["longitude"]],
            popup=popup_html,
            tooltip=doc["name"]
        ).add_to(m)

    return m.get_root().render()