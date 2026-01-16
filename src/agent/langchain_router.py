"""LangChain-based intent classification."""
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.rag.prompts import INTENT_CLASSIFICATION_PROMPT

class LangChainIntentRouter:
    """Intent router using LangChain framework."""
    
    def __init__(self, api_key):
        """Initialize with LangChain components."""
        self.llm = ChatMistralAI(
            model="mistral-small-latest",
            mistral_api_key=api_key,
            temperature=0.0
        )
        
        self.prompt = PromptTemplate(template=INTENT_CLASSIFICATION_PROMPT, input_variables=["query"])
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def classify_intent(self, query):
        """Classify user intent using LangChain."""
        result = self.chain.invoke({"query": query})
        intent = result.strip()
        
        if "ACTION_REQUEST" in intent:
            return "ACTION_REQUEST"
        return "INFO_QUERY"
