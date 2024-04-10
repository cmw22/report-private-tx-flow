# Bank Transactions Report Generator

[![Python Tests](https://github.com/cmw22/report-private-tx-flow/actions/workflows/python-tests.yml/badge.svg)](https://github.com/cmw22/report-private-tx-flow/actions/workflows/python-tests.yml)

This tool allows you to generate report for daily in/out flow in Privatbank accounts based on transactions.
Report is generated in either JSON or CSV format.
It queries a bank API to fetch transactions for specified accounts within a given date range.

## Setup

Before running the program, you might want to set up a Python virtual environment.
This is not strictly necessary but recommended to avoid conflicts with other Python packages you might have installed.
Here's how you can do it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

Next, install the required packages:

```bash
pip install requests
```

## Usage

Run the program with the following command:

```bash
python main.py -a <accounts> -t <token> [-tf <token-file>] [-s <start-date>] [-e <end-date>] [-f <format>]
```

### Parameters

- `-a`, `--accounts`: Comma-separated list of account numbers. **(Required)**
- `-t`, `--token`: Authorization token for API access. This or `--token-file` must be provided.
- `-tf`, `--token-file`: Path to a file containing the authorization token. This or `--token` must be provided.
- `-s`, `--start-date`: Start date in format 'dd-MM-yyyy'. Default is the first day of the previous month.
- `-e`, `--end-date`: End date in format 'dd-MM-yyyy'. Default is the current date.
- `-f`, `--format`: Format of the report (`json` or `csv`). Default is `csv`.

### Examples

To generate a CSV report for accounts UA1530000000000 and UA51305200000000000 for the current month:

```bash
python your_program.py -a UA1530000000000,UA51305200000000000 -t your_token_here -s 01-03-2024
```

Or, to generate a JSON report for the same accounts and date range, but with the token stored in a file:

```bash
python your_program.py -a UA1530000000000,UA51305200000000000 -tf path/to/your_token_file -s 01-03-2024 -f json
```

## Example Output

### CSV

```csv
date,money_in,money_out,money_in_UAH,money_out_UAH
2024-03-01,1000.00,500.00,27000.00,13500.00
2024-03-02,1500.00,700.00,40500.00,18900.00
```

### JSON

```json
[
  {
    "date": "2024-03-01",
    "money_in": 1000.00,
    "money_out": 500.00,
    "money_in_UAH": 27000.00,
    "money_out_UAH": 13500.00
  },
  {
    "date": "2024-03-02",
    "money_in": 1500.00,
    "money_out": 700.00,
    "money_in_UAH": 40500.00,
    "money_out_UAH": 18900.00
  }
]
```

## Contributing

### Setting Up Pre-commit Hooks

This project uses pre-commit hooks to ensure code standards and quality.
Pre-commit hooks run checks before each commit to ensure that changes adhere to our coding standards, 
including but not limited to code formatting with `black`.

To set up pre-commit hooks in your local environment, follow these steps:

1. **Install pre-commit**: If you haven't already, install the pre-commit tool. You can do so using pip:

   ```bash
   pip install pre-commit
   ```

2. **Install the pre-commit hook**: Navigate to the root directory of this project in your terminal 
and run the following command:

   ```bash
   pre-commit install
   ```

   This command installs the pre-commit hook into your `.git/` directory,
   enabling it to run the configured hooks (defined in `.pre-commit-config.yaml`) before each commit.

3. **Make a commit**: With pre-commit hooks installed, every time you commit changes, the configured hooks
(such as `black` for code formatting) will run automatically. If a hook makes changes (e.g., reformatting a file) 
or fails, you'll need to fix the reported issues and add the changes before committing again.

### Contributing Code

When contributing to this project, please ensure that you:

- Follow the project's coding standards and guidelines.
- Write or update tests as necessary.
- Update documentation for any changes you make.
- Install and run pre-commit hooks as described above to ensure your changes meet our code quality standards.
