# Run Python scripts

Logic that is too complex to embed in _pyproject.toml_ can be written in Python scripts in the _bin_ directory.
These can be called from aliases or from the command line with `pw <script-name>`.

The scripts run by default in the main tool context and hence can use all libraries installed in the main tool context.

To run a script in a different tool context, you need to define an alias:

```toml
[tool.pyprojectx.aliases]
# run the generate-data script in the 'jupyter' tool context
generate-data = { cmd = 'generate-data', ctx = 'jupyter' }
```

The script directory can be changed with the `scripts_dir` option in _pyproject.toml_:

```toml
[tool.pyprojectx]
scripts_dir = "scripts"
```
