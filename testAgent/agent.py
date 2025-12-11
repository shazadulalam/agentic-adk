from google.adk.agents.llm_agent import Agent

def get_current_time(city:str) -> dict:

    return{"status": "success", "city" : city, "time": "10:20 AM"}

root_agent = Agent(
    model='gemini-3-pro-preview',
    name='root_agent',
    description='Tells the current time in a specified city.',
    instruction='You are a helpful assistant that tells the current time in citis',
    tools = [get_current_time],
)
