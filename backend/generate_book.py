import os
from dotenv import load_dotenv
import google.generativeai as genai

# 1. Setup
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Woh model jo aapke laptop par chala
model = genai.GenerativeModel('gemini-flash-latest')

# 2. Syllabus (Hackathon Document se liya gaya)
chapters = {
    "01-Module-1-ROS2": """
    Write a detailed technical textbook chapter titled 'Module 1: The Robotic Nervous System (ROS 2)'.
    Cover:
    - Middleware for robot control.
    - ROS 2 Nodes, Topics, and Services.
    - Bridging Python Agents to ROS controllers using rclpy.
    - Understanding URDF (Unified Robot Description Format) for humanoids.
    Include Python code snippets where necessary. Format in Markdown for Docusaurus.
    """,
    
    "02-Module-2-Simulation": """
    Write a detailed technical textbook chapter titled 'Module 2: The Digital Twin (Gazebo & Unity)'.
    Cover:
    - Physics simulation and environment building.
    - Simulating physics, gravity, and collisions in Gazebo.
    - High-fidelity rendering and human-robot interaction in Unity.
    - Simulating sensors: LiDAR, Depth Cameras, and IMUs.
    Format in Markdown for Docusaurus.
    """,
    
    "03-Module-3-Isaac-Sim": """
    Write a detailed technical textbook chapter titled 'Module 3: The AI-Robot Brain (NVIDIA Isaac)'.
    Cover:
    - NVIDIA Isaac Sim: Photorealistic simulation and synthetic data generation.
    - Isaac ROS: Hardware-accelerated VSLAM (Visual SLAM) and navigation.
    - Nav2: Path planning for bipedal humanoid movement.
    Format in Markdown for Docusaurus.
    """,
    
    "04-Module-4-VLA": """
    Write a detailed technical textbook chapter titled 'Module 4: Vision-Language-Action (VLA)'.
    Cover:
    - The convergence of LLMs and Robotics.
    - Voice-to-Action: Using OpenAI Whisper for voice commands.
    - Cognitive Planning: Using LLMs to translate natural language into ROS 2 actions.
    - Capstone Project: The Autonomous Humanoid.
    Format in Markdown for Docusaurus.
    """
}

# 3. Generation Loop
print("🚀 Book Generation Started... (Ismein thoda time lagega)")

if not os.path.exists("generated_chapters"):
    os.makedirs("generated_chapters")

for filename, prompt in chapters.items():
    print(f"✍️ Writing {filename}...")
    try:
        response = model.generate_content(prompt)
        
        # File save karna
        with open(f"generated_chapters/{filename}.md", "w", encoding="utf-8") as f:
            # Docusaurus Header add kar rahe hain
            f.write(f"---\nid: {filename}\ntitle: {filename.replace('-', ' ')}\n---\n\n")
            f.write(response.text)
            
        print(f"✅ Saved: {filename}.md")
    except Exception as e:
        print(f"❌ Error in {filename}: {e}")

print("🎉 All Chapters Written Successfully!")