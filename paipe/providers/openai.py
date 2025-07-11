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
from ..util import kwargs_by_func_def


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
                reasoning_effort=model_settings.get('openai_reasoning_effort', NOT_GIVEN),
                **kwargs_by_func_def(self.client.chat.completions.create, model_settings),
            )
        except APIStatusError as e:
            if (status_code := e.status_code) >= 400:
                raise ModelHTTPError(status_code=status_code, model_name=self.model_name, body=e.body) from e
            raise