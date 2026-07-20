#include <iostream>
#include <fstream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <vector>
#include <atomic>
#include <opencv2/opencv.hpp>
#include <opencv2/core.hpp>
#include <opencv2/core/mat.hpp>
#include <opencv2/core/matx.hpp>
#include <opencv2/core/types.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/photo.hpp>
#include <string>
#include "CameraApi.h"
#include "CameraDefine.h"
#include <crow.h>
#include <csignal>

enum class mode{
    LOOP,
    RUN_ONCE,
};

class camera_control{
    private:
        int iCameraCounts = 1;
        int iStatus=-1;
        tSdkCameraDevInfo tCameraEnumList;
        BYTE* pbyBuffer;
        unsigned char* g_pRgbBuffer;
        int hCamera;
        int channels = 3;
        tSdkCameraCapbility tCapability;
        bool is_initialized = false;
        tSdkFrameHead tFrameInfo;
        std::thread tcapture;
        std::atomic<mode> act_mode{mode::LOOP};
        std::atomic<bool> running = false;
        cv::Mat last_frame_loop;
        std::mutex frame_mtx;
        std::mutex operation;
        void loopCapture();
        void stop();
        
    public:
        camera_control();
        ~camera_control();
        bool initialize();
        void setMode(mode newMode);
        mode get_mode() const;
        cv::Mat triggerOneShot();
        cv::Mat get_frameLoop();
        int get_hardware_mode();
};