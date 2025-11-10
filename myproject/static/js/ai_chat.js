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