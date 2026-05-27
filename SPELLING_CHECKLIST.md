# SPELLING_CHECKLIST — Tiếng Việt cho DS108 Electrimight

> File này giúp AI kiểm tra chính tả tiếng Việt trước khi ghi vào `.tex`.
> AI PHẢI đọc file này trước mỗi lần viết/sửa nội dung tiếng Việt.

## Nguyên tắc VÀNG

**Tiếng Việt KHÔNG CÓ từ nào có 2 chữ giống nhau ở cuối.**

Ví dụ lỗi AI hay mắc:
- `ngườii` ❌ (6 ký tự: n,g,ư,ờ,i,i) → `người` ✓ (5 ký tự: n,g,ư,ờ,i)
- `thờii` ❌ (5 ký tự: t,h,ờ,i,i) → `thời` ✓ (4 ký tự: t,h,ờ,i)
- `rờii` ❌ (4 ký tự: r,ờ,i,i) → `rời` ✓ (3 ký tự: r,ờ,i)
- `củaa` ❌ (5 ký tự: c,ủ,a,a) → `của` ✓ (4 ký tự: c,ủ,a)

**Quy tắc kiểm tra nhanh:** Nếu bạn thấy từ có 2 chữ `i` liên tiếp ở cuối (`...ii`), đó là LỖI.

## Các cặp từ hay bị nhầm lẫn

| Sai | Đúng | Unicode đúng | Ghi chú |
|-----|------|--------------|---------|
| `thởi` / `thỏi` | **thời** | `ờ` U+1EDD + 1×`i` | `thời gian`, `thời tiết`. `thởi` (U+1EDF, hỏi) là SAI. |
| `rởi` / `rỏi` | **rời** | `ờ` U+1EDD + 1×`i` | `rời rạc`. `rởi` (U+1EDF) là SAI. |
| `bở` / `bởi` | **bỏ** | `ỏ` U+1ECF | `loại bỏ`, `bỏ qua`. |
| `đồng thởi` | **đồng thời** | `ờ` U+1EDD + 1×`i` | `thởi` (hoi) là SAI. |
| `hởng hóc` | **hỏng hóc** | `ỏ` U+1ECF | |
| `mỏ rộng` | **mở rộng** | `ở` U+1EDF | |
| `trỏ nên` | **trở nên** | `ở` U+1EDF | |
| `thuần trỏ` | **thuần trở** | `ở` U+1EDF | |
| `bở qua` | **bỏ qua** | `ỏ` U+1ECF | |
| `ngườii` | **người** | `ờ` U+1EDD + 1×`i` | 2 chữ `i` ở cuối là SAI. |

## Quy tắc nhận biết nhanh

- `thời` (time/weather/epoch): `ờ` U+1EDD (grave), chỉ **1 chữ `i`** ở cuối.
- `rời` (discrete/sparse): `ờ` U+1EDD (grave), chỉ **1 chữ `i`** ở cuối.
- `người` (person): `ờ` U+1EDD (grave), chỉ **1 chữ `i`** ở cuối.
- `bỏ` (remove): `ỏ` U+1ECF (hoi trên `o`).
- `mở` (open/expand): `ở` U+1EDF (hoi trên `o`).
- `trở` (become): `ở` U+1EDF.
- `bởi` (because/by): `ở` U+1EDF.
- `hỏng` (broken): `ỏ` U+1ECF.

## Kiểm tra tự động (Python)

```python
import re

VIOLATIONS = {
    r"th\u1edf[ \n]gian": "th\u1edd gian",
    r"th\u1ecf[ \n]gian": "th\u1edd gian",
    r"r\u1edf[ \n]r\u1ea1c": "r\u1edd r\u1ea1c",
    r"loại b\u1edf": "loại b\u1ecf",
    r"đồng th\u1edf": "đồng th\u1edd",
    r"h\u1edfng h\u00f3c": "h\u1ecfng h\u00f3c",
    r"m\u1ecf r\u1ed9ng": "m\u1edf r\u1ed9ng",
}

def check_tex(path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    errors = []
    for bad_pat, good in VIOLATIONS.items():
        if re.search(bad_pat, text):
            errors.append(f"Found {bad_pat} -> should be {good}")
    for match in re.finditer(r"(\w)\1{1,}\b", text):
        word = match.group(0)
        if len(word) >= 2 and word[-1] == word[-2] and word[-1] in "iIaAeEoOuUyY":
            errors.append(f"Possible double-ending letter: {word}")
    return errors
```

## Khi nghi ngờ

Nếu không chắc chắn về một từ tiếng Việt có dấu:
1. Dùng tra cứu Unicode (vd: `ord("ờ")` = 7901/U+1EDD, `ord("ở")` = 7903/U+1EDF).
2. Nhớ: **KHÔNG có từ tiếng Việt nào kết thúc bằng 2 chữ cái giống nhau** (`ngườii`, `thờii`, `rờii`, `củaa`... đều SAI).
3. Hỏi lại người dùng thay vì đoán.
4. KHÔNG BAO GIỜ thay thế hàng loạt các từ chứa dấu nếu không chắc chắn.
