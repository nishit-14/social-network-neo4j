"""Convert a SNAP ego-Twitter edge list into users.csv and follows.csv."""

from pathlib import Path

import pandas as pd


RAW_PATH = Path("data/raw/twitter_combined.txt")
USERS_PATH = Path("data/processed/users.csv")
FOLLOWS_PATH = Path("data/processed/follows.csv")
EDGE_SAMPLE_SIZE = 20_000


def read_edge_sample(raw_path=RAW_PATH, limit=EDGE_SAMPLE_SIZE):
    """Read the first N valid directed edges from the SNAP text file."""
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Missing raw dataset file: {raw_path}\n"
            "Download twitter_combined.txt from "
            "https://snap.stanford.edu/data/ego-Twitter.html and place it there."
        )

    edges = []
    with raw_path.open("r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) != 2:
                continue
            source, target = parts
            if source == target:
                continue
            edges.append((source, target))
            if len(edges) >= limit:
                break

    if not edges:
        raise ValueError("No valid edges were found in the raw dataset file.")

    return edges


def build_users(edges):
    """Generate simple profile records for every user appearing in the edges."""
    user_ids = sorted({user_id for edge in edges for user_id in edge}, key=int)
    users = []
    for user_id in user_ids:
        users.append(
            {
                "userId": user_id,
                "name": f"User {user_id}",
                "username": f"user{user_id}",
                "email": f"user{user_id}@example.com",
                "password": f"pass{user_id}",
                "bio": "Imported Twitter user",
            }
        )
    return users


def save_processed_data(edges, users, users_path=USERS_PATH, follows_path=FOLLOWS_PATH):
    users_path.parent.mkdir(parents=True, exist_ok=True)
    follows_path.parent.mkdir(parents=True, exist_ok=True)

    users_df = pd.DataFrame(users)
    follows_df = pd.DataFrame(edges, columns=["source", "target"]).drop_duplicates()

    users_df.to_csv(users_path, index=False)
    follows_df.to_csv(follows_path, index=False)

    return users_df, follows_df


def main():
    try:
        print(f"Reading first {EDGE_SAMPLE_SIZE:,} edges from {RAW_PATH}...")
        edges = read_edge_sample()
        users = build_users(edges)
        users_df, follows_df = save_processed_data(edges, users)

        print("Processing complete.")
        print(f"Users written: {len(users_df):,} -> {USERS_PATH}")
        print(f"FOLLOWS relationships written: {len(follows_df):,} -> {FOLLOWS_PATH}")
    except (FileNotFoundError, ValueError) as exc:
        print(exc)


if __name__ == "__main__":
    main()
