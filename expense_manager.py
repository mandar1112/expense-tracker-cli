

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


def merge_sort(expenses: list, key) -> list:
    if len(expenses) <= 1:
        return expenses

    middle = len(expenses) // 2

    left = merge_sort(expenses[:middle], key)
    right = merge_sort(expenses[middle:], key)

    result = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):

        if key(left[left_index]) <= key(right[right_index]):
            result.append(left[left_index])
            left_index += 1
        else:
            result.append(right[right_index])
            right_index += 1

    result.extend(left[left_index:])
    result.extend(right[right_index:])

    return result


def sort_expenses(expenses: dict, sort_by: str, descending: bool = False) -> list:
    expense_list = []

    for category, category_expenses in expenses.items():
        for money, description, time in category_expenses:
            expense_list.append(
                {
                    "category": category,
                    "money": money,
                    "description": description,
                    "date": time
                }
            )

    sort_aliases = {
        "amount": "amount",
        "money": "amount",
        "price": "amount",
        "cost": "amount",
        "date": "date",
        "category": "category",
        "description": "description"
    }

    sort_by = sort_aliases.get(sort_by.lower())

    if sort_by is None:
        return []

    keys = {
        "amount": lambda expense: expense["money"],
        "date": lambda expense: expense["date"],
        "category": lambda expense: expense["category"].lower(),
        "description": lambda expense: expense["description"].lower()
    }
    
    expense_list = merge_sort(expense_list, keys[sort_by])

    if descending:
        expense_list.reverse()

    return expense_list

