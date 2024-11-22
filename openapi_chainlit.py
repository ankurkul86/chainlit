import chainlit as cl
from chainlit.input_widget import Select, Slider, Tags, Switch
from langchain.memory import ConversationBufferWindowMemory

from utility import *
from prompt_template import *
from llm import *





def execute_function(input, extra_param=None):

    input_intent = extract_single_json(input)

    function_value = input_intent.get('function')
    params = input_intent.get('parameter') 

    # print(function_value)
    # print(params)

    # Only append extra_param if it's not None
    if extra_param is not None:
        params.append(extra_param)

    # Map conditions to functions
    function_map = {
        'get_endpoints': get_endpoints,
        'list_types': list_types,
        'get_details': get_details,
    }

    # Execute the function based on the condition
    output = function_map[function_value](*params)   

    return output


@cl.on_chat_start
async def start():

    settings = await cl.ChatSettings(
        [
            Select(
                id="Tool_Calling_LLM",
                label="Tool Calling",
                values=LLM_LIST,
                initial_index=0,
            ),


            Select(
                id="Assistant_LLM",
                label="Assistant",
                values=LLM_LIST,
                initial_index=0,
            ),
       
        ]
    ).send()


    cl.user_session.set("Tool_Calling_LLM", LLM_LIST[0])
    cl.user_session.set("Assistant_LLM", LLM_LIST[0])


    elements = [ 
        cl.Text(name=f"Configurations:", content=f"Tool_Calling_LLM = {LLM_LIST[0]}\nAssistant_LLM = {LLM_LIST[0]}", display="inline")
    ]

    await cl.Message(
        content = '',
        elements=elements,
    ).send()




    files = None

    # Wait for the user to upload a file
    while files == None:
        files = await cl.AskFileMessage(
            content="Please upload a OpenAPI Spec File to begin!", accept={"text/plain": [".txt", ".py", ".json", ".yaml"]}
        ).send()

    spec_file = files[0]


    api_spec = load_api_file(spec_file.path)

    cl.user_session.set("API_SPEC", api_spec)

    # Let the user know that the system is ready
    await cl.Message(
        content=f"`{spec_file.name}` uploaded, you can now ask questions about it!"
    ).send()




    
@cl.on_settings_update
async def setup_agent(settings):
    print("on_settings_update", settings)

    cl.user_session.set("Tool_Calling_LLM", settings['Tool_Calling_LLM'])
    cl.user_session.set("Assistant_LLM", settings['Assistant_LLM'])

    elements = [ 
        cl.Text(name=f"Configurations Changed:", content=f"Tool_Calling_LLM = {settings['Tool_Calling_LLM']}\nAssistant_LLM = {settings['Assistant_LLM']}", display="inline")
    ]

    await cl.Message(
        content = '',
        elements=elements,
    ).send()




@cl.on_message
async def main(message: cl.Message):


    memory_buffer = ConversationBufferWindowMemory(k=2, return_messages=True)
    cl.user_session.set("memory", memory_buffer)


    Tool_Calling_LLM = cl.user_session.get("Tool_Calling_LLM")
    Assistant_LLM = cl.user_session.get("Assistant_LLM")

    prompt_template = step['TOOL_CALLING']['prompt_template'] 
    system_prompt = step['TOOL_CALLING']['system_prompt'] 

    user_input = message.content
    input_prompt = prompt_template.format(user_input=user_input) 

    output = LLM[Tool_Calling_LLM]['INFERENCE'](input_prompt,system_prompt,LLM[Tool_Calling_LLM]['MODEL'])

    await cl.Message(
        content = output,
    ).send()


    #####################################################################################################

    api_info = execute_function(output,cl.user_session.get("API_SPEC"))

    print(api_info)

    prompt_template = step['ASSISTANT']['prompt_template'] 
    system_prompt = step['ASSISTANT']['system_prompt'] 


    input_prompt = prompt_template.format(user_input=user_input,api_info=api_info)

    # Call the infer_llm function and stream the output

    # await infer_llm_stream(input_prompt, system_prompt, llm)
    await LLM[Assistant_LLM]['INFERENCE_STREAM'](input_prompt, system_prompt, LLM[Assistant_LLM]['MODEL'] )

    #print(final_output)

    # memory_buffer = cl.user_session.get("memory")
    # memory_buffer.save_context({"user": user_input}, {"AI": output})
    # cl.user_session.set("memory", memory_buffer)


