def format_subscript(value: int) -> str:
    subscript_map = {
        "0": "₀",
        "1": "₁",
        "2": "₂",
        "3": "₃",
        "4": "₄",
        "5": "₅",
        "6": "₆",
        "7": "₇",
        "8": "₈",
        "9": "₉",
        "-": "₋",
    }
    strified = str(value)
    result = ""
    for c in strified:
        result += subscript_map[c]
    return result
