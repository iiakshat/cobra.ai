function toggleSlider() {
    var slider = document.getElementById('slider');
    if (slider.classList.contains('minimized')) {
        slider.classList.remove('minimized');
    } else {
        slider.classList.add('minimized');
    }
}

function toggleMessenger() {
    var messenger = document.getElementById('messenger');
    if (messenger.classList.contains('minimized')) {
        messenger.classList.remove('minimized');
    } else {
        messenger.classList.add('minimized');
    }
}

function sendQuestion() {
}

function sendMessage() {
}
