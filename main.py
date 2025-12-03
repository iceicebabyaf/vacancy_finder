import argparse

from matcher.matcher import Matcher
from gigachat_api.dependencies_prompt import _cached_prompt_manager
from vk_parser.parser import analyze_vk_posts

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", type=str, help="User profile description.")
    parser.add_argument("--url", type=str, default=0.5, help="VK user URL.")
    parser.add_argument("--model_type", type=str, default="bert-l", help="Type for matcher model.", required=False)
    parser.add_argument("--matcher_threshold", type=float, default=0.5, help="Matcher threshold.", required=False)
    args = parser.parse_args()

    # parse vk
    parsed_posts = analyze_vk_posts(
        profile_url=args.url,
        depth=1,
        period_days=30
    )

    # ==== gigachat API ====
    import asyncio
    import json

    from gigachat_api.dependencies_prompt import get_giga_prompt_manager
    from gigachat_api.managers.auth_manager import get_giga_token_manager

    async def _call_llm_for_posts(posts):
        token_manager = await get_giga_token_manager()
        pm = await get_giga_prompt_manager(token_manager)

        results = []

        for post in posts:
            text = post.get("text", "").strip()
            if not text:
                continue

            try:
                raw_response = await pm.send_text(text)
                message = raw_response["choices"][0]["message"]

                if message.get("function_call"):
                    args = message["function_call"]["arguments"]

                    if isinstance(args, str):
                        try:
                            verdict = json.loads(args).get("answer", -1)
                        except Exception:
                            verdict = -1
                    else:
                        verdict = args.get("answer", -1)

                else:
                    content = message.get("content", "").strip()
                    verdict = 1 if "1" in content else 0

                verdict = int(verdict)
                if verdict not in (0, 1):
                    verdict = 0

                result_post = post.copy()
                result_post["llm_verdict"] = verdict
                result_post["llm_raw"] = raw_response

                results.append(result_post)

            except Exception as e:
                print(f"Ошибка при запросе к GigaChat для поста {post.get('author_id')}: {e}")

        return results
    
    llm_results = asyncio.run(_call_llm_for_posts(parsed_posts))
    # =========


    # match texts
    matcher = Matcher(model_type=args.model_type,
                      profile=args.profile,
                      threshold=args.matcher_threshold,
                      )
    print(matcher(llm_results))


if __name__ == "__main__":
    main()