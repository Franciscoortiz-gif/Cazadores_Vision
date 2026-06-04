#include <opencv2/opencv.hpp>
#include <iostream>
#include <vector>
#include <string>
#include <cmath>

struct image_adjuster{
    cv::Mat img;
    cv::Mat out;
    int min = 0;
    int max = 255;
};

cv::Mat process_image(cv::Mat& img);

void adjust_brigness_and_contrast(int, void* userdata);