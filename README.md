## Parking Space Detection and Storer

This repository contains two Java applications:

1. **ParkingSpaceStorer**: A graphical user interface (GUI) application for marking and saving parking space positions on an image.
2. **ParkingSpaceDetection**: An OpenCV-based application for detecting occupied and free parking spaces from a video feed using predefined positions.

### Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [ParkingSpaceStorer](#parking-space-storer)
  - [ParkingSpaceDetection](#parking-space-detection)
- [Dependencies](#dependencies)
- [License](#license)

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/krishnapree/Real-Time-Street-Parking/
   cd ParkingSpaceDetectionAndStorer
   ```

2. **Install Java Development Kit (JDK)**
   Ensure you have JDK installed. You can download it from [here](https://www.oracle.com/java/technologies/javase-jdk11-downloads.html).

3. **Install OpenCV**
   - Download and install OpenCV from [here](https://opencv.org/releases/).
   - Set up the OpenCV library in your Java environment.

## Usage

### Parking Space Storer

`ParkingSpaceStorer` is a GUI-based Java application that allows users to mark parking spaces on a given image and save these positions for further processing.

#### Running the Application

1. **Compile the Java file:**
   ```bash
   javac ParkingSpaceStorer.java
   ```

2. **Run the application:**
   ```bash
   java ParkingSpaceStorer
   ```

3. **Instructions:**
   - Left-click on the image to mark a parking space.
   - Right-click on an existing marked parking space to remove it.
   - The positions will be saved in the `CarParkPos.ser` file.

### Parking Space Detection

`ParkingSpaceDetection` is a Java application that uses OpenCV to detect occupied and free parking spaces from a video file.

#### Running the Application

1. **Compile the Java file:**
   ```bash
   javac -cp .;path\to\opencv\jar\opencv-450.jar ParkingSpaceDetection.java
   ```

2. **Run the application:**
   ```bash
   java -cp .;path\to\opencv\jar\opencv-450.jar ParkingSpaceDetection
   ```

3. **Instructions:**
   - The program loads the parking positions from the serialized file (`CarParkPos.pkl`).
   - It processes the `carPark.mp4` video file and displays the parking status.
   - Adjust the trackbars to fine-tune the detection parameters.

## Dependencies

1. **Java Development Kit (JDK 8 or higher)**
2. **OpenCV (version 4.5.0 or higher)**
3. **Swing GUI Toolkit (included with JDK)**
4. **Video files and parking space images**
   - `carPark.mp4`: The video file for parking space detection.
   - `carParkImg.jpeg`: The image file for marking parking spaces.
   - `CarParkPos.ser` and `CarParkPos.pkl`: Serialized files containing the parking positions.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Feel free to update the repository URL, dependenc![WhatsApp Image 2024-09-06 at 19 16 09 (1)](https://github.com/user-attachments/assets/851a37f0-893c-4b6b-a8da-503386775e93)
ies, and any other specifics relevant to your project.
