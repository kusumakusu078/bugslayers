ResilientAid is an offline-first, browser-based emergency command dashboard designed to provide critical coordination during urban crises. Developed for the Bangalore Mesh Protocol, it transforms any mobile device into a localized disaster hub—enabling incident reporting, community resource bartering, and SOS signaling via the Web Audio API without requiring active internet connectivity. By leveraging PWA architecture and localized grid nodes (like Indiranagar and HSR Layout), ResilientAid ensures that communication remains a utility, not a luxury, when traditional networks fail.

This Flask-powered backend acts as a centralized coordination server for the ResilientAid mesh network. It provides a lightweight, scalable API designed to manage emergency data across local devices.
 Core Backend Features
Network-Wide Accessibility: Configured to bind to 0.0.0.0:5005, allowing mobile devices on the local network to bypass typical connectivity barriers.
Automated Data Persistence: Uses a SQLite3 engine to store, index, and retrieve emergency reports, ensuring a permanent "Source of Truth" even during power loss.
Universal CORS Integration: Employs Flask-CORS to enable seamless, cross-origin communication between disparate browser-based nodes.
Live Broadcast Endpoints: Features dedicated routes for submitting new incident packets (/submit) and synchronizing the full network feed (/reports).

GPS feature of ResilianceAid has been updated and Upgraded
