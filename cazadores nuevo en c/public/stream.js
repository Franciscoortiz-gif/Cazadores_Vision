const API_URL = "/api/v1/camera/frame";
const REFRESH_RATE_MS = 30; // ~33 FPS teóricos

const streamImg = document.getElementById('live-stream');
const indicator = document.getElementById('indicator');
const cmd_once =  document.getElementById('runonce');
const cmd_run = document.getElementById('run');
const cmd_stop = document.getElementById('stop');
let isLoop = true;
let timeoutId = null;

function fetchNextFrame() {
    if(!isLoop)return;
    const hiddenImg = new Image();
    hiddenImg.onload = function() {
        streamImg.src = this.src;
        indicator.innerText = "Conectado";
        indicator.style.color = "#00e676";
        setTimeout(fetchNextFrame, REFRESH_RATE_MS);
    };
    hiddenImg.onerror = function() {
        indicator.innerText = "Desconectado";
        indicator.style.color = "#ff1744";
        setTimeout(fetchNextFrame, 1000);
    };
    hiddenImg.src = API_URL + "?t=" + new Date().getTime();
}

function fetchOnceFrame(){
    isLoop = false;
    clearTimeout(timeoutId); 

    indicator.innerText = "Tomando la foto";
    indicator.style.color = "#ffc107";

    const disparoUrl = "/api/v1/camera/run-once" + "?t=" + new Date().getTime();
    streamImg.src = disparoUrl; 
    indicator.innerText = "Frame adquirido";
    indicator.style.color = "#0BE35A";
}


window.onload = function() {
    fetchNextFrame();
    cmd_once.addEventListener('click', ()=>{
        fetchOnceFrame();
    });
    cmd_run.addEventListener('click', () =>{
       isLoop = true;
       fetchNextFrame();
    });
    cmd_stop.addEventListener('click', () =>{
        clearTimeout(timeoutId);
        isLoop = false;
    });
    
};
