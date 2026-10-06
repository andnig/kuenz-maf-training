import time
from agent_framework import function_middleware, FunctionInvocationContext
from lessons.runtime import run
from lessons.ue09_agent import build_agent


@function_middleware
async def observe_tool(context: FunctionInvocationContext, call_next):
    # TODO Ü10: Aufruf + Dauer ausgeben; await call_next(); Fehler protokollieren und erneut auslösen.
    # Keine Tokens/Secrets oder vollständigen privaten Daten protokollieren.
    raise NotImplementedError("Ü10: Middleware ergänzen")


async def compare_sessions(agent):
    # TODO Ü10: agent.create_session(); beide Fragen mit derselben Session.
    # Folgefrage zusätzlich ohne Session ausführen; Antworten getrennt zurückgeben.
    raise NotImplementedError("Ü10: Session und kontextfreien Kontrollaufruf ergänzen")


async def main(client, prompt):
    for label, text in (await compare_sessions(build_agent(client, [observe_tool]))).items():
        print(f"{label}: {text}")


if __name__ == "__main__":
    run(main)
