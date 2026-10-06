"""Isolierter Hosted-Adapter; unveränderte Trainingslogik wird daneben kopiert."""
import os
from uuid import uuid4

from agent_framework import AgentResponse, AgentResponseUpdate, AgentSession, Content, Message, ResponseStream
from agent_framework.foundry import FoundryChatClient
from agent_framework_foundry_hosting import ResponsesHostServer
from azure.identity.aio import DefaultAzureCredential

from pruefservice.workflow import review_id_bestimmen
from lessons.ue11_workflow import execute as workflow_pruefen
import json
from review_contract import CONTRACT_VERSION, PLATFORM_BINDING, result_record
from opentelemetry import trace


class HostedPruefservice:
    id = "kuenz-hosted-pruefung"
    name = "Spezifikationspruefung"
    description = "Synthetischer Trainings-Prüfservice, unveränderter MAF-Workflow"

    def create_session(self, *, session_id=None):
        return AgentSession(session_id=session_id)

    def get_session(self, service_session_id, *, session_id=None):
        return AgentSession(service_session_id=service_session_id, session_id=session_id)

    async def answer(self, messages):
        if isinstance(messages, str):
            text = messages
        else:
            messages = [messages] if isinstance(messages, Message) else list(messages or [])
            users = [m for m in messages if m.role == "user"]
            text = users[-1].text if users else ""
        try:
            review_id = review_id_bestimmen(text)
        except ValueError as error:
            return json.dumps({"contract_version": CONTRACT_VERSION, "processing_status": "input_required",
                               "message": str(error), "human_approval_status": "not_requested",
                               "dataverse_callback_status": "not_requested"}, ensure_ascii=False)
        async with DefaultAzureCredential() as credential:
            client = FoundryChatClient(project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
                                       model=os.environ["FOUNDRY_MODEL"], credential=credential)
            with trace.get_tracer(__name__).start_as_current_span("kuenz.hosted.review") as span:
                span.set_attribute("kuenz.review_id", review_id)
                result = await workflow_pruefen(review_id, client=client)
                record = result_record(result)
                span.set_attribute("kuenz.run_id", record["run_id"])
        return json.dumps(record, ensure_ascii=False)

    def run(self, messages=None, *, stream=False, session=None, **kwargs):
        async def complete():
            return AgentResponse(messages=[Message("assistant", [await self.answer(messages)])],
                                 response_id=str(uuid4()), agent_id=self.id)

        async def updates():
            yield AgentResponseUpdate(contents=[Content.from_text(await self.answer(messages))],
                                      role="assistant", response_id=str(uuid4()), message_id=str(uuid4()),
                                      agent_id=self.id, finish_reason="stop")

        return ResponseStream(updates(), finalizer=AgentResponse.from_updates) if stream else complete()


class TrainingResponsesHostServer(ResponsesHostServer):
    """Versionsgeprüfte Adapternaht: Plattform-IDs aus ResponseContext, nicht vom Modell."""
    async def _handle_response(self, request, context, cancellation_signal):
        token = PLATFORM_BINDING.set({"response_id": context.response_id, "conversation_id": context.conversation_id})
        try:
            async for event in super()._handle_response(request, context, cancellation_signal):
                yield event
        finally:
            PLATFORM_BINDING.reset(token)


def configure_training_telemetry(**kwargs):
    # Reuse the course's explicit Azure Monitor exporters under the hosted lifecycle.
    import logging
    from agent_framework.observability import configure_otel_providers
    from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter, AzureMonitorTraceExporter
    connection = os.getenv("TRAINING_APPINSIGHTS_CONNECTION_STRING")
    if not connection:
        configure_otel_providers(service_name="kuenz-hosted-pruefung")
        return
    # The exporter also parses the platform-injected standard variable.
    os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"] = connection
    logging.basicConfig(level=logging.INFO)
    configure_otel_providers(service_name="kuenz-hosted-pruefung",
        exporters=[AzureMonitorTraceExporter(connection_string=connection),
                   AzureMonitorLogExporter(connection_string=connection)])


if __name__ == "__main__":
    TrainingResponsesHostServer(HostedPruefservice(), history_source="agent", configure_observability=configure_training_telemetry).run()
