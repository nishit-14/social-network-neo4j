# Report Notes

## 1. Team Info

- Team Member 1: Name, email
- Team Member 2: Name, email
- Team Member 3: Name, email
- Team Member 4: Name, email

## 2. Property Graph Schema

Users are represented as `User` nodes.

Follow relationships are represented as directed `FOLLOWS` relationships.

Schema:

```cypher
(:User)-[:FOLLOWS]->(:User)
```

User node properties:

```text
userId, name, username, email, password, bio
```

Relationship:

```text
FOLLOWS
```

The direction matters. If `(:User {username: "user1"})-[:FOLLOWS]->(:User {username: "user2"})`, then `user1` follows `user2`.

## 3. Dataset Information

We used the SNAP ego-Twitter dataset.

The original dataset contains many Twitter users and follower relationships. Because the full dataset is large, we sampled around 20,000 edges and extracted the users from those edges.

This still satisfies the class requirement of at least 1,000 nodes and 5,000 relationships.

Dataset source:

```text
https://snap.stanford.edu/data/ego-Twitter.html
```

## 4. Raw Data Processing

The raw file contains pairs of user IDs. Each row represents one directed follow relationship.

Example:

```text
source_user target_user
```

This means `source_user` follows `target_user`.

The processing script `process_dataset.py`:

- Reads `data/raw/twitter_combined.txt`
- Takes the first 20,000 valid edges
- Extracts unique user IDs from those edges
- Generates fake profile fields for each user
- Creates `data/processed/users.csv`
- Creates `data/processed/follows.csv`

## 5. Use Case Evidence

### UC-1: User Registration

- Screenshot placeholder: `screenshots/uc01_registration.png`
- What the screenshot should show: A new user being registered successfully.
- Cypher query used:

```cypher
CREATE (:User {
  userId: $userId,
  name: $name,
  email: $email,
  username: $username,
  password: $password,
  bio: $bio
})
```

- Explanation: The app collects profile fields and creates a new `User` node.

### UC-2: User Login

- Screenshot placeholder: `screenshots/uc02_login.png`
- What the screenshot should show: A user logging in with username and password.
- Cypher query used:

```cypher
MATCH (u:User {username: $username, password: $password})
RETURN u
```

- Explanation: The app authenticates by matching a `User` node with the entered credentials.

### UC-3: View Profile

- Screenshot placeholder: `screenshots/uc03_view_profile.png`
- What the screenshot should show: The logged-in user's profile fields.
- Cypher query used:

```cypher
MATCH (u:User {username: $username})
RETURN u.userId AS userId,
       u.name AS name,
       u.username AS username,
       u.email AS email,
       u.bio AS bio
```

- Explanation: The app retrieves the current user's profile information.

### UC-4: Edit Profile

- Screenshot placeholder: `screenshots/uc04_edit_profile.png`
- What the screenshot should show: Profile fields being updated.
- Cypher query used:

```cypher
MATCH (u:User {username: $username})
SET u.name = $name,
    u.email = $email,
    u.password = $password,
    u.bio = $bio
RETURN u
```

- Explanation: The app updates editable profile fields on the current user's node.

### UC-5: Follow Another User

- Screenshot placeholder: `screenshots/uc05_follow_user.png`
- What the screenshot should show: The logged-in user following another user.
- Cypher query used:

```cypher
MATCH (a:User {username: $currentUser})
MATCH (b:User {username: $targetUser})
WHERE a <> b
MERGE (a)-[:FOLLOWS]->(b)
RETURN a.username AS follower, b.username AS following
```

- Explanation: The app creates a directed `FOLLOWS` relationship and uses `MERGE` to prevent duplicates.

### UC-6: Unfollow a User

- Screenshot placeholder: `screenshots/uc06_unfollow_user.png`
- What the screenshot should show: A follow relationship being removed.
- Cypher query used:

```cypher
MATCH (a:User {username: $currentUser})-[r:FOLLOWS]->(b:User {username: $targetUser})
DELETE r
RETURN a.username AS unfollower, b.username AS unfollowed
```

- Explanation: The app deletes the directed `FOLLOWS` relationship between two users.

### UC-7: View Friends/Connections

- Screenshot placeholder: `screenshots/uc07_connections.png`
- What the screenshot should show: Separate following and follower lists.
- Cypher query used:

```cypher
MATCH (u:User {username: $username})-[:FOLLOWS]->(following:User)
RETURN following.username AS username, following.name AS name
ORDER BY following.username
LIMIT 50
```

```cypher
MATCH (follower:User)-[:FOLLOWS]->(u:User {username: $username})
RETURN follower.username AS username, follower.name AS name
ORDER BY follower.username
LIMIT 50
```

- Explanation: The app shows outgoing and incoming relationships separately.

### UC-8: Mutual Connections

- Screenshot placeholder: `screenshots/uc08_mutual_connections.png`
- What the screenshot should show: Users followed by both the current user and another user.
- Cypher query used:

```cypher
MATCH (u1:User {username: $currentUser})-[:FOLLOWS]->(mutual:User)<-[:FOLLOWS]-(u2:User {username: $otherUser})
RETURN mutual.username AS username, mutual.name AS name
ORDER BY mutual.username
LIMIT 50
```

- Explanation: The app finds common outgoing follow targets.

### UC-9: Friend Recommendations

- Screenshot placeholder: `screenshots/uc09_recommendations.png`
- What the screenshot should show: Recommended users and common connection counts.
- Cypher query used:

```cypher
MATCH (u:User {username: $username})-[:FOLLOWS]->(:User)-[:FOLLOWS]->(rec:User)
WHERE NOT (u)-[:FOLLOWS]->(rec)
  AND u <> rec
RETURN rec.username AS username,
       rec.name AS name,
       COUNT(*) AS commonConnections
ORDER BY commonConnections DESC
LIMIT 10
```

- Explanation: The app recommends second-degree connections that the user does not already follow.

### UC-10: Search Users

- Screenshot placeholder: `screenshots/uc10_search_users.png`
- What the screenshot should show: Search results for a name or username.
- Cypher query used:

```cypher
MATCH (u:User)
WHERE toLower(u.name) CONTAINS toLower($searchText)
   OR toLower(u.username) CONTAINS toLower($searchText)
RETURN u.username AS username,
       u.name AS name,
       u.email AS email,
       u.bio AS bio
LIMIT 20
```

- Explanation: The app performs a case-insensitive search over names and usernames.

### UC-11: Explore Popular Users

- Screenshot placeholder: `screenshots/uc11_popular_users.png`
- What the screenshot should show: Top users ranked by follower count.
- Cypher query used:

```cypher
MATCH (u:User)<-[:FOLLOWS]-(follower:User)
RETURN u.username AS username,
       u.name AS name,
       COUNT(follower) AS followerCount
ORDER BY followerCount DESC
LIMIT 10
```

- Explanation: The app counts incoming `FOLLOWS` relationships and lists the users with the most followers.
