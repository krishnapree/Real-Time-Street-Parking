import org.opencv.core.Core;
import org.opencv.core.CvType;
import org.opencv.core.Mat;
import org.opencv.core.Point;
import org.opencv.core.Scalar;
import org.opencv.core.Size;
import org.opencv.imgproc.Imgproc;
import org.opencv.videoio.VideoCapture;
import org.opencv.videoio.Videoio;
import org.opencv.highgui.HighGui;
import org.opencv.imgcodecs.Imgcodecs;

import java.io.FileInputStream;
import java.io.ObjectInputStream;
import java.util.ArrayList;
import java.util.List;

public class ParkingSpaceDetection {
    static {
        System.loadLibrary(Core.NATIVE_LIBRARY_NAME);
    }

    private static List<Point> posList;
    private static final int width = 103;
    private static final int height = 43;

    public static void main(String[] args) {
        // Load parking positions from serialized file
        try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream("CarParkPos.pkl"))) {
            posList = (List<Point>) ois.readObject();
        } catch (Exception e) {
            e.printStackTrace();
        }

        VideoCapture cap = new VideoCapture("carPark.mp4");
        if (!cap.isOpened()) {
            System.out.println("Error: Could not open video file.");
            return;
        }

        HighGui.namedWindow("Vals", HighGui.WINDOW_NORMAL);
        HighGui.resizeWindow("Vals", 640, 240);

        // Trackbars for dynamic adjustments
        HighGui.createTrackbar("Val1", "Vals", 25, 50, v -> {});
        HighGui.createTrackbar("Val2", "Vals", 16, 50, v -> {});
        HighGui.createTrackbar("Val3", "Vals", 5, 50, v -> {});

        while (true) {
            Mat img = new Mat();
            if (!cap.read(img)) {
                cap.set(Videoio.CAP_PROP_POS_FRAMES, 0);
                continue;
            }

            Mat imgGray = new Mat();
            Imgproc.cvtColor(img, imgGray, Imgproc.COLOR_BGR2GRAY);

            Mat imgBlur = new Mat();
            Imgproc.GaussianBlur(imgGray, imgBlur, new Size(3, 3), 1);

            int val1 = HighGui.getTrackbarPos("Val1", "Vals");
            int val2 = HighGui.getTrackbarPos("Val2", "Vals");
            int val3 = HighGui.getTrackbarPos("Val3", "Vals");

            if (val1 % 2 == 0) val1++;
            if (val3 % 2 == 0) val3++;

            Mat imgThres = new Mat();
            Imgproc.adaptiveThreshold(imgBlur, imgThres, 255, Imgproc.ADAPTIVE_THRESH_GAUSSIAN_C,
                    Imgproc.THRESH_BINARY_INV, val1, val2);

            Imgproc.medianBlur(imgThres, imgThres, val3);

            Mat kernel = Mat.ones(new Size(3, 3), CvType.CV_8U);
            Imgproc.dilate(imgThres, imgThres, kernel);

            checkSpaces(img, imgThres);

            HighGui.imshow("Image", img);
            if (HighGui.waitKey(1) == 27) { // Exit on ESC key
                break;
            }
        }

        cap.release();
        HighGui.destroyAllWindows();
    }

    private static void checkSpaces(Mat img, Mat imgThres) {
        int spaces = 0;

        for (Point pos : posList) {
            int x = (int) pos.x;
            int y = (int) pos.y;

            Mat imgCrop = imgThres.submat(y, y + height, x, x + width);
            int count = Core.countNonZero(imgCrop);

            Scalar color;
            int thic;
            if (count < 900) {
                color = new Scalar(0, 200, 0);
                thic = 5;
                spaces++;
            } else {
                color = new Scalar(0, 0, 200);
                thic = 2;
            }

            Imgproc.rectangle(img, new Point(x, y), new Point(x + width, y + height), color, thic);
            Imgproc.putText(img, String.valueOf(count), new Point(x, y + height - 6),
                    Imgproc.FONT_HERSHEY_PLAIN, 1, color, 2);
        }

        Imgproc.putText(img, "Free: " + spaces + "/" + posList.size(), new Point(50, 60),
                Imgproc.FONT_HERSHEY_PLAIN, 3, new Scalar(0, 200, 0), 3);
    }
}
