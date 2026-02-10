# Subscription Feature Implementation Plan

- [x] **Phase 1: Core Functionality**
    - [x] **1. Project Setup:**
        - [x] Add `geopy` to `requirements.txt`.
        - [x] Create initial empty files: `src/subscription_manager.py`, `src/utils/geo.py`, `src/utils/messaging.py`, `tests/test_geo.py`, `tests/test_subscription_manager.py`.
    - [x] **2. Database and Subscription Logic:**
        - [x] Implement `subscription_manager.py` to handle adding subscribers to a new `subscriptions.db` (SQLite).
        - [x] Implement geocoding logic within the subscription manager to convert location names to lat/lon using `geopy`.
    - [x] **3. Geolocation Utility:**
        - [x] Implement the Haversine distance formula in `src/utils/geo.py`.
        - [x] Write tests for the distance calculation in `tests/test_geo.py`.
    - [x] **4. Frontend Subscription UI:**
        -   [x] Modify `src/dashboard.py` to add input fields for email and location.
        -   [x] Connect the UI to the `subscription_manager.add_subscriber` function.
    - [x] **5. Non-Blocking Alerting Logic:**
        -   [x] Create a mock, non-blocking `EmailService` in `src/utils/messaging.py` that logs alerts to the console.
        -   [x] Modify `analyze_and_alert.py` to find subscribers within the 300km radius and pass them to the `EmailService` without blocking.
    - [x] **6. Integration Testing:**
        -   [x] Write tests for `analyze_and_alert.py` to verify that the correct subscribers are identified and passed to the email service.
        -   [x] Write tests for `subscription_manager.py`.

- [ ] **Phase 2: Production Hardening (Future Work)**
    - [ ] Replace the mock `EmailService` with a real email provider (e.g., SendGrid, Mailgun).
    - [ ] Replace the non-blocking simulation with a true message queue (e.g., RabbitMQ, Redis) and a separate worker process for sending emails.