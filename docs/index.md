<h1>PyScript smoke test</h1>

<div id="viz"></div>

<!-- Recommended pattern: standard <script> with type="py" -->
<script type="py" src="main.py" config="pyscript.toml" target="#viz"></script>

<!-- Quick inline sanity check -->
<script type="py">
from pyscript import display
display("hello from Python")
</script>
