"""
Module to query bank API for transactions, calculate daily money in and out
in account currency and UAH currency, with added logging.
"""

import sys

import requests
import json
import logging
import csv
import argparse
from collections import defaultdict
from datetime import datetime, timedelta

PRIVATBANK_TX_STATEMENTS_URL = "https://acp.privatbank.ua/api/statements/transactions"


def get_transactions(account_number, start_date, end_date, token):
    """
    Get all transactions for a given account within a specified date range.

    Args:
    account_number (str): Bank account number.
    start_date (str): Start date in format 'dd-MM-yyyy'.
    end_date (str): End date in format 'dd-MM-yyyy'.
    token (str): Authorization token for API access.

    Returns:
    list: List of transaction dictionaries.
    """
    transactions = []
    follow_id = None
    headers = {"Content-Type": "application/json;utf8", "token": token}

    while True:
        response = requests.get(
            f"{PRIVATBANK_TX_STATEMENTS_URL}"
            f"?acc={account_number}&startDate={start_date}"
            f"&endDate={end_date}&followId={follow_id if follow_id else ''}",
            headers=headers,
        )
        data = response.json()

        if data["status"] != "SUCCESS":
            logging.error(f"Failed to fetch transactions: {data}")
            break

        transactions.extend([t for t in data["transactions"] if t["PR_PR"] == "r"])
        logging.info(f"Fetched {len(transactions)} transactions so far.")
        if not data["exist_next_page"]:
            break

        follow_id = data["next_page_id"]

    return transactions


def calculate_daily_amounts(transactions, start_date, end_date=None):
    """
    Calculate daily amounts of money in and out.

    Args:
    transactions (list): List of transaction dictionaries.
    start_date (str): Start date in format 'dd-MM-yyyy'.
    end_date (str, optional): End date in format 'dd-MM-yyyy'. Defaults to current date if None.

    Returns:
    dict: Dictionary with dates as keys and money in/out as values.
    """
    start = datetime.strptime(start_date, "%d-%m-%Y")
    end = datetime.strptime(end_date, "%d-%m-%Y") if end_date else datetime.now()
    day_count = (end - start).days + 1

    daily_totals = defaultdict(
        lambda: {"money_in": 0, "money_out": 0, "money_in_UAH": 0, "money_out_UAH": 0}
    )

    for transaction in transactions:
        date = datetime.strptime(
            transaction["DATE_TIME_DAT_OD_TIM_P"], "%d.%m.%Y %H:%M:%S"
        ).date()
        amount = float(transaction["SUM"])
        amount_uah = float(transaction["SUM_E"])
        if transaction["TRANTYPE"] == "C":
            daily_totals[date]["money_in"] += amount
            daily_totals[date]["money_in_UAH"] += amount_uah
        else:
            daily_totals[date]["money_out"] += amount
            daily_totals[date]["money_out_UAH"] += amount_uah

    for day in (start + timedelta(n) for n in range(day_count)):
        if day.date() not in daily_totals:
            daily_totals[day.date()] = {
                "money_in": 0,
                "money_out": 0,
                "money_in_UAH": 0,
                "money_out_UAH": 0,
            }

    sorted_totals = sorted(daily_totals.items())
    return [
        {"date": date.strftime("%Y-%m-%d"), **totals} for date, totals in sorted_totals
    ]


def generate_report(accounts, start_date, end_date, token, format="json"):
    """
    Generate a report for a list of accounts over a specified date range in either JSON or CSV format.

    Args:
    accounts (list): List of account numbers.
    start_date (str): Start date in format 'dd-MM-yyyy'.
    end_date (str): End date in format 'dd-MM-yyyy'.
    token (str): Authorization token for API access.
    format (str): Output format of the report ('json' or 'csv').

    Returns:
    None: Outputs a file for each account in the specified format.
    """
    for account in accounts:
        logging.info(f"Processing account {account}.")
        transactions = get_transactions(account, start_date, end_date, token)
        if not transactions:
            logging.warning(f"No transactions found for account {account}.")
            continue

        account_name = (
            transactions[0].get("AUT_MY_NAM", "Unknown") if transactions else "Unknown"
        )
        daily_amounts = calculate_daily_amounts(transactions, start_date, end_date)

        if format.lower() == "csv":
            file_name = f"{account_name}_{account}_report_{start_date}_{end_date}.csv"
            with open(file_name, "w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=daily_amounts[0].keys())
                writer.writeheader()
                writer.writerows(daily_amounts)
        else:
            file_name = f"{account_name}_{account}_report_{start_date}_{end_date}.json"
            with open(file_name, "w") as file:
                json.dump(daily_amounts, file, indent=4)

        logging.info(f"Report generated for account {account}: {file_name}")


def read_token_from_file(file_path):
    """
    Reads a token from a given file.

    Args:
    file_path (str): Path to the file containing the token.

    Returns:
    str: Token as a string.
    """
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except Exception as e:
        logging.error(f"Error reading token from file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    parser = argparse.ArgumentParser(
        description="Generate transaction report for given accounts."
    )
    parser.add_argument(
        "-s",
        "--start-date",
        type=str,
        default=(datetime.now().replace(day=1) - timedelta(days=1))
        .replace(day=1)
        .strftime("%d-%m-%Y"),
        help="Start date in format 'dd-MM-yyyy'. Default is first day of previous month.",
    )
    parser.add_argument(
        "-e",
        "--end-date",
        type=str,
        default="",
        help="End date in format 'dd-MM-yyyy'. Default is empty (current date).",
    )
    parser.add_argument(
        "-f",
        "--format",
        type=str,
        default="csv",
        choices=["json", "csv"],
        help="Format of the report. Default is 'csv'.",
    )
    parser.add_argument(
        "-t",
        "--token",
        type=str,
        default="",
        help="Authorization token for API access. This or -tf must be provided.",
    )
    parser.add_argument(
        "-tf",
        "--token-file",
        type=str,
        default="",
        help="Path to a file containing the authorization token. This or -t must be provided.",
    )
    parser.add_argument(
        "-a",
        "--accounts",
        type=lambda s: set(s.split(",")),
        required=True,
        help="Comma-separated list of account numbers.",
    )

    args = parser.parse_args()

    if not args.token and not args.token_file:
        parser.error("Either --token or --token-file must be provided.")
    elif args.token_file:
        args.token = read_token_from_file(args.token_file)

    generate_report(
        args.accounts, args.start_date, args.end_date, args.token, args.format
    )
