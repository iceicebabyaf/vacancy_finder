from pathlib import Path
from dotenv import load_dotenv
import os
import requests
import time
from urllib.parse import urlparse
from datetime import datetime, timedelta
from tqdm import tqdm
import json
import argparse

VK_API_VERSION = "5.199"

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")

VK_TOKEN = os.getenv("VK_TOKEN")
if not VK_TOKEN:
    raise ValueError("Не найден VK_TOKEN в .env")


def vk_api(method, params):
    params["access_token"] = VK_TOKEN
    params["v"] = VK_API_VERSION
    r = requests.get(f"https://api.vk.com/method/{method}", params=params).json()
    if "error" in r:
        raise Exception(r["error"])
    return r["response"]


def extract_id_from_url(url):
    screen_name = urlparse(url).path.strip("/")
    data = vk_api("users.get", {"user_ids": screen_name})
    return data[0]["id"]


def get_friends(user_id):
    try:
        data = vk_api("friends.get", {"user_id": user_id})
        return data["items"]
    except:
        return []


def simplify_post(item, owner_id, path):
    return {
        "author_id": owner_id,
        "author_url": f"https://vk.com/id{owner_id}",
        "date": item["date"],
        "text": item.get("text", ""),
        "path": path[:]
    }


def get_posts(user_id, min_timestamp, path):
    try:
        data = vk_api("wall.get", {"owner_id": user_id, "count": 100, "offset": 0})
    except Exception as e:
        err = e.args[0]
        if isinstance(err, dict):
            code = err.get("error_code")
            if code == 15:
                print(f"[WARN] Стена скрыта: {user_id}")
                return []
            if code == 30:
                print(f"[WARN] Профиль закрыт: {user_id}")
                return []
            if code == 18:
                print(f"[WARN] Пользователь удалён или забанен: {user_id}")
                return []
        print(f"[ERROR] Ошибка wall.get {user_id}: {err}")
        return []

    posts = []
    for item in data.get("items", []):
        if item["date"] >= min_timestamp:
            posts.append(simplify_post(item, user_id, path))
    return posts


def crawl(user_id, depth, min_timestamp, visited=None, seen_posts=None, progress=None, path=None):
    if visited is None:
        visited = set()
    if seen_posts is None:
        seen_posts = set()
    if path is None:
        path = []

    if user_id in visited:
        return []

    visited.add(user_id)
    new_path = path + [f"https://vk.com/id{user_id}"]
    results = []

    posts = get_posts(user_id, min_timestamp, new_path)
    for post in posts:
        post_key = post.get("id")
        if not post_key:
            post_key = f"{post['author_id']}_{post['date']}_{post['text'][:30]}"
        if post_key not in seen_posts:
            results.append(post)
            seen_posts.add(post_key)

    if depth > 0:
        friends = get_friends(user_id)
        for friend_id in friends:
            if progress is not None:
                progress.update(1)
            results.extend(crawl(friend_id, depth - 1, min_timestamp, visited, seen_posts, progress, new_path))

    return results


def analyze_vk_posts(profile_url, depth, period_days, json_file=None):
    """
    Возвращает список постов и опционально сохраняет в JSON.
    """
    user_id = extract_id_from_url(profile_url)
    min_timestamp = int((datetime.now() - timedelta(days=period_days)).timestamp())

    print(f"Анализ профиля {user_id} | глубина: {depth} | период: {period_days} дней")

    progress = tqdm(desc="Обход пользователей")
    parsed_posts = crawl(user_id, depth, min_timestamp, visited=set(), seen_posts=set(), progress=progress)
    progress.close()

    print(f"\nНайдено постов: {len(parsed_posts)}")

    if json_file:
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(parsed_posts, f, ensure_ascii=False, indent=4)
        print(f"Сохранено в JSON: {json_file}")

    return parsed_posts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VK Friends Posts Crawler")
    parser.add_argument("--url", required=True, help="Ссылка на профиль ВК")
    parser.add_argument("--depth", type=int, required=True, help="Глубина обхода")
    parser.add_argument("--days", type=int, default=30, help="Период анализа (дни)")
    parser.add_argument("--out", default=None, help="Имя JSON-файла для сохранения")

    args = parser.parse_args()

    analyze_vk_posts(
        args.url,
        args.depth,
        args.days,
        json_file=args.out
    )
