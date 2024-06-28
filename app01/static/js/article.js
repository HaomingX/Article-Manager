document.addEventListener('DOMContentLoaded', function() {
    var replyButtons = document.querySelectorAll('.reply-btn');
    replyButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var commentId = this.getAttribute('data-comment-id');
            var replyForm = document.getElementById('reply-form-' + commentId);
            if (replyForm.style.display === 'none') {
                replyForm.style.display = 'block';
            } else {
                replyForm.style.display = 'none';
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var comments = document.querySelectorAll('.comment, .comment-reply');
    comments.forEach(function(comment) {
        var level = parseInt(comment.getAttribute('data-level'));
        console.log(level);
        comment.style.marginLeft = (level * 20) + 'px'; // 设置缩进，每级增加20px
        comment.style.backgroundColor = 'hsl(' + (200 + (level * 10)) + ', 20%, 90%)'; // 设置背景色
    });
});


document.addEventListener('DOMContentLoaded', function() {
    // 如果用户未登录，隐藏所有 reply 按钮
    if (!userIsAuthenticated) {
        document.querySelectorAll('.reply-btn').forEach(function(button) {
            button.style.display = 'none';
        });
    } else {
        // 用户登录时的 hover 逻辑
        $('.comment-content-reply').hover(
            function() {
                $(this).find('.reply-btn').fadeIn(); // Show reply button on hover
            },
            function() {
                $(this).find('.reply-btn').fadeOut(); // Hide reply button on mouse leave
            }
        );
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('send-button');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');

    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });

    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        appendMessage('user', message);
        userInput.value = '';

        fetch(chat_api_url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ message: message, article_id: articleId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.reply) {
                appendMessage('bot', data.reply);
            }
        });
    }

    function appendMessage(sender, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', sender);
        const label = document.createElement('strong');
        label.classList.add('label');
        label.textContent = sender === 'user' ? 'User: ' : 'LLM: ';
        messageElement.appendChild(label);
        const text = document.createElement('span');
        text.textContent = message;
        messageElement.appendChild(text);
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
