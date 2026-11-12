import csv
import json


class InvalidRecordError(Exception):
    pass


class DailyRecord:
    def __init__(self, date, sleep, fitness, study, coding, class_time, 
                 classes_attended, other, feeling, satisfaction, energy, notes=""):
        self.date = date
        self.sleep = sleep
        self.fitness = fitness
        self.study = study
        self.coding = coding
        self.class_time = class_time
        self.classes_attended = classes_attended
        self.other = other
        self.feeling = feeling
        self.satisfaction = satisfaction
        self.energy = energy
        self.notes = notes

    def total_tracked(self):
        return (self.sleep + self.fitness + self.study + 
                self.coding + self.class_time + self.other)

    def free_time(self):
        return 1440 - self.total_tracked()

    def to_dict(self):
        return {
            "date": self.date,
            "sleep_minutes": self.sleep,
            "fitness_minutes": self.fitness,
            "study_minutes": self.study,
            "coding_minutes": self.coding,
            "class_minutes": self.class_time,
            "classes_attended": self.classes_attended,
            "other_minutes": self.other,
            "total_tracked_minutes": self.total_tracked(),
            "free_minutes": self.free_time(),
            "feeling": self.feeling,
            "satisfaction": self.satisfaction,
            "energy": self.energy,
            "notes": self.notes
        }

    def __str__(self):
        return (f"Date: {self.date} | Sleep: {self.sleep}m | Study: {self.study}m | "
                f"Coding: {self.coding}m | Mood: {self.feeling} | Sat: {self.satisfaction}")


def load_data(filepath):
    records = []
    skipped = 0
    total_days = 0

    with open(filepath, mode="r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)

        for row in reader:
            if row and row[0].strip().lower() == "date":
                break

        row_num = 5
        for row in reader:
            row_num += 1
            if not row or not any(row):
                continue

            total_days += 1

            try:
                if len(row) < 13 or row[0].strip() == "":
                    raise InvalidRecordError(f"Row {row_num}: Incomplete row.")

                date_val = row[0].strip()
                numeric_vals = [row[1], row[2], row[3], row[4], row[5], row[6], row[7]]

                if any(v.strip() == "" for v in numeric_vals):
                    raise InvalidRecordError(f"Row {row_num} ({date_val}): Missing minutes.")

                sleep = int(row[1])
                fitness = int(row[2])
                study = int(row[3])
                coding = int(row[4])
                class_time = int(row[5])
                classes_att = int(row[6])
                other = int(row[7])

                if any(x < 0 for x in [sleep, fitness, study, coding, class_time, classes_att, other]):
                    raise InvalidRecordError(f"Row {row_num} ({date_val}): Negative values found.")

                feeling = row[10].strip() if len(row) > 10 and row[10].strip() else "Neutral"
                satisfaction = row[11].strip() if len(row) > 11 and row[11].strip() else "Neutral"
                energy = row[12].strip() if len(row) > 12 and row[12].strip() else "Medium"
                notes = row[13].strip() if len(row) > 13 else ""

                rec = DailyRecord(date_val, sleep, fitness, study, coding,
                                  class_time, classes_att, other,
                                  feeling, satisfaction, energy, notes)
                records.append(rec)

            except InvalidRecordError as e:
                print(f"[Skipped Row] {e}")
                skipped += 1
            except ValueError as e:
                print(f"[Parse Error] Row {row_num}: {e}")
                skipped += 1

    print(f"Loaded: {len(records)} valid records. Skipped: {skipped} invalid rows.")
    return records, total_days


def export_json(records, filepath):
    data = [r.to_dict() for r in records]
    with open(filepath, mode="w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"JSON saved to: {filepath}")


def show_stats(records, total_days):
    if not records:
        print("No valid records found.")
        return

    n = len(records)
    avg_sleep = sum(r.sleep for r in records) / n
    avg_fitness = sum(r.fitness for r in records) / n
    avg_study = sum(r.study for r in records) / n
    avg_coding = sum(r.coding for r in records) / n
    avg_class = sum(r.class_time for r in records) / n
    avg_other = sum(r.other for r in records) / n
    avg_tracked = sum(r.total_tracked() for r in records) / n
    avg_free = sum(r.free_time() for r in records) / n

    tpi = avg_coding
    aai = avg_study + avg_class
    phai = avg_fitness
    sri = avg_sleep
    tui = avg_tracked
    abi = avg_free
    dci = (n / total_days) * 100 if total_days > 0 else 0

    all_feelings = [r.feeling for r in records]
    feeling_counts = {f: all_feelings.count(f) for f in set(all_feelings)}

    all_sats = [r.satisfaction for r in records]
    sat_counts = {s: all_sats.count(s) for s in set(all_sats)}

    print("\n" + "=" * 45)
    print("           ACTIVITY SUMMARY")
    print("=" * 45)
    print(f"Total Target Days      : {total_days}")
    print(f"Valid Days Processed   : {n}")
    print(f"Data Continuity (DCI)  : {dci:.2f}%")
    print("-" * 45)
    print(f"Sleep / day (SRI)      : {avg_sleep:.2f} min")
    print(f"Fitness / day (PhAI)   : {avg_fitness:.2f} min")
    print(f"Study / day            : {avg_study:.2f} min")
    print(f"Coding / day (TPI)     : {avg_coding:.2f} min")
    print(f"Class / day            : {avg_class:.2f} min")
    print(f"Academic Total (AAI)   : {aai:.2f} min")
    print(f"Other / day            : {avg_other:.2f} min")
    print(f"Tracked / day (TUI)    : {avg_tracked:.2f} min")
    print(f"Free Time / day (ABI)  : {avg_free:.2f} min")
    print("-" * 45)
    print("Feelings Breakdown     :", feeling_counts)
    print("Satisfaction Breakdown :", sat_counts)
    print("=" * 45)


def menu(records, total_days):
    while True:
        print("\n--- MENU ---")
        print("1. View Statistics & Indices")
        print("2. Search by Date")
        print("3. Filter by Satisfaction")
        print("4. Filter by Feeling")
        print("5. Save JSON")
        print("6. Exit")

        choice = input("Enter choice (1-6): ").strip()

        if choice == "1":
            show_stats(records, total_days)
        elif choice == "2":
            q_date = input("Enter date (e.g. 10/08/2026): ").strip()
            found = [r for r in records if q_date in r.date]
            if found:
                for r in found:
                    print(r)
            else:
                print("No record found.")
        elif choice == "3":
            sat_val = input("Enter Satisfaction level: ").strip().lower()
            matches = [r for r in records if r.satisfaction.lower() == sat_val]
            print(f"Found {len(matches)} matching days:")
            for r in matches:
                print(f"  {r.date} | Sleep: {r.sleep}m | Study: {r.study}m | Sat: {r.satisfaction}")
        elif choice == "4":
            feel_val = input("Enter Feeling: ").strip().lower()
            matches = [r for r in records if r.feeling.lower() == feel_val]
            print(f"Found {len(matches)} matching days:")
            for r in matches:
                print(f"  {r.date} | Mood: {r.feeling} | Energy: {r.energy}")
        elif choice == "5":
            export_json(records, "12604028_cleaned.json")
        elif choice == "6":
            print("Done.")
            break
        else:
            print("Invalid input. Choose 1 to 6.")


if __name__ == "__main__":
    csv_file = "12604028.csv"
    data, total_days = load_data(csv_file)

    if data:
        export_json(data, "12604028_cleaned.json")
        menu(data, total_days)