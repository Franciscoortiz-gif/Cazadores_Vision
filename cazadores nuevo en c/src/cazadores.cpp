#include <opencv2/core.hpp>
#include <opencv2/core/mat.hpp>
#include <opencv2/core/matx.hpp>
#include <opencv2/core/types.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/photo.hpp>
#include <vector>
#include <iostream>
#include <string>

struct image_adjuster{
    cv::Mat img;
    cv::Mat out;
    int min = 0;
    int max = 255;
};

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

void shiftDFT(cv::Mat& fImage){
    int cx = fImage.cols / 2;
    int cy =  fImage.rows / 2;
    cv::Mat q0(fImage, cv::Rect(0,0,cx,cy)),q1(fImage,cv::Rect(cx,0,cx,cy)),
            q2(fImage, cv::Rect(0,cy,cx,cy)), q3(fImage, cv::Rect(cx,cy,cx,cy));
    cv::Mat tmp;
    q0.copyTo(tmp); q3.copyTo(q0); tmp.copyTo(q3);
    q1.copyTo(tmp); q2.copyTo(q1); tmp.copyTo(q2);
}

cv::Mat bandpass_filter(const cv::Mat& src, double max, double min, int suppresStripes = 1, double tolerance = 5.0){
    cv::Mat padded;
    int m = cv::getOptimalDFTSize(src.rows);
    int n = cv::getOptimalDFTSize(src.cols);
    cv::copyMakeBorder(src,padded,0,m - src.rows, 0,n-src.cols,cv::BORDER_CONSTANT,cv::Scalar::all(0));
    cv::Mat planes[] = {cv::Mat_<float>(padded), cv::Mat::zeros(padded.size(),CV_32F)};
    cv::Mat complex;
    cv::merge(planes,2,complex);
    cv::dft(complex,complex);
    shiftDFT(complex);
    cv::Mat mask = cv::Mat::zeros(complex.size(),CV_32FC2);
    int cx = mask.cols / 2;
    int cy = mask.rows / 2;
    double maxDim = std::max(mask.cols, mask.rows);
    double rLow = (max > 0)? (maxDim / max):0;
    double rHigh = (min > 0)? (maxDim / min):maxDim;
    double toleranceAngle = (tolerance / 100.0) * (CV_PI / 2.0);
    for(int y = 0; y < mask.rows; y++){
        for(int x = 0; x < mask.cols; x++){
            double dx = x - cx;
            double dy = y - cy;
            double distance = std::sqrt(dx*dx + dy*dy);
            if(distance >= rLow && distance <= rHigh){
                mask.at<cv::Vec2f>(y,x)=cv::Vec2f(1.0,1.0);
                if(suppresStripes != 0 && distance > 0){
                    double angle = std::atan2(std::abs(dy), std::abs(dx));
                    if(suppresStripes == 1){
                        if(angle < toleranceAngle || angle > (CV_PI -toleranceAngle)){
                            mask.at<cv::Vec2f>(y,x) = cv::Vec2f(0.0f,0.0f);
                        }
                    }
                    else if(suppresStripes == 2){
                        if(std::abs(angle - CV_PI/2) < toleranceAngle){
                            mask.at<cv::Vec2f>(y, x) = cv::Vec2f(0.0f, 0.0f);
                        }
                    }
                }
            }
        }
    }

    cv::multiply(complex, mask, complex);
    shiftDFT(complex);
    cv::idft(complex, complex);

    cv::split(complex, planes);
    cv::Mat restored;
    cv::magnitude(planes[0], planes[1], restored);
    cv::Mat croppedRestored = restored(cv::Rect(0, 0, src.cols, src.rows));
    croppedRestored += cv::Scalar(128.0);
    double minVal, maxVal;
    cv::minMaxLoc(croppedRestored, &minVal, &maxVal);
    if (maxVal - minVal == 0) maxVal += 0.001;
    cv::Mat final8U;
    croppedRestored.convertTo(final8U, CV_8U, 255.0 / (maxVal - minVal), -minVal * (255.0 / (maxVal - minVal)));

    return final8U;
}

int determine_angle(cv::Rect cord, cv::Mat& img){
    std::cout << img.rows << std::endl;
    std::cout << img.cols << std::endl;
    std::cout << "[ x:" << cord.x << ", y:" << cord.y << ", w:" << cord.width << ", h:" << cord.height << "]" << std::endl;
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

void debug(){
    cv::Rect cord;
    std::vector<std::vector<cv::Point>> as;
    cv::Mat bin;
    cv::Mat src = cv::imread("im/im0.png");
    //cv::rotate(src,src, cv::ROTATE_90_CLOCKWISE);    
    //cv::rotate(src,src, cv::ROTATE_180);
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
    //xnt = xnt(glob); 
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
    cv::imshow("Channel XNT", src);
    cv::waitKey(0);
}

int main(){
    debug();
    return 0;
}