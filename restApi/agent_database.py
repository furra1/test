import sqlite3

class agent_db:
    def __init__(self, db_path="agents.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        db = sqlite3.connect(self.db_path)
        cur = db.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS AGENTS (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            location TEXT,
            ip TEXT,
            status TEXT DEFAULT 'inactive',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_heartbeat TIMESTAMP
            )
            """
        )
        db.commit()
        db.close()
    
    def create_agent(self, name, location, ip, token):
        db = sqlite3.connect(self.db_path)
        cur = db.cursor()
        cur.execute(
            """
            REPLACE INTO AGENTS (name, location, ip, token, status)
            VALUES (?,?,?,?, 'awaiting_heartbeat')
            """,
            (name, location, ip, token)
        )
        agent_id = cur.lastrowid
        db.commit()
        db.close()
        return agent_id
    
    def get_agent_by_token(self, token):
            db = sqlite3.connect(self.db_path)
            cur = db.cursor()
            cur.execute(
                '''
                SELECT id, name, token, location, ip, status, created_at, last_heartbeat
                FROM agents WHERE token = ?
                ''',
                (token,)
            )
            row = cur.fetchone()
            db.close()
            if row:
                return {
                    "id": row[0],
                    "name": row[1],
                    "token": row[2],
                    "location": row[3],
                    "ip": row[4],
                    "status": row[5],
                    "created_at": row[6],
                    "last_heartbeat": row[7]
                }
            return None
    
    def update_heartbeat(self, agent_id):
        db = sqlite3.connect(self.db_path)
        cur = db.cursor()
        cur.execute(
            """
            UPDATE AGENTS
            SET last_heartbeat = CURRENT_TIMESTAMP, status = 'active'
            WHERE id = ?
            """,
            (agent_id,)
        )
        db.commit()
        db.close()
    
    def get_all_agents(self):
        db = sqlite3.connect(self.db_path)
        cur = db.cursor()
        cur.execute(
            """
            SELECT id, name, location, ip, status, created_at, last_heartbeat
            FROM AGENTS
            """
        )
        agents = []
        for row in cur.fetchall():
            agents.append({
                "id": row[0],
                "name": row[1],
                "location": row[2],
                "ip": row[3],
                "status": row[4],
                "created_at": row[5],
                "last_heartbeat": row[6]
            })
        db.close()
        return agents

if __name__ == "__main__":
    adb = agent_db()
    #adb.create_agent("test agent", "Russia", "00.000.0.000", "2")
    adb.update_heartbeat(1)
    print(adb.get_agent_by_token("1"))
    print(adb.get_all_agents())