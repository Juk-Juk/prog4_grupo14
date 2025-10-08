import logging
from google import genai
from google.genai import types
import environ

env = environ.Env()
logger = logging.getLogger(__name__)

def get_client():
    #Create genai and vertex clients.
    api_key = env("GEMINI_API_KEY") or env("GOOGLE_API_KEY")
    use_vertex = False #env("GOOGLE_GENAI_USE_VERTEXAI", "false").lower() in ("1","true","yes")
    
    if use_vertex:
        project = env("GOOGLE_CLOUD_PROJECT")
        location = env("GOOGLE_CLOUD_LOCATION", "us-central1")
        client = genai.Client(vertexai=True, project=project, location=location)
    else:
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        client = genai.Client(api_key=api_key)
    return client

_client = None
def client():
    global _client
    if _client is None:
        _client = get_client()
    return _client

# Correct generated text
def generate_text(prompt, model="gemini-flash-latest", max_output_tokens=300):
    c = client()
    try:
        # New API config
        config = types.GenerateContentConfig(
            max_output_tokens=max_output_tokens,
            temperature=0.7
        )
        
        # Corrected call
        response = c.models.generate_content(
            model=model, 
            contents=prompt,
            config=config
        )
        
        # Extract text
        if hasattr(response, 'text'):
            return response.text
        elif hasattr(response, 'candidates') and response.candidates:
            return response.candidates[0].content.parts[0].text
        else:
            return str(response)
            
    except Exception as e:
        logger.exception("Error al llamar a Gemini generate_content")
        return f"Error al generar texto: {e}"

# Generate corrected embedding
def embed_text(text, model="text-embedding-004"):
    c = client()
    try:
        response = c.models.embed_content(
            model=model, 
            contents=text
        )
        
        if hasattr(response, 'embeddings'):
            embeddings = response.embeddings
            if isinstance(embeddings, list) and len(embeddings) > 0:
                return embeddings[0].values if hasattr(embeddings[0], 'values') else embeddings[0]
            return embeddings
        return response
        
    except Exception as e:
        logger.exception("Error al generar embedding")
        return None 