# ZAD ACADEMY

Gamified, Duolingo-inspired skill learning platform with a cyber-gaming theme.

## Included
- Flask/Python backend and SQLite persistence
- Responsive PWA install support
- Registration/login, course map, lessons and quiz checks
- XP, streaks, progress, leaderboard and profile
- Premium request workflow with manual UTR review
- Admin course/lesson management, user XP adjustment, payment approval
- Seed courses: cybersecurity, networking, Python, HTML/CSS, Java, web security, SQL, Linux and AI
- Safe cybersecurity curriculum focused on authorized practice

## Deploy on Render
1. Push this folder to a GitHub repository.
2. Create a Render Web Service from the repo (or use the included `render.yaml`).
3. Set `ADMIN_PASSWORD` to a strong unique password and keep `SECRET_KEY` private.
4. For persistent SQLite storage, attach a Render persistent disk at `/var/data`.
5. Deploy. Visit `/health` to check service health.

Default admin email: `admin@zadacademy.local`
Admin password: set the `ADMIN_PASSWORD` environment variable before first deployment. If unset, the local development default is `ChangeMe123!`; never use that default on a public deployment.

## Firebase
This starter is deployable without Firebase credentials using SQLite. Firebase is not required for the core MVP. To add Firebase/Firestore, configure a service account securely as an environment secret and implement the adapter before switching storage. Do not upload service-account JSON or private keys to GitHub.

## Payments
This build intentionally does not claim automatic payment gateway verification. Premium requests collect a payment reference and remain pending until an admin manually verifies the transaction in the admin panel. Connect a real payment provider's documented server-side API and webhook before enabling automatic activation. Never trust a browser-only "payment successful" message.

## PWA
The app includes a manifest and service worker for installability and basic offline caching of the shell. Dynamic account pages and lesson submissions require an internet connection.
