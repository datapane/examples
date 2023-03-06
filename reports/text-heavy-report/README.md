
# Datapane template: Text-heavy report

This is a Datapane template.

It can be used as a starting point for creating a text-heavy Datapane report that starts off as a Jupyter Notebook.

## Download the template

The template can be downloaded directly in archive file format.

## Preview

<img height="471" alt="text-heavy-report" src="https://user-images.githubusercontent.com/15690380/185621854-1ab0e1df-ef34-4956-ad92-90d905cbc09c.png">

## Dependencies

This template may require additional third-party packages. A full list of required packages can be found in `pyproject.toml`

## Moving from a notebook to a Datapane report

The process for moving from your article (in `ipynb` format) to a Datapane report is:

1. Place your notebook in the `assets/` directory, e.g. you will find one for this template named `article.ipynb`.
2. Within your notebook, add placeholders, e.g. `{{plot_my_visualization}}` in markdown cells where Datapane blocks should appear.
3. Run the following commands within the `assets/` directory to extract the markdown from your notebook:
    ```bash
    jupyter nbconvert --clear-output article.ipynb 
    jupyter nbconvert --to markdown article.ipynb
    ```
4. Copy your notebook cells into `template.ipynb`. You can delete all the markdown cells, but it's helpful to keep the ones containing the placeholders.
5. Wherever there's a placeholder, construct your Datapane block.
6. When constructing your Datapane report, load the `article.md` file into a `dp.Text` block, and pass in your Datapane blocks using the `.format()` method, where the keyword name matches the placeholder name. E.g.:
    ```python
    report = dp.Report(
        banner_block,
        dp.Text(file="assets/article.md").format(
            plot_my_visualization=plot_my_visualization
        )
    )
    ```
 
## Contributions

This template is open-source and accepts contributions!

## How to create a new Datapane template

Visit [datapane/dp-template](https://github.com/datapane/dp-template-classifier-dashboard) for instructions on how to create a new Datapane template.
