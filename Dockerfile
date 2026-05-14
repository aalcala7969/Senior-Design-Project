# Official ROS Melodic image (Ubuntu 18.04)
FROM osrf/ros:melodic-desktop

# Install standard dependencies
RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*
    
# Set the working directory to ROS workspace
WORKDIR /catkin_ws

# Copy everything from Jetson to the container
COPY ./catkin_ws/

# Compile ROS nodes
RUN /bin/bash -c "source /opt/ros/melodic/setup.bash && catkin_make"

# When container starts, source workspace and run a bash terminal
CMD ["/bin/bash", "-c", "source devel/setup.bash && bash"]