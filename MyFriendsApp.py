# MyFriendsApp.py
import csv
from datetime import datetime
from typing import List, Tuple, Optional
from Friend import Person
from Birthday import Birthday

CSV_FILE: str = "friends_database.csv"
CSV_FIELDS: List[str] = [
    "first_name", "last_name", "month", "day",
    "email_address", "nickname", "street_address", "city", "state", "zip", "phone"
]

# ---------- small helpers that work with Person/Birthday ----------
def full_name(p: Person) -> str:
    return f"{p.first_name} {p.last_name}"

def get_birthday_tuple(p: Person) -> Optional[Tuple[int, int]]:
    b = getattr(p, "_birthday", None) or getattr(p, "birthday", None)
    if not b:
        return None
    return (b.get_month(), b.get_day())

def set_birthday(p: Person, m: int, d: int) -> None:
    p.set_birthday(m, d)

def day_in_year(month: int, day: int) -> int:
    total = 0
    for i in range(month - 1):
        total += Birthday.days_in_month[i]
    return total + day

def days_until_bday(p: Person) -> int:
    bd = get_birthday_tuple(p)
    if not bd:
        return 10000
    m, d = bd
    today = datetime.today()
    tdoy = day_in_year(today.month, today.day)
    bdoy = day_in_year(m, d)
    if bdoy >= tdoy:
        return bdoy - tdoy
    return 365 - (tdoy - bdoy)

def bold(s: str) -> str:
    return "\033[1m" + s + "\033[0m"

# ---------- persistence ----------
def load_people(path: str = CSV_FILE) -> List[Person]:
    people: List[Person] = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            r = csv.DictReader(f)
            for row in r:
                p = Person((row.get("first_name") or "").strip(),
                           (row.get("last_name") or "").strip())

                m = (row.get("month") or "").strip()
                d = (row.get("day") or "").strip()
                if m.isdigit() and d.isdigit():
                    set_birthday(p, int(m), int(d))

                p.email_address  = (row.get("email_address")  or "") or None
                p.nickname       = (row.get("nickname")       or "") or None
                p.street_address = (row.get("street_address") or "") or None
                p.city           = (row.get("city")           or "") or None
                p.state          = (row.get("state")          or "") or None
                p.zip            = (row.get("zip")            or "") or None
                p.phone          = (row.get("phone")          or "") or None

                people.append(p)
    except FileNotFoundError:
        pass
    return people

def save_people(people: List[Person], path: str = CSV_FILE) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writeheader()
        for p in people:
            m, d = "", ""
            bd = get_birthday_tuple(p)
            if bd:
                m, d = bd
            w.writerow({
                "first_name": p.first_name,
                "last_name":  p.last_name,
                "month":      m,
                "day":        d,
                "email_address":  p.email_address or "",
                "nickname":       p.nickname or "",
                "street_address": p.street_address or "",
                "city":           p.city or "",
                "state":          p.state or "",
                "zip":            p.zip or "",
                "phone":          p.phone or "",
            })

# ---------- menus ----------
def main_menu() -> None:
    print()
    print(bold("Friends Manager"))
    print("1 - Create new friend record")
    print("2 - Search for a friend")
    print("3 - Run reports")
    print("4 - Exit")

def reports_menu() -> None:
    print()
    print(bold("Reports"))
    print("3.1 - List of friends alphabetically")
    print("3.2 - List of friends by upcoming birthdays")
    print("3.3 - Mailing labels for friends")
    print("3.9 - Return to the previous menu")

# ---------- actions ----------
def create_one(people: List[Person]) -> None:
    print()
    print(bold("Create a new friend"))
    fn = input("First name: ").strip()
    ln = input("Last  name: ").strip()
    p = Person(fn, ln)

    m = input("Birth month (1-12, blank to skip): ").strip()
    d = input("Birth day   (1-31, blank to skip): ").strip()
    if m.isdigit() and d.isdigit():
        set_birthday(p, int(m), int(d))

    p.email_address  = input("Email (optional): ").strip() or None
    p.nickname       = input("Nickname (optional): ").strip() or None
    p.street_address = input("Street (optional): ").strip() or None
    p.city           = input("City (optional): ").strip() or None
    p.state          = input("State (optional): ").strip() or None
    p.zip            = input("Zip (optional): ").strip() or None
    p.phone          = input("Phone (optional): ").strip() or None

    people.append(p)
    print("Added.")

def load_batch(people: List[Person]) -> None:
    path = input("CSV file to load (Enter to cancel): ").strip()
    if not path:
        return
    batch = load_people(path)
    people.extend(batch)
    print(f"Loaded {len(batch)} record(s).")

def create_menu(people: List[Person]) -> None:
    pick = input("1) Create one   2) Load from CSV  (Enter cancels): ").strip()
    if pick == "1":
        create_one(people)
    elif pick == "2":
        load_batch(people)

def find_matches(people: List[Person], q: str) -> List[Tuple[int, Person]]:
    ql = q.lower()
    out: List[Tuple[int, Person]] = []
    for i, p in enumerate(people):
        full = full_name(p).lower()
        if ql in p.first_name.lower() or ql in p.last_name.lower() or ql in full:
            out.append((i, p))
    return out

def edit_friend(p: Person) -> None:
    print()
    print(bold(f"Editing {full_name(p)} — leave blank to keep current"))

    fn = input(f"First name [{p.first_name}]: ").strip()
    ln = input(f"Last  name [{p.last_name}]: ").strip()
    if fn:
        p.first_name = fn
    if ln:
        p.last_name = ln

    m = input("Birth month (blank to skip): ").strip()
    d = input("Birth day   (blank to skip): ").strip()
    if m.isdigit() and d.isdigit():
        set_birthday(p, int(m), int(d))

    def upd(curr: Optional[str], label: str) -> Optional[str]:
        val = input(f"{label} [{curr or ''}]: ").strip()
        if val:
            return val
        return curr

    p.email_address  = upd(p.email_address,  "Email")
    p.nickname       = upd(p.nickname,       "Nickname")
    p.street_address = upd(p.street_address, "Street")
    p.city           = upd(p.city,           "City")
    p.state          = upd(p.state,          "State")
    p.zip            = upd(p.zip,            "Zip")
    p.phone          = upd(p.phone,          "Phone")
    print("Updated.")

def search_menu(people: List[Person]) -> None:
    print()
    print(bold("Search"))
    q = input("Search by name: ").strip()
    matches = find_matches(people, q)
    if not matches:
        print("No matches.")
        return

    for i, (_, p) in enumerate(matches, start=1):
        bd = get_birthday_tuple(p)
        bd_s = f"[ {bd[0]}/{bd[1]} ]" if bd else "[No birthday]"
        city = p.city or ""
        print(f"{i}) {full_name(p):25}  {bd_s:12}  {city}")

    pick = input("Pick a number to edit/delete (Enter cancels): ").strip()
    if not pick.isdigit():
        return
    sel = int(pick) - 1
    if sel < 0 or sel >= len(matches):
        print("Invalid choice.")
        return

    idx, person = matches[sel]
    act = input("E)dit  D)elete  (anything else cancels): ").strip().lower()
    if act == "e":
        edit_friend(person)
    elif act == "d":
        confirm = input("Type DELETE to confirm: ").strip()
        if confirm == "DELETE":
            del people[idx]
            print("Deleted.")
        else:
            print("Cancelled.")

# ---------- reports ----------
def _alpha_key(p: Person) -> Tuple[str, str]:
    return (p.last_name.lower(), p.first_name.lower())

def report_alpha(people: List[Person]) -> None:
    print()
    print(bold("Alphabetical (Last, First)"))
    for p in sorted(people, key=_alpha_key):
        print(f"{p.last_name}, {p.first_name}")

def report_birthdays(people: List[Person]) -> None:
    print()
    print(bold("Upcoming birthdays"))
    with_bd: List[Person] = []
    for p in people:
        if get_birthday_tuple(p):
            with_bd.append(p)

    if not with_bd:
        print("(no birthdays on file)")
        return

    # simple selection sort by days-until (beginner-friendly)
    sorted_people = with_bd[:]
    for i in range(len(sorted_people)):
        best = i
        for j in range(i + 1, len(sorted_people)):
            if days_until_bday(sorted_people[j]) < days_until_bday(sorted_people[best]):
                best = j
        if best != i:
            sorted_people[i], sorted_people[best] = sorted_people[best], sorted_people[i]

    for p in sorted_people:
        bd = get_birthday_tuple(p)
        print(f"{full_name(p):25} in {days_until_bday(p):3} days  [{bd[0]}/{bd[1]}]")

def report_labels(people: List[Person]) -> None:
    print()
    print(bold("Mailing labels"))
    any_printed = False
    for p in people:
        if p.street_address and p.city and p.state and p.zip:
            any_printed = True
            print(full_name(p))
            print(p.street_address)
            print(f"{p.city}, {p.state} {p.zip}")
            print("-" * 30)
    if not any_printed:
        print("(no complete addresses on file)")

def reports_controller(people: List[Person]) -> None:
    while True:
        reports_menu()
        sel = input("Select: ").strip()
        if sel == "3.1":
            report_alpha(people)
        elif sel == "3.2":
            report_birthdays(people)
        elif sel == "3.3":
            report_labels(people)
        elif sel == "3.9":
            break
        else:
            print("Invalid selection.")

# ---------- app entry ----------
def main() -> None:
    people = load_people()
    while True:
        main_menu()
        sel = input("Select: ").strip()
        if sel == "1":
            create_menu(people)
        elif sel == "2":
            search_menu(people)
        elif sel == "3":
            reports_controller(people)
        elif sel == "4":
            save_people(people)
            print("Saved. Goodbye!")
            break
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    main()
