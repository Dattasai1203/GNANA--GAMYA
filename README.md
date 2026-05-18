# 🤖 Gnana Gamya — AI-Interfaced Interactive & Object-Detecting Robot

> **Project Status:** Development paused (Phase I complete). Codebase preserved for future continuation.

A budget-friendly, AI-powered interactive robot capable of **real-time object detection**, **speech recognition**, **conversational AI**, **text-to-speech** response, and **Gazebo-simulated differential-drive navigation** — built entirely on open-source tools.

Submitted as a Bachelor of Engineering project in **Mechatronics Engineering** at
**Sri Chandrasekharendra Saraswathi Viswa Mahavidyalaya (SCSVMV)**, Kanchipuram — Academic Year 2024–25, Phase I.

---

## 👥 Team

| Name | Roll No | Contribution |
| --- | --- | --- |
| P. Anantha Padmanabban | 11219H001 | Project Report &  AI Brain (YOLOv5, DialoGPT, TTS, ASR)|
| Chittaluri Sai Phani Chandra | 11219H002 | Robot Package (ROS2, Gazebo Simulation, Nav2) |
| Dhulipala Datta Sai | 11219H003 | GitHub Repository & AI Brain (YOLOv5, DialoGPT, TTS, ASR) |

**Guided by:**
- Dr. T. Lakshmibai — HOD, Dept. of Electronics & Instrumentation Engineering
- Dr. T. Sundar — AP/EIE

---

## 📌 Overview

Gnana Gamya is a human-robot interaction (HRI) system that:

- Detects people and objects in real-time using a webcam (YOLOv5)
- Greets users and listens to voice commands (SpeechRecognition + Google Web Speech API)
- Generates context-aware conversational replies (DialoGPT via Hugging Face Transformers)
- Speaks responses aloud (pyttsx3 text-to-speech)
- Displays annotated video feed with bounding boxes (OpenCV)
- Simulates as a differential-drive robot in Gazebo with a 2D LiDAR, RGB camera, and expressive face

The system runs on standard consumer hardware — a laptop with a built-in camera, microphone, and speaker — with zero additional hardware cost.

---

## 🏗️ AI System Architecture

```
Start Program
     |
     v
Initialize Components
(TTS, ASR, DialoGPT, YOLO)
     |
     v
Start Video Capture (Webcam)
     |
     v
Object Detection (YOLO) ----------------------------+
     |                                              |
     v                                              v
"Person" Detected?                    Other Objects Detected?
     |                                              |
     v                                              v
Prompt Greeting ("Hello!")     Announce Detected Objects (TTS)
     |
     v
Listen for User Command (ASR)
     |
     v
Generate Response (DialoGPT)
     |
     v
Speak Response (TTS)
     |
     v
Display Annotated Video Feed
     |
     v
Continue / Exit on 'q' key
```

---

## 🧩 AI Software Modules

### 1. Speech Recognition
- **Library:** `speech_recognition`
- Captures audio via microphone; converts to text using Google Web Speech API
- Handles `UnknownValueError` and `RequestError` gracefully

### 2. Text-to-Speech (TTS)
- **Library:** `pyttsx3`
- Converts AI-generated text responses to spoken audio
- Works fully offline; supports rate, volume, and voice customisation

### 3. Conversational AI
- **Library:** `transformers` (Hugging Face)
- **Model:** `microsoft/DialoGPT-medium`
- Generates contextually coherent responses to user queries
- Maintains conversational context across multiple exchanges

### 4. Object Detection
- **Library:** `ultralytics` (YOLO)
- **Model:** `yolov5su.pt`
- Real-time detection of people and objects from webcam frames
- Triggers greeting interaction when a person enters the frame

### 5. Computer Vision
- **Library:** `cv2` (OpenCV)
- Manages video capture, frame annotation, and display
- Renders bounding boxes and class labels on the live feed

---

## 🤖 Robot Description (ROS 2 / Gazebo Simulation)

Alongside the AI brain, the repo contains a full **differential-drive robot model** for ROS 2 and Gazebo Sim (Ignition). This is the physical/simulated body of Gnana Gamya that the AI brain would eventually control.

### Robot Physical Specifications

| Parameter | Value |
|---|---|
| Chassis dimensions | 335 x 265 x 138 mm |
| Chassis mass | 1.0 kg |
| Drive wheels | 2 x continuous (radius 33 mm, width 26 mm, mass 50 g each) |
| Caster wheel | 1 x fixed front passive wheel (radius 10 mm) |
| Wheel separation | 280 mm |
| Max linear acceleration | 0.33 m/s² |
| Encoder resolution (real) | 3436 counts/rev |
| Arduino serial (real) | /dev/ttyUSB0 @ 57600 baud |

### Sensor Suite

| Sensor | Xacro File | Specifications |
|---|---|---|
| 2D LiDAR | `lidar.xacro` | 360 deg, 1 deg resolution, 0.3-12 m range, 10 Hz, GPU-accelerated |
| RGB Camera | `camera.xacro` | 640x480 R8G8B8, 62 deg FoV, 10 Hz, 0.18 rad downward tilt |
| Depth Camera (optional) | `depth_camera.xacro` | 640x480 RGBD, 0.1-100 m range — swap in via `robot.urdf.xacro` |
| Face (visual only) | `face.xacro` | Decorative eyes and mouth on front face, no sensor data |

### Robot Description Files

```
description/
├── robot.urdf.xacro      <- Top-level entry point (include this in launch files)
├── robot_core.xacro      <- Chassis, drive wheels, caster wheel, materials
├── inertial_macros.xacro <- Reusable inertia macros (sphere, box, cylinder)
├── camera.xacro          <- RGB camera sensor (default)
├── depth_camera.xacro    <- RGBD depth camera (optional swap)
├── lidar.xacro           <- 2D GPU LiDAR
├── face.xacro            <- Decorative face (eyes + mouth)
├── gazebo_control.xacro  <- DiffDrive plugin (use_ros2_control:=false)
└── ros2_control.xacro    <- ros2_control hardware interfaces (sim + real robot)
```

### Launch Files

| File | Purpose |
|---|---|
| `rsp.launch.py` | Robot State Publisher — processes URDF, base for all other launches |
| `launch_sim.launch.py` | **Full Gazebo simulation** — RSP + Gazebo + controllers + bridge + joystick |
| `launch_robot.launch.py` | **Real robot** — RSP + ros2_control + controllers (no Gazebo) |
| `joystick.launch.py` | Gamepad teleoperation (joy + teleop_twist_joy + twist_stamper) |
| `camera.launch.py` | USB camera driver for real robot (v4l2_camera) |
| `rplidar.launch.py` | RPLidar serial driver for real robot |
| `online_async_launch.py` | SLAM Toolbox — build or load a map |
| `localization_launch.py` | Nav2 AMCL — localise within a saved map |
| `navigation_launch.py` | Full Nav2 stack — path planning + DWB controller |

```bash
# Gazebo simulation (default empty world)
ros2 launch gnanagamya launch_sim.launch.py

# Gazebo with obstacle world
ros2 launch gnanagamya launch_sim.launch.py world:=worlds/obstacleworld.sdf

# Real robot
ros2 launch gnanagamya launch_robot.launch.py

# Build a map with SLAM Toolbox
ros2 launch gnanagamya online_async_launch.py use_sim_time:=true

# Navigate autonomously (after saving a map)
ros2 launch gnanagamya localization_launch.py map:=/path/to/map.yaml
ros2 launch gnanagamya navigation_launch.py use_sim_time:=true
```

### ROS 2 Topics

| Topic | Message Type | Description |
|---|---|---|
| `/cmd_vel` | geometry_msgs/Twist | Drive command input |
| `/odom` | nav_msgs/Odometry | Odometry output |
| `/scan` | sensor_msgs/LaserScan | LiDAR scan data |
| `/camera/image_raw` | sensor_msgs/Image | RGB camera frames |
| `/camera/camera_info` | sensor_msgs/CameraInfo | Camera calibration |
| `/joint_states` | sensor_msgs/JointState | Wheel joint positions and velocities |
| `/tf` | tf2_msgs/TFMessage | Transform tree (odom -> base_link) |

### ROS 2 Package Dependencies

```bash
sudo apt install ros-<distro>-gz-ros2-control
sudo apt install ros-<distro>-diff-drive-controller
sudo apt install ros-<distro>-joint-state-broadcaster
# Real robot only:
sudo apt install ros-<distro>-diffdrive-arduino
```

---

## 🛠️ Hardware Requirements

| Component | Specification | Notes |
|---|---|---|
| Computer | Any PC/Laptop with internet | For running ML models |
| Camera | USB Webcam, 720p minimum | Built-in or external |
| Microphone | USB Microphone | Noise-cancelling preferred |
| Speaker | USB or Bluetooth Speaker | Built-in works fine |

---

## 💻 Software Requirements

- Python 3.8 or later
- ROS 2 (Humble or later) and Gazebo Sim — required only for robot simulation

### Python Dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Getting Started

### Running the AI Brain (no ROS required)

```bash
# 1. Clone the repository
git clone https://github.com/saiphanichandra/gamya.git
cd gamya

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Run (YOLO model auto-downloads on first run)
python src/gnana_gamya.py
```

Press **`q`** in the video window to exit.

### Running the Robot Simulation (ROS 2 + Gazebo)

```bash
# Place the package in your ROS 2 workspace
cd ~/ros2_ws/src
git clone https://github.com/saiphanichandra/gamya.git gnanagamya

# Build
cd ~/ros2_ws
colcon build --packages-select gnanagamya
source install/setup.bash

# Launch (see launch/ directory for available launch files)
ros2 launch gnanagamya <your_launch_file>.py
```

---

## 📁 Complete Repository Structure

```
gamya/
├── src/
│   └── gnana_gamya.py                  # AI brain: YOLO + DialoGPT + TTS + ASR
│
├── description/                        # ROS 2 robot URDF/Xacro model
│   ├── robot.urdf.xacro                # Top-level entry point
│   ├── robot_core.xacro                # Chassis, drive wheels, caster, materials
│   ├── inertial_macros.xacro           # Reusable inertia macros
│   ├── camera.xacro                    # RGB camera sensor (default)
│   ├── depth_camera.xacro              # RGBD depth camera (optional swap)
│   ├── lidar.xacro                     # 2D GPU LiDAR
│   ├── face.xacro                      # Decorative eyes + mouth
│   ├── gazebo_control.xacro            # DiffDrive plugin (use_ros2_control:=false)
│   └── ros2_control.xacro              # ros2_control sim + real hardware
│
├── config/
│   ├── my_controllers.yaml             # diff_drive + joint_state_broadcaster
│   ├── gaz_ros2_ctl_use_sim.yaml       # Sim time flag for controller_manager
│   ├── gz_bridge.yaml                  # Gazebo <-> ROS 2 topic bridge map
│   ├── twist_mux.yaml                  # Velocity command priority mux
│   ├── joystick.yaml                   # Gamepad axes, buttons, speed scaling
│   ├── nav2_params.yaml                # Full Nav2 stack parameters
│   ├── mapper_params_online_async.yaml # SLAM Toolbox (mapping + localisation)
│   ├── main.rviz                       # RViz: simulation viewer (odom frame)
│   ├── map.rviz                        # RViz: navigation/mapping viewer (map frame)
│   └── view_bot.rviz                   # RViz: basic URDF viewer (base_link frame)
│
├── launch/
│   ├── rsp.launch.py                   # Robot State Publisher (base for all launches)
│   ├── launch_sim.launch.py            # Full Gazebo simulation stack
│   ├── launch_robot.launch.py          # Real robot hardware stack
│   ├── joystick.launch.py              # Gamepad teleoperation
│   ├── camera.launch.py                # USB camera (real robot)
│   ├── rplidar.launch.py               # RPLidar driver (real robot)
│   ├── online_async_launch.py          # SLAM Toolbox mapping/localisation
│   ├── localization_launch.py          # Nav2 AMCL localisation (map_server + amcl)
│   └── navigation_launch.py            # Full Nav2 navigation stack
│
├── worlds/
│   ├── empty.world                     # Minimal flat world for basic testing
│   ├── obstacleworld.sdf               # 20 boxes + cylinder + cones for nav testing
│   ├── gui.config                      # Gazebo GUI layout (toolbar, panels)
│   └── server.config                   # Gazebo server plugin defaults
│
├── docs/
│   └── AI_Project_report.pdf           # Full project report (Phase I)
│
├── requirements.txt                    # Python AI dependencies
├── CMakeLists.txt                      # ROS 2 CMake build file
├── package.xml                         # ROS 2 package manifest
└── README.md
```

---

## 🔬 How the AI Works

1. **Startup:** Initialises DialoGPT, YOLO, pyttsx3, and the speech recogniser.
2. **Video loop:** OpenCV continuously reads frames from the webcam.
3. **Detection:** Each frame is passed to YOLO; detected class names are extracted from bounding box results.
4. **Person detected:** If `"person"` appears and hasn't been greeted, the robot says *"Hello! How can I help you?"* via TTS.
5. **Listening:** The microphone is activated; audio is transcribed via Google Web Speech API.
6. **Stop command:** If the user says `"stop"`, the robot says *"Goodbye!"* and exits cleanly.
7. **Response:** All other inputs are fed into DialoGPT; the reply is spoken aloud and printed to console.
8. **Other objects:** Non-person detections are announced when no person is present.
9. **Exit:** Press `q` to release the camera and close all windows.

---

## 📊 Cost Analysis

| Component | Quantity | Cost |
|---|---|---|
| Speaker (Built-in) | 1 | Rs. 0 |
| Microphone (Built-in) | 1 | Rs. 0 |
| USB Camera (Built-in) | 1 | Rs. 0 |
| Software Libraries | 6 | Rs. 0 |
| **Total** | **9** | **Rs. 0** |

The entire system runs on freely available open-source software and existing laptop hardware — total additional cost: nil.

---

## 📚 Literature References

1. Thomaz & Breazeal — *Towards Social Human-Robot Interaction*
2. Bochkovskiy et al. — *YOLOv4: Optimal Speed and Accuracy of Object Detection*
3. Schizas et al. — *Deep Learning-Based Object Detection, Recognition and Tracking for HRI*
4. Tellez & Suleiman — *Face and Object Detection for Human-Robot Interaction*
5. Stone & Veloso — *Human-in-the-Loop Learning for Social Robots*
6. Girshick et al. — *Visual Object Detection Using Convolutional Neural Networks for Robotics*

---

## 🔮 Future Scope

- Fine-tune DialoGPT on domain-specific datasets (museum guide, retail assistant FAQs, etc.)
- Replace DialoGPT with a modern LLM (LLaMA 3, Mistral, Phi-3, etc.)
- Connect the AI brain to ROS 2: publish detected objects and voice commands as ROS topics to drive the robot
- Deploy on Raspberry Pi 5 or NVIDIA Jetson Orin for a fully embedded system
- Integrate the ROS 2 Nav2 navigation stack using the existing LiDAR for autonomous navigation
- Add face recognition to personalise greetings for known individuals
- Upgrade to a vision-language model (e.g. LLaVA) for richer scene understanding and description

---

## 📄 License

Licensed under the [Apache 2.0 License](LICENSE.md).

---

## 🙏 Acknowledgements

Thanks to Dr. Vempathy Kutumba Sastry (Chancellor), Dr. G. Srinivasu (Vice-Chancellor), Dr. G. Sriram (Registrar), Dr. M. Rathinakumar (Dean, E&I), and all faculty at SCSVMV, Kanchipuram for their guidance and support throughout this project.
