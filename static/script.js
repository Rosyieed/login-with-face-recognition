document.addEventListener('DOMContentLoaded', function() {
    const video = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const snapButton = document.getElementById('snap');
    const status = document.getElementById('status');

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
        const password = document.getElementById('password').value;
        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: dataURL, password: password }),
        })
        .then(response => response.json())
        .then(data => {
            status.textContent = data.status === 'success' ? `Welcome, ${data.user}` : 'Access Denied';
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
