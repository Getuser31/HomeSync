from datetime import datetime


def generate_period_key(recurrence_name: str, data_ref: datetime = None) -> str:
    if data_ref is None:
        data_ref = datetime.now()

    if recurrence_name == "Daily":
        return data_ref.strftime("%Y-%m-%d")

    elif recurrence_name == "Weekly":
        return data_ref.strftime("%G-W%V")

    elif recurrence_name == "Monthly":
        return data_ref.strftime("%Y-%m")

    return data_ref.strftime("%Y")
