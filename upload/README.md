1. Use Python + Watchdog (monitor directory)
2. Use Selenium (for login + navigation + upload)
3. Use Playwright instead of Selenium
    Playwright is:
        faster
        more stable
        more resistant to dynamic content
        easier logins
        better error recovery

Optional Advanced Features
You can add:
    Automatic retry
    Logging
    Email/SMS alerts
    Queueing system (RabbitMQ / Redis)
    Persistent task memory
    Vision inspection of UI (“Is the upload button visible?”)
    Automatic solving of MFA using TOTP secure tokens
    Headless mode running on a server
    Daily summary reports