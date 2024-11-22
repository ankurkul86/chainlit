
import chainlit as cl
from huggingface_hub import InferenceClient
from huggingface_hub import AsyncInferenceClient
from openai import AsyncOpenAI, OpenAI
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")


def infer_huggingface(input,system_prompt,llm):

    print(llm)

    client = InferenceClient(
    llm,
    token=HUGGINGFACE_API_KEY,
    )

    output = ''

    for message in client.chat_completion(
        messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": input}
                  
                  ],
        max_tokens=2000,
        stream=True,
    ):
        output = output + message.choices[0].delta.content


    return output


async def infer_huggingface_stream(input, system_prompt, llm):
    print('Input Prompt')
    print(input)

    final_output = ""

    client = AsyncInferenceClient(
        llm,
        token=HUGGINGFACE_API_KEY,
    )

    msg = cl.Message(content="")
    await msg.send()

    stream = await client.chat.completions.create(
    model=llm,
    messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": input}],
    stream=True,
    max_tokens=2000
    )

    async for part in stream:
        if token := part.choices[0].delta.content or "":
             await msg.stream_token(token)
            #  final_output += token  # Append token to the final output

    await msg.update()

    # return final_output


def infer_openai(input, system_prompt, llm):
    print('Input Prompt')
    print(input)

    client = OpenAI(api_key=OPENAI_API_KEY)

    completion = client.chat.completions.create(
        model=llm,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": input
            }
        ]
    )

    return completion.choices[0].message.content





async def infer_openai_stream(input, system_prompt, llm):
    print('Input Prompt')
    print(input)

    final_output = ""

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)


    settings = {
        "model": llm,
        "temperature": 0.7,
        "max_tokens": 2000,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
    }

    msg = cl.Message(content="")

    stream = await client.chat.completions.create(
            messages=[{"role": "system", "content": system_prompt},
                  {"role": "user", "content": input}]
            , stream=True, 
            **settings
    )

    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await msg.stream_token(token)
            final_output += token  # Append token to the final output

    #message_history.append({"role": "assistant", "content": msg.content})
    await msg.update()

    return final_output


LLM = {

        'gpt-3.5-turbo' : {

            'MODEL' : 'gpt-3.5-turbo',
            'INFERENCE_STREAM' : infer_openai_stream,
            'INFERENCE' : infer_openai

        },

        'Mistral-7B-Instruct' : {

            'MODEL' : 'mistralai/Mistral-7B-Instruct-v0.3',
            'INFERENCE_STREAM' : infer_huggingface_stream,
            'INFERENCE' : infer_huggingface


        },

        'Phi-3-mini-4k' : {

            'MODEL' : 'microsoft/Phi-3-mini-4k-instruct',
            'INFERENCE_STREAM' : infer_huggingface_stream,
            'INFERENCE' : infer_huggingface


        },


        'Llama-3.2-3B' : {

            'MODEL' : 'meta-llama/Llama-3.2-3B-Instruct',
            'INFERENCE_STREAM' : infer_huggingface_stream,
            'INFERENCE' : infer_huggingface


        },


        'Llama-3.2-1B' : {

            'MODEL' : 'meta-llama/Llama-3.2-1B-Instruct',
            'INFERENCE_STREAM' : infer_huggingface_stream,
            'INFERENCE' : infer_huggingface


        },


}


LLM_LIST = list(LLM.keys())