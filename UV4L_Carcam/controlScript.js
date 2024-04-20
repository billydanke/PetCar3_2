// PetCar Control Script by Aaron Barrett 8/2/21
// References joy.js by Robert D'Amico (Bobboteck) 9/6/20

// Movement Variables
var JoyMovement = new JoyStick('joyDiv');

var nightVisionText = document.getElementById('nightVisionText');

var batteryPercentText = document.getElementById('batteryPercentageLabel')
var batteryVoltageText = document.getElementById('batteryVoltageLabel')
var batteryIcon = document.getElementById('batteryIcon')

var connectionButton = document.getElementById('connectionButton')
var connectionIcon = document.getElementById('connectionIcon')

var lastXCoord;
var lastYCoord;

var isNightVisionEnabled = false;

function ReturnCoordinates() {

	xCoord = JoyMovement.GetX();
	yCoord = JoyMovement.GetY();

	if(xCoord != lastXCoord || yCoord != lastYCoord) {

		if(typeof datachannel != "undefined" && datachannel != null) {
			send_message("m " + xCoord + " " + yCoord);
		}

		lastXCoord = xCoord;
		lastYCoord = yCoord;
	}
}

// Servo Control Functions

document.addEventListener("keydown", onKeyDown, false);
document.addEventListener("keyup", onKeyUp, false);

function onKeyDown(event)
	 {
		switch(event.code) {
			case "ArrowUp":
				// Up
				upPress(10);
                document.getElementById('panUp').style.backgroundColor = '#e44d26';
				break;
			case "ArrowDown":
				// Down
				downPress(10);
                document.getElementById('panDown').style.backgroundColor = '#e44d26';
				break;
			case "ArrowLeft":
				// Left
				leftPress(10);
                document.getElementById('panLeft').style.backgroundColor = '#e44d26';
				break;
			case "ArrowRight":
				// Right
				rightPress(10);
                document.getElementById('panRight').style.backgroundColor = '#e44d26';
				break;
            case "KeyC":
                // Recenter
                recenterPress();
                document.getElementById('recenter').style.backgroundColor = '#e44d26';
                break;
            case "KeyN":
                // Toggle Nightvision
                toggleNightVision();
                document.getElementById('nightVisionButton').style.backgroundColor = '#e44d26';
                break;
		}
	 }

	 function onKeyUp(event)
	 {
		switch(event.code) {
			case "ArrowUp":
				// Up
                document.getElementById('panUp').style.backgroundColor = '#202020';
				break;
			case "ArrowDown":
				// Down
                document.getElementById('panDown').style.backgroundColor = '#202020';
				break;
			case "ArrowLeft":
				// Left
                document.getElementById('panLeft').style.backgroundColor = '#202020';
				break;
			case "ArrowRight":
				// Right
                document.getElementById('panRight').style.backgroundColor = '#202020';
				break;
            case "KeyC":
                // Recenter
                document.getElementById('recenter').style.backgroundColor = '#202020';
                break;
            case "KeyN":
                // Toggle Nightvision
                document.getElementById('nightVisionButton').style.backgroundColor = '#202020';
                break;
		}
	 }

function upPress(amt) {
    console.log("Servo Up Pressed")
    if(typeof datachannel != "undefined" && datachannel != null) {
	    send_message("s u " + amt.toString());
    }
}

function downPress(amt) {
    console.log("Servo Down Pressed")
    if(typeof datachannel != "undefined" && datachannel != null) {
	    send_message("s d " + amt.toString());
    }
}

function leftPress(amt) {
    console.log("Servo Left Pressed")
    if(typeof datachannel != "undefined" && datachannel != null) {
	    send_message("s l " + amt.toString());
    }
}

function rightPress(amt) {
    console.log("Servo Right Pressed")
    if(typeof datachannel != "undefined" && datachannel != null) {
	    send_message("s r " + amt.toString());
    }
}

function recenterPress() {
    console.log("Servo Recenter Pressed")
    if(typeof datachannel != "undefined" && datachannel != null) {
        send_message("s c");
    }
}

// Nightvision Control Functions
function queryNightVisionState() {
    if(typeof datachannel != "undefined" && datachannel != null) {
        send_message("n QUERY")
    }
}

function handleNightVisionStateUpdate(state) {
    if(state == "NVSTATE ON") {
        isNightVisionEnabled = true;
        // whatever settings on the ui need to be changed can go here
        nightVisionText.innerHTML = 'ON';
        nightVisionText.style.color = 'greenyellow';
    }
    else if(state == "NVSTATE OFF") {
        isNightVisionEnabled = false;
        // whatever settings on the ui need to be changed can go here
        nightVisionText.innerHTML = 'OFF';
        nightVisionText.style.color = 'orangered';
    }
}

function toggleNightVision() {
    console.log("Night Vision Toggle Pressed")
    if(typeof datachannel != "undefined" && datachannel != null) {
        if(!isNightVisionEnabled) {
            send_message("n ON");
            isNightVisionEnabled = true;
            nightVisionText.innerHTML = 'ON';
            nightVisionText.style.color = 'greenyellow';
        }
        else {
            send_message("n OFF");
            isNightVisionEnabled = false;
            nightVisionText.innerHTML = 'OFF';
            nightVisionText.style.color = 'orangered';
        }
    }
}

// Battery Functions
function queryBatteryState() {
    if(typeof datachannel != "undefined" && datachannel != null) {
        send_message("b QUERY");
    }
}

function handleBatteryStateUpdate(voltage) {
    var range = 8.4 - 6
    var distanceFromEmpty = voltage - 6
    var percentage = (distanceFromEmpty / range) * 100;

    batteryPercentText.innerHTML = percentage.toFixed(2) + "%";
    batteryVoltageText.innerHTML = voltage.toFixed(2) + " V";

    if(percentage > 75) {
        batteryIcon.src = "images/batteryHighIconWhite.png";
    }
    else if(percentage > 50) {
        batteryIcon.src = "images/batteryFairIconWhite.png";
    }
    else if(percentage > 25) {
        batteryIcon.src = "images/batteryMedIconWhite.png";
    }
    else {
        batteryIcon.src = "images/batteryLowIconWhite.png";
    }
}

// Connection Functions
function toggleConnection() {
    if(signalObj) {
        // close the connection
        window.CloseConnection();
        connectionIcon.src = "images/connectionIconRed.png";
        connectionButton.title = "Open Connection";
        console.log("Connection Closed.")

        // reset stuff
        nightVisionText.innerHTML = '--';
        nightVisionText.style.color = 'white';

        batteryPercentText.innerHTML = '--%';
        batteryVoltageText.innerHTML = '-- V';
        batteryIcon.src = "images/batteryEmptyIconWhite.png";
    }
    else {
        // open the connection
        window.OpenConnection();
        connectionIcon.src = "images/connectionIconGreen.png";
        connectionButton.title = "Close Connection";
        console.log("Connection Opened.")
    }
}

// Handle Intervals
setInterval(ReturnCoordinates, 100); // update drive position every 100ms
setInterval(queryBatteryState, 10000); // query battery voltage every 10 seconds