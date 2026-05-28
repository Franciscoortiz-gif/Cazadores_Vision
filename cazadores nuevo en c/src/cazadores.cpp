#include "cazadores.hpp"

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

void process_image(cv::Mat& img){
    cv::Mat mask = img.clone();
    cv::Mat mask_inv;
    cv::Mat mask_center = cv::Mat::zeros(img.size(), CV_8UC1);
    
    
    cv::inRange(img, cv::Scalar(147),cv::Scalar(255),mask);
    cv::bitwise_not(mask,mask_inv);
    cv::bitwise_and(img,mask_inv,img);
    cv::inRange(img,cv::Scalar(58), cv::Scalar(185),img);

    std::vector<std::vector<cv::Point>> contours;
    std::vector<cv::Vec4i> hierachy;
    cv::findContours(img,contours,hierachy, cv::RETR_TREE, cv::CHAIN_APPROX_NONE);
    for(size_t i = 0; i < contours.size(); i++){
        double area = cv::contourArea(contours[i]);
        cv::Rect box = cv::boundingRect(contours[i]);
        int center_x = img.cols / 2;
        int center_y = img.rows / 2;
        int tolerance = 100;
        cv::Point center_box(box.x + box.width / 2, box.y + box.height / 2);
        
        if(area > 400 && area < 1000){
            if(std::abs(center_box.x - center_x) < tolerance && std::abs(center_box.y - center_y) < tolerance){
                cv::drawContours(mask_center, contours, static_cast<int>(i), cv::Scalar(255), cv::FILLED);
            }
        }
    }
    cv::bitwise_and(img,mask_center,img);
}

void debug(){
    image_adjuster data;
    std::vector<std::string> path_im = {"im/1.png","im/2.png","im/3.png"};
    std::vector<cv::Mat> imgs;
    for(size_t i=0; i < path_im.size(); i++){
        cv::Mat img = cv::imread("im/1.png", 0);
        imgs.push_back(img); 
    }
    for(size_t j=0;j<imgs.size();j++){
        data.img = imgs[j];
        if(data.img.empty()){
            std::cout<<"Fallo al cargar la imagen"<<std::endl;
            return;
        }
        data.min = 65;
        data.max = 135;
        adjust_brigness_and_contrast(0, &data);
        process_image(data.out);
        cv::imshow("Cazadores" + std::to_string(j),data.out);
        cv::waitKey(0);
    }
}

int main(){
    debug();
    return 0;
}