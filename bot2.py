import json
from datetime import datetime, timedelta
import os

class Field:
    pass

class Name(Field):
    def __init__(self, value):
        self.value = value

class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone_number(value):
            raise ValueError("Invalid phone number format. Use format: XXXXXXXXXX")
        self.value = value

    def validate_phone_number(self, number):
        return len(number) == 10 and number.isdigit()

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

class AddressBook:
    def __init__(self):
        self.contacts = []

    def add_contact(self, name, phones=None, birthday=None):
        record = Record(name)
        if phones:
            for phone in phones:
                record.add_phone(phone)
        if birthday:
            record.add_birthday(birthday)
        self.contacts.append(record)

    def find_contact(self, name):
        for contact in self.contacts:
            if contact.name.value.lower() == name.lower():
                return contact
        return None

    def get_upcoming_birthdays(self):
        today = datetime.now().date()
        upcoming_birthdays = []

        for contact in self.contacts:
            if contact.birthday:
                birthday_date = contact.birthday.value.date()
                next_birthday = datetime(today.year, birthday_date.month, birthday_date.day).date()

                if next_birthday < today:
                    next_birthday = datetime(today.year + 1, birthday_date.month, birthday_date.day).date()

                days_until_birthday = (next_birthday - today).days

                if 0 <= days_until_birthday <= 7:
                    if next_birthday.weekday() >= 5:
                        days_until_birthday += (7 - next_birthday.weekday())
                        next_birthday += timedelta(days=(7 - next_birthday.weekday()))

                    congratulation_date = next_birthday.strftime("%Y.%m.%d")

                    upcoming_birthdays.append({"name": contact.name.value, "congratulation_date": congratulation_date})

        return upcoming_birthdays


def load_contacts():
    try:
        with open("/Users/oksanaluklan/goit-pycore-hw-07/contacts.json", "r") as file:
            contacts_data = json.load(file)
            address_book = AddressBook()
            for contact_data in contacts_data:
                record = Record(contact_data["name"])
                for phone in contact_data["phones"]:
                    record.add_phone(phone)
                if contact_data["birthday"]:
                    record.add_birthday(contact_data["birthday"])
                address_book.add_contact(name=record.name.value, phones=[phone.value for phone in record.phones], birthday=record.birthday.value.strftime("%d.%m.%Y") if record.birthday else None)
            return address_book
    except FileNotFoundError:
        return AddressBook()

def save_contacts(contacts):
    directory = "/Users/oksanaluklan/goit-pycore-hw-07/"
    file_path = os.path.join(directory, "contacts.json")
    serialized_contacts = []

    for contact in contacts:
        serialized_contact = {
            "name": contact.name.value,
            "phones": [phone.value for phone in contact.phones],
            "birthday": contact.birthday.value.strftime("%d.%m.%Y") if contact.birthday else None
        }
        serialized_contacts.append(serialized_contact)

    try:
        if not os.path.exists(directory):
            os.makedirs(directory)

        print("File path:", file_path)  
        with open(file_path, "w") as file:
            json.dump(serialized_contacts, file)
        print("Контакти успішно збережені у файлі:", file_path)
    except Exception as e:
        print("Помилка збереження контактів у файл:", e)

def save_to_file(book, filename):
    file_path = os.path.abspath(filename)
    print("Saving address book to file:", file_path)
    try:
        with open(file_path, 'w') as f:
            for contact in book.contacts:
                f.write("Name: {}\n".format(contact.name.value))
                for phone in contact.phones:
                    f.write("Phone: {}\n".format(phone.value))
                if contact.birthday:
                    f.write("Birthday: {}\n".format(contact.birthday.value.strftime("%d.%m.%Y")))
                f.write("\n")
        print("Address book saved to file:", filename)
    except Exception as e:
        print("Error saving address book to file:", e)

def read_from_file(filename):
    book = AddressBook()
    try:
        with open(filename, 'r') as f:
            record = None
            for line in f:
                line = line.strip()
                if line.startswith("Name:"):
                    name = line.split(": ")[1]
                    record = Record(name)
                    book.add_contact(record)
                elif line.startswith("Phone:"):
                    phone = line.split(": ")[1]
                    record.add_phone(phone)
                elif line.startswith("Birthday:"):
                    birthday = line.split(": ")[1]
                    record.add_birthday(birthday)
        print("Address book loaded from file:", filename)
    except Exception as e:
        print("Error loading address book from file:", e)
    return book

def parse_input(user_input):
    return user_input.split()

def input_error(func):
    def wrapper(args, book):
        try:
            return func(args, book)
        except IndexError:
            return "Missing arguments"
        except ValueError as e:
            return str(e)
    return wrapper

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    contact = book.find_contact(name)
    message = "Contact updated."
    if contact is None:
        contact = Record(name)
        book.add_contact(name, phones=[phone])
        message = "Contact added."
    else:
        contact.add_phone(phone)
    save_contacts(book.contacts)  
    return message

@input_error
def change_phone(args, book):
    name, old_phone, new_phone = args
    contact = book.find_contact(name)
    if contact:
        contact.phones.remove(Phone(old_phone))
        contact.add_phone(new_phone)
        return "Phone number changed for {}".format(name)
    else:
        return "Contact {} not found".format(name)

@input_error
def show_phones(args, book):
    name = args[0]
    contact = book.find_contact(name)
    if contact:
        return "Phone numbers for {}: {}".format(name, ", ".join([phone.value for phone in contact.phones]))
    else:
        return "Contact {} not found".format(name)

def show_all_contacts(book):
    if book.contacts:
        return "\n".join(["Name: {}, Phones: {}".format(contact.name.value, ", ".join([phone.value for phone in contact.phones])) for contact in book.contacts])
    else:
        return "No contacts in the address book"

@input_error
def add_birthday(args, book):
    name, birthday = args
    contact = book.find_contact(name)
    if contact:
        contact.add_birthday(birthday)
        return "Birthday added for {}".format(name)
    else:
        return "Contact {} not found".format(name)

@input_error
def show_birthday(args, book):
    name = args[0]
    contact = book.find_contact(name)
    if contact and contact.birthday:
        return "{}'s birthday: {}".format(name, contact.birthday.value.strftime("%d.%m.%Y"))
    elif contact:
        return "{}'s birthday not found".format(name)
    else:
        return "Contact {} not found".format(name)

@input_error
def birthdays(args, book):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "Upcoming birthdays: {}".format(", ".join([b["name"] for b in upcoming_birthdays]))
    else:
        return "No upcoming birthdays"

if __name__ == "__main__":
    book = load_contacts()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_phone(args, book))

        elif command == "phone":
            print(show_phones(args, book))

        elif command == "all":
            print(show_all_contacts(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")

    save_contacts(book.contacts)


    