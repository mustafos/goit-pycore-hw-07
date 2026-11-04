from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Name cannot be empty")

        super().__init__(value.strip())


class Phone(Field):
    def __init__(self, value):
        if not isinstance(value, str) or not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits")

        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            birthday = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

        super().__init__(birthday)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def find_phone(self, phone):
        for item in self.phones:
            if item.value == phone:
                return item

        return None

    def remove_phone(self, phone):
        found_phone = self.find_phone(phone)

        if found_phone is None:
            raise ValueError("Phone number not found")

        self.phones.remove(found_phone)

    def edit_phone(self, old_phone, new_phone):
        found_phone = self.find_phone(old_phone)

        if found_phone is None:
            raise ValueError("Phone number not found")

        validated_phone = Phone(new_phone)
        index = self.phones.index(found_phone)
        self.phones[index] = validated_phone

    def add_birthday(self, birthday):
        validated_birthday = Birthday(birthday)

        if self.birthday is not None:
            raise ValueError("Contact already has a birthday")

        self.birthday = validated_birthday

    def __str__(self):
        phones = "; ".join(phone.value for phone in self.phones)
        contact = f"Contact name: {self.name.value}, phones: {phones}"

        if self.birthday is not None:
            contact += f", birthday: {self.birthday}"

        return contact


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name not in self.data:
            raise ValueError("Contact not found")

        del self.data[name]

    def get_upcoming_birthdays(self):
        """Return birthdays in the next seven days.

        Weekend greetings move to the following Monday.
        """
        today = datetime.today().date()
        window_end = today + timedelta(days=6)
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = record.birthday.value.date()

            try:
                birthday_this_year = birthday.replace(year=today.year)
            except ValueError:
                # Treat February 29 as February 28 in non-leap years.
                birthday_this_year = birthday.replace(year=today.year, day=28)

            if birthday_this_year < today:
                try:
                    birthday_this_year = birthday_this_year.replace(
                        year=today.year + 1
                    )
                except ValueError:
                    birthday_this_year = birthday_this_year.replace(
                        year=today.year + 1, day=28
                    )

            if not today <= birthday_this_year <= window_end:
                continue

            congratulation_date = birthday_this_year

            if congratulation_date.weekday() == 5:
                congratulation_date += timedelta(days=2)
            elif congratulation_date.weekday() == 6:
                congratulation_date += timedelta(days=1)

            upcoming_birthdays.append(
                {
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime(
                        "%d.%m.%Y"
                    ),
                }
            )

        return upcoming_birthdays
