# Run Python scripts

Logic that is too complex to embed in _pyproject.toml_ can be written in Python scripts in the _bin_ directory.
These can be called from aliases or from the command line with `pw <script-name>`.

The scripts run by default in the main tool context and hence can use all libraries installed in the main tool context.


To run a script in a different tool context, you either:

* define an alias:

```toml
[tool.pyprojectx.aliases]
# run the generate-data script in the 'jupyter' tool context
generate-data = { cmd = 'generate-data', ctx = 'jupyter' }
```

* or specify the `scripts_ctx` in _pyproject.toml_ (see [recipes](/recipes#run-scripts-that-use-the-projects-packages)) :

```toml
[tool.pyprojectx]
scripts_ctx = "scripts"
```

The default script directory (_bin_) can be changed by specifying the `scripts_dir` in _pyproject.toml_:

```toml
[tool.pyprojectx]
scripts_dir = "scripts"
```
