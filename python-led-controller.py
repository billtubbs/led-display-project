import serial
import time
import numpy as np
from typing import Optional, Union

class LEDMatrixController:
    """
    Controller for sending video data to an Arduino-controlled LED matrix.

    This class handles the communication protocol with an Arduino running
    the FastLED controller code to drive a 40x40 RGB LED matrix.
    """

    def __init__(
        self,
        port: str,
        baud_rate: int = 921600,
        matrix_size: tuple = (100,)
    ):
        """
        Initialize the LED matrix controller.

        Args:
            port: Serial port name (e.g., 'COM3' on Windows,
                '/dev/ttyUSB0' on Linux)
            baud_rate: Serial baud rate (should match Arduino
                code)
            matrix_size: Dimensions of the LED matrix (width,
                height)
        """
        self.port = port
        self.baud_rate = baud_rate
        self.matrix_size = matrix_size
        self.num_pixels = matrix_size[0]
        self.ser = None
        self.connected = False
        self.header_marker = 0xAB  # Must match Arduino code

    def connect(self) -> bool:
        """Connect to the Arduino controller."""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=2.0
            )

            # Wait for Arduino to reset and send ready signal
            time.sleep(2.0)
            #breakpoint()
            #self.ser.reset_input_buffer()

            # Wait for ready signal ('R')
            start_time = time.time()
            while time.time() - start_time < 10.0:
                if self.ser.in_waiting > 0:
                    ready_byte = self.ser.read(1)
                    if ready_byte == b'R':
                        self.connected = True
                        print("Connected to Arduino LED controller")
                        return True
                time.sleep(0.1)

            print("Timed out waiting for Arduino ready signal")
            self.ser.close()
            return False

        except Exception as e:
            print(f"Error connecting to Arduino: {e}")
            return False

    def disconnect(self):
        """Disconnect from the Arduino controller."""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False

    def send_frame(self, frame: np.ndarray, wait_for_ack: bool = True) -> bool:
        """
        Send a single frame to the LED matrix.

        Args:
            frame: Numpy array with shape (height, width, 3) containing RGB values (0-255)
            wait_for_ack: Whether to wait for acknowledgment from Arduino

        Returns:
            True if frame was sent successfully, False otherwise
        """
        if not self.connected or not self.ser or not self.ser.is_open:
            print("Not connected to Arduino")
            return False

        # Ensure frame has the right dimensions
        if frame.shape != (self.matrix_size[0], 3):
            print(f"Frame has wrong dimensions: {frame.shape}, expected "\
                  f"{(self.matrix_size[0], 3)}")
            return False

        try:
            # Send header marker to signal start of new frame
            self.ser.write(bytes([self.header_marker]))

            # Flatten frame data row by row and send as bytes
            flattened = frame.reshape(-1, 3).astype(np.uint8)

            # Send all pixel data
            self.ser.write(flattened.tobytes())

            # Wait for acknowledgment if required
            if wait_for_ack:
                start_time = time.time()
                while time.time() - start_time < 1.0:
                    if self.ser.in_waiting > 0:
                        ack_byte = self.ser.read(1)
                        if ack_byte == b'A':
                            return True
                    time.sleep(0.001)
                print("Timed out waiting for frame acknowledgment")
                return False

            return True

        except Exception as e:
            print(f"Error sending frame: {e}")
            return False

    def play_video(self, video_data: np.ndarray, fps: int = 24, loop: bool = False) -> None:
        """
        Play a video on the LED matrix.

        Args:
            video_data: Numpy array with shape (frames, height, width, 3)
            fps: Frames per second to play at
            loop: Whether to loop the video
        """
        if not self.connected:
            print("Not connected to Arduino")
            return

        frame_time = 1.0 / fps

        try:
            playing = True
            while playing:
                for frame_idx in range(video_data.shape[0]):
                    start_time = time.time()

                    # Send the frame
                    success = self.send_frame(video_data[frame_idx])
                    if not success:
                        print(f"Failed to send frame {frame_idx}")
                        playing = False
                        break

                    # Calculate sleep time to maintain frame rate
                    elapsed = time.time() - start_time
                    sleep_time = max(0, frame_time - elapsed)
                    if sleep_time > 0:
                        time.sleep(sleep_time)

                if not loop:
                    break

        except KeyboardInterrupt:
            print("Video playback stopped")

        except Exception as e:
            print(f"Error during video playback: {e}")


# Example usage
if __name__ == "__main__":

    # Create test patterns
    def create_test_pattern(pattern_type="rainbow"):
        matrix = np.zeros((100, 3), dtype=np.uint8)

        if pattern_type == "rainbow":
            # Create a rainbow gradient
            for i in range(100):
                hue = i % 255
                # Simple HSV to RGB conversion
                if hue < 85:
                    matrix[i] = [255 - hue * 3, hue * 3, 0]
                elif hue < 170:
                    hue -= 85
                    matrix[i] = [0, 255 - hue * 3, hue * 3]
                else:
                    hue -= 170
                    matrix[i] = [hue * 3, 0, 255 - hue * 3]

        elif pattern_type == "snake":
            # Create a snake pattern
            matrix[:25] = [128, 0, 0]  # Red
            matrix[25:] = [0, 0, 128]  # Blue

        return matrix

    # Create an animated test video (10 frames of shifting rainbow)
    def create_test_video(frames=100):
        video = np.zeros((frames, 100, 3), dtype=np.uint8)
        for i in range(frames):
            pattern = create_test_pattern("snake")
            # Shift the pattern for each frame
            video[i] = np.roll(pattern, i, axis=0)
        return video

    # Connect and send test pattern
    try:
        # Replace with your Arduino's serial port
        controller = LEDMatrixController(port='/dev/cu.usbmodem6862001')

        if controller.connect():
            # Create and send a test video
            # 1 second of animation at 24fps
            test_video = create_test_video(frames=100)

            print("Playing test pattern...")
            controller.play_video(test_video, fps=24, loop=True)

    except KeyboardInterrupt:
        print("Program stopped by user")

    finally:
        if 'controller' in locals():
            controller.disconnect()
