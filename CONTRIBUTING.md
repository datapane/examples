# Contributing

Overview of how to add examples to this repo

## Structure of a Report

- **must** be a directory under the `./reports` directory
- **must** have either a `report.py` or `report.ipynb` file
  - **not both**
- **must** include calling `dp.upload_report`
  - **may** use `dp.save_report`, as per ["Supporting upload and save"](#supporting-upload-and-save)
- **must not** include its own `requirements.txt`
  - we currently run all reports against the shared dependencies only.

### Deploying

We deploy by executing the report file as a python script locally.

If using a Notebook (`.ipynb`), avoid use of Magics (`%` or `!` statements)

#### Supporting upload and save

When deploying, an environment variable `DATAPANE_DEPLOY=1` is set.
This can be used to select the action a report takes:

```py
import os
if os.getenv('DATAPANE_DEPLOY') == "1":
    dp.upload_report(v, "Text Heavy Report", publicly_visible=True)
else:
    dp.save_report(v, path="report.html", open=True)
```
