---
id: 02-Module-2-Simulation
title: 02 Module 2 Simulation
---

# Module 2: The Digital Twin (Gazebo & Unity)

The development and deployment of complex robotic systems necessitate exhaustive testing in environments that accurately mirror the real world. This process is formalized through the concept of the **Digital Twin**—a comprehensive virtual replica of a physical system, operating environment, and associated processes.

In modern robotics, the creation of a high-fidelity Digital Twin often requires the strategic integration of multiple simulation platforms. Gazebo (for robust, physics-driven backend simulation and ROS integration) and Unity (for GPU-accelerated rendering and advanced Human-Robot Interaction) together form a powerful dual-engine system capable of addressing the full spectrum of development needs.

---

## 2.1 Defining the Robotics Digital Twin

A robotics Digital Twin is more than a 3D model; it is a live, synchronized, and dynamic model that runs parallel to the physical system. It enables predictive analysis, remote control, and algorithm training.

### 2.1.1 Architectural Separation of Concerns

The effective use of a dual-platform Digital Twin hinges on defining the primary roles of each platform:

| Platform | Primary Role | Key Focus Areas | Communication Standard |
| :--- | :--- | :--- | :--- |
| **Gazebo (Classic/Ignition)** | Physics Engine & ROS Integration | Dynamics, Kinematics, Collision, Low-level Sensor Data Generation. | ROS Topics & Services |
| **Unity** | Visualization & Human-Robot Interaction (HRI) | High-fidelity rendering, lighting, user interfaces, VR/AR integration. | ROS-Unity Bridge (e.g., ROS#.NET) |

Gazebo maintains the authoritative state of the robot and environment physics, while Unity consumes this state data (joint positions, pose, sensor feeds) to produce a visually rich environment for operators and developers.

---

## 2.2 Physics Simulation and Environment Building

The fidelity of the Digital Twin begins with accurate modeling of mass, inertia, and frictional properties.

### 2.2.1 Simulation Description Formats (URDF & SDF)

Robot descriptions are typically handled using the Unified Robot Description Format (URDF) in ROS, which defines links, joints, and kinematic chains. However, Gazebo primarily uses the Simulation Description Format (SDF), which extends URDF to include simulation-specific parameters like gravity, friction coefficients, and physics engine selection.

**Key Components of a Physical Model:**

1.  **`<link>`**: Defines a rigid body, containing visual, collision, and inertial properties.
2.  **`<joint>`**: Defines the mechanical connection between links (e.g., revolute, prismatic, fixed).
3.  **`<inertial>`**: Crucial for accurate dynamics, defining the mass (`<mass>`) and the 3x3 Inertia Matrix (`<inertia>`). Incorrect inertial properties lead to unstable and unrealistic movement.

### 2.2.2 Gazebo Environment Setup

Gazebo utilizes the World Definition file (`.world`), an XML format based on SDF, to define global parameters and environmental objects (models).

#### Configuring Physics Parameters

The `<physics>` tag in the world file dictates which physics engine is used and sets global simulation parameters.

```xml
<world name="default">
  <physics name="ode_physics" type="ode">
    <max_step_size>0.001</max_step_size>
    <real_time_factor>1.0</real_time_factor>
    <real_time_update_rate>1000</real_time_update_rate>
    <ode>
      <solver>
        <type>quick</type>
        <iters>50</iters>
        <sor>1.3</sor>
      </solver>
      <constraints>
        <contact_max_correcting_vel>100.0</contact_max_correcting_vel>
      </constraints>
    </ode>
  </physics>
  
  <gravity>0 0 -9.81</gravity> 
  
  </world>
  