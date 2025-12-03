import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import json
from gigachat_api.dependencies_prompt import get_giga_prompt_manager
from gigachat_api.managers.auth_manager import get_giga_token_manager

async def test_simple_text(text: str):
    print(f"Тестируем текст:\n{text}\n{'='*60}")

    token_manager = await get_giga_token_manager()
    pm = await get_giga_prompt_manager(token_manager)
    raw_response = await pm.send_text(text)

    print("Полный ответ от GigaChat:")
    print(json.dumps(raw_response, ensure_ascii=False, indent=2))


    try:
        message = raw_response["choices"][0]["message"]
        if message.get("function_call"):
            args = message["function_call"]["arguments"]
            if isinstance(args, str):
                verdict = json.loads(args).get("answer", -1)
            else:
                verdict = args.get("answer", -1)
            
            print(f"\nВЕРДИКТ: {verdict} → {'Вакансия!!!' if verdict == 1 else 'Не вакансия'}")
        else:
            content = message.get("content", "").strip()
            print(f"\nGigaChat ответил текстом: {content}")
            verdict = 1 if "1" in content else 0
            print(f"Принудительный вердикт: {verdict}")

    except Exception as e:
        print(f"Ошибка парсинга: {e}")
        verdict = -1

    return verdict


async def main():
    test_texts = [
        "Ищем Senior Python разработчика в Москве, зарплата 400–600к, удалённо не рассматриваем, пишите в ЛС",
        "Продаю iPhone 15 Pro Max 256 гб, состояние новый, коробка, чек, 110к торг",
        "Требуется курьер в Яндекс.Еду, гибкий график, оплата каждый день",
        "Всем привет, как дела? Давно не писал)",
        "Нужен Middle QA инженер, стек: Python + Selenium + Pytest, офис в Питере, зп до 300к на руки",
    ]

    for i, text in enumerate(test_texts, 1):
        print(f"\nТЕСТ {i}/{len(test_texts)}")
        await test_simple_text(text)
        print("\n" + "—" * 80)
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())