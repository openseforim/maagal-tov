"""Dates for the bracketed civil dates in the English (diaspora readings, as in the Ḥida's travels). Needs pyluach.
  py -3.13 -I scripts/hebdate.py 5538 10 4          Hebrew date (year, month Nisan=1 ... Tishrei=7 ... Adar II=13, day)
                                                    -> civil date, weekday, the reading of that week
  py -3.13 -I scripts/hebdate.py week 5538 Vaera    the week (Sunday to Sabbath) whose Sabbath reads that portion
  py -3.13 -I scripts/hebdate.py greg 1778 1 3      civil date -> Hebrew date and reading
Weekday numbers in the text: יום א' = Sunday ... יום ו' = Friday, שבת = Sabbath. A day "of the week of X" (מס' X)
is the Sunday-to-Friday before the Sabbath that reads X; the evening before (ליל) is the previous civil day."""
import sys

from pyluach import dates, parshios

sys.stdout.reconfigure(encoding="utf-8")
DAYS = ["", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Sabbath"]


def show(h):
    g = h.to_greg()
    sab = h + (7 - h.weekday())
    sg = sab.to_greg()
    print(f"{h.year}-{h.month:02d}-{h.day:02d} ({h.month_name()} {h.day}) = {g.year}-{g.month:02d}-{g.day:02d}, "
          f"{DAYS[h.weekday()]}; Sabbath of that week: {sg.year}-{sg.month:02d}-{sg.day:02d} reads "
          f"{parshios.getparsha_string(sab, israel=False)}")


a = sys.argv[1:]
if a[0] == "week":
    year, name = int(a[1]), a[2].lower()
    h = dates.HebrewDate(year - 1, 7, 1)
    end = dates.HebrewDate(year + 1, 7, 1)
    while h < end:
        if h.weekday() == 7:
            p = parshios.getparsha_string(h, israel=False)
            if p and name.replace("'", "") in p.lower().replace("'", ""):
                for k in range(-6, 1):
                    show(h + k)
                print()
        h += 1
elif a[0] == "greg":
    show(dates.GregorianDate(int(a[1]), int(a[2]), int(a[3])).to_heb())
else:
    show(dates.HebrewDate(int(a[0]), int(a[1]), int(a[2])))
