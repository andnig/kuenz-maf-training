import asyncio
import os
import sys
from agent_framework.foundry import FoundryChatClient
from azure.identity.aio import AzureCliCredential
from dotenv import load_dotenv


def run(action):
    async def main():
        load_dotenv()
        endpoint, model = os.getenv("FOUNDRY_PROJECT_ENDPOINT"), os.getenv("FOUNDRY_MODEL")
        if not endpoint or not model:
            raise SystemExit(".env fehlt: FOUNDRY_PROJECT_ENDPOINT und FOUNDRY_MODEL")
        async with AzureCliCredential() as credential:
            client = FoundryChatClient(project_endpoint=endpoint, model=model, credential=credential)
            await action(client, " ".join(sys.argv[1:]))
    asyncio.run(main())
