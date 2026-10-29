import sys, datetime
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

out = sys.argv[1]
wb = Workbook()
ws = wb.active
ws.title = "thai"
ws.column_dimensions["A"].width = 46
ws.column_dimensions["B"].width = 46
ws.column_dimensions["C"].width = 46

d = datetime.datetime(2026, 10, 28)

rows = [
    # label, value/formula, number_format
    ("date Gregorian d mmmm yyyy", d, "d mmmm yyyy"),
    ("date th-TH Buddhist [$-107041E]", d, "[$-107041E]d mmmm yyyy"),
    ("date Thai digits [$-D07041E]", d, "[$-D07041E]d mmmm yyyy"),
    ("date bbbb", d, "d mmmm bbbb"),
    ("date short th [$-th-TH]", d, "[$-th-TH]d/m/yyyy"),
    ("TEXT th Buddhist", '=TEXT(DATE(2026,10,28),"[$-107041E]d mmmm yyyy")', "General"),
    ("TEXT thai digits", '=TEXT(2569,"[$-D000000]0")', "General"),
    ("BAHTTEXT 1234.5", "=BAHTTEXT(1234.5)", "General"),
    ("BAHTTEXT 21", "=BAHTTEXT(21)", "General"),
    ("THAIYEAR(date)", "=THAIYEAR(DATE(2026,10,28))", "General"),
    ("THAIDIGIT(2569)", '=THAIDIGIT("2569")', "General"),
    ("THAIMONTHOFYEAR(10)", "=THAIMONTHOFYEAR(10)", "General"),
    ("THAIDAYOFWEEK(1)", "=THAIDAYOFWEEK(1)", "General"),
    ("THAISTRINGLENGTH", '=THAISTRINGLENGTH("สวัสดี")', "General"),
    ("ISTHAIDIGIT", '=ISTHAIDIGIT("๒")', "General"),
    ("ROUNDBAHTUP(10.13)", "=ROUNDBAHTUP(10.13)", "General"),
    ("ROUNDBAHTDOWN(10.13)", "=ROUNDBAHTDOWN(10.13)", "General"),
    ("THAINUMSTRING(125)", "=THAINUMSTRING(125)", "General"),
    ("LEN(Thai with marks)", '=LEN("สวัสดี")', "General"),
    ("UPPER/LOWER keep Thai", '=UPPER("ก abc")', "General"),
    ("LEFT 3 of Thai", '=LEFT("สวัสดีครับ",3)', "General"),
    ("COMPARE กา<เก (Thai order: TRUE)", '="กา"<"เก"', "General"),
    ("COMPARE เก<ขา (Thai order: FALSE)", '="เก"<"ขา"', "General"),
    ("COMPARE ไข<กา (Thai order: FALSE)", '="ไข"<"กา"', "General"),
]
ws["A1"] = "case"
ws["B1"] = "GridCraft result"
for i, (label, v, fmt) in enumerate(rows, start=2):
    ws[f"A{i}"] = label
    ws[f"B{i}"] = v
    ws[f"B{i}"].number_format = fmt

# sort test column
ws["C1"] = "unsorted"
words = ["เก", "กา", "ไข", "ขา", "โค", "คา", "แต", "ตา", "ใจ", "จา"]
for i, w in enumerate(words, start=2):
    ws[f"C{i}"] = w

wb.save(out)
print("saved", out)
