from enum import StrEnum, auto
from typing import Annotated

from dishka import (
    FromComponent,
    Marker,
    Provider,
    Scope,
    activate,
    from_context,
    provide,
)
from fastapi import Request
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.mistral import MistralModel
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.models.xai import XaiModel
from pydantic_ai.providers.anthropic import AnthropicProvider
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.mistral import MistralProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.providers.xai import XaiProvider

from app.adapters import (
    ChatService,
)
from app.domain.ports import (
    ChatServicePort,
)
from app.infrastructure.config import Settings


class AvailableChat(StrEnum):
    xai = auto()
    anthropic = auto()
    openai = auto()
    google = auto()
    mistral = auto()


class LLMActivator(Provider):
    request = from_context(provides=Request, scope=Scope.REQUEST)

    @activate(Marker(AvailableChat.xai))
    def xai(self, request: Request) -> bool:
        return bool(request.url.path.endswith("/xai"))

    @activate(Marker(AvailableChat.anthropic))
    def anthropic(self, request: Request) -> bool:
        return bool(request.url.path.endswith("/anthropic"))

    @activate(Marker(AvailableChat.openai))
    def openai(self, request: Request) -> bool:
        return bool(request.url.path.endswith("/openai"))

    @activate(Marker(AvailableChat.google))
    def google(self, request: Request) -> bool:
        return bool(request.url.path.endswith("/google"))

    @activate(Marker(AvailableChat.mistral))
    def mistral(self, request: Request) -> bool:
        return bool(request.url.path.endswith("/mistral"))


class XaiAgentProvider(Provider):
    component = AvailableChat.xai

    @provide(scope=Scope.APP)
    def agent(self, model: Annotated[XaiModel, FromComponent("")]) -> Agent:
        return Agent(model)


class AnthropicAgentProvider(Provider):
    component = AvailableChat.anthropic

    @provide(scope=Scope.APP)
    def agent(self, model: Annotated[AnthropicModel, FromComponent("")]) -> Agent:
        return Agent(model)


class OpenAIAgentProvider(Provider):
    component = AvailableChat.openai

    @provide(scope=Scope.APP)
    def agent(self, model: Annotated[OpenAIChatModel, FromComponent("")]) -> Agent:
        return Agent(model)


class GoogleAgentProvider(Provider):
    component = AvailableChat.google

    @provide(scope=Scope.APP)
    def agent(self, model: Annotated[GoogleModel, FromComponent("")]) -> Agent:
        return Agent(model)


class MistralAgentProvider(Provider):
    component = AvailableChat.mistral

    @provide(scope=Scope.APP)
    def agent(self, model: Annotated[MistralModel, FromComponent("")]) -> Agent:
        return Agent(model)


class XaiProviders(Provider):
    @provide(scope=Scope.APP)
    def provider(self, settings: Settings) -> XaiProvider:
        return XaiProvider(api_key=settings.xai.xai_api_key.get_secret_value())

    @provide(scope=Scope.APP)
    def model(self, settings: Settings, provider: XaiProvider) -> XaiModel:
        return XaiModel(model_name=settings.xai.model, provider=provider)

    @provide(
        scope=Scope.REQUEST,
        provides=ChatServicePort,
        when=Marker(AvailableChat.xai),
    )
    def chat(
        self,
        agent: Annotated[Agent, FromComponent(AvailableChat.xai)],
    ) -> ChatService:
        return ChatService(agent)


class AnthropicProviders(Provider):
    @provide(scope=Scope.APP)
    def provider(self, settings: Settings) -> AnthropicProvider:
        return AnthropicProvider(
            api_key=settings.anthropic.anthropic_api_key.get_secret_value(),
        )

    @provide(scope=Scope.APP)
    def model(
        self,
        settings: Settings,
        provider: AnthropicProvider,
    ) -> AnthropicModel:
        return AnthropicModel(model_name=settings.anthropic.model, provider=provider)

    @provide(
        scope=Scope.REQUEST,
        provides=ChatServicePort,
        when=Marker(AvailableChat.anthropic),
    )
    def chat(
        self,
        agent: Annotated[Agent, FromComponent(AvailableChat.anthropic)],
    ) -> ChatService:
        return ChatService(agent)


class OpenAIProviders(Provider):
    @provide(scope=Scope.APP)
    def provider(self, settings: Settings) -> OpenAIProvider:
        return OpenAIProvider(api_key=settings.openai.openai_api_key.get_secret_value())

    @provide(scope=Scope.APP)
    def model(
        self,
        settings: Settings,
        provider: OpenAIProvider,
    ) -> OpenAIChatModel:
        return OpenAIChatModel(model_name=settings.openai.model, provider=provider)

    @provide(
        scope=Scope.REQUEST,
        provides=ChatServicePort,
        when=Marker(AvailableChat.openai),
    )
    def chat(
        self,
        agent: Annotated[Agent, FromComponent(AvailableChat.openai)],
    ) -> ChatService:
        return ChatService(agent)


class GoogleProviders(Provider):
    @provide(scope=Scope.APP)
    def provider(self, settings: Settings) -> GoogleProvider:
        return GoogleProvider(api_key=settings.google.google_api_key.get_secret_value())

    @provide(scope=Scope.APP)
    def model(
        self,
        settings: Settings,
        provider: GoogleProvider,
    ) -> GoogleModel:
        return GoogleModel(model_name=settings.google.model, provider=provider)

    @provide(
        scope=Scope.REQUEST,
        provides=ChatServicePort,
        when=Marker(AvailableChat.google),
    )
    def chat(
        self,
        agent: Annotated[Agent, FromComponent(AvailableChat.google)],
    ) -> ChatService:
        return ChatService(agent)


class MistralProviders(Provider):
    @provide(scope=Scope.APP)
    def provider(self, settings: Settings) -> MistralProvider:
        return MistralProvider(
            api_key=settings.mistral.mistral_api_key.get_secret_value(),
        )

    @provide(scope=Scope.APP)
    def model(
        self,
        settings: Settings,
        provider: MistralProvider,
    ) -> MistralModel:
        return MistralModel(model_name=settings.mistral.model, provider=provider)

    @provide(
        scope=Scope.REQUEST,
        provides=ChatServicePort,
        when=Marker(AvailableChat.mistral),
    )
    def chat(
        self,
        agent: Annotated[Agent, FromComponent(AvailableChat.mistral)],
    ) -> ChatService:
        return ChatService(agent)


def provide_ai() -> tuple[Provider]:
    return (
        MistralAgentProvider(),
        MistralProviders(),
        GoogleAgentProvider(),
        GoogleProviders(),
        OpenAIProviders(),
        OpenAIAgentProvider(),
        AnthropicAgentProvider(),
        AnthropicProviders(),
        LLMActivator(),
        XaiProviders(),
        XaiAgentProvider(),
    )
