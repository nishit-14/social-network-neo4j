# Social Network Neo4j Console App

This project is a basic console-based social networking application. It uses Python for the interface and Neo4j as the graph database backend. Users are stored as `User` nodes, and directed follow relationships are stored as `FOLLOWS` edges.

## Technologies Used

- Python 3
- Neo4j
- Neo4j Python driver
- pandas
- python-dotenv

## Dataset Source

The project uses the public SNAP ego-Twitter dataset:

https://snap.stanford.edu/data/ego-Twitter.html

The full dataset is large, so this project samples the first 20,000 directed edges from `twitter_combined.txt`. Users are then extracted from those sampled edges. In the current processed sample, the graph contains 1,102 users and 19,992 follow relationships.

## Project Structure

```text
social-network-neo4j/
├── app.py
├── db.py
├── load_data.py
├── process_dataset.py
├── requirements.txt
├── README.md
├── data/
│   ├── raw/
│   │   └── twitter_combined.txt        # optional, only needed for reprocessing
│   └── processed/
│       ├── users.csv
│       └── follows.csv
```

## Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Neo4j Setup

This project uses Neo4j as the backend database. The recommended setup is Neo4j Aura, Neo4j's cloud database service.

1. Create or open a Neo4j Aura database instance.
2. Copy the connection URI, username, password, and database name.
3. Create a `.env` file in the project root.

Example `.env` file:

```text
NEO4J_URI=neo4j+s://your-database.databases.neo4j.io
NEO4J_USERNAME=your_username
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
```

If using a local Neo4j database instead of Aura, the URI and username are often:

```text
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_local_neo4j_password
NEO4J_DATABASE=neo4j
```

Use the password that was set when the local Neo4j database was created.

The `.env` file is not committed to the repository because it contains database credentials.

## Running With an Already-Loaded Database

If the Neo4j database already contains the project data, you do not need the raw SNAP dataset and you do not need to run the processing or loading scripts.

After creating `.env`, run:

```bash
python app.py
```

The app connects directly to Neo4j and uses the data already loaded in the database.

## Download the Dataset

This section is only needed if you want to rebuild the processed CSV files or load the database from scratch.

1. Visit https://snap.stanford.edu/data/ego-Twitter.html
2. Download the Twitter combined network file.
3. Extract or place the edge list file at:

```text
data/raw/twitter_combined.txt
```

Each line should contain two user IDs:

```text
source_user target_user
```

This means `source_user` follows `target_user`.

## Process the Dataset

Only run this step if `data/raw/twitter_combined.txt` is available.

Run:

```bash
python process_dataset.py
```

This reads the first 20,000 valid edges, extracts unique users, generates simple fake profile fields, and creates:

```text
data/processed/users.csv
data/processed/follows.csv
```

`users.csv` columns:

```text
userId,name,username,email,password,bio
```

`follows.csv` columns:

```text
source,target
```

## Load Data Into Neo4j

Only run this step if you want to load or reload the database from the processed CSV files.

Run:

```bash
python load_data.py
```

The loader will ask whether to clear existing `User` and `FOLLOWS` data. It then creates these constraints:

```cypher
CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User)
REQUIRE u.userId IS UNIQUE;

CREATE CONSTRAINT username_unique IF NOT EXISTS
FOR (u:User)
REQUIRE u.username IS UNIQUE;
```

Then it loads users and relationships in batches.

## Run the App

Run:

```bash
python app.py
```

The console menu supports:

1. Register
2. Login
3. View Profile
4. Edit Profile
5. Follow User
6. Unfollow User
7. View Followers/Following
8. View Mutual Connections
9. Get Friend Recommendations
10. Search Users
11. Explore Popular Users
12. Logout
13. Exit

## Trying the Features

Use imported accounts such as `user12345` with password `pass12345`, replacing `12345` with an actual user ID from `data/processed/users.csv`.

1. User Registration: Choose option 1 and create a new user.
2. User Login: Choose option 2 and login with the new user or an imported user.
3. View Profile: Choose option 3 while logged in.
4. Edit Profile: Choose option 4 and update profile fields.
5. Follow Another User: Choose option 5 and enter another username.
6. Unfollow a User: Choose option 6 and enter a followed username.
7. View Friends/Connections: Choose option 7 to see following and followers separately.
8. Mutual Connections: Choose option 8 and enter another username.
9. Friend Recommendations: Choose option 9.
10. Search Users: Choose option 10 and search by name or username.
11. Explore Popular Users: Choose option 11.

## Notes on Local Files

The `.env` file contains Neo4j connection settings and should be kept local. The `.venv/` folder is also local because it contains installed Python packages that can be recreated with `pip install -r requirements.txt`.

The raw SNAP dataset files are only needed when rebuilding `users.csv` and `follows.csv` from scratch. If the Neo4j database is already loaded, the app can run without the raw dataset files.
