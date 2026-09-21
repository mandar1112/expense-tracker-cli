
import ollama

from storage import load_expenses
from expense_manager import show_total, category_summary



MODEL = "qwen2.5:3b"


tools = [
    {
        "type": "function",
        "function": {
            "name": "show_total",
            "description": "Calculate the total amount of all expenses in the expense tracker.",
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
    }
]


SYSTEM_PROMPT = (
    "You are an expense tracker assistant. "
    "The user has an expense tracker application with access to their expense data. "
    "When the user asks a question about their expenses, use the appropriate available tool. "
    "Do not ask the user to provide their expense records. "
    "Do not calculate expense totals yourself when a tool is available. "
    "After receiving a tool result, use that result to give the user a concise answer."
)


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

        else:
            messages.append(
                {
                    "role": "tool",
                    "content": f"Unknown tool: {tool_name}"
                }
            )

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