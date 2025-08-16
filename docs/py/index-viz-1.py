from pyscript import display
from vega_datasets import data
import altair as alt

df = data.cars()
chart = alt.Chart(df).mark_point().encode(
    x="Horsepower", y="Miles_per_Gallon",
    color="Origin",
    tooltip=["Name","Horsepower","Miles_per_Gallon"]
)
display(chart)