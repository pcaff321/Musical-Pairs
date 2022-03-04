

var recordButton = document.getElementById("recordButton");
var addButton = document.getElementById("addButton");
var waveDiv = document.getElementById("waveform");
var playButton = document.getElementById("playButton")
var playing = false;
var paused = false;
var url;

var fileButton = document.getElementById("file-upload-button");
var hiddenInput = document.getElementById("file-upload-input");
fileButton.addEventListener('click', function(){
    hiddenInput.click();
});


let regions = WaveSurfer.regions.create({
        regions: [
        ],
        dragSelection: false,
        slop: 10,
    })

let wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: 'white',
    progressColor: '#FFF',
    barWidth: 0,
    barGap: 0,
    height: 130,
    cursorWidth: 1,
    cursorColor: "white",
    //pixelRatio: 1,
    //scrollParent: true,
    responsive: 1000,
    normalize: true,
    //minimap: true,
    plugins: [
        regions,
        ],
    //  maxCanvasWidth: 100
});

wavesurfer.on("ready",() => {
wavesurfer.regions.clear();
wavesurfer.regions.add(  {
    start: 0,
    end: wavesurfer.getDuration() - (wavesurfer.getDuration() / 60),
    color: 'hsla(200, 50%, 70%, 0.3)',
});
});

// handle event for pre-recorded uploaded audio
function handleFiles(event) {
    var files = event.target.files;
    url = URL.createObjectURL(files[0]);
    wavesurfer.load(url);
}
// event listener for pre-recorded audio upload
hiddenInput.addEventListener("change", handleFiles, false);


function trimLeft() {
    if (!url){
        url = bufferToWave(wavesurfer.backend.buffer, 0, wavesurfer.backend.buffer.length);
    }
    const start = wavesurfer.regions.list[Object.keys(wavesurfer.regions.list)[0]].start.toFixed(2);
    const end = wavesurfer.regions.list[Object.keys(wavesurfer.regions.list)[0]].end.toFixed(2);
    const originalBuffer = wavesurfer.backend.buffer;
    console.log(end, start,end , start,originalBuffer, (end - start) * (originalBuffer.sampleRate * 1))
    var emptySegment = wavesurfer.backend.ac.createBuffer(
        originalBuffer.numberOfChannels,
        //segment duration
        (end - start) * (originalBuffer.sampleRate * 1),
        originalBuffer.sampleRate
    );
    
    for (var i = 0; i < originalBuffer.numberOfChannels; i++) {
        var chanData = originalBuffer.getChannelData(i);
        var segmentChanData = emptySegment.getChannelData(i);
        for (var j = 0, len = chanData.length; j < end * originalBuffer.sampleRate; j++) {
            segmentChanData[j] = chanData[j + (start * originalBuffer.sampleRate)];
        }
    }

    wavesurfer.loadDecodedBuffer(emptySegment); // Here you go!
                // Not empty anymore, contains a copy of the segment!
    console.log(end, start, end-start)
    }

function deleteChunk() {
    if (!url){
        url = bufferToWave(wavesurfer.backend.buffer, 0, wavesurfer.backend.buffer.length);
    }
    // I had to fixed to two decimal if I don't do this not work, I don't know whyyy
    const start = wavesurfer.regions.list[Object.keys(wavesurfer.regions.list)[0]].start.toFixed(2);
    const end = wavesurfer.regions.list[Object.keys(wavesurfer.regions.list)[0]].end.toFixed(2);
    const originalBuffer = wavesurfer.backend.buffer;
    console.log(end, start,end , start,originalBuffer, (end - start) * (originalBuffer.sampleRate * 1))
    var emptySegment = wavesurfer.backend.ac.createBuffer(
        originalBuffer.numberOfChannels,
        (wavesurfer.getDuration() - (end - start)) * (originalBuffer.sampleRate * 1),
        originalBuffer.sampleRate
    );
    console.log("total nueva wave",wavesurfer.getDuration(), end, start)
    
    for (let i = 0; i < originalBuffer.numberOfChannels; i++) {
        let chanData = originalBuffer.getChannelData(i);
        let segmentChanData = emptySegment.getChannelData(i);
        let offset = end * originalBuffer.sampleRate;
        for (let j = 0; j < originalBuffer.length; j++) {
            if (j < (start * originalBuffer.sampleRate)) {
                //TODO: contemplate other cases when the region is at the end
                segmentChanData[j] = chanData[j];
            } else {
                segmentChanData[j] = chanData[offset];
                offset++;
            }
        }
    }
    //wavesurfer.drawer.clearWave();
    
    //wavesurfer.empty();
    // reload()
    wavesurfer.loadDecodedBuffer(emptySegment); // Here you go!
                // Not empty anymore, contains a copy of the segment!
    console.log(end, start, end-start)
    //wavesurfer.drawBuffer();
}


function playRegion() {
    wavesurfer.backend.ac.resume()
    var position = wavesurfer.getCurrentTime();
    if (!playing && paused){
        wavesurfer.regions.list[Object.keys(wavesurfer.regions.list)[0]].play(position)
        paused = false;
    }
    else if (!playing) {
        wavesurfer.regions.list[Object.keys(wavesurfer.regions.list)[0]].play()
    }
    else {
        wavesurfer.pause()
        paused = true;
    }
}

function togglePlay() {
    if (playing){
        playing = false;
    }
    else {
        playing = true
    }
}

wavesurfer.on("stop", function() {
    togglePlay();
    paused = false;
});

wavesurfer.on("play", function() {
    togglePlay();
});

wavesurfer.on("pause", function() {
    togglePlay();
});


function revert(){
    wavesurfer.load(url);

setTimeout(()=>{},1200)
}


//FOR RECORD

var options = {
    width: 700,
    height: 130,
    plugins: {
        wavesurfer: {
            backend: 'WebAudio',
            waveColor: 'black',
            progressColor: 'black',
            displayMilliseconds: true,
            debug: true,
            cursorWidth: 1,
            hideScrollbar: true,
            plugins: [
                // enable microphone plugin
                WaveSurfer.microphone.create({
                    bufferSize: 4096,
                    numberOfInputChannels: 1,
                    numberOfOutputChannels: 1,
                    constraints: {
                        video: false,
                        audio: true
                    }
                })
            ]
        },
        record: {
            audio: true,
            video: false,
            maxLength: 20,
            displayMilliseconds: true,
            debug: true
            //audioEngine: "libvorbis.js",
            //audioSampleRate: 32000
            //audioEngine: "lamejs",
            //audioWorkerURL: "lib/lamejs/worker-example/worker-realtime.js",
            //audioSampleRate: 44100,
            //audioBitRate: 128
        }
    }
};

var player = videojs('myAudio', options, function() {
// print version information at startup
var msg = 'Using video.js ' + videojs.VERSION +
        ' with videojs-record ' + videojs.getPluginVersion('record') +
        ', videojs-wavesurfer ' + videojs.getPluginVersion('wavesurfer') +
        ' and wavesurfer.js ' + WaveSurfer.VERSION + ' and recordrtc ' + RecordRTC.version;
videojs.log(msg);

console.log("videojs-record is ready!");
});

// error handling
player.on('deviceError', function() {
    console.log('device error:', player.deviceErrorCode);
});

// user clicked the record button and started recording
player.on('startRecord', function() {
    console.log('started recording!');
});

// user completed recording and stream is available
player.on('finishRecord', function() {
    $(".record-container").hide();
    // the blob object contains the recorded data that
    // can be downloaded by the user, stored on server etc.
    console.log('finished recording: ', player.recordedData);
    let fileReader = new FileReader();
    fileReader.addEventListener('load', function(e){
        wavesurfer.loadArrayBuffer(e.target.result)
        }
    );
    fileReader.readAsArrayBuffer(player.recordedData);
    url = null;
    // the following line automatically saves the file to device
    //player.record().saveAs({'audio': 'my-audio-file-name.wav'});
});

player.on('ready', function() {
    player.record().getDevice();
});

function startRecording(event){
    if (!player.record().isRecording() || (player.record().isRecording() && player.record().paused)) {
        player.record().start();
        
        recordButton.style.backgroundColor = "red"
        recordButton.innerText = "Stop"
    } 
    else {
        player.record().stop();
        recordButton.style.backgroundColor = "transparent"
        recordButton.innerHTML = '<i class="fa-solid fa-circle fa-lg"</i>'
}
}

function add_audio(name){

    var li = document.createElement('li');
    var link = document.createElement('a');
    //add controls to the <audio> element 
    
    link.href = audioPlayer.src;
    link.download = name + '.wav';
    link.innerHTML = link.download;
    //add the new audio and a elements to the li element 
    li.appendChild(link);
    //add the li element to the ordered list 

    recordingsList.appendChild(li);
    var source = audioPlayer.src;
    return source;
}


    // Convert a audio-buffer segment to a Blob using WAVE representation
    // The returned Object URL can be set directly as a source for an Auido element.
    // (C) Ken Fyrstenberg / MIT license
    function bufferToWave(abuffer, offset, len, return_blob) {

        var numOfChan = abuffer.numberOfChannels,
        length = len * numOfChan * 2 + 44,
        buffer = new ArrayBuffer(length),
        view = new DataView(buffer),
        channels = [], i, sample,
        pos = 0;

        // write WAVE header
        setUint32(0x46464952);                         // "RIFF"
        setUint32(length - 8);                         // file length - 8
        setUint32(0x45564157);                         // "WAVE"

        setUint32(0x20746d66);                         // "fmt " chunk
        setUint32(16);                                 // length = 16
        setUint16(1);                                  // PCM (uncompressed)
        setUint16(numOfChan);
        setUint32(abuffer.sampleRate);
        setUint32(abuffer.sampleRate * 2 * numOfChan); // avg. bytes/sec
        setUint16(numOfChan * 2);                      // block-align
        setUint16(16);                                 // 16-bit (hardcoded in this demo)

        setUint32(0x61746164);                         // "data" - chunk
        setUint32(length - pos - 4);                   // chunk length

        // write interleaved data
        for(i = 0; i < abuffer.numberOfChannels; i++)
        channels.push(abuffer.getChannelData(i));

        while(pos < length) {
            for(i = 0; i < numOfChan; i++) {             // interleave channels
                sample = Math.max(-1, Math.min(1, channels[i][offset])); // clamp
                sample = (0.5 + sample < 0 ? sample * 32768 : sample * 32767)|0; // scale to 16-bit signed int
                view.setInt16(pos, sample, true);          // update data chunk
                pos += 2;
                }
                offset++                                     // next source sample
            }

            if (return_blob == 1){
                return new Blob([buffer], {type: "audio/wav"})
            }

            // create Blob
            return (URL || webkitURL).createObjectURL(new Blob([buffer], {type: "audio/wav"}));

        function setUint16(data) {
            view.setUint16(pos, data, true);
            pos += 2;
            }

        function setUint32(data) {
            view.setUint32(pos, data, true);
            pos += 4;
            }
        }