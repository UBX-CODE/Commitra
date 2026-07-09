import json
from groq import Groq
from models.schemas import CommitAnalysis, RepoContext
from llm.prompts import SYSTEM_PROMPT, build_analysis_prompt
from utils.config import config

class LLMClient:
    def __init__(self):
        if not config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not configured.")
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.GROQ_MODEL
    
    def analyze_commits(self, context: RepoContext, feedback: str = None) -> CommitAnalysis:
        context_json = context.model_dump_json(indent=2)
        prompt = build_analysis_prompt(context_json, feedback)
        
        # Try up to 2 times (1 initial + 1 correction)
        max_attempts = 2
        last_error = ""
        
        for attempt in range(max_attempts):
            try:
                msg = prompt
                if attempt > 0:
                    msg += f"\n\nYour previous response failed validation with error: {last_error}. Please provide a valid JSON object matching the schema."
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": msg}
                    ],
                    temperature=0.2,
                    response_format={"type": "json_object"}
                )
                
                raw_json = response.choices[0].message.content
                data = json.loads(raw_json)
                return CommitAnalysis(**data)
            
            except Exception as e:
                last_error = str(e)
                
        raise RuntimeError(f"AI response could not be validated after {max_attempts} attempts. Error: {last_error}")
