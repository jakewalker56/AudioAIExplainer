<link rel="stylesheet" href="https://pyscript.net/latest/pyscript.css" />
<script defer src="https://pyscript.net/latest/pyscript.js"></script>

<py-config>
  packages = ["altair", "pandas"]  # Pyodide will load these in-browser
</py-config>

<py-script>
import pandas as pd, altair as alt
df = pd.DataFrame({"x": range(10), "y": [v*v for v in range(10)]})
chart = alt.Chart(df).mark_line().encode(x="x", y="y")
display(chart)   # renders inline and interactive
</py-script>