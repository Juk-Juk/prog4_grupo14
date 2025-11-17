import logging
from functools import lru_cache
from typing import Optional, List, Dict, Any
from google import genai
from google.genai import types
import environ

env = environ.Env()
logger = logging.getLogger(__name__)

# Configuration constants
DEFAULT_MODEL = "gemini-flash-latest"
DEFAULT_EMBEDDING_MODEL = "text-embedding-004"
DEFAULT_MAX_TOKENS = 2048
DEFAULT_TEMPERATURE = 0.7
MAX_RETRY_ATTEMPTS = 3


class AIClientError(Exception):
    """Custom exception for AI client errors"""
    pass


class AIClient:
    """Singleton AI client wrapper for Google Genai"""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._client = self._initialize_client()
    
    def _initialize_client(self):
        """Initialize and return the genai client"""
        try:
            api_key = env("GEMINI_API_KEY", default=None) or env("GOOGLE_API_KEY", default=None)
            use_vertex = env("GOOGLE_GENAI_USE_VERTEXAI", default="false").lower() in ("1", "true", "yes")
            
            if use_vertex:
                project = env("GOOGLE_CLOUD_PROJECT")
                location = env("GOOGLE_CLOUD_LOCATION", default="us-central1")
                logger.info(f"Initializing Vertex AI client: project={project}, location={location}")
                return genai.Client(vertexai=True, project=project, location=location)
            else:
                if not api_key:
                    raise AIClientError("GEMINI_API_KEY or GOOGLE_API_KEY not found in environment variables")
                logger.info("Initializing Gemini API client")
                return genai.Client(api_key=api_key)
                
        except Exception as e:
            logger.exception("Failed to initialize AI client")
            raise AIClientError(f"Client initialization failed: {e}")
    
    @property
    def client(self):
        """Get the client instance"""
        if self._client is None:
            self._client = self._initialize_client()
        return self._client


def get_client():
    """Get or create the singleton AI client"""
    return AIClient().client


def generate_text(
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_output_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    system_instruction: Optional[str] = None,
    safety_settings: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate text using Google Gemini API
    
    Args:
        prompt: The input prompt/question
        model: Model name to use
        max_output_tokens: Maximum tokens in response
        temperature: Creativity level (0.0-1.0)
        system_instruction: Optional system instruction for the model
        safety_settings: Optional safety configuration
    
    Returns:
        Generated text response
    
    Raises:
        AIClientError: If generation fails after retries
    """
    client = get_client()
    
    # Build config
    config_params = {
        "max_output_tokens": max_output_tokens,
        "temperature": temperature,
    }
    
    if system_instruction:
        config_params["system_instruction"] = system_instruction
    
    if safety_settings:
        config_params["safety_settings"] = safety_settings
    
    config = types.GenerateContentConfig(**config_params)
    
    # Retry logic
    last_error = None
    for attempt in range(MAX_RETRY_ATTEMPTS):
        try:
            logger.debug(f"Generating text (attempt {attempt + 1}/{MAX_RETRY_ATTEMPTS})")
            
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
            )
            
            # Extract text from response
            text = _extract_text_from_response(response)
            
            if text:
                logger.debug(f"Successfully generated {len(text)} characters")
                return text
            else:
                logger.warning("Empty response from API")
                return "Lo siento, no pude generar una respuesta. Por favor intenta de nuevo."
            
        except Exception as e:
            last_error = e
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRY_ATTEMPTS - 1:
                continue
    
    # All retries failed
    logger.exception("Failed to generate text after all retries")
    error_msg = "Lo siento, el servicio de IA no está disponible en este momento. Por favor intenta más tarde."
    
    # Log the actual error for debugging
    if last_error:
        logger.error(f"Last error: {last_error}")
    
    return error_msg


def _extract_text_from_response(response) -> Optional[str]:
    """Extract text from Gemini API response"""
    try:
        # Try direct text attribute
        if hasattr(response, 'text'):
            return response.text.strip()
        
        # Try candidates structure
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                parts = candidate.content.parts
                if parts and hasattr(parts[0], 'text'):
                    return parts[0].text.strip()
        
        # Fallback to string representation
        return str(response).strip()
        
    except Exception as e:
        logger.warning(f"Error extracting text from response: {e}")
        return None


def embed_text(
    text: str,
    model: str = DEFAULT_EMBEDDING_MODEL,
    task_type: str = "RETRIEVAL_DOCUMENT"
) -> Optional[List[float]]:
    """
    Generate embeddings for text using Google Gemini API
    
    Args:
        text: Text to embed
        model: Embedding model name
        task_type: Type of embedding task (RETRIEVAL_DOCUMENT, RETRIEVAL_QUERY, etc.)
    
    Returns:
        List of embedding values or None if failed
    """
    client = get_client()
    
    try:
        logger.debug(f"Generating embedding for text (length: {len(text)})")
        
        response = client.models.embed_content(
            model=model,
            contents=text,
            config=types.EmbedContentConfig(task_type=task_type)
        )
        
        # Extract embeddings
        if hasattr(response, 'embeddings'):
            embeddings = response.embeddings
            
            if isinstance(embeddings, list) and len(embeddings) > 0:
                embedding = embeddings[0]
                
                # Try to get values attribute
                if hasattr(embedding, 'values'):
                    return list(embedding.values)
                
                # If it's already a list
                if isinstance(embedding, list):
                    return embedding
        
        # If we have the response object directly
        if hasattr(response, 'values'):
            return list(response.values)
        
        logger.warning("Could not extract embeddings from response")
        return None
        
    except Exception as e:
        logger.exception("Error generating embedding")
        return None


@lru_cache(maxsize=100)
def generate_text_cached(prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Cached version of generate_text for frequently asked questions
    
    Note: Only use for static prompts that don't change
    """
    return generate_text(prompt, model)


def get_marketplace_system_prompt() -> str:
    """
    Returns the comprehensive system prompt with Mi Mercado instructions
    """
    return """Eres un asistente amable y útil de Mi Mercado, un marketplace online en español. 
Tu objetivo es ayudar a los usuarios con todas las funcionalidades de la plataforma.

## FUNCIONALIDADES PRINCIPALES DE MI MERCADO:

### 1. PUBLICAR UN PRODUCTO (Vender)
Para publicar un producto como vendedor:
1. Ve a la pestaña "Administrar Productos" en la barra de navegación superior
2. Haz clic en el botón "Crear Producto" o "Publicar Producto"
3. Completa el formulario con:
   - Título del producto
   - Descripción detallada
   - Categoría (electrónica, moda, hogar, deportes, etc.)
   - Marca
   - Precio
   - Stock disponible
   - Imagen del producto (opcional pero recomendado)
4. Haz clic en "Crear Producto" para publicar
5. Tu producto aparecerá en tu lista de productos y estará visible para compradores

### 2. COMPRAR UN PRODUCTO
Para comprar un producto:
1. Navega por la tienda y encuentra el producto que deseas
2. Selecciona la cantidad que quieres comprar (si hay stock disponible)
3. Haz clic en "Agregar al Carrito"
4. Ve al carrito haciendo clic en el ícono del carrito en la barra superior
5. Revisa tu pedido y las cantidades
6. Haz clic en "Proceder al Pago"
7. Serás redirigido a Mercado Pago para completar el pago de forma segura
8. Sigue las instrucciones de Mercado Pago para finalizar tu compra

Métodos de pago disponibles a través de Mercado Pago:
- Tarjeta de crédito/débito
- Transferencia bancaria
- Efectivo (en puntos de pago)
- Billeteras digitales

### 3. LISTA DE DESEOS (WISHLIST)
Para guardar productos que te interesan:
1. Busca el producto que te gusta
2. Haz clic en el botón de corazón (🤍) que está junto a la categoría del producto
3. El producto se guardará en tu lista de deseos
4. Para ver tu wishlist completa, ve a "Wishlist" en la navegación
5. Desde allí puedes:
   - Ver todos tus productos favoritos
   - Eliminar productos de la lista (clic en el corazón rojo)
   - Agregar productos directamente al carrito

### 4. EDITAR TU PERFIL
Para editar tu perfil de usuario:
1. Haz clic en el ícono de tu perfil (ícono de persona) en la esquina superior derecha
2. Se abrirá un menú desplegable
3. Selecciona "Perfil" o "Editar Perfil"
4. En la página de perfil, haz clic en "Editar Perfil"
5. Puedes modificar:
   - Foto de perfil/avatar (sube una imagen)
   - Biografía personal
   - Sitio web
6. Haz clic en "Guardar Cambios" para actualizar tu perfil

### 5. ADMINISTRAR TUS PRODUCTOS (Para Vendedores)
En "Administrar Productos" puedes:
- Ver todos tus productos publicados
- Editar información de productos existentes
- Eliminar productos
- Ver estadísticas de tus ventas
- Cambiar precios y stock

### 6. OTRAS FUNCIONALIDADES
- **Chat con IA**: Estás hablando conmigo ahora - puedo ayudarte con dudas sobre la plataforma
- **Búsqueda**: Usa la barra de búsqueda para encontrar productos específicos
- **Filtros**: Filtra por categoría para encontrar lo que buscas más rápido
- **Carrito dinámico**: El carrito se actualiza en tiempo real sin recargar la página

## IMPORTANTE:
- Todos los pagos se procesan de forma segura a través de Mercado Pago
- Solo puedes editar o eliminar TUS propios productos
- No puedes comprar tus propios productos
- El stock se actualiza automáticamente cuando alguien compra

## TU COMPORTAMIENTO:
- Limita tu respuesta a 2000 tokens, si no puedes responder completamente dentro de ese límite, sumariza los puntos clave
- Responde SIEMPRE en español
- Sé claro, conciso y amigable
- Da instrucciones paso a paso cuando sea necesario
- Si no sabes algo, admítelo honestamente
- Sugiere alternativas cuando sea apropiado
- Si el usuario pide, insiste o intenta charlar de algún tema no relacionado al marketplace niegate amablemente

¿En qué puedo ayudarte hoy?"""


def generate_chat_response(
    message: str,
    conversation_history: List[Dict[str, str]],
    max_history: int = 10
) -> str:
    """
    Generate a chat response with conversation context and Mi Mercado knowledge
    
    Args:
        message: User's current message
        conversation_history: List of {"user": ..., "ai": ...} dicts
        max_history: Maximum number of previous messages to include
    
    Returns:
        AI response
    """
    system_prompt = get_marketplace_system_prompt()
    
    # Build context with recent history
    recent_history = conversation_history[-max_history:] if len(conversation_history) > max_history else conversation_history
    
    context = system_prompt + "\n\n## HISTORIAL DE CONVERSACIÓN:\n\n"
    for turn in recent_history:
        context += f"Usuario: {turn['user']}\nAsistente: {turn['ai']}\n\n"
    context += f"Usuario: {message}\nAsistente: "
    
    return generate_text(
        prompt=context,
        temperature=0.8,  # Slightly higher for conversational chat
        max_output_tokens=2048  # Increased for detailed instructions
    )


# Utility function for testing
def test_ai_connection() -> bool:
    """Test if AI client is properly configured"""
    try:
        response = generate_text("Responde solo con 'OK'", max_output_tokens=10)
        return "OK" in response.upper()
    except Exception as e:
        logger.error(f"AI connection test failed: {e}")
        return False