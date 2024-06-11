document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const snapButton = document.getElementById('snap');
    const registerButton = document.getElementById('registerButton');
    const imageDataInput = document.getElementById('imageData');

    let imageCaptured = false;

    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
            video.srcObject = stream;
            video.play();
        });
    }

    snapButton.addEventListener('click', function() {
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);

        const dataURL = canvas.toDataURL('image/png');
        imageDataInput.value = dataURL;
        imageCaptured = true;
        registerButton.style.display = 'inline';
    });
});
