# Run Python scripts

Logic that is too complex to embed in _pyproject.toml_ can be written in Python scripts in the _bin_ directory.
These can be called from aliases or from the command line with `pw <script-name>`.

The scripts run by default in the main tool context and hence can use all libraries installed in the main tool context.

## Example

Create a file `bin/check-version.py`:

```python
"""Print the current project version from pyproject.toml."""
import tomllib
from pathlib import Path

pyproject = Path("pyproject.toml")
data = tomllib.loads(pyproject.read_text())
version = data["project"]["version"]
print(f"Current version: {version}")
```

You can invoke it directly:

=== "Any OS with `px`"

    ```bash
    px check-version
    ```

=== "Linux/Mac"

    ```bash
    ./pw check-version
    ```

Or reference it from an alias:

```toml
[tool.pyprojectx.aliases]
release = ["check-version", "uv build"]
```

## Running scripts in a different tool context

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

## Changing the scripts directory

The default script directory (_bin_) can be changed by specifying the `scripts_dir` in _pyproject.toml_:

```toml
[tool.pyprojectx]
scripts_dir = "scripts"
```
