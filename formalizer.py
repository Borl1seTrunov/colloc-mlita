from gemini_api import call_gemini
import time

def formalize(task: str) -> str:
    prompt = f"""Переведи логическую задачу в клаузы КНФ для метода резолюций.
Выводи ТОЛЬКО клаузы через запятую. Никаких пояснений!
При отрицании существования используй ДРУГУЮ переменную (y, z и т.д.), а не ту же, что в универсальных кванторах!

Анна любит всех, кто любит кошек. Борис любит кошек. Докажи, что Анна любит Бориса.
→ ЛюбитКошек(Борис), ¬ЛюбитКошек(x) ∨ Любит(Анна,x), ¬Любит(Анна,Борис)

Примеры:
Сократ — человек. Все люди смертны. Докажи, что Сократ смертен.
→ Человек(Сократ), ¬Человек(x) ∨ Смертен(x), ¬Смертен(Сократ)

Задача: {task}
Клаузы:"""

    result = call_gemini(prompt)
    if result and "Клаузы:" in result:
        return result.split("Клаузы:")[-1].strip()
    return result.strip() if result else ""

def explain_proof(task: str, clauses: str, steps: list) -> str:
    if not steps:
        return "Доказательство не найдено."
    proof_text = "\n".join(steps)
    prompt = f"""Ты — учитель логики. Объясни доказательство студенту на русском языке.

Задача: {task}
Клаузы: {clauses}

Шаги:
{proof_text}

Объяснение:"""
    time.sleep(10)
    return call_gemini(prompt, temp=0.3) or "Не удалось получить объяснение."