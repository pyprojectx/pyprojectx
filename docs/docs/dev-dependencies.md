# A Note about Dev-Dependencies

[Poetry](https://python-poetry.org/) and [PDM](https://pdm.fming.dev/) let you define dev-dependencies similar to
npm's _devDependencies_. There is however a major difference between Python and npm dependencies:
npm can install multiple versions of the same package, meaning that devDependencies do not interfere
with main dependencies. Python, on the other hand, can only install one version of a package.
This means that all dependencies will have to meet both the main dependency constraints and all the dev-dependency
constraints.

If you install all your development tools as dev-dependencies, some packages that your production code depends on,
will likely be downgraded to older versions. Or worse: your project fails to install because of dependency conflicts.

!!! tip "Tip: Only install test packages as dev-dependencies"
    _pytest_ and friends need to be installed together with your code, so you will need to add them
    as Poetry or PDM dev-dependencies. Other tools and utilities can be managed by Pyprojectx in order to get
    reproducible builds.
