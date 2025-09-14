import requests

APP_ID = 730  # CS:GO
r = requests.get(
    f"https://store.steampowered.com/appreviews/{APP_ID}",
    params={
        "json": 1,
        "filter": "all",
        "language": "all",
        "day_range": 9223372036854775807,  # все отзывы
        "review_type": "all",
        "purchase_type": "all",
        "num_per_page": 0,  # без загрузки отзывов, только статистика
    },
    headers={"User-Agent": "Mozilla/5.0"}
)

data = r.json()
summary = data["query_summary"]

total = summary["total_reviews"]
positive = summary["total_positive"]
negative = summary["total_negative"]
score = (positive / total * 100) if total else 0

print("Всего отзывов:", total)
print("Положительных:", positive)
print("Отрицательных:", negative)
print("Процент положительных:", f"{score:.2f}%")
