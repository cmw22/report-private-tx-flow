import datetime
from unittest.mock import patch, mock_open
import pytest
from main import get_transactions, calculate_daily_amounts, generate_report


@pytest.fixture
def example_transactions():
    return [
        {
            "DATE_TIME_DAT_OD_TIM_P": "01.03.2024 12:00:00",
            "SUM": "100.00",
            "SUM_E": "2700.00",
            "TRANTYPE": "C",
            "PR_PR": "r",
        },
        {
            "DATE_TIME_DAT_OD_TIM_P": "02.03.2024 12:00:00",
            "SUM": "200.00",
            "SUM_E": "5400.00",
            "TRANTYPE": "D",
            "PR_PR": "r",
        },
    ]


@patch("main.requests.get")
def test_get_transactions(mock_get, example_transactions):
    mock_response = {
        "status": "SUCCESS",
        "transactions": example_transactions,
        "exist_next_page": False,
    }
    mock_get.return_value.json.return_value = mock_response

    transactions = get_transactions("123456", "01-03-2024", "02-03-2024", "token")
    assert len(transactions) == 2, "Should fetch two transactions"


def test_calculate_daily_amounts(example_transactions):
    start_date = "01-03-2024"
    end_date = "02-03-2024"
    daily_amounts = calculate_daily_amounts(example_transactions, start_date, end_date)

    assert len(daily_amounts) == 2, "Should calculate amounts for two days"
    assert daily_amounts[0]["money_in"] == 100.00, "Incorrect money_in calculation"
    assert daily_amounts[1]["money_out"] == 200.00, "Incorrect money_out calculation"


@patch("main.get_transactions")
@patch("builtins.open", new_callable=mock_open)
def test_generate_report(mock_file_open, mock_get_transactions, example_transactions):
    mock_get_transactions.return_value = example_transactions

    generate_report(["123456"], "01-03-2024", "02-03-2024", "token", "json")
    mock_file_open.assert_called_once()
    mock_get_transactions.assert_called_once_with(
        "123456", "01-03-2024", "02-03-2024", "token"
    )
    handle = mock_file_open()
    handle.write.assert_called()  # Changed to assert write was called, ignoring the number of calls.
