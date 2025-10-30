import folium
from .api.caching import Cache

def generate_earthquake_view(latitude: int, longitude: int):
    # using folium library to generate and display a map in html

    # initialize a Map object
    # the arguments are the coordinates of the designated location and starting zoom of the map
    m = folium.Map(
        location=[latitude, longitude],
        zoom_start=7
    )

    """
    initialize the map's marker Object on the same location
    use details such as:
        1. popup which is the detail shown when pressing the icon
        2. tooltip - detail shown when hovering the icon
        3. icon - Icon Object with a specified design
    """
    folium.Marker(
        location=[latitude, longitude],
        popup="Epicenter",
        tooltip=f"{latitude}, {longitude}",
        icon=folium.Icon(color="orange") # i use orange for the marker's color
    ).add_to(m) # connect the marker to the map object

    # set the height and width of the map
    m.get_root().width = "800px"
    m.get_root().height = "600px"

    # convert the map object into html text
    iframe = m.get_root()._repr_html_()

    # return the map's html text
    return iframe


# function for caching the earthquake's map and marker
def fetch_earthquake_view(latitude: int, longitude: int):
    # store using key of the latitude and longitude
    # reason: if two earthquakes have the same coordinates, the program can recycle the same map
    cache = Cache(f"view-{latitude},{longitude}")
    data = cache.get()

    # if there is cached data, return it
    if data is not None:
        return data
    # if none, generate the data, store it in cache, and return the data
    else:
        data = generate_earthquake_view(latitude, longitude)
        cache.set(data)
        return data