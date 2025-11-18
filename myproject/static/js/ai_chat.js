// Auto-scroll to bottom of chat
function scrollToBottom() {
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// Scroll on page load
document.addEventListener('DOMContentLoaded', scrollToBottom);

// Scroll after form submission (if using AJAX in the future)
document.getElementById('chat-form').addEventListener('submit', function() {
    setTimeout(scrollToBottom, 100);
});

// Suggestion links fill input
document.querySelectorAll('.suggestion-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        document.getElementById('id_message').value = this.textContent.replace(/['"]/g, '');
        document.getElementById('id_message').focus();
    });
});


function toggleExpand(messageId) {
    const bubble = document.querySelector(`.message-bubble[data-message-id="${messageId}"]`);
    if (!bubble) return;
    
    const button = bubble.querySelector('.expand-btn');
    if (!button) return;
    
    bubble.classList.toggle('collapsed');
    
    if (bubble.classList.contains('collapsed')) {
        button.innerHTML = '<i class="bi bi-chevron-down text-light"></i> Ver más';
    } else {
        button.innerHTML = '<i class="bi bi-chevron-up text-light"></i> Ver menos';
    }
}

// Chat initialization function
function initializeChatFeatures() {
    document.querySelectorAll('.message-bubble.collapsible').forEach(bubble => {
        bubble.classList.add('collapsed');
    });
    
    // Auto-scroll to bottom of chat
    const chatContainer = document.getElementById('chat-container');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}