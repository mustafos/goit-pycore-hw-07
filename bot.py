from functools import wraps

from address_book import AddressBook, Record


COMMAND_USAGE = {
    "add_contact": "Usage: add name phone",
    "change_contact": "Usage: change name old_phone new_phone",
    "show_phone": "Usage: phone name",
    "add_birthday": "Usage: add-birthday name DD.MM.YYYY",
    "show_birthday": "Usage: show-birthday name",
}


def input_error(func):
    """Return a user-friendly message for expected command errors."""

    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except KeyError as error:
            name = error.args[0] if error.args else ""

            if name:
                return f"Contact {name} not found."

            return "Contact not found."

        except ValueError as error:
            return str(error)

        except IndexError:
            return COMMAND_USAGE.get(
                func.__name__, "Missing command arguments."
            )

    return inner


def parse_input(user_input: str) -> tuple[str, list[str]]:
    parts = user_input.strip().split()

    if not parts:
        return "", []

    command = parts[0].lower()
    args = parts[1:]

    return command, args


def hello() -> str:
    return "How can I help you?"


def _get_record(book: AddressBook, name: str) -> Record:
    record = book.find(name)

    if record is None:
        raise KeyError(name)

    return record


@input_error
def add_contact(args: list[str], book: AddressBook) -> str:
    if len(args) != 2:
        raise IndexError

    name = args[0]
    phone = args[1]
    record = book.find(name)

    if record is None:
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."

    record.add_phone(phone)
    return "Phone added."


@input_error
def change_contact(args: list[str], book: AddressBook) -> str:
    if len(args) != 3:
        raise IndexError

    name = args[0]
    old_phone = args[1]
    new_phone = args[2]
    record = _get_record(book, name)
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args: list[str], book: AddressBook) -> str:
    if len(args) != 1:
        raise IndexError

    name = args[0]
    record = _get_record(book, name)

    if not record.phones:
        return "No phone numbers saved."

    return "; ".join(phone.value for phone in record.phones)


def show_all(book: AddressBook) -> str:
    if not book.data:
        return "No contacts found."

    return "\n".join(str(record) for record in book.data.values())


@input_error
def add_birthday(args: list[str], book: AddressBook) -> str:
    if len(args) != 2:
        raise IndexError

    name = args[0]
    birthday = args[1]
    record = _get_record(book, name)
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args: list[str], book: AddressBook) -> str:
    if len(args) != 1:
        raise IndexError

    name = args[0]
    record = _get_record(book, name)

    if record.birthday is None:
        return f"No birthday saved for {name}."

    return str(record.birthday)


def birthdays(book: AddressBook) -> str:
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No upcoming birthdays."

    return "\n".join(
        f"{item['name']}: {item['congratulation_date']}" for item in upcoming
    )
