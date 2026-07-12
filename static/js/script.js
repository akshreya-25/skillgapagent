/* Global Interactive JavaScript: Skill Gap Analysis Agent */

document.addEventListener("DOMContentLoaded", function() {
    // --- 1. DARK MODE TOGGLE ---
    const themeToggleBtn = document.getElementById("theme-toggle");
    const bodyEl = document.body;
    
    // Check local storage for theme setting
    const savedTheme = localStorage.getItem("theme");
    if (savedTheme === "dark") {
        bodyEl.classList.add("dark-theme");
        updateThemeIcon(true);
    }
    
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", function() {
            const isDark = bodyEl.classList.toggle("dark-theme");
            localStorage.setItem("theme", isDark ? "dark" : "light");
            updateThemeIcon(isDark);
        });
    }
    
    function updateThemeIcon(isDark) {
        if (!themeToggleBtn) return;
        const icon = themeToggleBtn.querySelector("i");
        if (isDark) {
            icon.className = "fa-solid fa-sun text-warning";
        } else {
            icon.className = "fa-solid fa-moon";
        }
    }
    
    // --- 2. FLOATING AI CAREER BUDDY DIALOGUE ---
    const chatToggle = document.getElementById("chat-toggle");
    const chatDrawer = document.getElementById("chat-drawer");
    const chatClose = document.getElementById("chat-close");
    const chatForm = document.getElementById("chat-form");
    const chatInput = document.getElementById("chat-input");
    const chatMessages = document.getElementById("chat-messages");
    
    if (chatToggle && chatDrawer) {
        // Toggle open
        chatToggle.addEventListener("click", function() {
            chatDrawer.classList.toggle("open");
            if (chatDrawer.classList.contains("open")) {
                chatInput.focus();
                scrollChatToBottom();
            }
        });
        
        // Close
        chatClose.addEventListener("click", function() {
            chatDrawer.classList.remove("open");
        });
        
        // Chat Form Submit
        chatForm.addEventListener("submit", function(e) {
            e.preventDefault();
            const messageText = chatInput.value.trim();
            if (!messageText) return;
            
            // Append User Message
            appendMessage("User", messageText, "user-msg");
            chatInput.value = "";
            
            // Add typing indicator
            const typingDiv = document.createElement("div");
            typingDiv.className = "chat-message bot-msg typing-indicator-msg";
            typingDiv.innerHTML = '<span class="spinner-grow spinner-grow-sm me-1" role="status"></span>Advisor is thinking...';
            chatMessages.appendChild(typingDiv);
            scrollChatToBottom();
            
            // Send AJAX POST
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: messageText })
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                typingDiv.remove();
                
                if (data.response) {
                    appendMessage("Career Buddy", data.response, "bot-msg");
                } else if (data.error) {
                    appendMessage("Career Buddy", `Error: ${data.error}`, "bot-msg text-danger");
                }
            })
            .catch(err => {
                typingDiv.remove();
                appendMessage("Career Buddy", "Connection offline. Please check your local network.", "bot-msg text-danger");
                console.error("Chat error:", err);
            });
        });
    }
    
    function appendMessage(sender, text, className) {
        if (!chatMessages) return;
        const msgDiv = document.createElement("div");
        msgDiv.className = `chat-message ${className}`;
        
        // Parse simple markdown links if present in response
        let formattedText = text;
        // Escape HTML
        formattedText = formattedText
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
            
        // Simple regex replace for bold **text** -> <strong>text</strong>
        formattedText = formattedText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
        
        // Simple regex replace for bullet lists
        formattedText = formattedText.replace(/^\s*-\s+(.*?)$/gm, "<li>$1</li>");
        formattedText = formattedText.replace(/(<li>.*?<\/li>)/gs, "<ul>$1</ul>");
        // Clean double nested lists
        formattedText = formattedText.replace(/<\/ul>\s*<ul>/g, "");

        // Simple regex for line breaks
        formattedText = formattedText.replace(/\n/g, "<br/>");
        
        msgDiv.innerHTML = formattedText;
        chatMessages.appendChild(msgDiv);
        scrollChatToBottom();
    }
    
    function scrollChatToBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }
});
