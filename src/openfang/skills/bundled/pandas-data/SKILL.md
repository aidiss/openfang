---
name: pandas-data
description: Analyze CSV, Excel, and JSON data using pandas in Python.
homepage: https://pandas.pydata.org/docs/
metadata:
  {
    "openfang":
      {
        "emoji": "🐼",
        "requires": { "modules": ["pandas"] },
        "install":
          [
            {
              "id": "pip",
              "kind": "pip",
              "package": "pandas",
              "label": "Install pandas (pip)",
            },
            {
              "id": "uv",
              "kind": "uv",
              "package": "pandas",
              "label": "Install pandas (uv)",
            },
          ],
      },
  }
---

# Pandas Data Analysis

Use Python with pandas for data analysis. Run via `python -c` or create scripts.

## Read Data

```python
import pandas as pd

# CSV
df = pd.read_csv("data.csv")

# Excel
df = pd.read_excel("data.xlsx", sheet_name="Sheet1")

# JSON
df = pd.read_json("data.json")

# From URL
df = pd.read_csv("https://example.com/data.csv")
```

## Quick Analysis

```python
import pandas as pd

df = pd.read_csv("data.csv")

# Overview
print(df.head())           # First 5 rows
print(df.info())           # Column types, nulls
print(df.describe())       # Stats for numeric columns
print(df.shape)            # (rows, cols)
print(df.columns.tolist()) # Column names
```

One-liner:

```bash
python -c "import pandas as pd; df = pd.read_csv('data.csv'); print(df.describe())"
```

## Filter & Select

```python
# Select columns
df[["name", "age"]]

# Filter rows
df[df["age"] > 30]
df[df["status"] == "active"]
df[(df["age"] > 30) & (df["status"] == "active")]

# Query syntax (cleaner)
df.query("age > 30 and status == 'active'")
```

## Group & Aggregate

```python
# Group by single column
df.groupby("category")["sales"].sum()

# Multiple aggregations
df.groupby("category").agg({
    "sales": ["sum", "mean"],
    "quantity": "count"
})

# Pivot table
pd.pivot_table(df, values="sales", index="region", columns="product", aggfunc="sum")
```

## Transform

```python
# Add column
df["total"] = df["price"] * df["quantity"]

# Apply function
df["name_upper"] = df["name"].str.upper()

# Map values
df["status_code"] = df["status"].map({"active": 1, "inactive": 0})

# Fill missing
df["value"].fillna(0, inplace=True)
```

## Sort

```python
# Sort by column
df.sort_values("date", ascending=False)

# Sort by multiple
df.sort_values(["category", "sales"], ascending=[True, False])
```

## Export

```python
# CSV
df.to_csv("output.csv", index=False)

# Excel
df.to_excel("output.xlsx", index=False)

# JSON
df.to_json("output.json", orient="records", indent=2)

# Markdown (for display)
print(df.to_markdown())
```

## Common Patterns

### Quick CSV summary

```bash
python -c "
import pandas as pd
df = pd.read_csv('data.csv')
print('Shape:', df.shape)
print('\\nColumns:', df.columns.tolist())
print('\\nSample:')
print(df.head(3).to_markdown())
"
```

### Filter and export

```bash
python -c "
import pandas as pd
df = pd.read_csv('input.csv')
filtered = df[df['status'] == 'active']
filtered.to_csv('active_only.csv', index=False)
print(f'Exported {len(filtered)} rows')
"
```

### Group and summarize

```bash
python -c "
import pandas as pd
df = pd.read_csv('sales.csv')
summary = df.groupby('region')['revenue'].agg(['sum', 'mean', 'count'])
print(summary.to_markdown())
"
```
