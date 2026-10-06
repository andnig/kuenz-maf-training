from agent_framework import Agent
from lessons.runtime import run


async def main(client, prompt):
    agent = Agent(client=client, name="ErsterModellaufruf", instructions="Antworte kurz auf Deutsch.")
    response = await agent.run(prompt or "Erkläre in einem Satz den Unterschied zwischen Modell und Tool.")
    print(response.text)


if __name__ == "__main__":
    run(main)
