extends RefCounted
class_name TravelCalendar

# One game timeline counted in whole minutes since 1970-01-01 00:00 (proleptic Gregorian).
# Travel, rest, tasks and weekly settlement all advance this single integer.
const MINUTES_PER_DAY := 1440
const MINUTES_PER_WEEK := 10080
# Game weeks begin on Monday 00:00. 1970-01-01 was a Thursday, so day -3 is a Monday.
const WEEK_ANCHOR_DAY_OFFSET := 3


static func is_leap_year(year: int) -> bool:
	return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0


static func days_in_month(year: int, month: int) -> int:
	if month == 2:
		return 29 if is_leap_year(year) else 28
	return 30 if month in [4, 6, 9, 11] else 31


static func is_valid_date(year: int, month: int, day: int) -> bool:
	return month >= 1 and month <= 12 and day >= 1 and day <= days_in_month(year, month)


static func floor_div(a: int, b: int) -> int:
	var q := a / b
	if (a % b != 0) and ((a < 0) != (b < 0)):
		q -= 1
	return q


# Days since 1970-01-01 (H. Hinnant's days_from_civil).
static func days_from_civil(year: int, month: int, day: int) -> int:
	var y := year - (1 if month <= 2 else 0)
	var era := floor_div(y, 400)
	var yoe := y - era * 400
	var doy := (153 * (month + (-3 if month > 2 else 9)) + 2) / 5 + day - 1
	var doe := yoe * 365 + yoe / 4 - yoe / 100 + doy
	return era * 146097 + doe - 719468


static func civil_from_days(day_index: int) -> Dictionary:
	var z := day_index + 719468
	var era := floor_div(z, 146097)
	var doe := z - era * 146097
	var yoe := (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365
	var doy := doe - (365 * yoe + yoe / 4 - yoe / 100)
	var mp := (5 * doy + 2) / 153
	var day := doy - (153 * mp + 2) / 5 + 1
	var month := mp + (3 if mp < 10 else -9)
	return {"year": yoe + era * 400 + (1 if month <= 2 else 0), "month": month, "day": day}


static func to_minutes(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> int:
	return days_from_civil(year, month, day) * MINUTES_PER_DAY + hour * 60 + minute


static func day_index(total_minutes: int) -> int:
	return floor_div(total_minutes, MINUTES_PER_DAY)


static func week_index(total_minutes: int) -> int:
	return floor_div(day_index(total_minutes) + WEEK_ANCHOR_DAY_OFFSET, 7)


static func from_minutes(total_minutes: int) -> Dictionary:
	var days := day_index(total_minutes)
	var minute_of_day := total_minutes - days * MINUTES_PER_DAY
	var result := civil_from_days(days)
	result["hour"] = minute_of_day / 60
	result["minute"] = minute_of_day % 60
	result["minute_of_day"] = minute_of_day
	result["day_index"] = days
	result["weekday"] = posmod(days + WEEK_ANCHOR_DAY_OFFSET, 7) + 1
	result["week_index"] = week_index(total_minutes)
	return result


static func iso_text(total_minutes: int) -> String:
	var dt := from_minutes(total_minutes)
	return "%04d-%02d-%02d %02d:%02d" % [dt["year"], dt["month"], dt["day"], dt["hour"], dt["minute"]]


# Parses "YYYY-MM-DD" plus optional "HH:MM" into {"ok": true, "minutes": int}; {"ok": false} on bad input.
static func parse_minutes(date_text: String, time_text: String = "00:00") -> Dictionary:
	var date_parts := date_text.split("-")
	var time_parts := time_text.split(":")
	if date_parts.size() != 3 or time_parts.size() != 2:
		return {"ok": false}
	for part in date_parts + time_parts:
		if not String(part).is_valid_int():
			return {"ok": false}
	var year := int(date_parts[0])
	var month := int(date_parts[1])
	var day := int(date_parts[2])
	var hour := int(time_parts[0])
	var minute := int(time_parts[1])
	if not is_valid_date(year, month, day) or hour < 0 or hour > 23 or minute < 0 or minute > 59:
		return {"ok": false}
	return {"ok": true, "minutes": to_minutes(year, month, day, hour, minute)}
