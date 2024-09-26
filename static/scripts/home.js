$(document).ready(function() {
    // Establish socket connection
    const socket = io.connect('http://localhost:5000');

    // Event listener for file and question input to toggle ask button
    $('#file, #question').on('input', function() {
        if ($('#file').val() && $('#question').val()) {
            $('#ask').prop('disabled', false);
        } else {
            $('#ask').prop('disabled', true);
        }
    });

    // Handle form submission with AJAX
    $('#uploadForm').on('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        $('#progress-section').html(''); // Clear progress section
        $('#answer-section').html(''); // Clear answer section
        const loading = $('<div class="loading"></div>');
        $('#progress-section').append(loading);

        socket.on('progress', function(data) {
            const progressMessage = $('<p></p>').text(data.message);
            $('#progress-section').append(progressMessage);
        });
        
        $.ajax({
            url: '/query',
            type: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(data) {
                $('#answer-section').html(`<p>${data.answer}</p><p>Response Time: ${data.response_time} seconds</p>`);
                loading.remove(); // Remove loading indicator
            },
            error: function(xhr, status, error) {
                $('#answer-section').html(`<p>Error: ${error}</p>`);
                loading.remove(); // Remove loading indicator
            }
        });
    });


    // Minimize sidebar
    $('#minimize-sidebar').on('click', function() {
        const sidebar = $('#sidebar');
        const content = $('#sidebar-content');
        if (content.is(':visible')) {
            content.hide();
            $(this).text('Maximize');
        } else {
            content.show();
            $(this).text('Minimize');
        }
    });

    // Minimize messenger
    $('#minimize-messenger').on('click', function() {
        const messenger = $('#messenger');
        const content = $('#message-section');
        if (content.is(':visible')) {
            content.hide();
            $(this).text('Maximize');
        } else {
            content.show();
            $(this).text('Minimize');
        }
    });

    // Send message via socket
    $('#sendMsg').on('click', function() {
        socket.send('{{ name }}' + ': ' + $('#message').val());
        $('#message').val(''); // Clear message input
    });

    // Display received message
    socket.on('message', function(msg) {
        $('#message-section').prepend($('<p>').text(msg));
    });
});
