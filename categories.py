


CATEGORY = {
    1 : "Food",
    2 : "Travel",
    3 : "Shopping",
    4 : "Bills",
    5 : "Education",
    6 : "Entertainment",
    7 : "Health",
    8 : "People",
    9 : "Other"
}


def category_selector() -> tuple[str, bool]:

    try:
        category = int(input(
            "\nSelect the Categoty from below (1-9)\n"
            "1. Food\n"
            "2. Travel\n"
            "3.Shopping\n"
            "4.Bills\n"
            "5.Education\n"
            "6.Entertainment\n"
            "7. Health\n"
            "8. People\n"
            "9. Other\n"
            "Choice: "
        ))
    except ValueError:
        return "Invalid input", False

    if category not in CATEGORY.keys():
        return f"{category} not available", False

    return CATEGORY[category], True
