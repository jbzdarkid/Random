#include <stdio.h>
#include <opencv2/opencv.hpp>
using namespace cv;

// http://docs.opencv.org/2.4/doc/tutorials/gpu/gpu-basics-similarity/gpu-basics-similarity.html
double getPSNR(const Mat& I1, const Mat& I2)
{
    Mat s1;
    absdiff(I1, I2, s1);       // |I1 - I2|
    s1.convertTo(s1, CV_32F);  // cannot make a square on 8 bits
    s1 = s1.mul(s1);           // |I1 - I2|^2

    Scalar s = sum(s1);         // sum elements per channel

    double sse = s.val[0] + s.val[1] + s.val[2]; // sum channels

    if( sse <= 1e-10) // for small values return zero
        return 0;
    else
    {
        double  mse =sse /(double)(I1.channels() * I1.total());
        double psnr = 10.0*log10((255*255)/mse);
        return psnr;
    }
}
// namedWindow("window", 1);
// imshow("window", frames[i]);
// waitKey(10000);

// Method 1: 2x redundancy 
int main(int argc, char* argv[]) {
	fprintf(stdout, "Started run\n");
	VideoCapture video("C:\\Users\\MLH Admin\\Downloads\\mario_race.mp4");
	// VideoCapture video2("C:\\Users\\MLH Admin\\Downloads\\kahmul2.mp4");
	int framelen = (int) video.get(CV_CAP_PROP_FRAME_COUNT);
	// int framelen2 = (int) video2.get(CV_CAP_PROP_FRAME_COUNT);
	// int FRAME_COUNT = min(framelen, framelen2);
	int FRAME_COUNT = framelen;
	int SKIP_SIZE = 30; // 30 FPS video => 1 frame per sec
	int REDUNDANCY = 2;
	
	int j=0;
	int k=-1;
	Mat frames[FRAME_COUNT/SKIP_SIZE];
	for(int i=0; i<FRAME_COUNT; i++) {
		Mat temp;
		video >> temp;
		Mat frame  = temp(Rect(840,   0, 435, 330));
		Mat frame2 = temp(Rect(  0, 335, 435, 330));
		
		if (i % SKIP_SIZE == 0) frames[j++] = frame;
		// fprintf(stdout, "%d %d %d\n", i, j, k);
		if (i % (SKIP_SIZE * REDUNDANCY) == 0) k++;

		double diff = getPSNR(frames[k], frame2);
		// fprintf(stdout, "%d %f\n", i-k*SKIP_SIZE, diff);
		if (diff < 4.0) {
			fprintf(stdout, "Video2 is %d frames behind\n", i-k*SKIP_SIZE);
			fprintf(stdout, "%f\n", diff);
			k = j-1; // Start comparing again from even
		} else if (j > k+30) { // More than 30s behind
			fprintf(stdout, "Couldn't find a match in reasonable time, restarted\n");
			k = j-1;
		}
    }
	video.release(); // close();
	// video2.release(); // close();
}