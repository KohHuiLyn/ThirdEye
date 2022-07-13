//assigning variables 
let camera_button = document.querySelector("#start-camera");
let video = document.querySelector("#video");
let start_button = document.querySelector("#start-record");
let stop_button = document.querySelector("#stop-record");
let download_link = document.querySelector("#download-video");
let pause_start_button=document.querySelector('#pause-resume');
let isPause=false;
let camera_stream = null;
let media_recorder = null;
let blobs_recorded = [];

camera_button.addEventListener('click', async function() {
   	// camera_stream = await navigator.mediaDevices.getUserMedia({ video:{ facingMode: { exact: "environment" } }, audio: false });
    camera_stream = await navigator.mediaDevices.getUserMedia({ video:true, audio: false });
	video.srcObject = camera_stream;
});

start_button.addEventListener('click', function() {
    // set MIME type of recording as video/webm
    media_recorder = new MediaRecorder(camera_stream, { mimeType: 'video/mp4' });

    // event : new recorded video blob available 
    media_recorder.addEventListener('dataavailable', function(e) {
		blobs_recorded.push(e.data);
    });

    // event : recording stopped & all blobs sent
    media_recorder.addEventListener('stop', function() {
    	// create local object URL from the recorded video blobs
    	let video_local = URL.createObjectURL(new Blob(blobs_recorded, { type: 'video/mp4' }));
    	download_link.href = video_local;
    });

    // start recording with each recorded blob having 1 second video
    media_recorder.start(1000);
});

pause_start_button.addEventListener('click',function(){
    if(isPause==false){
        media_recorder.pause();
        let isPause=true
        console.log("vid pause")
    }
    else if(isPause==true){
        media_recorder.resume();
        let isPause=false
        console.log("vid start")
        }

})

stop_button.addEventListener('click', function() {
	media_recorder.stop(); 
});

