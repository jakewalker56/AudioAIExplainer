<!-- Configure PyScript: tell it which packages to load -->
<py-config>
{
  "packages": ["pandas", "altair", "vega_datasets"]
}
</py-config>

<!-- Run inline Python in the page -->
<py-script>
from pyscript import display
import pandas as pd, altair as alt
from vega_datasets import data

df = data.cars()
chart = alt.Chart(df).mark_point().encode(
    x="Horsepower",
    y="Miles_per_Gallon",
    color="Origin",
    tooltip=["Name","Horsepower","Miles_per_Gallon"]
)

display(chart)  # renders the chart inline
</py-script>
