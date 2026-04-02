import geopandas as gpd
import polars as pl
import folium
import webbrowser


#pi-dataset
#Sorted by Column 1, State
jan_Medicaid = pl.read_csv("Data/pi-dataset-january-2026release.csv")


#TODO: Group each year of each state, formatted YYYY:MM, into a new (separate) dataframe.
# change reporting period into string

jan_Medicaid = jan_Medicaid.with_columns(
    (pl.col("Reporting Period") // 100).alias("Year"),
    (pl.col("Reporting Period") % 100).alias("Month")
)
#Sort "Final Report" for only Y
jan_Medicaid_filtered = jan_Medicaid.filter(pl.col("Final Report") == "Y")






#TODO: Change maps to map by year. (edit first 3 lines of map function, and map_df's merge.
# Can change map function to loop through all possible years)

def make_map(new_map, column, name, color, year):
    # Filter to the specific year
    year_filtered = jan_Medicaid_filtered.filter(pl.col("Year") == year)

    jan_total = (year_filtered.group_by(["State Name", "Year"]).agg(
        pl.col(column).sum()))
    jan_total_pd = jan_total.to_pandas()

    jan_total_pd = jan_total_pd.sort_values(["State Name", "Year"]).reset_index(drop=True)

    states = gpd.read_file("https://naturalearth.s3.amazonaws.com/50m_cultural/ne_50m_admin_1_states_provinces.zip")
    states = states[states["admin"] == "United States of America"]

    map_df = states.merge(
        jan_total_pd[["State Name", "Year", column]],
        left_on="name",
        right_on="State Name",
        how="left"
    )

    map_df = map_df.to_crs(epsg=4326)

    map_df.explore(
        m=new_map,
        column=column,
        scheme="naturalbreaks",
        k=5,
        cmap=color,
        tooltip=["name", "Year", column],  # Year now shows on hover
        legend=True,
        legend_kwds={
            "colorbar": False,
            "label": f"{column} ({year})"},  # Year shown in legend label
        style_kwds=dict(color="black"),
        name=f"{name} ({year})",  # Year shown in layer control
    )


# Create base map
m = folium.Map(location=[37, -96], zoom_start=4, tiles="CartoDB positron")

#Add Map Layers here
make_map(m, "Total Applications for Financial Assistance Submitted at State Level", "2024 TOTAL Medicaid + Chip Applications", "Reds", year=2024)
make_map(m, "Total Applications for Financial Assistance Submitted at State Level", "2025 TOTAL Medicaid + Chip Applications", "Reds", year=2025)

#make_map(m, "New Applications Submitted to Medicaid and CHIP Agencies", "NEW Medicaid + Chip Applications", "Reds")
#make_map(m, "Applications for Financial Assistance Submitted to the State Based Marketplace", "Applications to State Marketplace", "Reds")
#make_map(m, "Individuals Determined Eligible for Medicaid at Application", "Eligible Individuals", "Blues")

#make_map(m, "Total Medicaid and CHIP Determinations", "Total Medicaid and CHIP Determinations", "Blues")
#make_map(m, "Medicaid and CHIP Child Enrollment", "Medicaid and CHIP Child Enrollment", "Blues")
#make_map(m, "Total Medicaid and CHIP Enrollment", "Total Medicaid and CHIP Enrollment", "Blues")
#make_map(m, "Total Medicaid Enrollment", "Total Medicaid Enrollment", "Blues")
#make_map(m, "Total CHIP Enrollment", "Total CHIP Enrollment", "Blues")

# Add layer control ONCE
folium.LayerControl(collapsed=False).add_to(m)

#save and open map in webbrowser
m.save("medicaid_january_map.html")  # save to HTML
webbrowser.open("medicaid_january_map.html", new=2, autoraise=True)  # open in default browser


