import unittest
from collections import UserDict
from contextlib import contextmanager
from datetime import datetime
from unittest.mock import patch

from address_book import AddressBook, Birthday, Field, Name, Phone, Record
from bot import (
    add_birthday,
    add_contact,
    birthdays,
    change_contact,
    parse_input,
    show_all,
    show_birthday,
    show_phone,
)
from main import main


@contextmanager
def freeze_today(year, month, day):
    class FrozenDateTime(datetime):
        @classmethod
        def today(cls):
            return cls(year, month, day)

    with patch("address_book.datetime", FrozenDateTime):
        yield


class TestValidation(unittest.TestCase):
    def test_phone_must_contain_exactly_ten_digits(self):
        self.assertEqual(Phone("1234567890").value, "1234567890")

        for phone in (
            "123456789",
            "12345678901",
            "12345abcde",
            "123 456789",
            "123-456789",
            "",
            None,
        ):
            with self.subTest(phone=phone):
                with self.assertRaises(ValueError) as error:
                    Phone(phone)

                self.assertEqual(
                    str(error.exception),
                    "Phone number must contain exactly 10 digits",
                )

    def test_birthday_accepts_valid_date(self):
        birthday = Birthday("07.11.1990")

        self.assertIsInstance(birthday.value, datetime)
        self.assertEqual(birthday.value, datetime(1990, 11, 7))
        self.assertEqual(str(birthday), "07.11.1990")

    def test_birthday_rejects_invalid_format_and_impossible_dates(self):
        for value in (
            "1990-11-07",
            "07/11/1990",
            "7.11.1990",
            "07.1.1990",
            "31.02.2025",
            "31.04.2025",
            "29.02.2025",
            "29.02.1900",
            "32.01.2020",
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError) as error:
                    Birthday(value)

                self.assertEqual(
                    str(error.exception),
                    "Invalid date format. Use DD.MM.YYYY",
                )

    def test_leap_day_is_accepted_in_a_leap_year(self):
        birthday = Birthday("29.02.2024")
        century_leap_day = Birthday("29.02.2000")

        self.assertEqual(birthday.value, datetime(2024, 2, 29))
        self.assertEqual(century_leap_day.value, datetime(2000, 2, 29))


class TestRecordAndAddressBook(unittest.TestCase):
    def test_fields_inherit_from_field_and_record_composes_them(self):
        name = Name("Anna")
        phone = Phone("1234567890")
        birthday = Birthday("01.01.2000")

        self.assertIsInstance(name, Field)
        self.assertIsInstance(phone, Field)
        self.assertIsInstance(birthday, Field)

        record = Record("Anna")
        record.add_phone("1234567890")
        record.add_birthday("01.01.2000")

        self.assertIsInstance(record.name, Name)
        self.assertEqual(record.name.value, name.value)
        self.assertEqual(len(record.phones), 1)
        self.assertIsInstance(record.phones[0], Phone)
        self.assertEqual(record.phones[0].value, phone.value)
        self.assertIsInstance(record.birthday, Birthday)
        self.assertEqual(record.birthday.value, birthday.value)

        book = AddressBook()
        self.assertIsInstance(book, UserDict)
        book.add_record(record)
        self.assertIs(book.data["Anna"], record)
        self.assertIs(book.find("Anna"), record)
    def test_record_keeps_homework_06_phone_behavior(self):
        record = Record("John")
        record.add_phone("1234567890")
        record.add_phone("5555555555")

        self.assertEqual(
            str(record),
            "Contact name: John, phones: 1234567890; 5555555555",
        )
        self.assertEqual(record.find_phone("5555555555").value, "5555555555")

        record.edit_phone("1234567890", "1112223333")
        self.assertEqual(
            str(record),
            "Contact name: John, phones: 1112223333; 5555555555",
        )

        with self.assertRaises(ValueError):
            record.edit_phone("1234567890", "0000000000")

        self.assertEqual(record.phones[0].value, "1112223333")

        with self.assertRaises(ValueError):
            record.edit_phone("1112223333", "123")

        self.assertEqual(record.phones[0].value, "1112223333")
        record.remove_phone("5555555555")
        self.assertIsNone(record.find_phone("5555555555"))

    def test_contact_can_store_only_one_birthday(self):
        record = Record("John")

        self.assertIsNone(record.birthday)
        record.add_birthday("07.11.1990")
        self.assertEqual(str(record.birthday), "07.11.1990")
        self.assertIn("birthday: 07.11.1990", str(record))

        with self.assertRaises(ValueError) as error:
            record.add_birthday("08.11.1990")

        self.assertEqual(str(error.exception), "Contact already has a birthday")
        self.assertEqual(str(record.birthday), "07.11.1990")

        with self.assertRaises(ValueError):
            record.add_birthday("31.04.2025")

        self.assertEqual(str(record.birthday), "07.11.1990")

    def test_address_book_find_and_delete(self):
        book = AddressBook()
        record = Record("Jane")
        record.add_phone("9876543210")
        book.add_record(record)

        self.assertEqual(book.find("Jane").name.value, "Jane")
        self.assertIsNone(book.find("John"))

        book.delete("Jane")
        self.assertIsNone(book.find("Jane"))

        with self.assertRaises(ValueError) as error:
            book.delete("Jane")

        self.assertEqual(str(error.exception), "Contact not found")


class TestUpcomingBirthdays(unittest.TestCase):
    def _book_with(self, contacts):
        book = AddressBook()

        for name, birthday in contacts:
            record = Record(name)
            record.add_phone("1234567890")

            if birthday is not None:
                record.add_birthday(birthday)

            book.add_record(record)

        return book

    def test_weekend_birthdays_move_to_monday_and_window_is_seven_days(self):
        book = self._book_with(
            [
                ("Today", "04.11.1990"),
                ("Saturday", "07.11.1992"),
                ("Sunday", "08.11.1988"),
                ("Inside", "10.11.2000"),
                ("Outside", "11.11.2001"),
                ("NoBirthday", None),
            ]
        )

        with freeze_today(2026, 11, 4):
            upcoming = book.get_upcoming_birthdays()

        by_name = {item["name"]: item["congratulation_date"] for item in upcoming}

        self.assertEqual(
            by_name,
            {
                "Today": "04.11.2026",
                "Saturday": "09.11.2026",
                "Sunday": "09.11.2026",
                "Inside": "10.11.2026",
            },
        )
        self.assertNotIn("Outside", by_name)
        self.assertNotIn("NoBirthday", by_name)

    def test_birthdays_around_new_year(self):
        book = self._book_with(
            [
                ("NewYearEve", "31.12.1990"),
                ("Friday", "01.01.1991"),
                ("Saturday", "02.01.1992"),
                ("Sunday", "03.01.1993"),
                ("LastDay", "05.01.1994"),
                ("TooLate", "06.01.1995"),
                ("AlreadyPassed", "29.12.1996"),
            ]
        )

        with freeze_today(2026, 12, 30):
            upcoming = book.get_upcoming_birthdays()

        by_name = {item["name"]: item["congratulation_date"] for item in upcoming}

        self.assertEqual(
            by_name,
            {
                "NewYearEve": "31.12.2026",
                "Friday": "01.01.2027",
                "Saturday": "04.01.2027",
                "Sunday": "04.01.2027",
                "LastDay": "05.01.2027",
            },
        )

    def test_passed_january_birthday_is_not_moved_backward(self):
        book = self._book_with(
            [
                ("Passed", "01.01.1990"),
                ("TodaySunday", "03.01.1991"),
                ("Inside", "08.01.1992"),
                ("Outside", "10.01.1993"),
            ]
        )

        with freeze_today(2027, 1, 3):
            upcoming = book.get_upcoming_birthdays()

        by_name = {item["name"]: item["congratulation_date"] for item in upcoming}

        self.assertEqual(
            by_name,
            {
                "TodaySunday": "04.01.2027",
                "Inside": "08.01.2027",
            },
        )

    def test_day_seven_and_day_eight_are_outside_the_window(self):
        book = self._book_with(
            [
                ("LastDay", "10.11.2000"),
                ("SevenDays", "11.11.2001"),
                ("EightDays", "12.11.2002"),
            ]
        )

        with freeze_today(2026, 11, 4):
            upcoming = book.get_upcoming_birthdays()

        self.assertEqual(
            upcoming,
            [{"name": "LastDay", "congratulation_date": "10.11.2026"}],
        )

    def test_monday_after_a_weekend_can_fall_outside_the_window(self):
        book = self._book_with([("EdgeSaturday", "09.01.1990")])

        with freeze_today(2027, 1, 3):
            upcoming = book.get_upcoming_birthdays()

        self.assertEqual(
            upcoming,
            [{"name": "EdgeSaturday", "congratulation_date": "11.01.2027"}],
        )

    def test_february_29_stays_on_february_29_in_a_leap_year(self):
        book = self._book_with([("Leap", "29.02.2000")])

        with freeze_today(2028, 2, 24):
            upcoming = book.get_upcoming_birthdays()

        self.assertEqual(
            upcoming,
            [{"name": "Leap", "congratulation_date": "29.02.2028"}],
        )

    def test_february_29_on_sunday_moves_to_monday_outside_the_window(self):
        book = self._book_with([("LeapSunday", "29.02.2000")])

        with freeze_today(2032, 2, 23):
            upcoming = book.get_upcoming_birthdays()

        self.assertEqual(
            upcoming,
            [{"name": "LeapSunday", "congratulation_date": "01.03.2032"}],
        )

    def test_february_29_in_non_leap_year_does_not_crash(self):
        book = self._book_with([("Leap", "29.02.2024")])

        with freeze_today(2027, 2, 26):
            upcoming = book.get_upcoming_birthdays()

        self.assertEqual(
            upcoming,
            [{"name": "Leap", "congratulation_date": "01.03.2027"}],
        )

    def test_non_leap_february_29_monday_can_fall_outside_the_window(self):
        book = self._book_with([("Leap", "29.02.2024")])

        with freeze_today(2027, 2, 22):
            upcoming = book.get_upcoming_birthdays()

        self.assertEqual(
            upcoming,
            [{"name": "Leap", "congratulation_date": "01.03.2027"}],
        )


class TestCommands(unittest.TestCase):
    def setUp(self):
        self.book = AddressBook()

    def test_add_new_contact_and_another_phone(self):
        self.assertEqual(add_contact(["John", "1234567890"], self.book), "Contact added.")
        self.assertEqual(add_contact(["John", "0987654321"], self.book), "Phone added.")
        self.assertEqual(show_phone(["John"], self.book), "1234567890; 0987654321")

    def test_change_and_show_phones(self):
        add_contact(["Anna", "1234567890"], self.book)

        self.assertEqual(
            change_contact(["Anna", "1234567890", "1112223333"], self.book),
            "Contact updated.",
        )
        self.assertEqual(show_phone(["Anna"], self.book), "1112223333")

    def test_invalid_phone_is_reported_and_not_saved(self):
        self.assertEqual(
            add_contact(["John", "12345"], self.book),
            "Phone number must contain exactly 10 digits",
        )
        self.assertIsNone(self.book.find("John"))

        add_contact(["John", "1234567890"], self.book)
        self.assertEqual(
            change_contact(["John", "1234567890", "123456789012"], self.book),
            "Phone number must contain exactly 10 digits",
        )
        self.assertEqual(show_phone(["John"], self.book), "1234567890")

    def test_all_contacts_include_birthday_and_empty_book(self):
        self.assertEqual(show_all(self.book), "No contacts found.")

        add_contact(["John", "1234567890"], self.book)
        add_birthday(["John", "07.11.1990"], self.book)
        add_contact(["Anna", "0987654321"], self.book)

        output = show_all(self.book)

        self.assertIn(
            "Contact name: John, phones: 1234567890, birthday: 07.11.1990",
            output,
        )
        self.assertIn("Contact name: Anna, phones: 0987654321", output)
        self.assertNotIn("Anna, phones: 0987654321, birthday", output)

    def test_birthday_commands(self):
        add_contact(["John", "1234567890"], self.book)

        self.assertEqual(show_birthday(["John"], self.book), "No birthday saved for John.")
        self.assertEqual(add_birthday(["John", "07.11.1990"], self.book), "Birthday added.")
        self.assertEqual(show_birthday(["John"], self.book), "07.11.1990")
        self.assertEqual(
            add_birthday(["John", "08.11.1990"], self.book),
            "Contact already has a birthday",
        )
        self.assertEqual(
            add_birthday(["John", "31.02.2025"], self.book),
            "Invalid date format. Use DD.MM.YYYY",
        )
        self.assertEqual(
            add_birthday(["John", "1990-11-07"], self.book),
            "Invalid date format. Use DD.MM.YYYY",
        )

    def test_birthdays_command_uses_address_book_result(self):
        add_contact(["John", "1234567890"], self.book)
        add_birthday(["John", "07.11.1990"], self.book)
        add_contact(["Anna", "0987654321"], self.book)

        with freeze_today(2026, 11, 4):
            self.assertEqual(birthdays(self.book), "John: 09.11.2026")

        with freeze_today(2026, 6, 1):
            self.assertEqual(birthdays(self.book), "No upcoming birthdays.")

    def test_missing_contacts_and_arguments(self):
        self.assertEqual(show_phone(["Nobody"], self.book), "Contact Nobody not found.")
        self.assertEqual(
            change_contact(["Nobody", "1234567890", "0987654321"], self.book),
            "Contact Nobody not found.",
        )
        self.assertEqual(
            add_birthday(["Nobody", "01.01.2000"], self.book),
            "Contact Nobody not found.",
        )
        self.assertEqual(show_birthday(["Nobody"], self.book), "Contact Nobody not found.")

        self.assertEqual(add_contact([], self.book), "Usage: add name phone")
        self.assertEqual(add_contact(["John"], self.book), "Usage: add name phone")
        self.assertEqual(
            change_contact(["John", "1234567890"], self.book),
            "Usage: change name old_phone new_phone",
        )
        self.assertEqual(show_phone([], self.book), "Usage: phone name")
        self.assertEqual(add_birthday(["John"], self.book), "Usage: add-birthday name DD.MM.YYYY")
        self.assertEqual(show_birthday([], self.book), "Usage: show-birthday name")

    def test_duplicate_phone_is_stored_again(self):
        add_contact(["John", "1234567890"], self.book)

        self.assertEqual(
            add_contact(["John", "1234567890"], self.book),
            "Phone added.",
        )
        self.assertEqual(
            show_phone(["John"], self.book),
            "1234567890; 1234567890",
        )

    def test_invalid_extra_phone_does_not_change_existing_contact(self):
        add_contact(["John", "1234567890"], self.book)

        self.assertEqual(
            add_contact(["John", "12345"], self.book),
            "Phone number must contain exactly 10 digits",
        )
        self.assertEqual(show_phone(["John"], self.book), "1234567890")

    def test_change_missing_phone_keeps_the_old_number(self):
        add_contact(["John", "1234567890"], self.book)

        self.assertEqual(
            change_contact(["John", "0000000000", "1111111111"], self.book),
            "Phone number not found",
        )
        self.assertEqual(show_phone(["John"], self.book), "1234567890")

    def test_excessive_arguments_are_rejected_without_changes(self):
        self.assertEqual(
            add_contact(["John", "1234567890", "0987654321"], self.book),
            "Usage: add name phone",
        )
        self.assertIsNone(self.book.find("John"))

        add_contact(["John", "1234567890"], self.book)
        self.assertEqual(
            change_contact(
                ["John", "1234567890", "1111111111", "extra"],
                self.book,
            ),
            "Usage: change name old_phone new_phone",
        )
        self.assertEqual(show_phone(["John"], self.book), "1234567890")
        self.assertEqual(
            show_phone(["John", "extra"], self.book),
            "Usage: phone name",
        )
        self.assertEqual(
            add_birthday(["John", "01.01.2000", "extra"], self.book),
            "Usage: add-birthday name DD.MM.YYYY",
        )
        self.assertIsNone(self.book.find("John").birthday)
        self.assertEqual(
            show_birthday(["John", "extra"], self.book),
            "Usage: show-birthday name",
        )

    def test_empty_book_has_no_upcoming_birthdays(self):
        self.assertEqual(show_all(self.book), "No contacts found.")
        self.assertEqual(birthdays(self.book), "No upcoming birthdays.")

    def test_parse_input_keeps_name_and_birthday_tokens(self):
        self.assertEqual(parse_input("  ADD John 1234567890  "), ("add", ["John", "1234567890"]))
        self.assertEqual(
            parse_input("add-birthday John 07.11.1990"),
            ("add-birthday", ["John", "07.11.1990"]),
        )
        self.assertEqual(parse_input("   "), ("", []))


class TestMainLoop(unittest.TestCase):
    def _run(self, commands):
        commands = iter(commands)
        printed = []

        def fake_input(_prompt):
            try:
                return next(commands)
            except StopIteration as error:
                raise AssertionError("Command loop did not exit.") from error

        with patch("builtins.input", fake_input):
            with patch("builtins.print", lambda *args: printed.append(" ".join(map(str, args)))):
                main()

        return printed

    def test_command_session(self):
        printed = self._run(
            [
                "hello",
                "add John 1234567890",
                "add John 0987654321",
                "change John 1234567890 1112223333",
                "phone John",
                "add-birthday John 07.11.1990",
                "show-birthday John",
                "all",
                "",
                "unknown",
                "close",
            ]
        )

        self.assertEqual(printed[0], "Welcome to the assistant bot!")
        self.assertIn("How can I help you?", printed)
        self.assertIn("Contact added.", printed)
        self.assertIn("Phone added.", printed)
        self.assertIn("Contact updated.", printed)
        self.assertIn("1112223333; 0987654321", printed)
        self.assertIn("Birthday added.", printed)
        self.assertIn("07.11.1990", printed)
        self.assertTrue(any("birthday: 07.11.1990" in line for line in printed))
        self.assertEqual(printed.count("Invalid command."), 2)
        self.assertEqual(printed[-1], "Good bye!")

    def test_exit_command(self):
        printed = self._run(["EXIT"])

        self.assertEqual(printed, ["Welcome to the assistant bot!", "Good bye!"])

    def test_close_and_invalid_command(self):
        printed = self._run(["birthday", "Close"])

        self.assertEqual(
            printed,
            [
                "Welcome to the assistant bot!",
                "Invalid command.",
                "Good bye!",
            ],
        )

    def test_excessive_add_arguments_do_not_create_a_contact(self):
        printed = self._run(
            [
                "add John 1234567890 extra",
                "phone John",
                "exit",
            ]
        )

        self.assertIn("Usage: add name phone", printed)
        self.assertIn("Contact John not found.", printed)
        self.assertEqual(printed[-1], "Good bye!")


if __name__ == "__main__":
    unittest.main()
