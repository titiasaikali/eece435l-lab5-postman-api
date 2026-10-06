# Lab 5 - Postman and APIs

Flask user management API backed by SQLite, with the five routes required by the lab.

## Run

From this folder in PowerShell:

```powershell
.\.venv\Scripts\python.exe app.py
```

The virtual environment and dependencies have been installed. For a fresh checkout:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

The app creates `database.db` automatically. Python includes sqlite3; a separate db-sqlite3 package is unnecessary. CORS is enabled as in the lab.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | /api/users | List users |
| GET | /api/users/1 | Read user 1 |
| POST | /api/users/add | Create user |
| PUT | /api/users/update | Update user, including user_id in JSON |
| DELETE | /api/users/delete/1 | Delete user 1 |

Add/update JSON includes name, email, phone, address and country as nonempty strings. Successful requests return HTTP 200, matching the lab. Invalid bodies return 400; missing users return 404. SQL statements use parameters and connections are closed after use.

## Graded Postman exercise

1. Start the Flask app with the command above.
2. Open Postman and create/select a workspace for Lab5.
3. Import both JSON files in `postman/`.
4. Select the **Lab5 Local** environment. Its `base_url` stores the API URL; every request uses `{{base_url}}`.
5. Run the **Flask user app** collection in numbered order. Add user automatically saves `user_id`; subsequent requests use it. The update and delete operate only on the user created by that run.
6. Each request already contains a saved example captured from a real HTTP response. Open a request's example to inspect it. To capture another example in Postman, send the request and choose Save Response / Save as example.
7. While the app is running, open `http://127.0.0.1:5000/api/users` in a browser. After Add user, use the returned ID in `/api/users/<id>` to check the second GET route.

The collection includes assertions for each response. Re-run the whole collection rather than starting at an update/delete request.

Tutorial references from the handout: [Postman quick start](https://learning.postman.com/docs/getting-started/quick-start/) and [sending requests](https://learning.postman.com/docs/use/send-requests/requests/).

## Verification

```powershell
.\.venv\Scripts\python.exe verify_and_export.py
```

This exercises the API over real local HTTP using a temporary database, verifies CRUD and invalid requests, and regenerates the saved examples plus `verification.json`. It leaves the application's database untouched.

## GitHub submission

The project is uploaded to [titiasaikali/eece435l-lab5-postman-api](https://github.com/titiasaikali/eece435l-lab5-postman-api). Both main and feature/rest-api are on GitHub. Git history contains the database commit, a REST API feature branch, and its merge into main.

The repository is private. Give your instructor access before submitting the link, or change visibility to public if your course requires it.

The feature branch was created locally from the database commit; the handout's intermediate remote pull was not performed. Postman workspace import, browser viewing, and any screenshots required by your instructor remain account/UI steps; the exports and HTTP verification do not claim those actions were performed.
