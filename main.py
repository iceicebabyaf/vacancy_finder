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
    # call llm
    llm_results = []
    for parsed_post in parsed_posts:
        if _cached_prompt_manager.send_text(parsed_post["text"]):
            llm_results.append(parsed_post)

    # match texts
    matcher = Matcher(model_type=args.model_type,
                      profile=args.profile,
                      threshold=args.matcher_threshold,
                      )
    print(matcher(llm_results))


if __name__ == "__main__":
    main()