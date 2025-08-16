<h1>PyScript smoke test</h1>

<div id="viz">
  <img src="assets/cars_scatter.png" alt="Loading interactive chart…" />
</div>
<script type="py" src="main.py" config="pyscript.toml" target="#viz"></script>

<!-- Quick inline sanity check -->
<script type="py">
from pyscript import display
display("hello from Python")
</script>
