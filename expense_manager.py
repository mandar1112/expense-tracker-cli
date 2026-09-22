

from storage import save_expenses
from datetime import datetime



def add_expense(expenses: dict, category: str, money: float, description: str) -> str:

    if category not in expenses:
        expenses[category] = []

    time = datetime.now().strftime("%Y-%m-%d")

    expenses[category].append([money, description, time])
    save_expenses(expenses)

    return "Expense added successfully"


def delete_expense(expenses: dict, category: str, index: int) -> str:

    deleted_expense = expenses[category].pop(index)

    if not expenses[category]:
        del expenses[category]

    save_expenses(expenses)

    return f"Removed Expense: ${deleted_expense[0]:.2f} - {deleted_expense[1]} - {deleted_expense[2]}"


def edit_expense(expenses: dict, category: str, index: int, money: float, description: str) -> str:
    expenses[category][index][0] = money
    expenses[category][index][1] = description

    save_expenses(expenses)

    return "Expense updated successfully."


def search_expenses(expenses: dict, search_term: str) -> dict:
    results = {}

    search_term = search_term.lower()

    for category, category_expenses in expenses.items():
        for expense in category_expenses:
            money, description, time  = expense

            if (search_term in category.lower()) or (search_term in description.lower()) or (search_term in time.lower()):
                if category not in results:
                    results[category] = []

                results[category].append(expense)

    return results


def show_total(expenses: dict) -> float:

    if not expenses:
        return 0.0

    total = 0.0

    for category_expenses in expenses.values():
        for money, _, _ in category_expenses:
            total += money

    return total


def category_summary(expenses: dict) -> tuple[dict, float]:

    result = {}

    all_total = 0

    for category, value in expenses.items():
        total = 0
        for money, _, _ in value:
            total += money

        result[category] = total
        all_total += total
    
    return result, all_total

