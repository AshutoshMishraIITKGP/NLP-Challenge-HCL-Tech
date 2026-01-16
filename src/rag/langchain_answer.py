"""LangChain-based RAG answer generation."""
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

class LangChainAnswerGenerator:
    """RAG answer generator using LangChain framework."""
    
    def __init__(self, api_key, retriever):
        """Initialize with LangChain components."""
        self.retriever = retriever
        self.llm = ChatMistralAI(
            model="mistral-small-latest",
            mistral_api_key=api_key,
            temperature=0.3
        )
        
        template = """You are a helpful assistant that answers questions strictly based on the provided context from the HCLTech Annual Report.

STRICT RULES:
1. Answer ONLY using information from the context below
2. If the answer is not in the context, respond with: "The requested information is not available in the provided document."
3. DO NOT use external knowledge
4. ALWAYS cite the page numbers where you found the information
5. Be concise and accurate
6. If the user asks for "inside", "confidential", "private", or "non-public" information, respond that the document is a publicly released annual report and can only summarize publicly available information, not confidential or internal-only details
7. For vague or overly broad queries, ask for clarification or provide only a brief high-level summary to avoid oversharing

Previous conversation context:
{conversation_context}

Context:
{context}

User Question: {query}

Provide your answer in this exact format:

Answer:
<your answer here>

Citations:
<list page numbers>"""
        
        self.prompt = PromptTemplate(
            template=template,
            input_variables=["conversation_context", "context", "query"]
        )
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def generate_answer(self, query, conversation_context=""):
        """Generate answer using LangChain with conversation context."""
        # Retrieve relevant chunks
        chunks = self.retriever.retrieve(query, top_k=5)
        
        # Format context
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"[Chunk {i} - Page {chunk['page']}]\n{chunk['text']}")
        
        context = "\n\n".join(context_parts)
        
        # Generate answer
        answer = self.chain.invoke({
            "conversation_context": conversation_context,
            "context": context,
            "query": query
        })
        
        return answer.strip()
