
<h1>PyScript smoke test</h1>

<div id="viz">
  <img src="assets/cars_scatter.png" alt="Loading interactive chart…" />
</div>
<script type="py" src="py/index-viz-1.py" config="pyscript.toml" target="#viz"></script>

<!-- Quick inline sanity check -->
<script type="py">
from pyscript import display
display("hello from Python")
</script>




This is the github repository for the [Audio AI Explainer](https://jakewalker56.github.io/AudioAIExplainer/) project.

![Chart gif](assets/anim.gif)
<audio controls src="assets/clip.mp3"></audio>

See [How Older Audio Models Work](how-older-audio-models-work.md).