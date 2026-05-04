# Cypher Queries for Social Network Use Cases

## UC-1: User Registration

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

## UC-2: User Login

```cypher
MATCH (u:User {username: $username, password: $password})
RETURN u
```

## UC-3: View Profile

```cypher
MATCH (u:User {username: $username})
RETURN u.userId AS userId,
       u.name AS name,
       u.username AS username,
       u.email AS email,
       u.bio AS bio
```

## UC-4: Edit Profile

```cypher
MATCH (u:User {username: $username})
SET u.name = $name,
    u.email = $email,
    u.password = $password,
    u.bio = $bio
RETURN u
```

## UC-5: Follow Another User

```cypher
MATCH (a:User {username: $currentUser})
MATCH (b:User {username: $targetUser})
WHERE a <> b
MERGE (a)-[:FOLLOWS]->(b)
RETURN a.username AS follower, b.username AS following
```

## UC-6: Unfollow a User

```cypher
MATCH (a:User {username: $currentUser})-[r:FOLLOWS]->(b:User {username: $targetUser})
DELETE r
RETURN a.username AS unfollower, b.username AS unfollowed
```

## UC-7: View Friends/Connections

People the user follows:

```cypher
MATCH (u:User {username: $username})-[:FOLLOWS]->(following:User)
RETURN following.username AS username, following.name AS name
ORDER BY following.username
LIMIT 50
```

People who follow the user:

```cypher
MATCH (follower:User)-[:FOLLOWS]->(u:User {username: $username})
RETURN follower.username AS username, follower.name AS name
ORDER BY follower.username
LIMIT 50
```

## UC-8: Mutual Connections

```cypher
MATCH (u1:User {username: $currentUser})-[:FOLLOWS]->(mutual:User)<-[:FOLLOWS]-(u2:User {username: $otherUser})
RETURN mutual.username AS username, mutual.name AS name
ORDER BY mutual.username
LIMIT 50
```

## UC-9: Friend Recommendations

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

## UC-10: Search Users

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

## UC-11: Explore Popular Users

```cypher
MATCH (u:User)<-[:FOLLOWS]-(follower:User)
RETURN u.username AS username,
       u.name AS name,
       COUNT(follower) AS followerCount
ORDER BY followerCount DESC
LIMIT 10
```

## Database Setup Queries

```cypher
CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User)
REQUIRE u.userId IS UNIQUE;

CREATE CONSTRAINT username_unique IF NOT EXISTS
FOR (u:User)
REQUIRE u.username IS UNIQUE;
```
