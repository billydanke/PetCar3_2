var signalObj = 1;

(function() {
    signalObj = null;

    function startPlay() {
        if (signalObj)
            return;
 
        var hostname = location.hostname;
        var address = hostname + ':' + (location.port || (location.protocol === 'https:' ? 443 : 80)) + '/webrtc';
        var protocol = location.protocol === "https:" ? "wss:" : "ws:";
        var wsurl = protocol + '//' + address;

        var video = document.getElementById('v');

        signalObj = new signal(wsurl,
            function (stream) {
                console.log('got a stream!');
                video.srcObject = stream;
                video.play();
            },
            function (error) {
                alert(error);
                signalObj = null;
            },
            function () {
                console.log('websocket closed. bye bye!');
                video.srcObject = null;
                signalObj = null;
            },
            function (message) {
                alert(message);
            }
        );
    }

    function stopPlay() {
        if (signalObj) {
            signalObj.hangup();
            signalObj = null;
        }
    }

    window.addEventListener('DOMContentLoaded', function () {
        // App will call viewPause/viewResume for view status change
        window.viewPause = stopPlay;
        window.viewResume = startPlay;

        var settingsContainer = document.getElementById('settings')
        var dropdownButton = document.getElementById('settingsButton');
        var dropdownMenu = document.getElementById('settingsDropdownContent');
        var dropdownButtonIcon = document.getElementById('settingsIcon');

        dropdownButton.onclick = function() {
            dropdownMenu.style.display = dropdownMenu.style.display === "block" ? "none" : "block";
        }

        window.onclick = function(event) {
            if(!settingsContainer.contains(event.target)) {
                if(dropdownMenu.style.display === "block") {
                    dropdownMenu.style.display = "none";
                }
            }
        }
    });

    window.OpenConnection = startPlay;
    window.CloseConnection = stopPlay;
})();