from typing import Any, Literal
import pydantic_ai.models.openai
from pydantic_ai.models.openai import (
    ModelMessage,
    ModelSettings,
    ModelRequestParameters,
    OpenAIModelSettings,
    chat,
    AsyncStream,
    ChatCompletionChunk,
    NOT_GIVEN,
    APIStatusError,
    ModelHTTPError
)


def non_annotated(model_settings: ModelSettings) -> dict[str, Any]:
    """Extract non annotated key-value pairs from model_settings."""
    return {k: v for (k, v) in model_settings.items() if k not in OpenAIModelSettings.__annotations__}


class OpenAIModel(pydantic_ai.models.openai.OpenAIModel):
    '''
    Subclass of OpenAIModel to allow for custom model settings.
    '''
    async def _completions_create(
        self,
        messages: list[ModelMessage],
        stream: bool,
        model_settings: OpenAIModelSettings,
        model_request_parameters: ModelRequestParameters,
    ) -> chat.ChatCompletion | AsyncStream[ChatCompletionChunk]:
        tools = self._get_tools(model_request_parameters)

        # standalone function to make it easier to override
        if not tools:
            tool_choice: Literal['none', 'required', 'auto'] | None = None
        elif not model_request_parameters.allow_text_result:
            tool_choice = 'required'
        else:
            tool_choice = 'auto'

        if hasattr(self, '_map_messages'):
            openai_messages = await self._map_messages(messages)
        else:
            openai_messages: list[chat.ChatCompletionMessageParam] = []
            for m in messages:
                async for msg in self._map_message(m):
                    openai_messages.append(msg)
        try:
            return await self.client.chat.completions.create(
                model=self._model_name,
                messages=openai_messages,
                n=1,
                parallel_tool_calls=model_settings.get('parallel_tool_calls', NOT_GIVEN),
                tools=tools or NOT_GIVEN,
                tool_choice=tool_choice or NOT_GIVEN,
                stream=stream,
                stream_options={'include_usage': True} if stream else NOT_GIVEN,
                max_tokens=model_settings.get('max_tokens', NOT_GIVEN),
                temperature=model_settings.get('temperature', NOT_GIVEN),
                top_p=model_settings.get('top_p', NOT_GIVEN),
                timeout=model_settings.get('timeout', NOT_GIVEN),
                seed=model_settings.get('seed', NOT_GIVEN),
                presence_penalty=model_settings.get('presence_penalty', NOT_GIVEN),
                frequency_penalty=model_settings.get('frequency_penalty', NOT_GIVEN),
                logit_bias=model_settings.get('logit_bias', NOT_GIVEN),
                reasoning_effort=model_settings.get('openai_reasoning_effort', NOT_GIVEN),
                **non_annotated(model_settings),
            )
        except APIStatusError as e:
            if (status_code := e.status_code) >= 400:
                raise ModelHTTPError(status_code=status_code, model_name=self.model_name, body=e.body) from e
            raise