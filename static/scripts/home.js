document.getElementById('minimize-sidebar').addEventListener('click', function() {
    var sidebar = document.getElementById('sidebar');
    var content = document.getElementById('sidebar-content');
    if (content.style.display === 'none') {
        content.style.display = 'block';
        this.textContent = 'Minimize';
    } else {
        content.style.display = 'none';
        this.textContent = 'Maximize';
    }
});

document.getElementById('minimize-messenger').addEventListener('click', function() {
    var messenger = document.getElementById('messenger');
    var content = document.getElementById('messenger-content');
    if (content.style.display === 'none') {
        content.style.display = 'block';
        this.textContent = 'Minimize';
    } else {
        content.style.display = 'none';
        this.textContent = 'Maximize';
    }
});

function sendQuestion() {
    var question = document.getElementById('question').value;
    fetch('/send_question', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            question: question,
            preview_images: false,
            image_only: false 
        }),
    })
    .then(response => response.json())
    .then(data => {
        var answerSection = document.getElementById('answer-section');
        answerSection.innerHTML = `<p>${data.answer}</p>`;
    })
    .catch(error => console.error('Error:', error));
}

function sendMessage() {
    var question = document.getElementById('message').value;
    fetch('/messages', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            message: message,
        }),
    })
    .then(response => response.json())
    .then(data => {
        var messageSection = document.getElementById('message-section');
        messageSection.innerHTML = `<p>${data.message}</p>`;
    })
    .catch(error => console.error('Error:', error));
}

