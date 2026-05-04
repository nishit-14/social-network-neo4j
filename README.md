# Social Network Neo4j Console App

This project is a basic social networking application for a graph database class. It uses Python for a console interface and Neo4j as the graph database backend. Users are stored as `User` nodes, and directed follow relationships are stored as `FOLLOWS` edges.

## Technologies Used

- Python 3
- Neo4j
- Neo4j Python driver
- pandas
- python-dotenv

## Dataset Source

The project uses the public SNAP ego-Twitter dataset:

https://snap.stanford.edu/data/ego-Twitter.html

The full dataset is large, so this project samples the first 20,000 directed edges from `twitter_combined.txt`. Users are then extracted from those sampled edges. This produces thousands of users and tens of thousands of relationships, satisfying the project requirement of at least 1,000 nodes and 5,000 relationships without loading the entire dataset.

## Project Structure

```text
social-network-neo4j/
├── app.py
├── db.py
├── load_data.py
├── process_dataset.py
├── requirements.txt
├── README.md
├── cypher_queries.md
├── report_notes.md
├── data/
│   ├── raw/
│   │   └── twitter_combined.txt
│   └── processed/
│       ├── users.csv
│       └── follows.csv
└── screenshots/
    └── put_screenshots_here.txt
```

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Start Neo4j locally. The default connection settings are:

```text
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

You can override these with environment variables or by creating a `.env` file:

```text
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j
```

## Download the Dataset

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

## Testing the 11 Use Cases

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

## Screenshots for the Report

Take one screenshot per use case while running the console app. Store the screenshots in the `screenshots/` folder. Good screenshots should show:

- The selected menu option
- The user input
- The resulting output
- Evidence that the Cypher-backed feature worked

The `report_notes.md` file includes placeholders for all 11 screenshots and short explanations.

## Packaging

The final submission can be zipped as:

```text
projects.zip
├── report.pdf
└── social-network-neo4j/
    ├── app.py
    ├── db.py
    ├── load_data.py
    ├── process_dataset.py
    ├── requirements.txt
    ├── README.md
    ├── cypher_queries.md
    ├── report_notes.md
    └── data/
```
