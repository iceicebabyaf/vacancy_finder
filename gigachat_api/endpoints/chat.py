from fastapi import APIRouter
import json

from gigachat_api.dependencies_prompt import GigaChatPromptManagerDep

app = APIRouter()
@app.post("/ask-gigachat", description="this is endpoint for dialog with GigaChat (is there any vacancy in the query). You can edit gigachat parameters in utils/config.py. Input: query (str) Output: True / False")
async def ask(query: str, pm: GigaChatPromptManagerDep):
    response = await pm.send_text(text=query)

    message = response["choices"][0]["message"]

    if "function_call" in message:
        func = message["function_call"]
        args = func["arguments"]

        if isinstance(args, dict):
            answer = args.get("answer", 0)
        else:
            answer = json.loads(args).get("answer", 0)

        return {"answer": int(answer)}

    content = message.get("content", "").strip()
    if content.startswith("{"):
        try:
            return {"answer": json.loads(content).get("answer", 0)}
        except:
            pass

    return {"answer": 0}