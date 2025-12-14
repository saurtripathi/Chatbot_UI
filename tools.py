from langchain_tavily import TavilySearch
from langchain_core.tools import tool, Tool
from langchain_classic.chains import LLMMathChain
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_deepseek import ChatDeepSeek
import os, requests
from dotenv import load_dotenv


load_dotenv()

llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=0,
    max_tokens=1000,
    timeout=None,
    max_retries=2,
)


search_tool = TavilySearch(
            max_results=5,
            topic="general",
        )


chain = LLMMathChain.from_llm(llm=llm, verbose=False)

math_tool = Tool.from_function(name="Calculator",
                        func=chain.run,
                        description="""
perform a basic arithmatic operation on two numbers
""")


wikipedia = WikipediaAPIWrapper()
wikipedia_tool = Tool(name="Wikipedia",
                      func=wikipedia.run,
                  description="""A useful tool for searching the Internet 
to find information on world events, issues, dates, years, etc. Worth 
using for general topics. Use precise questions.""")


@tool
def get_weather_data(city):

    """
    Fetch the weather data for given city, and show description,minimum temparature, max temparature 
    in degree celcius, city name, country name in tabular format.
    """
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={os.getenv("weather_api_key")}"
    # print(url)
    req = requests.get(url)
    return req.json()

