# Lab 5 - Postman and APIs

Flask user management API backed by SQLite, including GET, POST, PUT, PATCH and DELETE requests.

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

The repository includes `database.db`, a valid SQLite database with the users table and no personal records. The app creates the table automatically if needed. Python includes sqlite3; a separate db-sqlite3 package is unnecessary. CORS is enabled as in the lab.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | /api/users | List users |
| GET | /api/users/1 | Read user 1 |
| POST | /api/users/add | Create user |
| PUT | /api/users/update | Update user, including user_id in JSON |
| PATCH | /api/users/1 | Update only supplied fields for user 1 |
| DELETE | /api/users/delete/1 | Delete user 1 |

POST/PUT JSON includes name, email, phone, address and country as nonempty strings. PATCH accepts a nonempty subset of those fields, for example `{"country":"Lebanon"}`, and preserves the other fields. Successful requests return HTTP 200, matching the lab. Invalid bodies return 400; missing users return 404. SQL statements use parameters and connections are closed after use.

## Graded Postman exercise

1. Start the Flask app with the command above.
2. Open Postman and create/select a workspace for Lab5.
3. Import both JSON files in `postman/`.
4. Select the **Lab5 Local** environment, or create an environment with just one variable: `base_url` = `http://localhost:5000`. Every request uses `{{base_url}}`.
5. Run the **Flask user app** collection in numbered order. Add user automatically saves `user_id`; subsequent requests use it. The update and delete operate only on the user created by that run.
6. Each request already contains a saved example captured from a real HTTP response. Open a request's example to inspect it. To capture another example in Postman, send the request and choose Save Response / Save as example.
7. While the app is running, open `http://127.0.0.1:5000/api/users` in a browser. After Add user, use the returned ID in `/api/users/<id>` to check the second GET route.

The collection includes assertions for each response. Re-run the whole collection rather than starting at an update/delete request.

## API request screenshots

The [snapshots](snapshots/) folder contains browser screenshots of live API requests and corresponding actual responses. They were captured using the included browser API client, not Postman. [requests-and-results.json](snapshots/requests-and-results.json) contains the request bodies and responses used for those screenshots.

| Snapshot | Evidence |
| --- | --- |
| [01](snapshots/01-get-empty.png) | GET: initial empty list |
| [02](snapshots/02-post-create.png) | POST: create user |
| [03](snapshots/03-get-list.png) | GET: list users |
| [04](snapshots/04-get-user.png) | GET: retrieve user by ID |
| [05](snapshots/05-put-update.png) | PUT: update user |
| [06](snapshots/06-patch-update.png) | PATCH: update only country |
| [07](snapshots/07-get-after-update.png) | GET: verify persisted updates |
| [08](snapshots/08-delete-user.png) | DELETE: remove user |
| [09](snapshots/09-get-after-delete.png) | GET: confirm empty list after deletion |
| [10](snapshots/10-get-not-found.png) | GET: deleted user returns 404 |

To reproduce screenshots, install the optional capture dependency and ensure Microsoft Edge is installed and port 5000 is free:

```powershell
.\.venv\Scripts\python.exe -m pip install playwright
.\.venv\Scripts\python.exe capture_snapshots.py
```

The capture script starts and stops its own server with an isolated temporary database. It leaves the submitted `database.db` untouched.

Tutorial references from the handout: [Postman quick start](https://learning.postman.com/docs/getting-started/quick-start/) and [sending requests](https://learning.postman.com/docs/use/send-requests/requests/).

## Verification

```powershell
.\.venv\Scripts\python.exe verify_and_export.py
```

This exercises the API over real local HTTP using a temporary database, verifies CRUD and invalid requests, and regenerates the saved examples plus `verification.json`. It leaves the application's database untouched.

## GitHub submission

The project is uploaded to [titiasaikali/eece435l-lab5-postman-api](https://github.com/titiasaikali/eece435l-lab5-postman-api). Both main and feature/rest-api are on GitHub. Git history contains the database commit, a REST API feature branch, and its merge into main.

The repository is public. Your instructor can open the submission link without signing in or requesting access.

The feature branch was created locally from the database commit; the handout's intermediate remote pull was not performed. The importable Postman collection and live browser screenshots are included. No signed-in Postman workspace is required to use the collection.
