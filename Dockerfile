# 1. Base Image: Official ROS Melodic (Ubuntu 18.04)
FROM osrf/ros:melodic-desktop-full

# 2. System Updates & Essential Tools
# We install 'nano' for quick edits and 'python-catkin-tools' for building
RUN apt-get update && apt-get install -y \
    nano \
    git \
    python-catkin-tools \
    python-pip \
    && rm -rf /var/lib/apt/lists/*

# 3. Fix Gazebo Black Screen Issue (Software Rendering)
ENV LIBGL_ALWAYS_SOFTWARE=1

# 4. Automate ROS Environment Setup
# This adds the "source" command to the bash config automatically
RUN echo "source /opt/ros/melodic/setup.bash" >> /root/.bashrc

# 5. Set Default Workspace
WORKDIR /root/catkin_ws