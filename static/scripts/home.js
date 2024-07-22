function toggleSlider() {
    var slider = document.getElementById('slider');
    var sliderToggleBtn = document.getElementById('slider-toggle-btn');
    if (slider.classList.contains('minimized')) {
        slider.classList.remove('minimized');
        sliderToggleBtn.textContent = 'Minimise';
    } else {
        slider.classList.add('minimized');
        sliderToggleBtn.textContent = 'Maximise';
    }
}

function toggleMessenger() {
    var messenger = document.getElementById('messenger');
    var messengerToggleBtn = document.getElementById('messenger-toggle-btn');
    if (messenger.classList.contains('minimized')) {
        messenger.classList.remove('minimized');
        messengerToggleBtn.textContent = 'Minimise';
    } else {
        messenger.classList.add('minimized');
        messengerToggleBtn.textContent = 'Maximise';
    }
}

function sendQuestion() {
    var question = $('#question-input').val();
    var previewImages = $('#preview-images').is(':checked');
    var imageOnly = $('#image-only').is(':checked');
    
    $.ajax({
        type: 'POST',
        url: '/send_question',
        data: JSON.stringify({
            'question': question,
            'preview_images': previewImages,
            'image_only': imageOnly
        }),
        contentType: 'application/json',
        success: function(response) {
            $('#answer-text').text(response.answer);
        },
        error: function() {
            $('#answer-text').text('An error occurred while processing your question.');
        }
    });
}

function sendMessage() {
    var message = $('#message-input').val();
    
    // Add the message to the display
    $('#message-display').append('<div>' + message + '</div>');
    
    // Clear the input
    $('#message-input').val('');
}
