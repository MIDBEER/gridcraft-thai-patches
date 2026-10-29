import sys
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment

out = sys.argv[1]
wb = Workbook()
ws = wb.active
ws.title = "wrap"
ws.column_dimensions["A"].width = 12
ws.column_dimensions["B"].width = 24
ws.column_dimensions["C"].width = 24

ws["A1"] = "case"
ws["B1"] = "wrap on (Tahoma 12)"
ws["C1"] = "shrink/no wrap"

texts = [
    ("no spaces", "ขอเชิญทุกท่านร่วมกิจกรรมวันสงกรานต์ประจำปีที่สวนสาธารณะเทศบาลนครในช่วงเช้า"),
    ("with spaces", "ขอเชิญ ทุกท่าน ร่วมกิจกรรม วันสงกรานต์ ประจำปี ที่ สวนสาธารณะ เทศบาลนคร 2569"),
    ("tone marks", "ค่าบริการรายเดือนห้อง ๑๐๑ ชำระภายในวันที่ ๕ ยอดรวม ๑,๒๓๔ บาท ก่อนเที่ยง"),
]
for i, (label, t) in enumerate(texts, start=2):
    ws.row_dimensions[i].height = 78
    ws[f"A{i}"] = label
    ws[f"B{i}"] = t
    ws[f"B{i}"].font = Font(name="Tahoma", size=12)
    ws[f"B{i}"].alignment = Alignment(wrap_text=True, vertical="top")
    ws[f"C{i}"] = t
    ws[f"C{i}"].font = Font(name="Tahoma", size=12)

wb.save(out)
print("saved", out)
