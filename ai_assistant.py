
import ollama

from storage import load_expenses
from expense_manager import show_total, category_summary, search_expenses, add_expense, delete_expense, edit_expense, sort_expenses


MODEL = "qwen2.5:3b"

VALID_CATEGORIES = {
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Education",
    "Entertainment",
    "Health",
    "People",
    "Other"
}


SYSTEM_PROMPT = (
    "You are an expense tracker assistant. "
    "When the user asks about their expenses, use the appropriate available tool. "
    "Do not ask the user to provide their expense records. "
    "Do not perform expense calculations yourself when a tool is available. "

    "When adding an expense, the category must be exactly one of: "
    "Food, Travel, Shopping, Bills, Education, Entertainment, Health, People, Other. "

    "Use these category definitions to choose the most appropriate category: "

    "Food means anything primarily related to eating or drinking. "
    "Travel means transportation, fuel, parking, and travel-related costs. "
    "Shopping means buying physical goods or personal items. "
    "Bills means recurring or necessary payments such as electricity, internet, phone, rent, and similar services. "
    "Education means college, courses, books, exams, educational materials, and similar expenses. "
    "Entertainment means movies, games, entertainment subscriptions, events, and hobbies. "
    "Health means medicine, doctor visits, medical tests, healthcare, and fitness-related expenses. "
    "People means money given to or spent specifically for another person. "
    "Other means expenses that do not reasonably fit any of the other categories. "

    "Choose the category based on the meaning and context of the expense, "
    "not simply on individual keywords. "
    "For example, coffee, meals, restaurants, groceries, and food delivery normally belong to Food. "
    "If an expense is ambiguous, choose the category that best matches the overall context. "

    "For sorting requests, always use the sort_expenses tool. "
    "Use amount when sorting by money or spending. "
    "Use date when sorting by newest or oldest. "
    "Use category when sorting alphabetically by category. "
    "Use description when sorting alphabetically by description. "
    "Use ascending for lowest amount, oldest date, A-Z category, or A-Z description. "
    "Use descending for highest amount, newest date, Z-A category, or Z-A description. "

    "After receiving a tool result, give the user a concise natural-language answer."
)


tools = [
    {
        "type": "function",
        "function": {
            "name": "show_total",
            "description": "Calculate the total amount of all expenses.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "category_summary",
            "description": "Calculate the exact total expense for every expense category.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_expenses",
            "description": "Search expenses by category, description, or date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "The text to search for in the expense category, description, or date."
                    }
                },
                "required": ["search_term"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_expense",
            "description": "Add a new expense to the expense tracker.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "The expense category. Must be exactly Food, Travel, Shopping, Bills, Education, Entertainment, Health, People, or Other."
                    },
                    "money": {
                        "type": "number",
                        "description": "The amount of money spent. Must be greater than zero."
                    },
                    "description": {
                        "type": "string",
                        "description": "A short description of what the money was spent on."
                    }
                },
                "required": ["category", "money", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_expense",
            "description": "Find an existing expense that the user wants to delete. Extract only the important identifying term from the user's request, such as 'gaming', 'coffee', 'pizza', or 'petrol'. Do not include words such as 'expense', 'delete', 'remove', or 'my' in the search term. Do not invent an expense.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Only the important identifying term from the expense. Examples: 'gaming', 'coffee', 'pizza', 'petrol'."
                    }
                },
                "required": ["search_term"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_expense",
            "description": "Find an existing expense that the user wants to edit. Extract only the important identifying term from the expense, such as 'gaming', 'coffee', 'pizza', or 'petrol'. Do not include words such as 'expense', 'edit', 'change', 'update', or 'my' in the search term.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_term": {
                        "type": "string",
                        "description": "Only the important identifying term used to find the existing expense."
                    },
                    "money": {
                        "type": "number",
                        "description": "The new amount for the expense. Must be greater than zero."
                    },
                    "description": {
                        "type": "string",
                        "description": "The new description for the expense."
                    }
                },
                "required": ["search_term"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "sort_expenses",
            "description": "Sort expenses temporarily. Use this tool whenever the user asks to sort, order, arrange, or list expenses by amount, date, category, or description.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sort_by": {
                        "type": "string",
                        "enum": [
                            "amount",
                            "date",
                            "category",
                            "description"
                        ],
                        "description": "Choose exactly one: amount for money, date for newest or oldest, category for category alphabetical order, description for description alphabetical order."
                    },
                    "order": {
                        "type": "string",
                        "enum": [
                            "ascending",
                            "descending"
                        ],
                        "description": "Choose ascending or descending. A-Z and oldest/lowest use ascending. Z-A and newest/highest use descending."
                    }
                },
                "required": [
                    "sort_by",
                    "order"
                ]
            }
        }
    }
]


def ask_ai(question: str, expenses: dict) -> str:
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": question
        }
    ]

    response = ollama.chat(
        model=MODEL,
        messages=messages,
        tools=tools
    )

    if not response.message.tool_calls:
        return response.message.content

    messages.append(response.message)

    for tool_call in response.message.tool_calls:

        tool_name = tool_call.function.name

        print(f"Tool requested: {tool_name}")

        if tool_name == "show_total":

            result = show_total(expenses)

            messages.append(
                {
                    "role": "tool",
                    "content": str(result)
                }
            )

        elif tool_name == "category_summary":

            summary, total = category_summary(expenses)

            result = {
                "categories": summary,
                "total": total
            }

            messages.append(
                {
                    "role": "tool",
                    "content": str(result)
                }
            )

        elif tool_name == "search_expenses":

            arguments = tool_call.function.arguments

            search_term = arguments.get("search_term", "").strip()

            if not search_term:
                result = "Search term cannot be empty."
            else:
                result = search_expenses(expenses, search_term)

            messages.append(
                {
                    "role": "tool",
                    "content": str(result)
                }
            )

        elif tool_name == "add_expense":
            arguments = tool_call.function.arguments

            category = arguments.get("category", "").strip()
            money = arguments.get("money")
            description = arguments.get("description", "").strip()

            if category not in VALID_CATEGORIES:

                return f"Invalid category selected by AI: {category}"

            if type(money) not in (int, float) or money <= 0:

                return "Invalid expense amount selected by AI."

            if not description:

                return "Expense description cannot be empty."

            print("\nExpense to add:")
            print(f"Category: {category}")
            print(f"Amount: ${money:.2f}")
            print(f"Description: {description}")

            confirmation = input(
                "Confirm adding this expense? (y/n): "
            ).strip().lower()

            if confirmation != "y":

                return "Expense addition cancelled."

            result = add_expense(
                expenses,
                category,
                float(money),
                description
            )

            return result

        elif tool_name == "delete_expense":
            arguments = tool_call.function.arguments

            search_term = arguments.get("search_term", "").strip()

            if not search_term:
                return "I couldn't determine which expense you want to delete."

            matches = []

            for category, category_expenses in expenses.items():
                for orig_idx, expense in enumerate(category_expenses):
                    money, description, time = expense

                    if (search_term.lower() in category.lower()) or (search_term.lower() in description.lower()) or (search_term.lower() in time.lower()):
                        matches.append(
                            {
                                "category": category,
                                "index": orig_idx,
                                "money": money,
                                "description": description,
                                "time": time
                            }
                        )

            if not matches:
                return f"No expenses found for '{search_term}'."

            print("\nExpenses found: ")

            for i, expense in enumerate(matches, start=1):
                print(f"{i}. {expense['category']} - ${expense['money']:.2f} - {expense['description']} - {expense['time']}")

            if len(matches) > 1:

                try:
                    selection = int(input("Select the expense you want to delete: "))

                    if selection < 1 or selection > len(matches):
                        return "Invalid expense selection."

                except ValueError:
                    return "Invalid expense selection."

                selected = matches[selection - 1]

            else:

                selected = matches[0]

            print("\nExpense to delete:")
            print(f"Category: {selected['category']}")
            print(f"Amount: ${selected['money']:.2f}")
            print(f"Description: {selected['description']}")
            print(f"Date: {selected['time']}")

            confirmation = input("Confirm deleting this expense? (y/n): ").strip().lower()

            if confirmation != "y":
                return "Expense deletion cancelled."

            result = delete_expense(expenses, selected["category"], selected["index"])
            return result

        elif tool_name == "edit_expense":

            arguments = tool_call.function.arguments

            search_term = arguments.get("search_term", "").strip()
            new_money = arguments.get("money")
            new_description = arguments.get("description")

            if not search_term:
                return "I couldn't determine which expense you want to edit."

            matches = []

            for category, category_expenses in expenses.items():
                for orig_idx, expense in enumerate(category_expenses):
                    money, description, time = expense

                    if (search_term.lower() in category.lower()) or (search_term.lower() in description.lower()) or (search_term.lower() in time.lower()):
                        matches.append(
                            {
                                "category": category,
                                "index": orig_idx,
                                "money": money,
                                "description": description,
                                "time": time
                            }
                        )

            if not matches:
                return f"No expenses found for '{search_term}'."

            print("\nExpenses found:")

            for i, expense in enumerate(matches, start=1):
                print(f"{i}. {expense['category']} - ${expense['money']:.2f} - {expense['description']} - {expense['time']}")

            if len(matches) > 1:

                try:
                    selection = int(input("Select the expense you want to edit: "))

                    if selection < 1 or selection > len(matches):
                        return "Invalid expense selection."

                except ValueError:
                    return "Invalid expense selection."

                selected = matches[selection - 1]

            else:

                selected = matches[0]

            if new_money is None:
                new_money = selected["money"]

            if new_description is None or not str(new_description).strip():
                new_description = selected["description"]
            else:
                new_description = str(new_description).strip()

            if type(new_money) not in (int, float) or new_money <= 0:
                return "Invalid new expense amount."

            print("\nExpense to update:")
            print(f"Category: {selected['category']}")
            print(f"Old Amount: ${selected['money']:.2f}")
            print(f"New Amount: ${new_money:.2f}")
            print(f"Old Description: {selected['description']}")
            print(f"New Description: {new_description}")
            print(f"Date: {selected['time']}")

            confirmation = input("Confirm updating this expense? (y/n): ").strip().lower()
            if confirmation != "y":
                return "Expense update cancelled."

            result = edit_expense(expenses, selected["category"], selected["index"], float(new_money), new_description)
            return result

        elif tool_name == "sort_expenses":
            arguments = tool_call.function.arguments

            sort_by = arguments.get("sort_by", "").strip().lower()
            order = arguments.get("order", "").strip().lower()

            valid_sort_fields = {
                "amount",
                "date",
                "category",
                "description"
            }

            valid_orders = {"ascending", "descending"}

            if sort_by not in valid_sort_fields:
                return f"Invalid sorting field: {sort_by}"

            if order not in valid_orders:
                return f"Invalid sorting order: {order}"

            descending = order == "descending"

            result = sort_expenses(expenses, sort_by, descending)

            if not result:
                return "No expenses found."

            print("\nSorted Expenses: ")

            for index, expense in enumerate(result, start=1):
                print(f"{index}. {expense['category']} - ${expense['money']:.2f} - {expense['description']} - {expense['date']}")

            return f"Expenses sorted by {sort_by} in {order} order successfully."

        else:
            return f"Unknown tool: {tool_name}"


    final_response = ollama.chat(
        model=MODEL,
        messages=messages
    )

    return final_response.message.content


def main() -> None:
    while True:

        expenses = load_expenses()

        question = input("Ask AI: ").strip()

        if not question:
            print("Question cannot be empty.\n")
            continue

        if question.lower() == "q":
            print("Exiting AI Assistant...")
            break

        try:
            answer = ask_ai(question, expenses)
            print(f"\n{answer}\n")

        except Exception as error:
            print(f"\nError: {error}\n")


if __name__ == "__main__":
    main()