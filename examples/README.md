# Examples

- **`quickstart.ipynb`** — walks through every `WattnetClient` method against the real, live wattnet API, with the actual DataFrame outputs saved in the notebook. Read it directly on GitHub, no credentials needed.

## Regenerating `quickstart.ipynb`

The notebook's cells are generated from `_build_notebook.py` (not part of the published package) rather than edited by hand, so the source stays readable and diffable. To add or change a cell, edit `_build_notebook.py` and rebuild:

```bash
poetry install --with examples
poetry run python examples/_build_notebook.py
```

Then re-execute it with a valid token to refresh the real outputs:

```bash
WATTNET_TOKEN=<your-token> poetry run jupyter nbconvert --to notebook --execute --inplace examples/quickstart.ipynb
```

Never hardcode a token/password into `_build_notebook.py` or commit a notebook containing one — always read credentials from an environment variable at execution time.
