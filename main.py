import geopandas as gpd
import polars as pl
import folium
import webbrowser


#pi-dataset
#Sorted by Column 1, State
jan_Medicaid = pl.read_csv("Data/pi-dataset-january-2026release.csv")

#Sort "Final Report" for only Y
jan_Medicaid_filtered = jan_Medicaid.filter(pl.col("Final Report") == "Y")

#Total Applications for Financial Assistance Submitted at State Level
#^updated every day, total them for each state for January (dict)
jan_total_apps = (jan_Medicaid_filtered.group_by("State Name").agg(pl.col("Total Applications for Financial Assistance Submitted at State Level").sum()))

#Get map of state x Total Apps for January

# Convert Polars → pandas for GeoPandas
jan_total_apps_pd = jan_total_apps.to_pandas()

# Rename column in jan_total_apps_pd, makes it easier to reference
jan_total_apps_pd = jan_total_apps_pd.rename(
    columns={"Total Applications for Financial Assistance Submitted at State Level": "Total_Apps"}
)

# --- Load US states ---
states = gpd.read_file("https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_1_states_provinces.zip")
states = states[states["admin"] == "United States of America"]

# Merge the formatted column too
map_df = states.merge(
    jan_total_apps_pd[["State Name", "Total_Apps"]],
    left_on="name",
    right_on="State Name",
    how="left"
)

map_df = map_df.to_crs(epsg=4326) #required for tiles

#Interactive map
m = map_df.explore(
    column= "Total_Apps",
    scheme="naturalbreaks",
    k=10,  # use 10 bins for legend
    cmap= "Blues",
    tooltip=["name", "Total_Apps"], #shows data on hover
    legend = True,
    legend_kwds={
        "colorbar": False, #blocks, makes legend more readable for large datasets
        "label": "Total Applications"},
    style_kwds=dict(color="black"),
    tiles="CartoDB positron",
    name="Medicaid + Chip Applications",
)

#Useful if you add more layers
folium.LayerControl().add_to(m)

#save and open map in webbrowser
m.save("medicaid_january_map.html")  # save to HTML
webbrowser.open("medicaid_january_map.html")  # open in default browser


