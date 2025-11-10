from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from .forms import ChatForm
from .gemini_client import generate_text  # Your AI function
import json

@login_required
def ai_chat(request):
    """AI chat assistant with conversation history"""
    
    # Initialize chat history in session
    if "ai_chat_history" not in request.session:
        request.session["ai_chat_history"] = []
    
    history = request.session["ai_chat_history"]
    
    if request.method == "POST":
        # Handle clear history action
        if 'clear_history' in request.POST:
            request.session["ai_chat_history"] = []
            messages.success(request, 'Historial de chat borrado')
            return render(request, "ai_chat.html", {"form": ChatForm(), "history": []})
        
        form = ChatForm(request.POST)
        if form.is_valid():
            user_msg = form.cleaned_data["message"].strip()
            
            # Prevent empty messages
            if not user_msg:
                messages.warning(request, 'Por favor escribe un mensaje')
                return render(request, "ai_chat.html", {"form": form, "history": history})
            
            # Build context with system prompt and recent history
            system_prompt = (
                "Eres un asistente amable y útil de Mi Mercado, un marketplace online. "
                "Tu objetivo es ayudar a los usuarios con:\n"
                "- Publicar productos para vender\n"
                "- Comprar productos de otros usuarios\n"
                "- Realizar intercambios o trueques\n"
                "- Navegar por la plataforma\n"
                "- Resolver dudas sobre el proceso de compra/venta\n\n"
                "Responde siempre en español de manera clara, concisa y amigable. "
                "Si no sabes algo, admítelo honestamente."
            )
            
            # Keep last 10 messages for context (5 pairs of user-AI)
            recent_history = history[-10:] if len(history) > 10 else history
            
            # Build conversation context
            context = system_prompt + "\n\n"
            for turn in recent_history:
                context += f"Usuario: {turn['user']}\nAsistente: {turn['ai']}\n\n"
            context += f"Usuario: {user_msg}\nAsistente: "
            
            try:
                # Generate AI response
                ai_resp = generate_text(context)
                
                # Validate AI response
                if not ai_resp or ai_resp.strip() == "":
                    ai_resp = "Lo siento, no pude generar una respuesta. ¿Podrías reformular tu pregunta?"
                
                # Save to history with timestamp
                from datetime import datetime
                history.append({
                    "user": user_msg,
                    "ai": ai_resp.strip(),
                    "timestamp": datetime.now().isoformat()
                })
                
                # Limit total history to 50 messages to prevent session bloat
                if len(history) > 50:
                    history = history[-50:]
                
                request.session["ai_chat_history"] = history
                request.session.modified = True
                
                # Clear form after successful submission
                form = ChatForm()
                
            except Exception as e:
                messages.error(request, 'Error al comunicarse con el asistente. Intenta nuevamente.')
                print(f"AI Chat Error: {e}")  # Log for debugging
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = ChatForm()
    
    return render(request, "ai_chat.html", {
        "form": form, 
        "history": history,
        "message_count": len(history)
    })