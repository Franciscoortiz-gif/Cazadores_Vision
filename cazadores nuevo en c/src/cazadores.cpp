#include "cazadores.hpp"
#include "crow/http_request.h"
#include "crow/http_response.h"
#include <opencv2/highgui.hpp>
#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>
#include <string>
#include <thread>
#include <vector>

struct image_adjuster{
    cv::Mat img;
    cv::Mat out;
    int min = 0;
    int max = 255;
};
crow::SimpleApp* global_app = nullptr;
void adjust_brigness_and_contrast(int, void* userdata){
    image_adjuster* data = static_cast<image_adjuster*>(userdata);
    int range = data-> max - data-> min;
    if(range < 0) range = 1;
    cv::Mat lut(1, 256, CV_8U);
    uchar* p = lut.ptr();
    for(int j = 0; j < 256; j++){
        float val = static_cast<float>(j - data->min) * 255.0f / static_cast<float>(range);
        p[j] = cv::saturate_cast<uchar>(val);
    }
    cv::LUT(data->img, lut, data->out);
}
cv::Mat sharp(const cv::Mat& src){
    cv::Mat dst;
    cv::Mat kernel = (cv::Mat_<float>(3,3) <<
        0,-1,0,
        -1,5,-1,
        0,-1,0
    );
    cv::filter2D(src,dst,-1,kernel);
    return dst;
}
cv::Mat process_image(cv::Mat& img){
    cv::Mat bin;
    cv::pow(img,2.0,bin);
    cv::blur(bin,bin,cv::Size(3,3));
    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(2,2));
    cv::morphologyEx(bin,bin,cv::MORPH_BLACKHAT, kernel);
    bin = sharp(bin);
    cv::Mat krn = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(5,5));
    cv::dilate(bin,bin,krn);
    return bin;
}
cv::Mat gamma(const cv::Mat& src, double gamma){
    if(gamma < 0)gamma = 0.1;
    cv::Mat lookUpTable(1,256,CV_8U);
    uchar* p = lookUpTable.ptr();
    for(int i=0;i<256;i++){
        double normalize = static_cast<double>(i)/255.0;
        double gammacorrect = std::pow(normalize,gamma);
        p[i] = cv::saturate_cast<uchar>(gammacorrect * 255.0);
    }
    cv::Mat dst;
    cv::LUT(src,lookUpTable,dst);
    return dst;
}
cv::Mat unsharp_mask(const cv::Mat& src, double radius, double ammount){
    cv::Mat blurred, sharpened;
    int ksize = 2 * cvRound(2 * radius) + 1;
    if(ksize % 2 == 0) ksize++;
    cv::GaussianBlur(src,blurred,cv::Size(ksize,ksize),radius,radius);
    double alpha = 1.0 + ammount;
    double beta = -ammount;
    cv::addWeighted(src,alpha,blurred,beta,0.0,sharpened);
    return sharpened;
}

int determine_angle(cv::Rect cord, cv::Mat& img){
    //std::cout << img.rows << std::endl;
    //std::cout << img.cols << std::endl;
    //std::cout << "[ x:" << cord.x << ", y:" << cord.y << ", w:" << cord.width << ", h:" << cord.height << "]" << std::endl;
    cv::Point center(0,0);
    if(cord.width > cord.height){
        //esta hotizontal
        center.x = img.cols / 2;
        center.y = img.rows / 2;
        std::cout << "Horizontal" <<center << std::endl;
        if(cord.y > center.y){
            return 0;
        }else{
            return 180;
        }
    }else{
        //esta vertical
        center.x = img.cols / 2;
        center.y = img.rows / 2;
        std::cout <<"Vertical"<< center << std::endl;
        if(cord.x > center.x){
            return 90;
        }else{
            return 270;
        }
    }
    cv::circle(img,center,10,cv::Scalar(255,255,0),cv::FILLED);
}

/*void debug(){
    cv::Rect cord;
    std::vector<std::vector<cv::Point>> as;
    cv::Mat bin;
    cv::Mat src = cv::imread("im/im0.png");
    cv::Mat xnt = cv::Mat::zeros(src.size(), CV_8UC3);
    std::vector<cv::Mat> ch;
    cv::split(src,ch);
    cv::Mat fin = gamma(ch[2],6.75);
    fin = sharp(fin);
    fin = unsharp_mask(fin,4.0,0.60);
    cv::blur(fin, fin, cv::Size(2,2));
    cv::inRange(fin, 160, 255, fin);
    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(21,21));
    cv::morphologyEx(fin, fin, cv::MORPH_CLOSE,kernel);
    cv::morphologyEx(fin,fin,cv::MORPH_ERODE,cv::getStructuringElement(cv::MORPH_RECT,cv::Size(7,7)));
    std::vector<std::vector<cv::Point>> cont;
    std::vector<cv::Vec4i> hera;
    cv::findContours(fin,cont,hera, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
    cv::Rect glob;
    std::vector<std::vector<cv::Point>> fconts;
    bool first = false;
    for(const auto& co : cont){
        double area = cv::contourArea(co);
        if(area > 5000.0 && area < 10000.0){
                fconts.push_back(co);
                cv::Rect oner = cv::boundingRect(co);
                if(!first){
                    glob = oner;
                    first = true;
                }else{
                    glob = glob | oner;
                }
            }
    }
    if (glob.width > 0 && glob.height > 0) {
        int padding = 10;
        glob.x = std::max(0, glob.x - padding);
        glob.y = std::max(0, glob.y - padding);
        glob.width = std::min(src.cols - glob.x, glob.width + (padding * 2));
        glob.height = std::min(src.rows - glob.y, glob.height+ (padding * 2));}
    cv::drawContours(xnt, fconts,-1, cv::Scalar(255,255,255),cv::FILLED);
    for(const auto& c : fconts){
        double a = cv::contourArea(c);
        std::cout << "area" << a <<std::endl;
        if(a < 6000.0 && a > 5000){
            cord = cv::boundingRect(c);
            cv::circle(xnt, cv::Point(cord.x + (cord.width / 2),cord.y + (cord.height /2)), 3,cv::Scalar(0,255,0), 2);
        }
    } 
    int angle = determine_angle(cord,xnt);
    std::cout << "Angle of bottle" << angle << std::endl;
    std::string text = "Rotacion de la botella " + std::to_string(angle) + " grados";
    cv::putText(src,text,cv::Point(100,100),cv::FONT_HERSHEY_COMPLEX,1.2,cv::Scalar(155,255,0),3);
    cv::imshow("Channel XNT", xnt);
    cv::waitKey(0);
}*/

cv::Mat process(cv::Mat& src){
    cv::Rect cord;
    std::vector<std::vector<cv::Point>> as;
    cv::Mat bin;
    cv::Mat xnt = cv::Mat::zeros(src.size(), CV_8UC3);
    std::vector<cv::Mat> ch;
    cv::split(src,ch);
    cv::Mat fin = gamma(ch[2],6.75);
    fin = sharp(fin);
    fin = unsharp_mask(fin,4.0,0.60);
    cv::blur(fin, fin, cv::Size(2,2));
    cv::inRange(fin, 160, 255, fin);
    cv::Mat kernel = cv::getStructuringElement(cv::MORPH_RECT, cv::Size(21,21));
    cv::morphologyEx(fin, fin, cv::MORPH_CLOSE,kernel);
    cv::morphologyEx(fin,fin,cv::MORPH_ERODE,cv::getStructuringElement(cv::MORPH_RECT,cv::Size(7,7)));
    std::vector<std::vector<cv::Point>> cont;
    std::vector<cv::Vec4i> hera;
    cv::findContours(fin,cont,hera, cv::RETR_EXTERNAL, cv::CHAIN_APPROX_SIMPLE);
    cv::Rect glob;
    std::vector<std::vector<cv::Point>> fconts;
    bool first = false;
    for(const auto& co : cont){
        double area = cv::contourArea(co);
        if(area > 5000.0 && area < 10000.0){
                fconts.push_back(co);
                cv::Rect oner = cv::boundingRect(co);
                if(!first){
                    glob = oner;
                    first = true;
                }else{
                    glob = glob | oner;
                }
            }
    }
    if (glob.width > 0 && glob.height > 0) {
        int padding = 10;
        glob.x = std::max(0, glob.x - padding);
        glob.y = std::max(0, glob.y - padding);
        glob.width = std::min(src.cols - glob.x, glob.width + (padding * 2));
        glob.height = std::min(src.rows - glob.y, glob.height+ (padding * 2));}
    cv::drawContours(xnt, fconts,-1, cv::Scalar(255,255,255),cv::FILLED);
    for(const auto& c : fconts){
        double a = cv::contourArea(c);
        //std::cout << "area" << a <<std::endl;
        if(a < 6000.0 && a > 5000){
            cord = cv::boundingRect(c);
            cv::circle(xnt, cv::Point(cord.x + (cord.width / 2),cord.y + (cord.height /2)), 3,cv::Scalar(0,255,0), 2);
        }
    } 
    int angle = determine_angle(cord,xnt);
    //std::cout << "Angle of bottle" << angle << std::endl;
    std::string text = "Rotacion de la botella " + std::to_string(angle) + " grados";
    cv::putText(src,text,cv::Point(10,50),cv::FONT_HERSHEY_COMPLEX,1.0,cv::Scalar(155,255,0),2);
    return xnt;
}

void signal_handler(int signal) {
    if (signal == SIGINT && global_app) {
        std::cout << "\n[Señal] Ctrl+C detectado. Apagando servidor Crow de forma limpia...\n";
        global_app->stop(); // Detiene el servidor y permite que el main continúe al return
    }
}

std::string read_file(const std::string& path) {
    std::ifstream in(path, std::ios::in | std::ios::binary);
    if (!in) return "";
    return std::string((std::istreambuf_iterator<char>(in)), std::istreambuf_iterator<char>());
}

int main(){
    //debug();
    crow::SimpleApp app;
    global_app = &app;
    camera_control camera;
    std::signal(SIGINT, signal_handler);
    while(true) {
        std::cerr << "[Main] Error crítico: No se pudo conectar con la cámara.\n" << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(1000));
        if(camera.initialize())break;
    }

    std::cout << "[Main] Cámara inicializada correctamente.\n";
    CROW_ROUTE(app, "/")
    ([]() {
        std::string html_content = read_file("public/index.html");
        if (html_content.empty()) {
            return crow::response(404, "Error: No se encontró public/index.html");
        }
        crow::response res(html_content);
        res.set_header("Content-Type", "text/html");
        return res;
    });

    // Ruta del Script: Sirve el archivo JavaScript encargado del streaming
    CROW_ROUTE(app, "/stream.js")
    ([]() {
        std::string js_content = read_file("public/stream.js");
        if (js_content.empty()) {
            return crow::response(404, "Error: No se encontró public/stream.js");
        }
        crow::response res(js_content);
        res.set_header("Content-Type", "application/javascript");
        return res;
    });
    
    CROW_ROUTE(app, "/styles.css")
    ([]() {
        std::string css_content = read_file("public/styles.css");
        if (css_content.empty()) return crow::response(404, "Error: No se encontró public/styles.css");
        
        crow::response res(css_content);
        res.set_header("Content-Type", "text/css"); // <-- Importante para que el navegador lo aplique
        return res;
    });
    CROW_ROUTE(app,"/api/debug")
    ([&camera](const crow::request& req){
       auto val = req.url_params.get("isactive"); 
       return crow::response(200,"a");
    });
    CROW_ROUTE(app,"/api/config")
    ([&camera](const crow::request& req){
       auto typefilter = req.url_params.get("filter");
       return crow::response(200,"Ok"); 
    });

    CROW_ROUTE(app, "/api/v1/camera/mode/loop")
    ([&camera]() {
        camera.setMode(mode::LOOP);
        return crow::response(200, "Modo continuo (LOOP) activado.");
    });

    // Endpoint 2: Cambiar a modo Trigger por Software (Disparo bajo demanda)
    CROW_ROUTE(app, "/api/v1/camera/run-once")
    ([&camera]() {
        if(camera.get_mode() != mode::RUN_ONCE)camera.setMode(mode::RUN_ONCE);
        while(true){
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            if(camera.get_hardware_mode() == 1)break;
        }
        cv::Mat img = camera.triggerOneShot();
        if(img.empty())return crow::response(500,"image not found");
        cv::resize(img, img, cv::Size(640,480));
        cv::Mat debug = process(img);
        std::vector<uchar> enc_buff;
        std::vector<int> params = {cv::IMWRITE_JPEG_QUALITY, 80};
        cv::imencode(".jpg", img, enc_buff,params);
        crow::response res;
        res.set_header("Content-Type", "image/jpeg");
        res.body = std::string(enc_buff.begin(),enc_buff.end());
        return res;
    });

    // Endpoint 3: Obtener imagen (Se adapta automáticamente según el modo activo)
    CROW_ROUTE(app, "/api/v1/camera/frame")
    ([&camera]() {
        cv::Mat frame;
        if (camera.get_mode() != mode::LOOP){
            camera.setMode(mode::LOOP);
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
         }
        frame = camera.get_frameLoop();
        if (frame.empty()) {
            return crow::response(500, "Error: Sensor sin datos disponibles o timeout.");
            std::cout << "vacio" << std::endl;
        }
        cv::resize(frame, frame, cv::Size(640, 480));
        cv::Mat debug = process(frame);
        std::vector<uchar> encoded_buffer;
        std::vector<int> compression_params = { cv::IMWRITE_JPEG_QUALITY, 80 };
        cv::imencode(".jpg", frame, encoded_buffer, compression_params);
        crow::response res;
        res.set_header("Content-Type", "image/jpeg");
        res.body = std::string(encoded_buffer.begin(), encoded_buffer.end());
        return res;
    });
    app.port(18080).multithreaded().run();
    return 0;
}