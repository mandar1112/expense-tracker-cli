
from categories import category_selector
from storage import load_expenses
from expense_manager import add_expense, edit_expense, search_expenses, show_total, delete_expense, category_summary



expenses = load_expenses()

def select_existing_category(expenses: dict) -> str | None:
    category, status = category_selector()

    if not status:
        print(f"\n{category}\n")
        return None

    if category not in expenses:
        print(f"\nNo expenses found for {category}.\n")
        return None

    return category


def display_category_expenses(expenses: dict, category: str) -> None:
    for i, (money, description, time) in enumerate(expenses[category], start=1):
        print(f"{i}. ${money:.2f} - {description} - {time}")




def main() -> None:

    while True:
        try:
            choice = int(input(
                "\nSelect Option from below:\n"
                "1. Add Expense\n"
                "2. View Expenses\n"
                "3. Total Expense\n"
                "4. Delete Expense\n"
                "5. Category Summary\n"
                "6. Edit Expense\n"
                "7. Search Expenses\n"
                "8. Exit\n"
                "Choice: "
            ))

            if choice < 1 or choice > 8:
                raise ValueError
            
        except ValueError:
            print("Please enter a valid number.")
            continue


        match choice:
            case 1:
                category, status = category_selector()

                if not status:
                    print(f"\n{category}\n")
                    continue

                print(f"\nCategory Selected: {category}")

                try:
                    money = float(input("Enter the amount: "))

                    if money <= 0:
                        raise ValueError
            
                except ValueError:
                    print(f"\nPlease enter a valid positive amount.\n")
                    continue

                description = input("Enter the Description: ").strip()

                if not description:
                    print("\nDescription cannot be empty.\n")
                    continue
                
                result = add_expense(expenses, category, money, description)

                print(f"\n{result}\n")


            case 2:
                print("\n" + 30 * "=")
                print(f"{'EXPENSES' : ^30}")
                print(30 * "=")

                if not expenses:
                    print("No expenses found.")
                    continue

                for category, category_expenses in expenses.items():
                    print(f"\n{category}")

                    for i, (money, description, time) in enumerate(category_expenses, start=1):
                        print(f"{i}. ${money:.2f} - {description} - {time}")



            case 3:
                print("\n" + 30 * "=")
                print(f"{'TOTAL EXPENSE' : ^30}")
                print(30 * "=")

                total = show_total(expenses)
                print(f"Total Expense: ${total:.2f}")


            case 4:
                category = select_existing_category(expenses)

                if category is None:
                    continue

                print(f"Select Category: {category}")
                
                display_category_expenses(expenses, category)

                try:
                    user_selection = int(input("Select the Option you want to delete: "))

                    if user_selection < 1 or user_selection > len(expenses[category]):
                        raise ValueError
                    result = delete_expense(expenses, category, user_selection - 1)
                    print(f"\n{result}\n")

                except ValueError:
                    print(f"Please enter a valid option between 1 and {len(expenses[category])}. ")
                    continue
                

            case 5:
                print("\n" + 30*"=")
                print(f"{'CATEGORY SUMMARY' :^30}")
                print("\n" + 30*"=")

                category_total, total = category_summary(expenses)

                for category, money in category_total.items():
                    print(f"{category:<15} ${money:.2f}")
                
                print("-" * 30)
                print(f"{'Total':<15} ${total:.2f}")


            case 6:
                category = select_existing_category(expenses)

                if category is None:
                    continue

                print(f"\nSelect Expense from {category}:")

                display_category_expenses(expenses, category)
                try:
                    user_selection = int(input("Select the Expense you want to edit: "))

                    if user_selection < 1 or user_selection > len(expenses[category]):
                        raise ValueError

                    index = user_selection - 1

                    new_money = float(input("Enter the new amount: "))

                    if new_money <= 0:
                        raise ValueError

                    new_description = input("Enter the new description: ").strip()

                    if not new_description:
                        raise ValueError

                    result = edit_expense(expenses, category, index, new_money, new_description)
                    print(f"\n{result}\n")

                except ValueError:
                    print("\nInvalid input.\n")
                    continue
                

            case 7:
                if not expenses:
                    print("\nNo expenses found.\n")
                    continue

                search_term = input("Enter what you want to search: ").strip()

                if not search_term:
                    print("\nSearch term cannot be empty.\n")
                    continue

                result = search_expenses(expenses, search_term)

                if not result:
                    print(f"\nNo expenses found for '{search_term}'.\n")
                    continue

                print("\n" + 30 * "=")
                print(f"{'SEARCH RESULT':^30}")
                print(30 * "=")

                for category, category_expenses in result.items():
                    print(f"\n{category}")

                    for i, (money, description, time) in enumerate(category_expenses, start=1):
                        print(f"{i}. ${money:.2f} - {description} - {time}")

            
            case 8:
                print("Exiting...")
                break


            case _:
                print("Invalid Choice.")


if __name__ == "__main__":
    main()
