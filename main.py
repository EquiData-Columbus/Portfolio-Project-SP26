import geopandas as gpd
import polars as pl
import folium
import webbrowser


#pi-dataset
#Sorted by Column 1, State
jan_Medicaid = pl.read_csv("Data/pi-dataset-january-2026release.csv")

#Sort "Final Report" for only Y
jan_Medicaid_filtered = jan_Medicaid.filter(pl.col("Final Report") == "Y")

#TODO: Group each year of each state, formatted YYYY:MM, into a new (separate) dataframe.

#TODO: Change maps to map by year. (edit first 3 lines of map function, and map_df's merge.
# Can change map function to loop through all possible years)

def make_map(new_map, column, name, color):
    jan_total = (jan_Medicaid_filtered.group_by("State Name").agg(
        pl.col(column).sum()))
    jan_total_pd = jan_total.to_pandas()

    # --- Load US states ---
    states = gpd.read_file("https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_1_states_provinces.zip")
    states = states[states["admin"] == "United States of America"]

    # Merge the formatted column too
    map_df = states.merge(
        jan_total_pd[["State Name", column]],
        left_on="name",
        right_on="State Name",
        how="left"
    )

    map_df = map_df.to_crs(epsg=4326)  # required for tiles

    # Interactive map
    map_df.explore(
        m = new_map,
        column=column,
        scheme="naturalbreaks",
        k=5,  # use 5 bins for legend, TODO: should make this scalable based on column max-min
        cmap=color,
        tooltip=["name", column],  # shows data on hover
        legend=True,
        legend_kwds={
            "colorbar": False,  # blocks, makes legend more readable for large datasets
            "label": column},
        style_kwds=dict(color="black"),
        name=name,
    )


# Create base map
m = folium.Map(location=[37, -96], zoom_start=4, tiles="CartoDB positron")

#Add Map Layers here
make_map(m, "Total Applications for Financial Assistance Submitted at State Level", "TOTAL Medicaid + Chip Applications", "Blues")
make_map(m, "New Applications Submitted to Medicaid and CHIP Agencies", "NEW Medicaid + Chip Applications", "Reds")


# Add layer control ONCE
folium.LayerControl(collapsed=False).add_to(m)

#save and open map in webbrowser
m.save("medicaid_january_map.html")  # save to HTML
webbrowser.open("medicaid_january_map.html", new=2, autoraise=True)  # open in default browser


