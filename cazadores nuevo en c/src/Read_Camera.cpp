#include "CameraApi.h"
#include "cazadores.hpp"
#include <mutex>
#include <stdexcept>

camera_control::camera_control() : hCamera(0),running(false),act_mode(mode::LOOP) {}
camera_control::~camera_control(){
    camera_control::stop();
}
bool camera_control::initialize(){
    try{
    CameraSdkInit(0);
    iStatus = CameraEnumerateDevice(&tCameraEnumList, &iCameraCounts);
    if(iCameraCounts == 0)return false;
    iStatus = CameraInit(&tCameraEnumList, -1,-1,&hCamera);
    if(iStatus != CAMERA_STATUS_SUCCESS){std::cout<< iStatus <<std::endl; return false;}
    CameraGetCapability(hCamera, &tCapability);
    g_pRgbBuffer = (unsigned char*)malloc(tCapability.sResolutionRange.iHeightMax*tCapability.sResolutionRange.iWidthMax*3);
    CameraSetTriggerMode(hCamera,0);
    CameraPlay(hCamera);
    channels = 3;
    CameraSetIspOutFormat(hCamera, CAMERA_MEDIA_TYPE_BGR8);
    running = true;
    tcapture = std::thread(&camera_control::loopCapture, this);
    return true;
    }catch (std::runtime_error& error){
        std::cout << "No se logro conectar con la camara" << error.what() << std::endl;
        return false;
    }catch (...){
        return false;
    }
}

void camera_control::setMode(mode newMode){
    std::lock_guard<std::mutex> lock(operation);
    if(act_mode.load() == newMode)return;
    if(newMode == mode::LOOP){
        CameraSetTriggerMode(hCamera,0);
        CameraPlay(hCamera);
    }else{
        CameraSetTriggerMode(hCamera, 1);
        CameraSetTriggerCount(hCamera, 1);
    }
    act_mode = newMode;
}
int camera_control::get_hardware_mode(){
    std::lock_guard<std::mutex> lock(operation);
    int modeH;
    if(CameraGetTriggerMode(hCamera,&modeH) == CAMERA_STATUS_SUCCESS)return modeH;
    return -1;
}

mode camera_control::get_mode() const {
    return act_mode.load();
}

cv::Mat camera_control::triggerOneShot(){
    if(act_mode.load() != mode::RUN_ONCE){
        return cv::Mat();
    }
    std::lock_guard<std::mutex> lock(operation);
    
    if (CameraSoftTrigger(hCamera) != CAMERA_STATUS_SUCCESS) {
        std::cout << "Camera no success" << std::endl;
        return cv::Mat();
    }

    if (CameraGetImageBuffer(hCamera, &tFrameInfo, &pbyBuffer, 1000) == CAMERA_STATUS_SUCCESS) {
        CameraImageProcess(hCamera,pbyBuffer,g_pRgbBuffer,&tFrameInfo);
        // Mapear el buffer raw (Gris o monocromático)
        cv::Mat raw(cv::Size(tFrameInfo.iWidth, tFrameInfo.iHeight), tFrameInfo.uiMediaType == CAMERA_MEDIA_TYPE_MONO8 ? CV_8UC1 : CV_8UC3, g_pRgbBuffer);
        cv::Mat out = raw.clone(); // Clonar para liberar el hardware rápido
        
        CameraReleaseImageBuffer(hCamera, pbyBuffer);
        return out;
    }
    return cv::Mat();
}

cv::Mat camera_control::get_frameLoop() {
    std::lock_guard<std::mutex> lock(frame_mtx);
    if (last_frame_loop.empty()) return cv::Mat();
    return last_frame_loop.clone();
}

void camera_control::loopCapture() {
    while (running.load()) {
        if (act_mode.load() == mode::LOOP) {
            if (CameraGetImageBuffer(hCamera, &tFrameInfo, &pbyBuffer, 1000) == CAMERA_STATUS_SUCCESS) {
                CameraImageProcess(hCamera,pbyBuffer,g_pRgbBuffer,&tFrameInfo);
                cv::Mat raw(cv::Size(tFrameInfo.iWidth, tFrameInfo.iHeight), tFrameInfo.uiMediaType == CAMERA_MEDIA_TYPE_MONO8 ? CV_8UC1 : CV_8UC3, g_pRgbBuffer);
                
                {
                    std::lock_guard<std::mutex> lock(frame_mtx);
                    last_frame_loop = raw.clone();
                }

                CameraReleaseImageBuffer(hCamera, pbyBuffer);
            }
        } else {
            std::this_thread::sleep_for(std::chrono::milliseconds(20));
        }
    }
}
void camera_control::stop() {
    std::cout << "Saliendo" << std::endl;
    if (running.load()) {
        running = false;
        if (tcapture.joinable()) {
            tcapture.join();
        }
    }
    CameraStop(hCamera);
    CameraUnInit(hCamera);
    hCamera = 0;
    if (g_pRgbBuffer) {
        free(g_pRgbBuffer);
        g_pRgbBuffer = nullptr;
    }
}