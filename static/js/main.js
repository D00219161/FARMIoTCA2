var alive_second = 0;
var heartbeat_rate = 5000;

var myChannel = "Homesafe";

function keep_alive()
{
	var request = new XMLHttpRequest();
	request.onreadystatechange = function(){
		if(this.readyState === 4){
			if(this.status === 200){
				if(this.responseText !== null){
					var date = new Date();
					alive_second = date.getTime();
					var keep_alive_data = this.responseText;
					console.log(keep_alive_data);
				}
			}

		}
	};
	request.open("GET", "keep_alive", true);
	request.send(null);
	setTimeout('keep_alive()', heartbeat_rate);
}

function time(){
	var d = new Date();
	var current_sec = d.getTime();
	if(current_sec - alive_second > heartbeat_rate + 1000){
		document.getElementById("Connection_id").innerHTML = " Dead";
	}
	else{
		document.getElementById("Connection_id").innerHTML = " Alive";
	}
	setTimeout('time()', 1000);
}

function handleClick(cb){
	if(cb.checked)
	{
		value = true;
	}
	else
	{
		value = false;
	}
	var btnStatus = new Object();
	btnStatus[cb.id] = value;
	var event = new Object();
	event.event = btnStatus;
	console.log("Calling publishUpdate from handleClick");
	publishUpdate(event, myChannel);
}

pubnub = new PubNub({
        publishKey : "pub-c-4c71c151-b075-498f-bfbc-c6f3221ed3b6",
        subscribeKey : "sub-c-12924b4c-2f48-11eb-9713-12bae088af96",
        uuid: ""
    })

pubnub.addListener({
        status: function(statusEvent) {
            if (statusEvent.category === "PNConnectedCategory") {
                console.log("Connected to PubNub");
            }
        },
        message: function(message) {
            var msg = message.message;
            console.log(msg);
            document.getElementById("Motion_id").innerHTML = msg["motion"];
        },
        presence: function(presenceEvent) {
        }
    })

pubnub.subscribe({
        channels: [myChannel]
    });

function publishUpdate(data, channel){
    pubnub.publish({
        channel: channel,
        message: data
        },
        function(status, response){
            if(status.error){
                console.log(status)
            }
            else{
                console.log("Message published with timetoken", response.timetoken)
                }
            }
        );
}


