import sys
from collections import UserDict
from datetime import datetime, timedelta

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            return f"Error: {e}" if str(e) else "Error: Give me name and phone/birthday please."
        except KeyError:
            return "Error: Contact not found."
        except IndexError:
            return "Error: Enter user name."
    return inner

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        if not (len(value) == 10 and value.isdigit()):
            raise ValueError("Phone format must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
            
    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))

    def remove_phone(self, phone_number):
        for p in self.phones:
            if p.value == phone_number:
                self.phones.remove(p)
                break

    def edit_phone(self, old_phone, new_phone):
        for i, p in enumerate(self.phones):
            if p.value == old_phone:
                self.phones[i] = Phone(new_phone)
                return
        raise ValueError("Phone not found in the list.")

    def find_phone(self, phone_number):
        for p in self.phones:
            if p.value == phone_number:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones_str = ', '.join(p.value for p in self.phones) if self.phones else "No phones"
        bday_str = f" | 🎂 Birthday: {self.birthday}" if self.birthday else ""
        return f"👤 {self.name.value}: 📞 {phones_str}{bday_str}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        upcoming = []
        today = datetime.today().date()
        for record in self.data.values():
            if record.birthday:
                bday = record.birthday.value
                bday_this_year = bday.replace(year=today.year)
                
                if bday_this_year < today:
                    bday_this_year = bday_this_year.replace(year=today.year + 1)
                
                days_until = (bday_this_year - today).days
                if 0 <= days_until <= 7:
                    if bday_this_year.weekday() == 5:
                        bday_this_year += timedelta(days=2)
                    elif bday_this_year.weekday() == 6:
                        bday_this_year += timedelta(days=1)
                    upcoming.append({"name": record.name.value, "congratulation_date": bday_this_year.strftime("%d.%m.%Y")})
        return upcoming

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Give me name and phone please.")
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated successfully."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added successfully."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_contact(args, book: AddressBook):
    if len(args) < 3:
        raise ValueError("Give me name, old phone and new phone please.")
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.edit_phone(old_phone, new_phone)
    return "Contact phone updated successfully."

@input_error
def show_phone(args, book: AddressBook):
    if len(args) < 1:
        raise IndexError
    name, *_ = args
    record = book.find(name)
    if not record:
        raise KeyError
    return f"{name}'s phones: {', '.join(p.value for p in record.phones)}"

@input_error
def add_birthday(args, book: AddressBook):
    if len(args) < 2:
        raise ValueError("Give me name and birthday please.")
    name, birthday, *_ = args
    record = book.find(name)
    if not record:
        raise KeyError
    record.add_birthday(birthday)
    return "Birthday added successfully."

@input_error
def show_birthday(args, book: AddressBook):
    if len(args) < 1:
        raise IndexError
    name, *_ = args
    record = book.find(name)
    if not record:
        raise KeyError
    if not record.birthday:
        return f"No birthday set for {name}."
    return f"{name}'s birthday is {record.birthday}"

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No upcoming birthdays next week."
    return "Upcoming birthdays:\n" + "\n".join([f"🎉 {item['name']}: {item['congratulation_date']}" for item in upcoming])

@input_error
def show_all(args, book: AddressBook):
    if not book.data:
        return "No contacts saved yet."
    return "Address Book:\n" + "\n".join([str(record) for record in book.data.values()])

def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    
    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            continue
            
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(args, book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Error: Invalid command.")

if __name__ == "__main__":
    main()