# 🩺 Doctor Appointment System (Multi‑Agent Architecture)

**A conversational, multi‑agent appointment platform** that allows users to book, cancel, reschedule, and check doctor availability using coordinated autonomous agents.

---

## 🚀 Overview

This project implements a Doctor Appointment System using a multi‑agent architecture. A single **Supervisor Agent** routes user queries to specialized agents (Booking, Information, Cancellation, etc.), and each agent executes domain‑specific tools to manage appointments. The result is a resilient, modular, and easily‑extensible conversational scheduling system.

---

## 🔹 Key Features

* **Multi‑Agent Workflow** — Supervisor Agent dispatches requests to the correct sub‑agent.
* **Booking** — Book appointments by doctor, date/time, and user ID.
* **Cancellation & Rescheduling** — Cancel or reschedule existing appointments with validation.
* **Availability & Info** — Query doctor availability, working hours, and next open slots.
* **Tool-Based Actions** — Agents call structured tools (e.g. `set_appointment()`, `cancel_appointment()`) for deterministic behavior.
* **Conversational Interface** — Natural language friendly input handling and confirmation messages.
* **Audit & Validation** — Input validation, conflict detection, and basic audit logging.

---

## 🧭 System Architecture

<img width="486" height="249" alt="image" src="https://github.com/user-attachments/assets/bc4fa0ca-58cf-415a-a3e1-7980e249e3fa" />


* **Supervisor Agent**: Parses user intent, extracts entities (doctor name, date, time, ID), and chooses the appropriate agent by calling an internal `tool` or routing function.
* **Booking Agent**: Validates requested slot, checks doctor availability, creates appointment,cancel appointment,rescheduling appointment and returns confirmation.
* **Information Agent**: Reads availability, returns next available slots or full schedule for a doctor.


---





