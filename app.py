"""Console-based social networking app backed by Neo4j."""

import uuid

from neo4j.exceptions import Neo4jError

from db import get_connection


MENU = """

===== Social Network Menu =====
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
"""


def prompt(label, required=True, default=None):
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"{label}{suffix}: ").strip()
        if value:
            return value
        if default is not None:
            return default
        if not required:
            return ""
        print("This field is required.")


def require_login(current_user):
    if not current_user:
        print("Please login first.")
        return False
    return True


def print_user_list(title, rows, empty_message="No users found."):
    print(f"\n{title}")
    if not rows:
        print(empty_message)
        return
    for row in rows:
        details = [f"@{row.get('username')}", row.get("name")]
        if "email" in row:
            details.append(row.get("email"))
        if "followerCount" in row:
            details.append(f"{row.get('followerCount')} followers")
        if "commonConnections" in row:
            details.append(f"{row.get('commonConnections')} common connections")
        print(" - " + " | ".join(str(item) for item in details if item is not None))
        if row.get("bio") and "email" in row:
            print(f"   {row.get('bio')}")


def register(conn):
    print("\nCreate a new account")
    name = prompt("Name")
    email = prompt("Email")
    username = prompt("Username").lower()
    password = prompt("Password")
    bio = prompt("Bio", required=False)
    user_id = str(uuid.uuid4())

    query = """
    CREATE (:User {
      userId: $userId,
      name: $name,
      email: $email,
      username: $username,
      password: $password,
      bio: $bio
    })
    """
    try:
        conn.execute_write(
            query,
            userId=user_id,
            name=name,
            email=email,
            username=username,
            password=password,
            bio=bio,
        )
        print(f"Registration complete. You can now login as @{username}.")
    except Neo4jError as exc:
        print(f"Could not register user. Username may already exist. Details: {exc}")


def login(conn):
    print("\nLogin")
    username = prompt("Username").lower()
    password = prompt("Password")
    query = """
    MATCH (u:User {username: $username, password: $password})
    RETURN u.username AS username, u.name AS name
    """
    rows = conn.execute_read(query, username=username, password=password)
    if rows:
        print(f"Welcome, {rows[0]['name']} (@{rows[0]['username']}).")
        return rows[0]["username"]
    print("Invalid username or password.")
    return None


def view_profile(conn, username):
    query = """
    MATCH (u:User {username: $username})
    RETURN u.userId AS userId,
           u.name AS name,
           u.username AS username,
           u.email AS email,
           u.bio AS bio
    """
    rows = conn.execute_read(query, username=username)
    if not rows:
        print("Profile not found.")
        return
    user = rows[0]
    print("\nProfile")
    print(f"User ID : {user['userId']}")
    print(f"Name    : {user['name']}")
    print(f"Username: @{user['username']}")
    print(f"Email   : {user['email']}")
    print(f"Bio     : {user.get('bio') or ''}")


def edit_profile(conn, username):
    current = conn.execute_read(
        """
        MATCH (u:User {username: $username})
        RETURN u.name AS name, u.email AS email, u.password AS password, u.bio AS bio
        """,
        username=username,
    )
    if not current:
        print("Profile not found.")
        return

    user = current[0]
    print("\nEdit Profile. Press Enter to keep the current value.")
    name = prompt("Name", default=user["name"])
    email = prompt("Email", default=user["email"])
    password = prompt("Password", default=user["password"])
    bio = prompt("Bio", required=False, default=user.get("bio") or "")

    query = """
    MATCH (u:User {username: $username})
    SET u.name = $name,
        u.email = $email,
        u.password = $password,
        u.bio = $bio
    RETURN u.username AS username
    """
    conn.execute_write(
        query,
        username=username,
        name=name,
        email=email,
        password=password,
        bio=bio,
    )
    print("Profile updated.")


def follow_user(conn, current_user):
    target_user = prompt("Target username").lower()
    if target_user == current_user:
        print("You cannot follow yourself.")
        return
    query = """
    MATCH (a:User {username: $currentUser})
    MATCH (b:User {username: $targetUser})
    WHERE a <> b
    MERGE (a)-[:FOLLOWS]->(b)
    RETURN a.username AS follower, b.username AS following
    """
    rows = conn.execute_write(query, currentUser=current_user, targetUser=target_user)
    if rows:
        print(f"@{rows[0]['follower']} now follows @{rows[0]['following']}.")
    else:
        print("Target user was not found.")


def unfollow_user(conn, current_user):
    target_user = prompt("Target username").lower()
    query = """
    MATCH (a:User {username: $currentUser})-[r:FOLLOWS]->(b:User {username: $targetUser})
    WITH a, b, r
    DELETE r
    RETURN a.username AS unfollower, b.username AS unfollowed
    """
    rows = conn.execute_write(query, currentUser=current_user, targetUser=target_user)
    if rows:
        print(f"@{rows[0]['unfollower']} unfollowed @{rows[0]['unfollowed']}.")
    else:
        print("No matching follow relationship was found.")


def view_connections(conn, username):
    following_query = """
    MATCH (u:User {username: $username})-[:FOLLOWS]->(following:User)
    RETURN following.username AS username, following.name AS name
    ORDER BY following.username
    LIMIT 50
    """
    followers_query = """
    MATCH (follower:User)-[:FOLLOWS]->(u:User {username: $username})
    RETURN follower.username AS username, follower.name AS name
    ORDER BY follower.username
    LIMIT 50
    """
    following = conn.execute_read(following_query, username=username)
    followers = conn.execute_read(followers_query, username=username)
    print_user_list("People You Follow", following)
    print_user_list("People Who Follow You", followers)


def mutual_connections(conn, current_user):
    other_user = prompt("Other username").lower()
    query = """
    MATCH (u1:User {username: $currentUser})-[:FOLLOWS]->(mutual:User)<-[:FOLLOWS]-(u2:User {username: $otherUser})
    RETURN mutual.username AS username, mutual.name AS name
    ORDER BY mutual.username
    LIMIT 50
    """
    rows = conn.execute_read(query, currentUser=current_user, otherUser=other_user)
    print_user_list("Mutual Connections", rows, "No mutual connections found.")


def friend_recommendations(conn, username):
    query = """
    MATCH (u:User {username: $username})-[:FOLLOWS]->(:User)-[:FOLLOWS]->(rec:User)
    WHERE NOT (u)-[:FOLLOWS]->(rec)
      AND u <> rec
    RETURN rec.username AS username,
           rec.name AS name,
           COUNT(*) AS commonConnections
    ORDER BY commonConnections DESC
    LIMIT 10
    """
    rows = conn.execute_read(query, username=username)
    print_user_list("Friend Recommendations", rows, "No recommendations found.")


def search_users(conn):
    search_text = prompt("Search text")
    query = """
    MATCH (u:User)
    WHERE toLower(u.name) CONTAINS toLower($searchText)
       OR toLower(u.username) CONTAINS toLower($searchText)
    RETURN u.username AS username,
           u.name AS name,
           u.email AS email,
           u.bio AS bio
    LIMIT 20
    """
    rows = conn.execute_read(query, searchText=search_text)
    print_user_list("Search Results", rows)


def popular_users(conn):
    query = """
    MATCH (u:User)<-[:FOLLOWS]-(follower:User)
    RETURN u.username AS username,
           u.name AS name,
           COUNT(follower) AS followerCount
    ORDER BY followerCount DESC
    LIMIT 10
    """
    rows = conn.execute_read(query)
    print_user_list("Popular Users", rows)


def main():
    conn = None
    current_user = None
    try:
        conn = get_connection()
        while True:
            print(MENU)
            print(f"Logged in as: @{current_user}" if current_user else "Not logged in.")
            choice = input("Choose an option: ").strip()

            if choice == "1":
                register(conn)
            elif choice == "2":
                current_user = login(conn)
            elif choice == "3" and require_login(current_user):
                view_profile(conn, current_user)
            elif choice == "4" and require_login(current_user):
                edit_profile(conn, current_user)
            elif choice == "5" and require_login(current_user):
                follow_user(conn, current_user)
            elif choice == "6" and require_login(current_user):
                unfollow_user(conn, current_user)
            elif choice == "7" and require_login(current_user):
                view_connections(conn, current_user)
            elif choice == "8" and require_login(current_user):
                mutual_connections(conn, current_user)
            elif choice == "9" and require_login(current_user):
                friend_recommendations(conn, current_user)
            elif choice == "10":
                search_users(conn)
            elif choice == "11":
                popular_users(conn)
            elif choice == "12":
                current_user = None
                print("Logged out.")
            elif choice == "13":
                print("Goodbye.")
                break
            else:
                print("Invalid option. Please choose 1-13.")
    except (RuntimeError, Neo4jError) as exc:
        print(f"Application error: {exc}")
    except KeyboardInterrupt:
        print("\nGoodbye.")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    main()
