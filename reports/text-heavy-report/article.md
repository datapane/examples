## Preamble


```python
import numpy as np  # for multi-dimensional containers
import pandas as pd  # for DataFrames
import platypus as plat  # multi-objective optimisation framework
import plotly.graph_objects as go  # for data visualisation
import plotly.express as px  # for express data visualization
```

## Introduction

In this section from the book [Practical Evolutionary Algorithms](https://datacrayon.com/shop/product/practical-evolutionary-algorithms-book/), we're going to take a look at how to use the Platypus framework to apply the non-dominated sorting algorithm to a population of randomly generated solutions. Non-dominated sorting is important during the selection stage of an Evolutionary Algorithm because it allows us to prioritise the selection of solutions based on their dominance relations with respect to the rest of the population. For example, we may wish to only select 25 solutions from a population of 50, with the intention to use these 25 solutions in the variation stage that follows.

## Non-Dominated Sorting with Platypus

Let's define some necessary variables before invoking the Platypus implementation of the non-dominated sorting algorithm. We will use the ZDT1 test function with the number design variables `D=30` throughout this example, and with the population size `N=50`.


```python
problem = plat.ZDT1()
D = 30
N = 50
```

With these variables defined, we will now move onto generating our initial population. We will be using Platypus `Solution` objects for this, which we will initialise with random problem variables, evaluate, and then append to a list named `solutions`.


```python
solutions = []

for i in range(N):
    solution = plat.Solution(problem)
    solution.variables = np.random.rand(D)
    solution.evaluate()
    solutions.append(solution)
```

Let's print out the `variables` and `objectives` for the first solution in this list to see what they look like.


```python
print(f"Design variables: {solutions[0].variables}")
print(f"Objective values: {solutions[0].objectives}")
```

{{text_variables_and_objectives}}

Now that we have a population of solutions stored in the `solutions` variable, we can pass this into the `Platypus.nondominated_sort()` function that will assign each solution a `rank` parameter, starting at 0 for the first non-dominated front and incrementing for every additional front that is detected.


```python
plat.nondominated_sort(solutions)
```

Let's check to see if the first solution in our `solutions` list has one of these newly calculated `rank` parameters.


```python
solutions[0].rank
```

{{text_solution_rank}}

We now have a population of solutions that have been assigned their design variables, their objective values, and their ranks according to the non-dominated sorting algorithm.

## Visualising the Non-Dominated Fronts

It would be useful to visualise these non-dominated fronts, according to their newly assigned ranks, using a scatterplot for further investigation. Before we do this, we will migrate our solution variables from their Platypus data-structure to a DataFrame. We will do this for the simple reason that our visualisation tools, e.g. Plotly, work quite well with the DataFrame format. 

Let's begin by creating a new DataFrame with the columns `f1`, `f2`, and `front_rank`. `f1` and `f2` will be used to store our objective values for each solution, which is sufficient for the two-objective ZDT1 problem, and `rank_front` will be used to store the non-dominated sorting ranks that were calculated earlier.


```python
solutions_df = pd.DataFrame(index=range(N), columns=["f1", "f2", "front_rank"])
solutions_df.head()
```

{{datatable_solutions_initialised}}

We can see that we've also defined an index range that covers the number of solutions in our population, `N=50`. This means we have 50 rows ready, but their values are initialised to `NaN` (Not A Number), which in this case simply indicates missing data.

Let's use a loop to iterate through our `solutions` list of 50 solutions and assign the desired values to the corresponding row in our `solutions_df` DataFrame


```python
for i in range(N):
    solutions_df.loc[i].f1 = solutions[i].objectives[0]
    solutions_df.loc[i].f2 = solutions[i].objectives[1]
    solutions_df.loc[i].front_rank = solutions[i].rank

solutions_df
```

{{datatable_solutions_evaluated}}

We can see our DataFrame now contains the desired values. We're now ready to go with some visualisation, so let's start with a simple scatterplot for the entire population in the objective space.


```python
fig = go.Figure(layout=dict(xaxis=dict(title="f1"), yaxis=dict(title="f2")))

fig.add_scatter(x=solutions_df.f1, y=solutions_df.f2, mode="markers")

fig.show()
```

{{plot_objective_space}}

This visualisation gives us an idea of how our solutions look in the objective space. However, we can do better and visualise each front using a different colour. This way, we can visually distinguish between the different non-dominated fronts in our population.

Before producing the visualisation, we may fish to determine the number of fronts found.


```python
solutions_df.front_rank.nunique()
```

{{text_unique_fronts}}

We will then need to produce a sorted vector containing the rank of each front.


```python
fronts = sorted(solutions_df.front_rank.unique())
print(fronts)
```

{{text_fronts}}

With this vector, we can now visualise each front on the same scatterplot, using different colours to distinguish between their ranking. If you click on items in the legend, you can also disable/enable each front to examine them independently.


```python
fig = go.Figure(layout=dict(xaxis=dict(title="f1"), yaxis=dict(title="f2")))

for front in fronts:
    front_solutions_df = solutions_df.loc[solutions_df.front_rank == front]
    fig.add_scatter(
        x=front_solutions_df.f1,
        y=front_solutions_df.f2,
        name=f"front {front}",
        mode="markers",
        marker=dict(color=px.colors.qualitative.Plotly[front]),
    )

fig.show()
```

{{plot_solutions_ranked}}

The above visualising is great and the code we used to generate it gave us some finer control over the order in which they are plotted, the colours, the axis labels, and so on. However, I wanted to also share with you an approach to get a very similar plot using the `plotly.express`. As you can see below, we have achieved a very similar plot in only a single line of code.


```python
px.scatter(solutions_df, x="f1", y="f2", color="front_rank")
```

{{plot_solutions_ranked_px}}

## Conclusion

In this section, we have demonstrated how we can use a software package such as Platypus to calculate the non-dominated sorting ranks for a population, which is a useful technique in the selection stage of an Evolutionary Algorithm. We then used this information to create a scatterplot that distinguishes between each non-dominated front using different colours for every rank. This is useful when visualising a population either during runtime or after a search has concluded.
