#include "cazadores.hpp"
#include <opencv2/core.hpp>
#include <opencv2/core/mat.hpp>
#include <opencv2/highgui.hpp>
#include <vector>

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
/*void debug(){
    image_adjuster data;
    std::vector<std::string> path_im = {"im/1.png","im/2.png","im/3.png","im/im0.png"};
    std::vector<cv::Mat> imgs;
    for(size_t i=0; i < path_im.size(); i++){
        cv::Mat img = cv::imread("im/1.png", 0);
        cv::resize(img, img,cv::Size(540,540));
        imgs.push_back(img); 
    }
    for(size_t j=0;j<imgs.size();j++){
        data.img = imgs[j];
        if(data.img.empty()){
            std::cout<<"Fallo al cargar la imagen"<<std::endl;` 
            return;
        }
        data.min = 65;
        data.max = 135;
        adjust_brigness_and_contrast(0, &data);
        process_image(data.out);
        cv::imshow("Cazadores" + std::to_string(j),data.out);
        cv::waitKey(0);
    }
}*/

/*void debug(){
    cv::Mat img = cv::imread("im/im0.png");
    if(img.empty())return;
    cv::Mat gamma_adj = gamma(img,9.75);
    cv::Mat sh1 = sharp(gamma_adj);
    cv::Mat ush1 = unsharp_mask(sh1,4.0,0.60);
    cv::Mat hsv;
    cv::cvtColor(ush1,hsv,cv::COLOR_BGR2BGRA);
    std::vector<cv::Mat> channels;
    cv::split(img,channels);
    cv::Mat bin;
    cv::bitwise_not(channels[1],bin);
    image_adjuster data;
    data.img = bin;
    data.min = 220;
    data.max = 253;
    adjust_brigness_and_contrast(0,&data);
    cv::Mat binary;
    binary = process_image(data.out);
    cv::imshow("Gamma", gamma_adj);
    cv::imshow("Sharpness", sh1);
    cv::imshow("UnSharpness", ush1);
    cv::imshow("UnSharpness B", channels[0]);
    cv::imshow("UnSharpness G", channels[1]);
    cv::imshow("UnSharpness R", channels[2]);
    //cv::imshow("UnSharpness A", channels[3]);
    cv::imshow("TH", binary);
    //cv::imshow("Band Filetered", bandFiltered);
    //cv::imshow("Sharpness2", sh2);
    //cv::imshow("Denoise", s);
    cv::waitKey(0);
    cv::destroyAllWindows();

}*/

void debug(){
    cv::Mat src = cv::imread("im/im0.png");
    std::vector<cv::Mat> ch;
    cv::split(src,ch);
    ch[0] = gamma(ch[0],1.75);
    cv::imshow("Channel B", ch[0]);    
    cv::imshow("Channel G", ch[1]);
    cv::imshow("Channel R", ch[2]);
    cv::waitKey(0);
}

int main(){
    debug();
    return 0;
}