# AreoVis 
> *Project developed during Spaceshield Hack 2026*

## About The Project
AreoVis is a next-generation emergency response platform inspired by the standard 112 dispatch system. It combines a user-facing web application for incident reporting with an AI-powered dispatcher and a real-time 3D drone flight simulation. The goal of the system is to drastically reduce response times and improve situational awareness for emergency units (Police, Fire Department, etc.) by deploying reconnaissance drones directly to the incident area.

## Key Features

### 1. Web-Based Reporting Application
Users can quickly report ongoing emergencies (e.g., assault, fire, riots) through a dedicated web interface.
* **Interactive Map:** Pinpoint the exact location of the incident.
* **Detailed Descriptions:** Add critical context and text descriptions to the report.
* **Instant Dispatch:** One-click submission to the centralized system.
<img width="368" height="634" alt="Mapa" src="https://github.com/user-attachments/assets/9f36c871-ce85-435d-b965-fd0cce96bc5c" />
<br><br>
<img width="608" height="383" alt="Rekomendacja" src="https://github.com/user-attachments/assets/64f63c01-326c-47eb-9b96-b555b4faf7cf" />

### 2. AI Dispatcher & Triage
Once a report is submitted, our integrated AI model takes over the triage process.
* **Intelligent Routing:** The AI analyzes the event type and description to determine which specific emergency unit (e.g., Fire Department, Police) should handle it.
* **Transparent Reasoning:** The AI provides a detailed explanation of *why* a drone was dispatched and why a specific unit was selected.

### 3. Dedicated Monitoring Dashboards
The system features a multi-tiered dashboard architecture to manage incoming crises:
* **Global Command Panel:** A master view showing all active reports, AI reasoning, and current drone dispatch status.
* **Unit-Specific Panels:** Separate, secure views tailored for individual emergency units (e.g., a specific dashboard just for the Fire Department).
* **Crisis Resolution:** Once the situation is under control, operators can mark the incident as "Resolved" directly from the dashboard.

<p align="center">
  <img alt="LOG" src="https://github.com/user-attachments/assets/8690acc9-c2bd-4129-8503-000114f7e6b3" width="28%" />
  <img alt="AI" src="https://github.com/user-attachments/assets/305bb24f-92fb-4ee0-bfa8-92ac12815bec" width="70%" />
</p>

### 4. 3D Drone Flight Simulation
To visualize the drone's path to the emergency, we implemented a fully functional 3D simulation.
* **Stalowa Wola 3D Map:** A realistic, generated 3D environment based on the city of Stalowa Wola.
* **Manual Controller Support:** Users can manually pilot the drone through the city towards the target using a physical controller.
* **Real-time Camera Feed:** Simulates the visual data an operator would see during an actual drone flight.

<img width="932" height="391" alt="image" src="https://github.com/user-attachments/assets/66dfc1f9-c471-4ecd-aa43-02d0a93db04e" />
<br><br>
<img width="935" height="394" alt="image" src="https://github.com/user-attachments/assets/e8707f9e-15e8-489c-a498-2661c8073455" />
<br><br>
<img width="928" height="393" alt="image" src="https://github.com/user-attachments/assets/42a53c92-4067-4f4b-8711-7da3adbc74fd" />

---

## Architecture & Technologies
* **Frontend:** HTML, CSS
* **Backend:** Flask (Python)
* **AI Integration:** Ollama
* **Simulation Engine:** Unreal Engine
* **Input Control:** PyGame (used for handling the physical controller inputs for manual drone piloting)

---

## Repository Structure
*Since the 3D simulation files are too large to be fully hosted on GitHub, this repository contains the core logic and web application codebase.*

* `/UnrealAssets` - Some of Unreal Assets we have used
* `/UnrealPycode` - Gamepad input handler script 
* `/steel_will_2067` - Website code

---

## The Team
This project was successfully built by a multidisciplinary team during the Spaceshield Hack 2026:

* **Jakub**: Simulation
* **Grzegorz**: Simulation
* **Kamil**: Website Development
* **Paulina**: Design & Research
* **Katarzyna**: Design & Graphics
* **Krzysztof**: Research & Graphics
