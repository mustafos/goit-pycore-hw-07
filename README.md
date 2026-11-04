# GoIT Python Core — Homework 07

## Description

This project is a command-line contact assistant written with object-oriented Python. Contacts live in an address book. Each contact has a name, one or more phone numbers, and an optional birthday.

The assistant keeps the book in memory for the current session. It does not save contacts to a file.

## Features

- Add a contact, add another phone, change a phone, and show saved numbers.
- Store more than one phone number for the same contact.
- Accept only phone numbers of exactly 10 digits.
- Save one birthday per contact in `DD.MM.YYYY` format.
- Reject an invalid date format and an impossible calendar date.
- List birthdays that fall today or within the next six days.
- Move a Saturday or Sunday greeting to the following Monday.
- Run the assistant from the terminal.
- Report missing arguments, unknown contacts, and invalid values without stopping the program.

## Project structure

```text
goit-pycore-hw-07/
├── address_book.py    # Contact fields, records, and the address book
├── bot.py             # Command parsing, handlers, and input errors
├── main.py            # Program entry point and command loop
├── test_hw07.py       # Unit tests
├── README.md
└── .gitignore
```

| File | Responsibility |
| --- | --- |
| `address_book.py` | `Field`, `Name`, `Phone`, `Birthday`, `Record`, and `AddressBook` |
| `bot.py` | Parses input and handles each assistant command |
| `main.py` | Creates the address book and reads commands until `close` or `exit` |
| `test_hw07.py` | Checks validation, upcoming birthdays, commands, and the command loop |

## Requirements

- Python 3.9 or newer. The type hints use built-in forms such as `list[str]`.
- The Python standard library only. No packages need to be installed.

The tests were run with Python 3.15.

## Installation and execution

```bash
git clone git@github.com:mustafos/goit-pycore-hw-07.git
cd goit-pycore-hw-07
python3 main.py
```

## Available commands

A contact name is one word. `add`, `change`, `phone`, `add-birthday`, and `show-birthday` need the exact number of arguments shown below. A missing or extra argument prints a usage message and does not change the book.

| Command | Syntax | Description |
| --- | --- | --- |
| `hello` | `hello` | Greets the user. |
| `add` | `add John 1234567890` | Creates a contact, or adds a phone to an existing one. |
| `change` | `change John 1234567890 0987654321` | Replaces one saved phone number. |
| `phone` | `phone John` | Shows all phone numbers for a contact. |
| `all` | `all` | Shows every contact, including a birthday when one is saved. |
| `add-birthday` | `add-birthday John 07.11.1990` | Saves one birthday. The date is a single argument. |
| `show-birthday` | `show-birthday John` | Shows the saved birthday. |
| `birthdays` | `birthdays` | Shows greetings for the next seven days, including today. |
| `close` | `close` | Prints `Good bye!` and exits. |
| `exit` | `exit` | Prints `Good bye!` and exits. |

An empty line or an unknown command prints `Invalid command.`

## Running tests

```bash
python3 -m unittest test_hw07 -v
```

The same tests are found by discovery:

```bash
python3 -m unittest discover -v
```

## Example session

`birthdays` below was produced on 4 November 2026. John's birthday, 7 November, fell on Saturday, so the greeting moved to Monday.

```text
Welcome to the assistant bot!
Enter a command: hello
How can I help you?
Enter a command: add John 1234567890
Contact added.
Enter a command: add John 0987654321
Phone added.
Enter a command: change John 1234567890 1112223333
Contact updated.
Enter a command: phone John
1112223333; 0987654321
Enter a command: add-birthday John 07.11.1990
Birthday added.
Enter a command: show-birthday John
07.11.1990
Enter a command: all
Contact name: John, phones: 1112223333; 0987654321, birthday: 07.11.1990
Enter a command: birthdays
John: 09.11.2026
Enter a command: exit
Good bye!
```
