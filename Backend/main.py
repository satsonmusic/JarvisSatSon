from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.agents.orchestrator import run_agent

app = FastAPI()

# This is CRITICAL: It allows your frontend (running on port 3000) 
# to talk to your backend (running on port 8000) without being blocked by security.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: str = "scott_123"

@app.post("/chat")
def chat_with_jarvis(request: ChatRequest):
    print(f"\n========================================")
    print(f"📥 Received message: {request.message}")
    print(f"========================================")
    
    # Send the message to Jarvis
    result = run_agent(request.message, request.user_id)
    
    # 🚨 NEW: Print exactly what his brain outputs to the terminal so we can debug!
    print(f"🧠 Brain Output: {result}\n")
    
    # Format the response for the frontend
    if result.get("status") == "success":
        thoughts = result.get('plan', {}).get('thoughts', '')
        action_summary = ""
        
        # Check if he actually used tools, or just wanted to talk
        if result.get('results'):
            for step in result['results']:
                action_summary += f"\n✅ Executed `{step.get('tool', 'tool')}`\nOutput: {step.get('output', '')}\n"
        
        final_reply = f"{thoughts}\n{action_summary}"
        return {"response": final_reply.strip()}
    else:
        # Pass the EXACT error message to the frontend so we can see it
        error_msg = result.get('error', 'Unknown internal error.')
        return {"response": f"❌ Error: {error_msg}"}